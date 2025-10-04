"""
This script automatically increments or resets [tool.flet].build_number
based on [project].version. Also preserves pyproject.toml formatting using tomlkit.

If you want to run this script separately, you can with (if with `uv`):
    uv run py -m tools.bump_build
"""

from pathlib import Path
from tomlkit import parse, dumps

PYPROJECT_FILE = Path(__file__).resolve().parent.parent / "pyproject.toml"
LAST_VERSION_FILE = PYPROJECT_FILE.parent / ".last_version"

def main():
    if not PYPROJECT_FILE.exists():
        raise FileNotFoundError(f"❌ Can't find {PYPROJECT_FILE}")

    # Read and parse preserving formatting
    text = PYPROJECT_FILE.read_text(encoding="utf-8")
    doc = parse(text)

    # Extract current version & build number
    version = doc["project"]["version"]
    flet_table = doc["tool"]["flet"]
    build_number = int(flet_table.get("build_number", 0))

    # Load previous version (if exists)
    last_version = (
        LAST_VERSION_FILE.read_text(encoding="utf-8").strip()
        if LAST_VERSION_FILE.exists()
        else None
    )

    if last_version != version:
        print(f"🔄 Version changed from {last_version} → {version}, resetting build_number to 1")
        new_build = 1
    else:
        new_build = build_number + 1
        print(f"⬆️  Incrementing build_number: {build_number} → {new_build}")

    # Update the value
    flet_table["build_number"] = new_build

    # Write back preserving original formatting
    PYPROJECT_FILE.write_text(dumps(doc), encoding="utf-8")
    LAST_VERSION_FILE.write_text(version, encoding="utf-8")

    print(f"✅ Updated pyproject.toml — build_number = {new_build}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")