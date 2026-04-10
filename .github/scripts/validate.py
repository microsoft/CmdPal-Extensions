#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Validate extension submissions for the CmdPal-Extensions gallery.

Checks that every modified extension folder contains a well-formed
extension.json that satisfies the JSON Schema, references a valid icon,
and has no duplicate IDs across the gallery.

Usage:
    # Validate extensions touched by specific changed files (CI mode)
    python scripts/validate.py extensions/quick-notes/extension.json

    # Validate ALL extensions in the gallery
    python scripts/validate.py

    # Auto-detect changes against origin/main
    python scripts/validate.py --diff
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
from typing import List, Set

try:
    import jsonschema
except ImportError:
    sys.exit(
        "ERROR: 'jsonschema' package is required. "
        "Install it with:  pip install -r scripts/requirements.txt"
    )

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
EXTENSIONS_DIR = REPO_ROOT / "extensions"
SCHEMA_PATH = REPO_ROOT / ".github" / "schemas" / "extension.schema.json"


MAX_TAGS = 5
MAX_TAG_LENGTH = 30
MAX_ICON_SIZE_KB = 100
VALID_ICON_EXTENSIONS = {".png", ".svg"}

MAX_CATEGORIES = 3
VALID_CATEGORIES = {
    "developer-tools",
    "education",
    "entertainment",
    "music",
    "news-and-weather",
    "personalization",
    "photo-and-video",
    "productivity",
    "social",
    "utilities-and-tools",
}

MAX_SCREENSHOTS = 5
MAX_SCREENSHOT_SIZE_KB = 1024  # 1 MB
VALID_SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# V2 id format: author.extension-name (e.g. "jiripolasek.media-controls")
ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.[a-z0-9]+(-[a-z0-9]+)*$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_schema() -> dict:
    """Load and return the JSON Schema for extension.json."""
    if not SCHEMA_PATH.exists():
        sys.exit(f"ERROR: Schema file not found at {SCHEMA_PATH}")
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def discover_extension_folders_from_files(changed_files: List[str]) -> Set[pathlib.Path]:
    """Given a list of changed file paths, return the set of extension folder
    paths (absolute) that were touched.
    Extensions live at extensions/<author>/<extension-name>/."""
    folders: Set[pathlib.Path] = set()
    for raw in changed_files:
        p = pathlib.Path(raw).resolve()
        try:
            rel = p.relative_to(EXTENSIONS_DIR)
        except ValueError:
            continue  # not under extensions/
        # Need at least 2 levels: author/extension-name
        if len(rel.parts) >= 2:
            ext_folder = EXTENSIONS_DIR / rel.parts[0] / rel.parts[1]
            if ext_folder.is_dir():
                folders.add(ext_folder)
    return folders


def discover_all_extension_folders() -> Set[pathlib.Path]:
    """Return every extension folder under extensions/<author>/<ext>/."""
    if not EXTENSIONS_DIR.is_dir():
        return set()
    folders: Set[pathlib.Path] = set()
    for author_dir in EXTENSIONS_DIR.iterdir():
        if not author_dir.is_dir():
            continue
        for ext_dir in author_dir.iterdir():
            if ext_dir.is_dir():
                folders.add(ext_dir)
    return folders


def git_diff_changed_files() -> List[str]:
    """Use git diff to find files changed relative to origin/main."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/main", "--", "extensions/"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=True,
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def build_id_index(exclude_folder: pathlib.Path | None = None) -> dict[str, pathlib.Path]:
    """Build a mapping of extension id -> folder for all extensions in the
    gallery, optionally excluding one folder (the one being validated)."""
    index: dict[str, pathlib.Path] = {}
    if not EXTENSIONS_DIR.is_dir():
        return index
    for author_dir in EXTENSIONS_DIR.iterdir():
        if not author_dir.is_dir():
            continue
        for folder in author_dir.iterdir():
            if not folder.is_dir():
                continue
            if exclude_folder and folder.resolve() == exclude_folder.resolve():
                continue
            ext_json = folder / "extension.json"
            if ext_json.exists():
                try:
                    with open(ext_json, encoding="utf-8") as fh:
                        data = json.load(fh)
                    ext_id = data.get("id")
                    if ext_id:
                        index[ext_id] = folder
                except (json.JSONDecodeError, OSError):
                    pass
    return index


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_extension(folder: pathlib.Path, schema: dict, id_index: dict[str, pathlib.Path]) -> List[str]:
    """Validate a single extension folder. Returns a list of error strings."""
    errors: List[str] = []
    folder_name = folder.name
    author_name = folder.parent.name
    display_path = f"{author_name}/{folder_name}"
    ext_json_path = folder / "extension.json"

    # 1. extension.json must exist
    if not ext_json_path.exists():
        errors.append(f"{display_path}: Missing required file extension.json")
        return errors  # nothing more to check

    # 2. Must be valid JSON
    try:
        with open(ext_json_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        errors.append(f"{display_path}/extension.json: Invalid JSON – {exc}")
        return errors

    # 3. JSON Schema validation
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as exc:
        path = " -> ".join(str(p) for p in exc.absolute_path) if exc.absolute_path else "(root)"
        errors.append(f"{display_path}/extension.json: Schema validation error at '{path}': {exc.message}")

    # 4. id must match folder path (author/extension-name -> author.extension-name)
    ext_id = data.get("id", "")
    author_dir = folder.parent.name
    expected_id = f"{author_dir}.{folder_name}"
    if ext_id != expected_id:
        errors.append(
            f"{author_dir}/{folder_name}/extension.json: 'id' field \"{ext_id}\" "
            f"does not match expected \"{expected_id}\" (from folder path {author_dir}/{folder_name}/)"
        )

    # 5. id must be a valid author.extension-name format
    if ext_id and not ID_PATTERN.match(ext_id):
        errors.append(
            f"{author_dir}/{folder_name}/extension.json: 'id' field \"{ext_id}\" is not valid. "
            f"Must be author.extension-name format (e.g. \"jiripolasek.media-controls\")."
        )

    # 6. Icon file must exist, be PNG/SVG, and ≤100 KB
    icon_filename = data.get("icon", "")
    if icon_filename:
        icon_path = folder / icon_filename
        if not icon_path.exists():
            errors.append(
                f"{display_path}/extension.json: Icon file \"{icon_filename}\" "
                f"not found in {display_path}/"
            )
        else:
            suffix = icon_path.suffix.lower()
            if suffix not in VALID_ICON_EXTENSIONS:
                errors.append(
                    f"{display_path}/{icon_filename}: Icon must be .png or .svg "
                    f"(got \"{suffix}\")"
                )
            size_kb = icon_path.stat().st_size / 1024
            if size_kb > MAX_ICON_SIZE_KB:
                errors.append(
                    f"{display_path}/{icon_filename}: Icon is {size_kb:.1f} KB, "
                    f"exceeds {MAX_ICON_SIZE_KB} KB limit"
                )

    # 7. Tags validation (when provided)
    tags = data.get("tags", [])
    if isinstance(tags, list):
        if len(tags) > MAX_TAGS:
            errors.append(
                f"{display_path}/extension.json: Too many tags ({len(tags)}). "
                f"Maximum is {MAX_TAGS}."
            )
        for i, tag in enumerate(tags):
            if isinstance(tag, str) and len(tag) > MAX_TAG_LENGTH:
                errors.append(
                    f"{display_path}/extension.json: Tag #{i + 1} \"{tag}\" "
                    f"exceeds {MAX_TAG_LENGTH} character limit ({len(tag)} chars)"
                )

    # 8. Duplicate ID check across the gallery
    if ext_id and ext_id in id_index:
        other = id_index[ext_id]
        other_display = f"{other.parent.name}/{other.name}"
        errors.append(
            f"{display_path}/extension.json: Duplicate id \"{ext_id}\" — "
            f"already used by {other_display}/"
        )

    # 9. Categories validation (when provided)
    categories = data.get("categories", [])
    if isinstance(categories, list):
        if len(categories) > MAX_CATEGORIES:
            errors.append(
                f"{display_path}/extension.json: Too many categories ({len(categories)}). "
                f"Maximum is {MAX_CATEGORIES}."
            )
        for i, cat in enumerate(categories):
            if isinstance(cat, str) and cat not in VALID_CATEGORIES:
                errors.append(
                    f"{display_path}/extension.json: Category #{i + 1} \"{cat}\" "
                    f"is not a valid category. "
                    f"Allowed values: {', '.join(sorted(VALID_CATEGORIES))}"
                )
        if len(categories) != len(set(categories)):
            errors.append(
                f"{display_path}/extension.json: Duplicate categories found. "
                f"Each category must be unique."
            )

    # 10. Screenshots validation (optional folder)
    screenshots_dir = folder / "screenshots"
    if screenshots_dir.is_dir():
        screenshot_files = [
            f for f in screenshots_dir.iterdir() if f.is_file()
        ]

        # Check for invalid file types
        for sf in screenshot_files:
            if sf.suffix.lower() not in VALID_SCREENSHOT_EXTENSIONS:
                errors.append(
                    f"{display_path}/screenshots/{sf.name}: Invalid file type "
                    f"\"{sf.suffix}\". Screenshots must be .png, .jpg, or .jpeg"
                )

        valid_screenshots = [
            f for f in screenshot_files
            if f.suffix.lower() in VALID_SCREENSHOT_EXTENSIONS
        ]

        # Check max number of screenshots
        if len(valid_screenshots) > MAX_SCREENSHOTS:
            errors.append(
                f"{display_path}/screenshots: Too many screenshots "
                f"({len(valid_screenshots)}). Maximum is {MAX_SCREENSHOTS}."
            )

        # Check file sizes
        for sf in valid_screenshots:
            size_kb = sf.stat().st_size / 1024
            if size_kb > MAX_SCREENSHOT_SIZE_KB:
                errors.append(
                    f"{display_path}/screenshots/{sf.name}: Screenshot is "
                    f"{size_kb:.1f} KB, exceeds {MAX_SCREENSHOT_SIZE_KB} KB limit"
                )

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate CmdPal extension submissions.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Changed file paths (e.g. extensions/quick-notes/extension.json). "
        "If omitted, validates ALL extensions under extensions/.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Auto-detect changed files via git diff against origin/main.",
    )
    args = parser.parse_args()

    # Determine which extension folders to validate
    if args.files:
        folders = discover_extension_folders_from_files(args.files)
    elif args.diff:
        changed = git_diff_changed_files()
        if not changed:
            print("No extension files changed relative to origin/main.")
            return 0
        folders = discover_extension_folders_from_files(changed)
    else:
        folders = discover_all_extension_folders()

    if not folders:
        print("No extension folders to validate.")
        return 0

    schema = load_schema()

    total_errors: List[str] = []
    validated_count = 0

    for folder in sorted(folders):
        display = f"{folder.parent.name}/{folder.name}"
        print(f"Validating {display}/ ...")
        # Build ID index excluding the current folder to detect duplicates elsewhere
        id_index = build_id_index(exclude_folder=folder)
        errors = validate_extension(folder, schema, id_index)
        if errors:
            for err in errors:
                print(f"  ❌ {err}")
            total_errors.extend(errors)
        else:
            print(f"  ✅ {display} is valid")
        validated_count += 1

    # Summary
    print()
    if total_errors:
        print(f"❌ {len(total_errors)} error(s) found across {validated_count} extension(s).")
        return 1
    else:
        print(f"✅ {validated_count} extension(s) validated successfully.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
