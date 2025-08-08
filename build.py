#!/usr/bin/python3

import os
import subprocess
import shutil
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KiwiOS Build Script")

    parser.add_argument(
        "--iso",
        help="compile and generate an iso file using grub-mkrescue",
        action="store_true",
    )
    parser.add_argument(
        "-q", "--qemu", help="compile and run qemu", action="store_true"
    )
    app_args = parser.parse_args()
    os.chdir(os.path.dirname(__file__))

    os.makedirs("out", exist_ok=True)
    for file in os.listdir("out"):
        try:
            os.remove("out/" + file)
        except IsADirectoryError:
            continue

    print("Copying files...")
    for file in os.listdir("src/copy"):
        shutil.copy("src/copy/" + file, "out/")

    print("Building KiwiOS")

    print("Running NASM")
    subprocess.run(
        ("nasm", "-felf32", "src/boot.asm", "-o", "out/boot.o"),
        check=True,
        cwd=os.getcwd(),
    )

    print("Running clang")
    subprocess.run(
        (
            "clang",
            "-target",
            "i386-elf",
            "-c",
            "src/kernel.cpp",
            "-o",
            "out/kernel.o",
            "-ffreestanding",
            "-fno-builtin",
            "-nostdlib",
            "-O2",
            "-Wall",
            "-Wextra",
            "-fno-exceptions",
            "-fno-rtti",
            # "-nostdinc",
            # "-nostdinc++"
        ),
        check=True,
        cwd=os.getcwd(),
    )

    print("Retrieving clang runtime dir...", end=" ")
    runtime_dir = subprocess.run(
        ("clang", "--print-runtime-dir"), capture_output=True
    ).stdout.decode("utf-8")[:-1]
    print(runtime_dir)

    print("Linking with ld.lld")
    subprocess.run(
        (
            "clang",
            "--target=i386-pc-none-elf",
            "-march=i386",
            "-T",
            "linker.ld",
            "-o",
            "kiwios.bin",
            "-ffreestanding",
            "-O2",
            "-nostdlib",
            "boot.o",
            "kernel.o",
            f"{runtime_dir}/libclang_rt.builtins-i386.a",
            "-fuse-ld=lld",
            "-static",
        ),
        check=True,
        cwd=f"{os.getcwd()}/out",
    )

    print("Checking multiboot...", end=" ")
    if (
        subprocess.run(
            ("grub-file", "--is-x86-multiboot", "kiwios.bin"),
            check=True,
            cwd=f"{os.getcwd()}/out",
        ).returncode
        == 0
    ):
        print("Success!")
    else:
        assert False, "The binary is not multibootable"

    if app_args.iso:
        print("Generating isodir & grub stuff...")

        os.makedirs("out/isodir/", exist_ok=True)

        subprocess.run(("rm", "-rf", "out/isodir"), check=True, cwd=os.getcwd())

        os.makedirs("out/isodir/boot/grub", exist_ok=True)

        shutil.copy("out/kiwios.bin", "out/isodir/boot/kiwios.bin")
        shutil.copy("src/grub/grub.cfg", "out/isodir/boot/grub/grub.cfg")

        print("Building the ISO...")
        subprocess.run(
            ("grub-mkrescue", "-o", "kiwios.iso", "isodir"),
            check=True,
            cwd=f"{os.getcwd()}/out",
        )

    print("Complete!")

    if app_args.qemu:
        print("Starting qemu")
        subprocess.run(
            ("qemu-system-i386", "-kernel", "kiwios.bin"),
            check=True,
            cwd=f"{os.getcwd()}/out",
        )
