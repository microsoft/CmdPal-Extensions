# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Generate the aggregate gallery JSON for CmdPal-Extensions.

Scans extensions/*/extension.json, merges them into a single
extensions.json at the repo root that the Command Palette app fetches at runtime.

Usage:
    python .github/scripts/generate.py
"""

import glob
import json
import os
import sys
from datetime import datetime, timezone

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXTENSIONS_DIR = os.path.join(REPO_ROOT, "extensions")
OUTPUT_FILE = os.path.join(REPO_ROOT, "extensions.json")

BASE_RAW_URL = (
    "https://raw.githubusercontent.com/microsoft/CmdPal-Extensions/main"
)
GALLERY_SCHEMA_URL = (
    f"{BASE_RAW_URL}/.github/schemas/gallery.schema.json"
)

# Fields from extension.json that should not appear in the gallery output.
FIELDS_TO_REMOVE = {"$schema", "icon"}

VALID_SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_SCREENSHOTS = 5


def discover_extension_paths() -> list[str]:
    """Return sorted paths to every extension.json under extensions/<author>/<ext>/."""
    pattern = os.path.join(EXTENSIONS_DIR, "*", "*", "extension.json")
    return sorted(glob.glob(pattern))


def load_extension(path: str) -> dict | None:
    """Load and validate a single extension.json.

    Returns the parsed dict on success, or None if the file is invalid.
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"WARNING: skipping {path} — {exc}", file=sys.stderr)
        return None

    # Minimal sanity check: must have an id and an icon field.
    if "id" not in data:
        print(f"WARNING: skipping {path} — missing 'id' field", file=sys.stderr)
        return None
    if "icon" not in data:
        print(
            f"WARNING: skipping {path} — missing 'icon' field", file=sys.stderr
        )
        return None

    return data


def build_icon_url(extension_id: str, icon_filename: str) -> str:
    """Build the absolute raw GitHub URL for an extension's icon.
    The id is author.extension-name, mapping to extensions/author/extension-name/."""
    author, ext_name = extension_id.split(".", 1)
    return f"{BASE_RAW_URL}/extensions/{author}/{ext_name}/{icon_filename}"


def discover_screenshots(extension_id: str) -> list[str]:
    """Discover screenshot images in an extension's screenshots/ folder.

    Returns a sorted list of absolute raw GitHub URLs for each valid image,
    or an empty list if the screenshots folder does not exist.
    """
    author, ext_name = extension_id.split(".", 1)
    screenshots_dir = os.path.join(EXTENSIONS_DIR, author, ext_name, "screenshots")

    if not os.path.isdir(screenshots_dir):
        return []

    filenames = []
    for name in sorted(os.listdir(screenshots_dir)):
        full_path = os.path.join(screenshots_dir, name)
        ext = os.path.splitext(name)[1].lower()
        if os.path.isfile(full_path) and ext in VALID_SCREENSHOT_EXTENSIONS:
            filenames.append(name)

    filenames = filenames[:MAX_SCREENSHOTS]

    return [
        f"{BASE_RAW_URL}/extensions/{author}/{ext_name}/screenshots/{name}"
        for name in filenames
    ]


def transform_extension(data: dict) -> dict:
    """Transform a raw extension.json dict into its gallery representation.

    * Replaces the relative ``icon`` field with an absolute ``iconUrl``.
    * Strips fields that should not appear in the gallery output.
    """
    entry = {}
    icon_url = build_icon_url(data["id"], data["icon"])

    for key, value in data.items():
        if key in FIELDS_TO_REMOVE:
            continue
        entry[key] = value

    entry["iconUrl"] = icon_url

    screenshot_urls = discover_screenshots(data["id"])
    if screenshot_urls:
        entry["screenshotUrls"] = screenshot_urls

    return entry


def generate_gallery() -> dict:
    """Scan all extensions and return the complete gallery dict."""
    paths = discover_extension_paths()
    extensions: list[dict] = []
    skipped = 0

    for path in paths:
        data = load_extension(path)
        if data is None:
            skipped += 1
            continue
        extensions.append(transform_extension(data))

    # Sort alphabetically by id.
    extensions.sort(key=lambda ext: ext["id"])

    gallery = {
        "$schema": GALLERY_SCHEMA_URL,
        "version": "1.0",
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "extensionCount": len(extensions),
        "extensions": extensions,
    }

    if skipped:
        print(
            f"WARNING: {skipped} extension(s) skipped due to errors",
            file=sys.stderr,
        )

    return gallery


def write_gallery(gallery: dict) -> None:
    """Write the gallery JSON to the output file."""
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(gallery, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> None:
    gallery = generate_gallery()
    write_gallery(gallery)
    count = gallery["extensionCount"]
    print(f"Generated gallery with {count} extension{'s' if count != 1 else ''}")


if __name__ == "__main__":
    main()
