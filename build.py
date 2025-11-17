#!/usr/bin/env python3
"""
QuillScribe Build Script (Python)
Replaces the PowerShell build script with a cross-platform Python script

Functionality:
- Checks/installs Nuitka (optional)
- Cleans previous build artifacts and Nuitka cache (preserving downloads)
- Installs pip dependencies
- Builds using Nuitka with options (onefile, pyside6 plugin, icon, data dirs)
- Optionally creates an NSIS installer if makensis is available

Usage examples:
    python build.py            # Default: runs installs and creates an exe
    python build.py --skip-install  # skip pip installs (Nuitka & requirements)
    python build.py --skip-nsis     # skip NSIS installer creation
    python build.py --onefile=false # build in folder mode

"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def print_header(msg: str):
    print("""
=========================================
  {}
=========================================""".format(msg))


def command_exists(command: str) -> bool:
    from shutil import which

    return which(command) is not None


def run(cmd: Iterable[str], check: bool = True, env=None) -> subprocess.CompletedProcess:
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, env=env)
    if check and res.returncode != 0:
        raise SystemExit(f"Command failed with exit {res.returncode}: {' '.join(cmd)}")
    return res


def pip_install(packages: Iterable[str]):
    if not packages:
        return
    cmd = [sys.executable, "-m", "pip", "install", *packages]
    run(cmd)


def pip_install_requirements(requirements_file: Path):
    if not requirements_file.exists():
        print(f"Requirements file not found: {requirements_file}")
        return
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
    run(cmd)


def remove_if_exists(path: Path):
    if path.exists():
        if path.is_dir():
            print(f"Removing directory {path}")
            shutil.rmtree(path, ignore_errors=True)
        else:
            print(f"Removing file {path}")
            path.unlink(missing_ok=True)


def clean_nuitka_cache():
    localappdata = os.environ.get("LOCALAPPDATA")
    if not localappdata:
        print("LOCALAPPDATA not set; skipping Nuitka cache cleanup")
        return
    cache_path = Path(localappdata) / "Nuitka" / "Nuitka" / "Cache"
    if not cache_path.exists():
        print("Nuitka cache not found; skipped")
        return
    # Only remove ccache and bytecode
    for k in ("ccache", "bytecode"):
        p = cache_path / k
        if p.exists():
            print(f"Removing Nuitka cache {p}")
            shutil.rmtree(p, ignore_errors=True)
    print("Preserved compiler downloads (MinGW64 will not be re-downloaded)")


def get_makensis_path() -> str | None:
    # check PATH
    makensis = shutil.which("makensis")
    if makensis:
        return makensis
    # check common locations
    candidates = [
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)") and os.path.join(os.environ.get("ProgramFiles(x86)"), "NSIS"),
        os.environ.get("ProgramFiles") and os.path.join(os.environ.get("ProgramFiles"), "NSIS"),
    ]
    for c in filter(None, candidates):
        p = Path(c) / "makensis.exe"
        if p.exists():
            return str(p)
    return None


def build_nuitka(args: argparse.Namespace):
    project_root = Path.cwd()
    src_dir = project_root / "src"
    # Clean previous builds
    print("Cleaning previous builds...")
    for candidate in ("build", "run.build", "run.dist", "run.onefile-build"):
        remove_if_exists(project_root / candidate)
    remove_if_exists(project_root / "QuillScribe.exe")
    remove_if_exists(project_root / "QuillScribe-Installer.exe")

    # Clean Nuitka specific cache
    clean_nuitka_cache()

    if not args.skip_install:
        print("Installing dependencies from requirements.txt...")
        pip_install_requirements(project_root / "requirements.txt")

    # Ensure Nuitka present
    try:
        import nuitka  # type: ignore
    except Exception:
        if args.skip_install:
            print("Nuitka not found and --skip-install provided; aborting.")
            raise
        print("Nuitka not found; installing... (nuitka, ordered-set, zstandard)")
        pip_install(["nuitka", "ordered-set", "zstandard"])

    # Build args
    nuitka_cmd = [sys.executable, "-m", "nuitka"]
    # Mode: standalone vs. onefile
    mode_onefile = args.onefile
    if mode_onefile:
        nuitka_cmd += ["--standalone", "--onefile"]
    else:
        # standalone build folder
        nuitka_cmd += ["--standalone"]

    if args.disable_console:
        nuitka_cmd.append("--windows-console-mode=disable")
    if args.pyside6:
        nuitka_cmd.append("--enable-plugin=pyside6")

    # Icon and data
    nuitka_cmd += [
        "--windows-icon-from-ico=src/quillscribe/icons/app_logo.ico",
        "--include-data-dir=src/quillscribe/icons=icons",
        "--include-data-dir=src/sounds=sounds",
        "--include-package=quillscribe",
    ]

    # Packages to ignore - keep similar to the PS1 script
    nofollow = [
        "PyQt5",
        "PyQt6",
        "torch",
        "torchvision",
        "torchaudio",
        "tensorflow",
        "keras",
        "matplotlib",
        "scipy",
        "pandas",
        "tkinter",
        "test",
        "tests",
        "unittest",
        "mypy",
        "PIL",
        "psutil",
        "aioquic",
        "brotlicffi",
        "websockets",
    ]
    for p in nofollow:
        nuitka_cmd += [f"--nofollow-import-to={p}"]

    # Output / version info
    nuitka_cmd += [
        "--output-filename=QuillScribe.exe",
        "--company-name=QuillScribe Team",
        "--product-name=QuillScribe",
        "--file-version=1.0.0.0",
        "--product-version=1.0.0",
        "--file-description=Beautiful Voice-to-Text Transcription App",
        "--assume-yes-for-downloads",
    ]

    # Entry point
    nuitka_cmd.append("run.py")

    # Set PYTHONPATH so Nuitka finds quillscribe package
    env = os.environ.copy()
    pypath = str(src_dir)
    existing = env.get("PYTHONPATH")
    if existing:
        env["PYTHONPATH"] = pypath + os.pathsep + existing
    else:
        env["PYTHONPATH"] = pypath

    # Run Nuitka
    print("Building executable with Nuitka...")
    run(nuitka_cmd, env=env)

    # Verify executable
    exe_path = project_root / "QuillScribe.exe"
    if not exe_path.exists():
        print("ERROR: QuillScribe.exe not found in current directory")
        sys.exit(1)

    print("Executable built successfully:", exe_path)

    if args.skip_nsis:
        print("--skip-nsis supplied; skipping installer creation")
        return

    makensis_path = get_makensis_path()
    if not makensis_path:
        print("NSIS (makensis) not found; skipping installer creation")
        return

    # Build installer
    print("Creating NSIS installer...")
    # Ensure we call the correct makensis
    run([makensis_path, "installer.nsi"])
    installer_exe = project_root / "QuillScribe-Installer.exe"
    if installer_exe.exists():
        print("Installer created successfully:", installer_exe)
    else:
        print("Installer not created; makensis returned successfully but no installer found")


def main():
    parser = argparse.ArgumentParser(description="Build QuillScribe using Nuitka")
    parser.add_argument("--skip-install", dest="skip_install", action="store_true", help="Skip pip installs for requirements and Nuitka")
    parser.add_argument("--skip-nsis", dest="skip_nsis", action="store_true", help="Skip creating NSIS installer even if makensis is found")
    parser.add_argument("--onefile", dest="onefile", action="store_true", default=True, help="Build as onefile executable (default True)")
    parser.add_argument("--no-onefile", dest="onefile", action="store_false", help="Build in folder mode (disable onefile)")
    parser.add_argument("--disable-console", dest="disable_console", action="store_true", help="Disable Windows console mode")
    parser.add_argument("--no-pyside6", dest="pyside6", action="store_false", help="Do not enable the pyside6 plugin (enabled by default)")
    parser.add_argument("--pyside6", dest="pyside6", action="store_true", default=True, help="Enable the pyside6 plugin (default True)")
    args = parser.parse_args()

    print_header("QuillScribe Build Script - Python")
    try:
        build_nuitka(args)
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
