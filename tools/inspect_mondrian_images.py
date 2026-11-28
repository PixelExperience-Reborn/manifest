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
  lists, AVB keys);
- the EROFS on-disk format of the logical partitions (feature_incompat 0x1
  like the stock images, which the GKI 5.10 mounts without its EXPERIMENTAL
  big pcluster backport) and the fstab mount points of the vendor image;
- the mount context types of the fstab in the vendor policy;
- hwservicemanager on system_ext with android.hidl.manager in the system_ext
  manifest: Android 17 installs it only for shipping API levels up to 34, and
  without the manifest entry it never sets hwservicemanager.ready, which
  init.target.rc waits for in late-fs before mounting /data.

    inspect_mondrian_images.py <android tree>
"""
import gzip
import lzma
import struct
import subprocess
import sys
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
PRODUCT_OUT = TREE / "out/target/product/mondrian"


def images_dir():
    """The complete image set of the last build: target-files IMAGES of `m bacon`
    (product out holds only some images there), or product out itself."""
    found = sorted(PRODUCT_OUT.glob("obj/PACKAGING/target_files_intermediates/*/IMAGES/vbmeta.img"),
                   key=lambda p: p.stat().st_mtime)
    if found:
        return found[-1].parent
    return PRODUCT_OUT


OUT = images_dir()
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
                listed = [m.split("/")[-1] for m in content.decode(errors="replace").split()]
                extra = f", {len(listed)} modules"
                # sda15 log store (mondrian BoardConfig.mk, userdebug/eng only)
                store = [m for m in ("block2mtd.ko", "mtdoops.ko") if m in listed]
                extra += f", sda15 log store: {' '.join(store) or 'not loaded'}"
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


EROFS_MAGIC = 0xE0F5E1E2
SPARSE_MAGIC = 0xED26FF3A
STOCK_EROFS_INCOMPAT = 0x1
VENDOR_MOUNT_POINTS = ("firmware_mnt", "dsp", "bt_firmware")
MOUNT_CONTEXT_TYPES = ("firmware_file", "bt_firmware_file", "vendor_qmcs_file")


def raw_image(path):
    """A path to the raw image: sparse images are expanded with simg2img."""
    with open(path, "rb") as f:
        magic, = struct.unpack("<I", f.read(4))
    if magic != SPARSE_MAGIC:
        return path
    raw = Path("/tmp") / f"pe-inspect-{path.name}"
    run([HOST / "simg2img", path, raw])
    return raw


def erofs_root(path):
    """(feature_incompat, names in the root directory) of an EROFS image."""
    with open(path, "rb") as f:
        sb = f.read(2048)[1024:1152]
        if struct.unpack_from("<I", sb, 0)[0] != EROFS_MAGIC:
            return None, None
        bs = 1 << sb[12]
        root_nid, = struct.unpack_from("<H", sb, 14)
        meta_blkaddr, = struct.unpack_from("<I", sb, 40)
        incompat, = struct.unpack_from("<I", sb, 80)
        f.seek(meta_blkaddr * bs + root_nid * 32)
        raw = f.read(64)
        fmt, xcount = struct.unpack_from("<HH", raw, 0)
        layout = (fmt >> 1) & 7
        size = struct.unpack_from("<Q" if fmt & 1 else "<I", raw, 8)[0]
        blkaddr, = struct.unpack_from("<I", raw, 16)
        inline = meta_blkaddr * bs + root_nid * 32 + (64 if fmt & 1 else 32) + (12 + (xcount - 1) * 4 if xcount else 0)
        if layout not in (0, 2):  # flat plain / flat inline directories only
            return incompat, None
        nblocks = size // bs if layout == 2 else (size + bs - 1) // bs
        f.seek(blkaddr * bs)
        data = f.read(nblocks * bs) if nblocks else b""
        if layout == 2 and size % bs:
            f.seek(inline)
            data += f.read(size % bs)
    names = []
    for blk in range(0, len(data), bs):
        chunk = data[blk:blk + bs]
        count = struct.unpack_from("<H", chunk, 8)[0] // 12
        for i in range(count):
            nameoff, = struct.unpack_from("<H", chunk, i * 12 + 8)
            end = struct.unpack_from("<H", chunk, (i + 1) * 12 + 8)[0] if i + 1 < count else len(chunk)
            names.append(chunk[nameoff:end].split(b"\0")[0].decode(errors="replace"))
    return incompat, [n for n in names if n not in (".", "..")]


def check_erofs():
    for name in ("system", "system_ext", "product", "vendor", "vendor_dlkm", "odm"):
        path = OUT / f"{name}.img"
        if not path.exists():
            problems.append(f"{name}.img absent")
            continue
        incompat, names = erofs_root(raw_image(path))
        print(f"{name}.img: erofs feature_incompat {incompat if incompat is None else hex(incompat)}, "
              f"root: {' '.join(names or [])}")
        if incompat != STOCK_EROFS_INCOMPAT:
            problems.append(f"{name}.img: EROFS feature_incompat {incompat}, stock images use 0x1")
        if name == "vendor":
            for d in VENDOR_MOUNT_POINTS:
                if d not in (names or []):
                    problems.append(f"vendor.img: no /vendor/{d} mount point")


def check_vendor_policy():
    for cil in (OUT.parent / "VENDOR/etc/selinux/vendor_sepolicy.cil",
                PRODUCT_OUT / "vendor/etc/selinux/vendor_sepolicy.cil"):
        if cil.exists():
            text = cil.read_text(errors="replace")
            for t in MOUNT_CONTEXT_TYPES:
                ok = f"(type {t})" in text
                print(f"vendor policy {cil}: {t} {'declared' if ok else 'MISSING'}")
                if not ok:
                    problems.append(f"vendor policy: {t} not declared (fstab context= fails with EINVAL)")
            return
    problems.append("vendor_sepolicy.cil not found")


def check_hwservicemanager():
    for root in (OUT.parent / "SYSTEM_EXT", PRODUCT_OUT / "system_ext"):
        manifest = root / "etc/vintf/manifest.xml"
        if root.is_dir():
            binary = (root / "bin/hwservicemanager").exists()
            declared = manifest.exists() and "android.hidl.manager" in manifest.read_text(errors="replace")
            print(f"{root}: bin/hwservicemanager {'present' if binary else 'MISSING'}, "
                  f"android.hidl.manager {'declared' if declared else 'MISSING'}")
            if not binary or not declared:
                problems.append("hwservicemanager or its android.hidl.manager entry missing on system_ext "
                                "(late-fs waits for hwservicemanager.ready)")
            return
    problems.append("system_ext tree not found")


BOOT_FILES = {
    # init.qti.kernel.rc: on early-init start vendor.modprobe, on init wait_for_prop
    # vendor.all.modules.ready 1, which only vendor_modprobe.sh sets.
    "VENDOR": ("bin/sh", "bin/modprobe", "bin/toybox_vendor", "bin/vendor_modprobe.sh",
               "etc/init/hw/init.qti.kernel.rc"),
    "VENDOR_DLKM": ("lib/modules/modules.load", "lib/modules/modules.dep"),
}


def check_boot_files():
    for part, files in BOOT_FILES.items():
        root = OUT.parent / part
        if not root.is_dir():
            root = PRODUCT_OUT / part.lower()
        for f in files:
            ok = (root / f).exists() or (root / f).is_symlink()
            print(f"{part.lower()}/{f}: {'present' if ok else 'MISSING'}")
            if not ok:
                problems.append(f"{part.lower()}/{f} missing")


def main():
    print(f"images in {OUT}")
    for name in ("boot", "vendor_boot", "dtbo", "recovery", "vbmeta", "vbmeta_system", "system", "system_ext",
                 "product", "vendor", "vendor_dlkm", "odm", "super_empty"):
        p = OUT / f"{name}.img"
        print(f"  {name}.img: {p.stat().st_size if p.exists() else 'absent'}")
    boot_header(OUT / "boot.img")
    vendor_boot_header(OUT / "vendor_boot.img")
    check_erofs()
    check_vendor_policy()
    check_hwservicemanager()
    check_boot_files()
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
