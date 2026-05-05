from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "SchedulerSimulator"
APP_TITLE = "Scheduler Simulator"
APP_ID = "kr.ac.koreatech.scheduler-simulator"
DEFAULT_VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[1]
MIN_PYTHON = (3, 10, 8)


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def require_pyinstaller() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import PyInstaller"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            "PyInstaller is not installed. Run: python -m pip install -r requirements.txt"
        )


def build_pyinstaller(app_name: str) -> Path:
    if not (ROOT / "main.py").exists():
        raise SystemExit("Run this script from the project checkout that contains main.py.")

    separator = ";" if os.name == "nt" else ":"
    assets_arg = f"{ROOT / 'assets'}{separator}assets"

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        app_name,
        "--distpath",
        str(ROOT / "dist"),
        "--workpath",
        str(ROOT / ".pyinstaller-build"),
        "--add-data",
        assets_arg,
        "--collect-data",
        "matplotlib",
        "--hidden-import",
        "matplotlib.backends.backend_qtagg",
        str(ROOT / "main.py"),
    ]
    run(command)

    if platform.system() == "Darwin":
        return ROOT / "dist" / f"{app_name}.app"
    if platform.system() == "Windows":
        return ROOT / "dist" / app_name / f"{app_name}.exe"
    return ROOT / "dist" / app_name / app_name


def build_windows_installer(app_name: str, version: str) -> None:
    iscc = shutil.which("ISCC.exe") or shutil.which("ISCC")
    if not iscc:
        print(
            "Inno Setup was not found. The portable app folder is ready at "
            f"{ROOT / 'dist' / app_name}."
        )
        print(
            "Install Inno Setup on the Windows build PC and rerun this script "
            "to create release/SchedulerSimulatorSetup.exe."
        )
        print(f"Run this executable: {ROOT / 'dist' / app_name / f'{app_name}.exe'}")
        return

    iss = ROOT / "installer" / "windows" / "SchedulerSimulator.iss"
    run([iscc, f"/DAppVersion={version}", str(iss)])
    print(f"Windows installer: {ROOT / 'release' / 'SchedulerSimulatorSetup.exe'}")


def build_macos_installers(app_name: str, version: str) -> None:
    app_path = ROOT / "dist" / f"{app_name}.app"
    if not app_path.exists():
        raise SystemExit(f"Missing app bundle: {app_path}")

    release_dir = ROOT / "release"
    release_dir.mkdir(exist_ok=True)

    pkg_path = release_dir / f"{app_name}.pkg"
    run(
        [
            "pkgbuild",
            "--component",
            str(app_path),
            "--install-location",
            "/Applications",
            "--identifier",
            APP_ID,
            "--version",
            version,
            str(pkg_path),
        ]
    )

    dmg_path = release_dir / f"{app_name}-mac.dmg"
    run(
        [
            "hdiutil",
            "create",
            "-volname",
            APP_TITLE,
            "-srcfolder",
            str(app_path),
            "-ov",
            "-format",
            "UDZO",
            str(dmg_path),
        ]
    )
    print("")
    print("macOS installer files are ready:")
    print(f"- Installer wizard: {pkg_path}")
    print(f"- DMG package:       {dmg_path}")
    print(f"- Direct app:        {app_path}")
    print("")
    print("Use the files in release/. Do not run files inside build/ or .pyinstaller-build/.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a standalone Scheduler Simulator app for the current OS."
    )
    parser.add_argument("--name", default=APP_NAME, help="PyInstaller app name.")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Installer version.")
    parser.add_argument(
        "--skip-installer",
        action="store_true",
        help="Only build the PyInstaller app bundle/folder.",
    )
    args = parser.parse_args()

    if sys.version_info < MIN_PYTHON:
        required = ".".join(str(part) for part in MIN_PYTHON)
        raise SystemExit(f"Python {required} or newer is required to build the app.")

    require_pyinstaller()
    output = build_pyinstaller(args.name)
    print(f"Built app: {output}")

    if args.skip_installer:
        return 0

    system = platform.system()
    if system == "Windows":
        build_windows_installer(args.name, args.version)
    elif system == "Darwin":
        build_macos_installers(args.name, args.version)
    else:
        print("Installer packaging is only configured for Windows and macOS.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
