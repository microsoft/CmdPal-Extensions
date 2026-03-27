# Contributing to the Command Palette Extensions Gallery

Welcome! We're excited that you want to share your extension with the Command Palette community. This guide walks you through submitting your extension to the gallery so users can discover and install it.

## Overview

This repository is the **community gallery** for [Microsoft Command Palette](https://github.com/microsoft/PowerToys) extensions. Each extension is represented by a folder containing metadata and an icon. A CI pipeline aggregates all submissions into a single `generated/extensions.json` file that the Command Palette app fetches at runtime.

## Prerequisites

Before you begin, make sure you have:

- **Git** installed on your machine
- A **GitHub account**
- Your extension **already published** on one of the supported install sources:
  - [winget](https://github.com/microsoft/winget-pkgs) (Windows Package Manager)
  - [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
  - [Microsoft Store](https://apps.microsoft.com/)

## Step-by-step submission guide

### 1. Fork this repository

Click the **Fork** button at the top-right of the [CmdPal-Extensions](https://github.com/microsoft/CmdPal-Extensions) repository page to create your own copy.

### 2. Create a new branch

```bash
git checkout -b add-my-extension
```

### 3. Create your extension folder

Create a folder under `extensions/` using the naming convention:

```
extensions/<publisher>.<extension-id>/
```

**Naming rules:**

| Rule | Detail |
|------|--------|
| Format | `<publisher>.<extension-id>` |
| Characters | Lowercase alphanumeric characters and hyphens only (`a-z`, `0-9`, `-`) |
| Separator | A single dot (`.`) separates publisher from extension name |
| Hyphens | Use hyphens to separate words (e.g., `quick-notes`, not `quicknotes`) |
| No leading/trailing hyphens | Each segment must start and end with an alphanumeric character |

**Examples:**

- ✅ `contoso.quick-notes`
- ✅ `my-company.clipboard-manager`
- ❌ `Contoso.QuickNotes` (uppercase not allowed)
- ❌ `contoso_quick_notes` (underscores not allowed, missing dot separator)

### 4. Add `extension.json`

Create an `extension.json` file inside your folder. Here is the full template with all available fields:

```json
{
  "$schema": "../../schemas/extension.schema.json",
  "id": "publisher.extension-id",
  "name": "My Extension",
  "description": "A short description of what the extension does (max 200 characters).",
  "publisher": "Publisher Display Name",
  "version": "1.0.0",
  "category": "Utilities",
  "tags": ["tag1", "tag2"],
  "icon": "icon.png",
  "installSource": {
    "type": "winget",
    "value": "Publisher.PackageName"
  },
  "homepage": "https://github.com/publisher/extension",
  "license": "MIT"
}
```

#### Field reference

| Field | Required | Description |
|-------|----------|-------------|
| `$schema` | Optional | Path to the JSON schema. Enables editor autocompletion and validation. Use `"../../schemas/extension.schema.json"`. |
| `id` | **Required** | Unique identifier in `<publisher>.<extension-id>` format. **Must match your folder name exactly.** |
| `name` | **Required** | Human-readable display name (max 100 characters). |
| `description` | **Required** | Short description of the extension (max 200 characters). |
| `publisher` | **Required** | Publisher display name (max 100 characters). |
| `version` | **Required** | Semantic version string (e.g., `1.0.0`, `2.1.0-beta.1`). |
| `category` | **Required** | Primary category. Must be one of the valid categories listed below. |
| `tags` | Optional | Up to 5 freeform tags for filtering (each max 30 characters). |
| `icon` | **Required** | Filename of the icon in the same folder (e.g., `icon.png`). |
| `installSource` | **Required** | Object with `type` and `value` describing where to install the extension. |
| `homepage` | Optional | URL to the project homepage or repository. |
| `license` | Optional | SPDX license identifier (e.g., `MIT`, `Apache-2.0`). |

#### Valid categories

- `Developer Tools`
- `Productivity`
- `Utilities`
- `System`
- `Media`
- `Communication`
- `Education`
- `Entertainment`
- `Security`
- `Other`

#### Install source types

The `installSource` object has two fields — `type` and `value`:

| Type | Value | Example |
|------|-------|---------|
| `winget` | The winget package identifier | `"Publisher.PackageName"` |
| `github` | Full URL to the GitHub repository or releases page | `"https://github.com/publisher/repo"` |
| `store` | Microsoft Store link or product ID | `"https://apps.microsoft.com/detail/..."` |

### 5. Add an icon

Place an icon file in your extension folder alongside `extension.json`.

- **Formats:** PNG (`.png`) or SVG (`.svg`)
- **Max file size:** 100 KB
- **Recommended dimensions:** 256×256 pixels for PNG files
- The filename must match the `icon` field in your `extension.json`

### 6. Open a pull request

Push your branch to your fork and open a pull request targeting the `main` branch of this repository.

```bash
git add extensions/my-publisher.my-extension/
git commit -m "Add my-publisher.my-extension to gallery"
git push origin add-my-extension
```

Then open a PR on GitHub.

### 7. CI validation

Our CI pipeline automatically validates your submission. It checks that:

- Your `extension.json` conforms to the schema
- Required fields are present and correctly formatted
- The `id` matches the folder name
- The icon file exists and is within size limits

If the CI reports errors, review the logs, fix the issues, and push updated commits to your PR branch.

### 8. Maintainer review and merge

A maintainer will review your PR. Once approved and merged, your extension will appear in the gallery the next time the app refreshes its extension list.

## Updating an existing extension

To update an already-published extension (e.g., bump the version, update the description, or change the icon):

1. Create a new branch in your fork
2. Update the files in your existing `extensions/<publisher>.<extension-id>/` folder
3. Open a new pull request targeting `main`

The same CI validation and review process applies.

## Reference

See [`extensions/microsoft.sample-extension/`](../extensions/microsoft.sample-extension/) for a complete working example of a gallery submission.

## Schema reference

For editor autocompletion and inline validation, add the `$schema` property to the top of your `extension.json`:

```json
{
  "$schema": "../../schemas/extension.schema.json"
}
```

This enables IntelliSense in VS Code and other editors that support JSON Schema, giving you autocomplete suggestions, field descriptions, and real-time validation as you edit.
