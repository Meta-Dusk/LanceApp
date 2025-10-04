"""
Automated build script for the MikuMiku App.

Steps:
    1. Run bump_build.py to update build_number.
    2. Run Flet Windows build with icon.
    3. Optionally compile installer with Inno Setup.

Syntax:
    build_app.py [--flags]

Usage:
    uv run py -m tools.build_app
    (Remove `uv run` if not using uv)

Available Flags:
    --no-installer
    --no-build
"""

import subprocess, sys, argparse, tomlkit, time
from pathlib import Path
from colorama import Fore, Style, init as colorama_init


# Initialize colorama (auto resets colors after each print)
colorama_init(autoreset=True)


# === PATHS ===
ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
INSTALLER = ROOT / "installer" / "miku_installer.iss"
PYPROJECT = ROOT / "pyproject.toml"
BUMP_SCRIPT = TOOLS / "bump_build.py"
BUILD_DIR = ROOT / "build" / "windows"


# === UTILITIES ===
def print_section(title: str):
    """Pretty print a centered section header."""
    bar = f"{Fore.CYAN}{'=' * 50}"
    centered = f"{Fore.CYAN}{title.center(50)}"
    print(f"\n{bar}\n{centered}\n{bar}")

def print_block(text: str, color=Fore.WHITE):
    """Print a multi-line block of text cleanly."""
    print(f"\n{color}{text.strip()}\n")
    
def print_warning(text: str, color=Fore.YELLOW):
    print(f"⚠️  {color}{text}")


def run(cmd: list[str], cwd: Path | None = None):
    """Run a shell command and stream output."""
    print(f"\n{Fore.BLUE}🟦 Running: {Style.BRIGHT}{' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=cwd or ROOT)
    if result.returncode != 0:
        print(f"{Fore.RED}❌ Command failed with exit code {result.returncode}: {' '.join(cmd)}")
        sys.exit(result.returncode)
    print(f"{Fore.GREEN}✅ Done.")


def get_build_info():
    """Read and return version and build number from pyproject.toml."""
    if not PYPROJECT.exists():
        print(f"{Fore.RED}❌ pyproject.toml not found.")
        sys.exit(1)

    doc = tomlkit.parse(PYPROJECT.read_text(encoding="utf-8"))
    version = doc.get("project", {}).get("version", "unknown")
    build_number = doc.get("tool", {}).get("flet", {}).get("build_number", 0)
    return version, build_number


# === MAIN BUILD PROCESS ===
def main():
    parser = argparse.ArgumentParser(description="Automated Flet build script for MikuMiku.")
    parser.add_argument("--no-build", action="store_true", help="Only bump build number without building.")
    parser.add_argument("--no-installer", action="store_true", help="Skip Inno Setup installer compilation.")
    args = parser.parse_args()
    
    # Start timer
    start_time = time.perf_counter()

    # Step 1: Initial info
    version_before, build_before = get_build_info()
    print_section("🚀 BUILDING MIKUMIKU APP")
    print_block(f"""
📦 Version: {version_before}
🔢 Build number (before): {build_before}
    """, color=Fore.LIGHTWHITE_EX)

    # Step 2: Bump build number
    print_section("STEP 1: BUMP BUILD NUMBER")
    run([sys.executable, str(BUMP_SCRIPT)])
    version_after, build_after = get_build_info()

    # Step 3: Build app (unless skipped)
    if not args.no_build:
        print_section("STEP 2: BUILD FLET APP")
        build_cmd = ["uv", "run", "flet", "build", "windows", "-v"]
        run(build_cmd)

        if BUILD_DIR.exists():
            print_block(f"📁 Build output located at:\n{BUILD_DIR}", color=Fore.CYAN)
        else:
            print_warning("No build directory found after build.")
    else:
        print_warning("Skipping app build (--no-build flag used).")

    # Step 4: Build installer (if requested)
    if not args.no_installer and INSTALLER.exists():
        print_section("STEP 3: BUILD INSTALLER")
        inno_output_dir = ROOT / "dist" / "installer"
        inno_output_dir.mkdir(parents=True, exist_ok=True)

        version_tag = f"MikuMiku-v{version_after}"
        inno_cmd = [
            "iscc",
            f"/O{inno_output_dir}",             # Output folder
            f"/F{version_tag}",                 # Output file name
            f"/DMyAppVersion={version_after}",  # Pass version from pyproject.toml
            str(INSTALLER)
        ]
        run(inno_cmd)

        output_exe = inno_output_dir / f"{version_tag}.exe"
        if output_exe.exists():
            print_block(f"🎉 Installer created:\n{output_exe}", color=Fore.GREEN)
        else:
            print_warning("Installer compilation finished, but file not found.")
    elif args.no_installer:
        print_warning("Skipping installer build (--no-installer flag used).")
    else:
        print_warning("No Inno Setup script found, skipping installer build.")

    # Step 5: Summary
    elapsed = time.perf_counter() - start_time
    print_section("✅ BUILD SUMMARY")
    print_block(f"""
📦 Version: {version_after}
🔢 Build number: {build_after}
⏱️ Elapsed time: {elapsed:.2f} seconds

🎉 Build process completed successfully!
    """, color=Fore.GREEN)


if __name__ == "__main__":
    main()