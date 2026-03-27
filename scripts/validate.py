#!/usr/bin/env python3
"""Validate extension submissions for the CmdPal-Extensions gallery.

Checks that every modified extension folder contains a well-formed
extension.json that satisfies the JSON Schema, references a valid icon,
and has no duplicate IDs across the gallery.

Usage:
    # Validate extensions touched by specific changed files (CI mode)
    python scripts/validate.py extensions/contoso.quick-notes/extension.json

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

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
EXTENSIONS_DIR = REPO_ROOT / "extensions"
SCHEMA_PATH = REPO_ROOT / "schemas" / "extension.schema.json"

VALID_CATEGORIES = {
    "Developer Tools",
    "Productivity",
    "Utilities",
    "System",
    "Media",
    "Communication",
    "Education",
    "Entertainment",
    "Security",
    "Other",
}

MAX_TAGS = 5
MAX_TAG_LENGTH = 30
MAX_ICON_SIZE_KB = 100
VALID_ICON_EXTENSIONS = {".png", ".svg"}


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
    paths (absolute) that were touched."""
    folders: Set[pathlib.Path] = set()
    for raw in changed_files:
        p = pathlib.Path(raw).resolve()
        # Walk up to find a path whose parent is the extensions/ dir.
        # e.g. extensions/contoso.quick-notes/extension.json -> extensions/contoso.quick-notes
        try:
            rel = p.relative_to(EXTENSIONS_DIR)
        except ValueError:
            continue  # not under extensions/
        top_folder = EXTENSIONS_DIR / rel.parts[0]
        if top_folder.is_dir():
            folders.add(top_folder)
    return folders


def discover_all_extension_folders() -> Set[pathlib.Path]:
    """Return every immediate sub-directory of extensions/."""
    if not EXTENSIONS_DIR.is_dir():
        return set()
    return {d for d in EXTENSIONS_DIR.iterdir() if d.is_dir()}


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
    for folder in EXTENSIONS_DIR.iterdir():
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
                pass  # skip broken files; they'll be caught during their own validation
    return index


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_extension(folder: pathlib.Path, schema: dict, id_index: dict[str, pathlib.Path]) -> List[str]:
    """Validate a single extension folder. Returns a list of error strings."""
    errors: List[str] = []
    folder_name = folder.name
    ext_json_path = folder / "extension.json"

    # 1. extension.json must exist
    if not ext_json_path.exists():
        errors.append(f"{folder_name}: Missing required file extension.json")
        return errors  # nothing more to check

    # 2. Must be valid JSON
    try:
        with open(ext_json_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        errors.append(f"{folder_name}/extension.json: Invalid JSON – {exc}")
        return errors

    # 3. JSON Schema validation
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as exc:
        path = " -> ".join(str(p) for p in exc.absolute_path) if exc.absolute_path else "(root)"
        errors.append(f"{folder_name}/extension.json: Schema validation error at '{path}': {exc.message}")

    # 4. id must match folder name
    ext_id = data.get("id", "")
    if ext_id != folder_name:
        errors.append(
            f"{folder_name}/extension.json: 'id' field \"{ext_id}\" "
            f"does not match folder name \"{folder_name}\""
        )

    # 5. Icon file must exist, be PNG/SVG, and ≤100 KB
    icon_filename = data.get("icon", "")
    if icon_filename:
        icon_path = folder / icon_filename
        if not icon_path.exists():
            errors.append(
                f"{folder_name}/extension.json: Icon file \"{icon_filename}\" "
                f"not found in {folder_name}/"
            )
        else:
            suffix = icon_path.suffix.lower()
            if suffix not in VALID_ICON_EXTENSIONS:
                errors.append(
                    f"{folder_name}/{icon_filename}: Icon must be .png or .svg "
                    f"(got \"{suffix}\")"
                )
            size_kb = icon_path.stat().st_size / 1024
            if size_kb > MAX_ICON_SIZE_KB:
                errors.append(
                    f"{folder_name}/{icon_filename}: Icon is {size_kb:.1f} KB, "
                    f"exceeds {MAX_ICON_SIZE_KB} KB limit"
                )

    # 6. Category must be from the predefined list
    category = data.get("category", "")
    if category and category not in VALID_CATEGORIES:
        errors.append(
            f"{folder_name}/extension.json: Invalid category \"{category}\". "
            f"Must be one of: {', '.join(sorted(VALID_CATEGORIES))}"
        )

    # 7. Tags validation
    tags = data.get("tags", [])
    if isinstance(tags, list):
        if len(tags) > MAX_TAGS:
            errors.append(
                f"{folder_name}/extension.json: Too many tags ({len(tags)}). "
                f"Maximum is {MAX_TAGS}."
            )
        for i, tag in enumerate(tags):
            if isinstance(tag, str) and len(tag) > MAX_TAG_LENGTH:
                errors.append(
                    f"{folder_name}/extension.json: Tag #{i + 1} \"{tag}\" "
                    f"exceeds {MAX_TAG_LENGTH} character limit ({len(tag)} chars)"
                )

    # 8. Duplicate ID check across the gallery
    if ext_id and ext_id in id_index:
        other = id_index[ext_id]
        errors.append(
            f"{folder_name}/extension.json: Duplicate id \"{ext_id}\" — "
            f"already used by {other.name}/"
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
        help="Changed file paths (e.g. extensions/contoso.quick-notes/extension.json). "
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
        print(f"Validating {folder.name}/ ...")
        # Build ID index excluding the current folder to detect duplicates elsewhere
        id_index = build_id_index(exclude_folder=folder)
        errors = validate_extension(folder, schema, id_index)
        if errors:
            for err in errors:
                print(f"  ❌ {err}")
            total_errors.extend(errors)
        else:
            print(f"  ✅ {folder.name} is valid")
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
