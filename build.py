#!/usr/bin/env python3
"""
QuillScribe Build Script (Python)
Builds executable using Nuitka for optimized native performance

Functionality:
- Checks/installs Nuitka and dependencies
- Cleans previous build artifacts and Nuitka cache (preserving compiler downloads)
- Installs pip dependencies
- Builds using Nuitka with options (onefile, pyside6 plugin, icon, data dirs)
- Optionally creates an NSIS installer if makensis is available
- Cross-platform compatible (Windows/Linux/macOS)

Usage examples:
    python build.py                    # Default: build standalone onefile exe
    python build.py --skip-install     # Skip pip installs (Nuitka & requirements)
    python build.py --skip-nsis        # Skip NSIS installer creation
    python build.py --no-onefile       # Build in folder mode instead of onefile
    python build.py --disable-console  # Disable Windows console
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def print_header(msg: str) -> None:
    """Print a formatted header message."""
    print()
    print("=" * 41)
    print(f"  {msg}")
    print("=" * 41)
    print()


def print_section(msg: str) -> None:
    """Print a section message."""
    print(f"\n{msg}")


def command_exists(command: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(command) is not None


def run(cmd: Iterable[str], check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run a subprocess command."""
    cmd_list = list(cmd)
    print(f"Running: {' '.join(cmd_list)}")
    res = subprocess.run(cmd_list, env=env)
    if check and res.returncode != 0:
        raise SystemExit(f"Command failed with exit code {res.returncode}: {' '.join(cmd_list)}")
    return res


def pip_install(packages: Iterable[str]) -> None:
    """Install pip packages."""
    packages_list = list(packages)
    if not packages_list:
        return
    cmd = [sys.executable, "-m", "pip", "install", *packages_list]
    run(cmd)


def pip_install_requirements(requirements_file: Path) -> None:
    """Install packages from requirements file."""
    if not requirements_file.exists():
        print(f"Requirements file not found: {requirements_file}")
        return
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
    run(cmd)


def remove_if_exists(path: Path) -> None:
    """Remove a file or directory if it exists."""
    if path.exists():
        if path.is_dir():
            print(f"Removing directory: {path}")
            shutil.rmtree(path, ignore_errors=True)
        else:
            print(f"Removing file: {path}")
            path.unlink(missing_ok=True)


def clean_nuitka_cache() -> None:
    """Clean Nuitka cache while preserving compiler downloads."""
    localappdata = os.environ.get("LOCALAPPDATA")
    if not localappdata:
        print("LOCALAPPDATA not set; skipping Nuitka cache cleanup")
        return

    cache_path = Path(localappdata) / "Nuitka" / "Nuitka" / "Cache"
    if not cache_path.exists():
        print("Nuitka cache not found; skipped")
        return

    # Only remove ccache and bytecode, preserve downloads (MinGW64, depends.exe, etc.)
    for cache_type in ("ccache", "bytecode"):
        cache_dir = cache_path / cache_type
        if cache_dir.exists():
            print(f"Removing Nuitka {cache_type}...")
            shutil.rmtree(cache_dir, ignore_errors=True)

    print("Preserved compiler downloads (MinGW64 will not be re-downloaded)")


def get_makensis_path() -> str | None:
    """Find makensis executable in PATH or common installation directories."""
    # Check if makensis is in PATH
    makensis = shutil.which("makensis")
    if makensis:
        return makensis

    # Check common NSIS installation directories
    candidates = [
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("ProgramFiles"),
    ]

    for base_dir in filter(None, candidates):
        nsis_path = Path(base_dir) / "NSIS" / "makensis.exe"
        if nsis_path.exists():
            print(f"Found NSIS at: {nsis_path}")
            return str(nsis_path)

    return None


def build_nuitka(args: argparse.Namespace) -> None:
    """Build QuillScribe using Nuitka."""
    project_root = Path.cwd()
    src_dir = project_root / "src"

    # Verify we're in the right directory
    if not (project_root / "run.py").exists():
        print("ERROR: run.py not found. Make sure you're in the QuillScribe project root directory.")
        sys.exit(1)

    # Clean previous builds
    print_section("Cleaning previous builds...")
    for candidate in ("build", "run.build", "run.dist", "run.onefile-build"):
        remove_if_exists(project_root / candidate)
    remove_if_exists(project_root / "QuillScribe.exe")
    remove_if_exists(project_root / "QuillScribe-Installer.exe")

    # Clean Nuitka cache
    print_section("Cleaning Nuitka compilation cache (preserving compiler)...")
    clean_nuitka_cache()

    # Install dependencies
    if not args.skip_install:
        print_section("Installing dependencies from requirements.txt...")
        pip_install_requirements(project_root / "requirements.txt")

    # Ensure Nuitka is installed
    try:
        import nuitka  # type: ignore  # noqa: F401
    except ImportError:
        if args.skip_install:
            print("ERROR: Nuitka not found and --skip-install was provided")
            sys.exit(1)
        print_section("Nuitka not found; installing (nuitka, ordered-set, zstandard)...")
        pip_install(["nuitka", "ordered-set", "zstandard"])

    # Build Nuitka command
    nuitka_cmd = [sys.executable, "-m", "nuitka"]

    # Standalone mode
    if args.onefile:
        nuitka_cmd.extend(["--standalone", "--onefile"])
    else:
        nuitka_cmd.append("--standalone")

    # Platform-specific options
    if sys.platform == "win32":
        nuitka_cmd.append("--windows-console-mode=disable")

    # Plugin and resources
    if args.pyside6:
        nuitka_cmd.append("--enable-plugin=pyside6")

    nuitka_cmd.extend([
        "--windows-icon-from-ico=src/quillscribe/icons/app_logo.ico",
        "--include-data-dir=src/quillscribe/icons=icons",
        "--include-data-dir=src/sounds=sounds",
        "--include-package=quillscribe",
    ])

    # Packages to exclude from following imports
    nofollow_packages = [
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
    for package in nofollow_packages:
        nuitka_cmd.append(f"--nofollow-import-to={package}")

    # Version and metadata
    nuitka_cmd.extend([
        "--output-filename=QuillScribe.exe",
        "--company-name=QuillScribe Team",
        "--product-name=QuillScribe",
        "--file-version=1.0.0.0",
        "--product-version=1.0.0",
        "--file-description=Beautiful Voice-to-Text Transcription App",
        "--assume-yes-for-downloads",
        "run.py",
    ])

    # Set PYTHONPATH so Nuitka can find the quillscribe package
    env = os.environ.copy()
    pypath = str(src_dir)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (pypath + os.pathsep + existing) if existing else pypath

    # Build
    print_section("Building executable with Nuitka...")
    print("This will take several minutes on first build (compiling to native code)...")
    print("Nuitka will automatically download MinGW64 compiler if needed...")
    run(nuitka_cmd, env=env)

    # Verify executable
    exe_path = project_root / "QuillScribe.exe"
    if not exe_path.exists():
        print("ERROR: QuillScribe.exe not found in current directory")
        sys.exit(1)

    print(f"✓ Executable built successfully: {exe_path}")

    # Optional: Create installer
    if args.skip_nsis:
        print_section("--skip-nsis provided; skipping installer creation")
        return

    makensis_path = get_makensis_path()
    if not makensis_path:
        print_section("WARNING: NSIS (makensis) not found")
        print("Skipping installer creation. You can run QuillScribe.exe directly.")
        print("To create an installer, install NSIS from https://nsis.sourceforge.io/")
        return

    print_section("Creating NSIS installer...")
    run([makensis_path, "installer.nsi"])

    installer_exe = project_root / "QuillScribe-Installer.exe"
    if installer_exe.exists():
        print(f"✓ Installer created successfully: {installer_exe}")
    else:
        print("Installer not created; makensis completed but no output found")

    # Summary
    print_header("BUILD COMPLETED SUCCESSFULLY!")
    print(f"Executable:  {exe_path}")
    if installer_exe.exists():
        print(f"Installer:   {installer_exe}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build QuillScribe using Nuitka",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip pip installs (Nuitka & requirements.txt)",
    )
    parser.add_argument(
        "--skip-nsis",
        action="store_true",
        help="Skip NSIS installer creation",
    )
    parser.add_argument(
        "--no-onefile",
        dest="onefile",
        action="store_false",
        help="Build in folder mode instead of onefile executable",
    )
    parser.add_argument(
        "--disable-console",
        action="store_true",
        help="Disable Windows console window",
    )
    parser.add_argument(
        "--no-pyside6",
        dest="pyside6",
        action="store_false",
        help="Disable PySide6 plugin",
    )

    # Set defaults
    parser.set_defaults(onefile=True, pyside6=True, disable_console=True)

    args = parser.parse_args()

    print_header("QuillScribe Nuitka Build Script")

    try:
        build_nuitka(args)
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
