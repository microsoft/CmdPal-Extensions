# Architecture

This document describes the internal architecture of the CmdPal-Extensions gallery repository — how submissions are validated, how the gallery JSON is generated, and how the CI/CD pipeline ties everything together.

## Repository structure

```
CmdPal-Extensions/
├── extensions/                        # Extension submissions
│   └── <author>/
│       └── <extension-name>/
│           ├── extension.json         # Extension metadata
│           ├── icon.png               # Extension icon
│           └── screenshots/           # Optional extension screenshots
│               ├── 01-main.png
│               └── 02-settings.png
├── extensions.json                    # Generated gallery (do not edit manually)
├── .github/
│   ├── schemas/
│   │   └── extension.schema.json      # JSON Schema for extension.json
│   ├── scripts/
│   │   ├── generate.py                # Gallery generation script
│   │   ├── validate.py                # Submission validation script
│   │   └── requirements.txt           # Python dependencies
│   ├── workflows/
│   │   └── validate-pr.yml            # CI: validates PRs
│   └── PULL_REQUEST_TEMPLATE.md
└── docs/
    ├── CONTRIBUTING.md                # Contributor guide
    └── ARCHITECTURE.md                # This file
```

## Data flow

The end-to-end flow from submission to gallery update:

```
Contributor opens PR
        │
        ▼
┌─────────────────────┐
│  validate-pr.yml    │  Runs on: pull_request → main (extensions/** changed)
│  (CI validation)    │  Checks schema, icon, id format, duplicates
└────────┬────────────┘
         │ ✅ passes
         ▼
  Maintainer reviews & merges PR
         │
         ▼
  Maintainer runs generate.py locally
  (python .github/scripts/generate.py)
         │
         ▼
  Maintainer opens a PR with updated extensions.json
         │
         ▼
  extensions.json updated on main
  (Command Palette app fetches this at runtime)
```

## GitHub Actions workflows

### `validate-pr.yml` — Validate Extension Submission

**Trigger:** Pull requests targeting `main` that modify files under `extensions/`.

**What it does:**
1. Checks out the repository with full history (`fetch-depth: 0`)
2. Identifies which extension folders were changed using `git diff` against `origin/main`
3. Runs `validate.py` on the changed files

**Validation checks** (performed by `validate.py`):
- `extension.json` exists and is valid JSON
- Conforms to the JSON Schema (`.github/schemas/extension.schema.json`)
- The `id` field matches the folder path (`author/extension-name` → `author.extension-name`)
- The `id` format is valid (lowercase alphanumeric + hyphens, dot-separated)
- Icon file exists, is PNG or JPEG, and is under 100 KB
- Tags are within limits (max 5 tags, each max 30 characters)
- Categories (if present) are from the allowed list, max 3, no duplicates
- No duplicate IDs across the gallery
- Screenshots (if present) are valid: max 5 files, PNG/JPEG only, max 1 MB each

### Gallery generation (manual)

Gallery generation is a manual process performed by maintainers. After merging a contributor's PR that adds or updates extensions, a maintainer regenerates `extensions.json`:

```bash
pip install -r .github/scripts/requirements.txt
python .github/scripts/generate.py
```

The maintainer then opens a separate PR with the updated `extensions.json` and merges it.

> **Why manual?** The Microsoft GitHub org enforces read-only `GITHUB_TOKEN` permissions and disables automated PR creation at the org level. This prevents GitHub Actions workflows from creating PRs or pushing directly to protected branches.

## Scripts

### `generate.py`

Scans all `extensions/<author>/<extension-name>/extension.json` files, transforms each into a gallery entry, and writes the aggregate result to `extensions.json` at the repo root.

Key transformations:
- The relative `icon` field is replaced with an absolute `iconUrl` pointing to the raw GitHub URL
- Screenshots in the `screenshots/` folder are discovered and added as `screenshotUrls` (sorted alphabetically)
- An `addedAt` date is stamped on each extension — new extensions get today's date, existing extensions preserve their original date from the previous `extensions.json`
- Fields like `$schema` and `icon` are stripped from the gallery output
- Extensions are sorted alphabetically by `id`
- A `generatedAt` timestamp and `extensionCount` are added to the gallery metadata

### `validate.py`

Validates extension submissions. Can be run in three modes:
- **File list mode:** `python validate.py <file1> <file2> ...` — validates extensions touched by specific files (used by CI)
- **Diff mode:** `python validate.py --diff` — auto-detects changes against `origin/main`
- **Full mode:** `python validate.py` — validates all extensions in the gallery

## Schema files

### `extension.schema.json`

JSON Schema (draft-07) defining the structure of individual `extension.json` files. Used by:
- `validate.py` for CI validation
- Editors (VS Code, etc.) for autocompletion and inline validation when contributors add `"$schema"` to their `extension.json`

### `gallery.schema.json`

Defined via URL in the generated `extensions.json`. Describes the shape of the aggregate gallery file that the Command Palette app consumes at runtime.
