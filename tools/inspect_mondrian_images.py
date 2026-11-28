#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the flashable images of the last aosp_mondrian build in out/.

Run by aosp17_mondrian_build.sh with STAGE=verify, without sync or build.
It prints what the bootloader and first stage init will meet:

- the AVB chain of vbmeta (avbtool verify_image --follow_chain_partitions):
  the hash descriptors of boot, vendor_boot, dtbo and recovery and the
  hashtrees of the logical partitions, recomputed from the images;
- the headers of boot.img and vendor_boot.img, their bootconfig and command
  line, and the files of their ramdisks (first stage init, fstab, module
  lists, AVB keys).

    inspect_mondrian_images.py <android tree>
"""
import gzip
import lzma
import struct
import subprocess
import sys
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
OUT = TREE / "out/target/product/mondrian"
HOST = TREE / "out/host/linux-x86/bin"
problems = []


def run(args, cwd=None):
    print("$", " ".join(str(a) for a in args), flush=True)
    p = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True)
    out = (p.stdout + p.stderr).rstrip()
    print(out[-20000:], flush=True)
    return p.returncode, out


def lz4_legacy(data):
    sys.path.insert(0, str(TREE / "device/xiaomi/sm8450-common/tools"))
    from stock_kernel import lz4_legacy as decode  # noqa: E402
    return decode(data)


def decompress(data):
    if data[:4] == b"\x02\x21\x4c\x18":
        return lz4_legacy(data)
    if data[:2] == b"\x1f\x8b":
        return gzip.decompress(data)
    if data[:6] == b"\xfd7zXZ\x00":
        return lzma.decompress(data)
    return data


def cpio_names(data):
    names, i = [], 0
    while i + 110 <= len(data):
        if data[i:i + 6] != b"070701":
            if data[i] == 0:
                i += 1
                continue
            problems.append(f"bad cpio header at {i}")
            break
        f = [int(data[i + 6 + 8 * k:i + 14 + 8 * k], 16) for k in range(13)]
        mode, size, namesize = f[1], f[6], f[11]
        name = data[i + 110:i + 110 + namesize - 1].decode()
        i = (i + 110 + namesize + 3) & ~3
        if name != "TRAILER!!!":
            names.append((name, mode, data[i:i + size]))
        i = (i + size + 3) & ~3
    return names


def show_ramdisk(label, raw):
    data = decompress(raw)
    files = cpio_names(data)
    print(f"{label}: {len(raw)} bytes compressed ({raw[:4].hex()}), {len(data)} bytes, {len(files)} entries")
    by_name = {n: (m, c) for n, m, c in files}
    for key in ("init", "system/bin/init", "first_stage_ramdisk/fstab.qcom", "fstab.qcom",
                "lib/modules/modules.load", "lib/modules/modules.load.recovery", "lib/modules/modules.dep",
                "avb/q-gsi.avbpubkey", "system/bin/snapuserd", "first_stage_ramdisk", "lib/modules"):
        if key in by_name:
            mode, content = by_name[key]
            extra = ""
            if key.endswith((".load", ".recovery")):
                extra = f", {len(content.split())} modules"
            print(f"  {key}: mode {oct(mode)}, {len(content)} bytes{extra}")
        else:
            print(f"  {key}: absent")
    kos = [n for n, _, _ in files if n.endswith(".ko")]
    print(f"  .ko files: {len(kos)}")
    top = sorted({n.split('/')[0] for n, _, _ in files})
    print("  top level:", " ".join(top))
    return by_name


def boot_header(path):
    data = path.read_bytes()
    if data[:8] != b"ANDROID!":
        problems.append(f"{path.name}: not a boot image")
        return
    kernel, ramdisk, osv, header_size = struct.unpack_from("<4I", data, 8)
    version, = struct.unpack_from("<I", data, 40)
    cmdline = data[44:44 + 1536].split(b"\0")[0].decode(errors="replace")
    sig, = struct.unpack_from("<I", data, 44 + 1536) if version >= 4 else (0,)
    print(f"{path.name}: v{version}, kernel {kernel}, ramdisk {ramdisk}, os_version {osv:#x}, "
          f"signature {sig}, cmdline {cmdline!r}")
    page = 4096
    k_off = page
    r_off = k_off + (kernel + page - 1) // page * page
    print(f"  kernel magic at 56: {data[k_off + 56:k_off + 60]!r}")
    show_ramdisk("  boot ramdisk", data[r_off:r_off + ramdisk])


def vendor_boot_header(path):
    data = path.read_bytes()
    version, page, kaddr, raddr, vsize = struct.unpack_from("<5I", data, 8)
    cmdline = data[28:28 + 2048].split(b"\0")[0].decode(errors="replace")
    o = 28 + 2048
    tags, = struct.unpack_from("<I", data, o)
    header_size, dtb_size = struct.unpack_from("<II", data, o + 20)
    dtb_addr, = struct.unpack_from("<Q", data, o + 28)
    table_size, entries, entry_size, bootconfig_size = struct.unpack_from("<4I", data, o + 36)
    print(f"{path.name}: v{version}, page {page}, kernel_addr {kaddr:#x}, ramdisk_addr {raddr:#x}, "
          f"tags {tags:#x}, dtb_addr {dtb_addr:#x}, vendor ramdisk {vsize}, dtb {dtb_size}, "
          f"ramdisk table {entries} x {entry_size}, bootconfig {bootconfig_size}")
    print(f"  cmdline {cmdline!r}")
    align = lambda x: (x + page - 1) // page * page
    r_off = align(header_size)
    d_off = r_off + align(vsize)
    t_off = d_off + align(dtb_size)
    b_off = t_off + align(table_size)
    print("  bootconfig:", data[b_off:b_off + bootconfig_size].decode(errors="replace").split("\n"))
    for n in range(entries):
        e = t_off + n * entry_size
        size, offset, rtype = struct.unpack_from("<3I", data, e)
        name = data[e + 12:e + 44].split(b"\0")[0].decode()
        show_ramdisk(f"  vendor ramdisk {n} {name!r} type {rtype}",
                     data[r_off + offset:r_off + offset + size])


def main():
    print(f"images in {OUT}")
    for name in ("boot", "vendor_boot", "dtbo", "recovery", "vbmeta", "vbmeta_system", "system", "system_ext",
                 "product", "vendor", "vendor_dlkm", "odm", "super_empty"):
        p = OUT / f"{name}.img"
        print(f"  {name}.img: {p.stat().st_size if p.exists() else 'absent'}")
    boot_header(OUT / "boot.img")
    vendor_boot_header(OUT / "vendor_boot.img")
    avbtool = HOST / "avbtool"
    for name in ("vbmeta", "vbmeta_system", "boot", "vendor_boot", "recovery", "system"):
        run([avbtool, "info_image", "--image", OUT / f"{name}.img"])
    rc, out = run([avbtool, "verify_image", "--image", OUT / "vbmeta.img", "--follow_chain_partitions"], cwd=OUT)
    if rc != 0:
        problems.append("avbtool verify_image failed (see above)")
    print("== problems:" if problems else "== no problems found", *problems, sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
