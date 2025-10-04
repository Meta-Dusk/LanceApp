"""
This is an automated build script for the MikuMiku App.
Steps:
    1. Run bump_build.py to update build_number.
    2. Run Flet Windows build with icon.
    3. Optionally compile installer with Inno Setup.
    
You can run this with (remove `uv run` if not with `uv`):
    uv run py -m tools.build_app
"""

import subprocess
import sys
import argparse
from pathlib import Path
import tomlkit

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
INSTALLER = ROOT / "installer" / "miku_installer.iss"
PYPROJECT = ROOT / "pyproject.toml"
BUMP_SCRIPT = TOOLS / "bump_build.py"


def run(cmd: list[str], cwd: Path | None = None):
    """Run a shell command and stream output."""
    print(f"\n🟦 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT)
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}: {' '.join(cmd)}")
        sys.exit(result.returncode)
    print("✅ Done.")


def get_build_info():
    """Read and return version and build number from pyproject.toml."""
    if not PYPROJECT.exists():
        print("❌ pyproject.toml not found.")
        sys.exit(1)

    doc = tomlkit.parse(PYPROJECT.read_text(encoding="utf-8"))
    version = doc.get("project", {}).get("version", "unknown")
    build_number = doc.get("tool", {}).get("flet", {}).get("build_number", 0)
    return version, build_number


def main():
    parser = argparse.ArgumentParser(description="Automated Flet build script for MikuMiku.")
    parser.add_argument("--no-build", action="store_true", help="Only bump build number without building.")
    parser.add_argument("--no-installer", action="store_true", help="Skip Inno Setup installer compilation.")
    args = parser.parse_args()

    # Step 1: Show current build info
    version_before, build_before = get_build_info()
    print("========================================")
    print("🚀 Building Flet App: MikuMiku")
    print("========================================")
    print(f"📦 Version: {version_before}")
    print(f"🔢 Build number (before): {build_before}")
    print("----------------------------------------")

    # Step 2: Bump build number
    run([sys.executable, str(BUMP_SCRIPT)])

    # Step 3: Read updated build number
    version_after, build_after = get_build_info()

    # Step 4: Optionally build app
    if not args.no_build:
        print("\n🛠️ Building Flet Windows app...")
        build_cmd = [
            "uv", "run", "flet", "build", "windows",
            "-v",
        ]
        run(build_cmd)
    else:
        print("⚠️  Skipping app build (--no-build flag used).")

    # Step 5: Optionally build installer
    if not args.no_installer and INSTALLER.exists():
        print("\n📦 Compiling installer using Inno Setup...\n")
        run(["iscc", str(INSTALLER)])
    elif args.no_installer:
        print("⚠️  Skipping installer build (--no-installer flag used).")
    else:
        print("⚠️  No Inno Setup script found, skipping installer build.")

    print("========================================")
    print(f"📦 Version: {version_after}")
    print(f"🔢 Build number: {build_after}")
    print("🎉 Build process completed successfully!")
    print("========================================")


if __name__ == "__main__":
    main()
