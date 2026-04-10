# Contributing to the Command Palette Extensions Gallery

Welcome! We're excited that you want to share your extension with the Command Palette community. This guide walks you through submitting your extension to the gallery so users can discover and install it.

## Overview

This repository is the **community gallery** for [Microsoft Command Palette](https://github.com/microsoft/PowerToys) extensions. Each extension is represented by a folder containing metadata and an icon. A CI pipeline aggregates all submissions into a single `extensions.json` file at the repo root that the Command Palette app fetches at runtime.

## Prerequisites

Before you begin, make sure you have:

- **Git** installed on your machine
- A **GitHub account**
- Your extension **already published** on one of the supported install sources:
  - [winget](https://github.com/microsoft/winget-pkgs) (Windows Package Manager)
  - [Microsoft Store](https://apps.microsoft.com/)
  - Direct download or release page URL

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
extensions/<author>/<extension-name>/
```

**Naming rules:**

| Rule | Detail |
|------|--------|
| Structure | `<author>/<extension-name>` — author folder containing extension folder |
| Author | Your name or org, lowercase alphanumeric + hyphens (e.g., `jiripolasek`, `microsoft`) |
| Extension name | Lowercase alphanumeric + hyphens (e.g., `media-controls`) |
| No leading/trailing hyphens | Each segment must start and end with an alphanumeric character |

**Examples:**

- ✅ `jiripolasek/media-controls`
- ✅ `my-company/clipboard-manager`
- ❌ `MediaControls` (missing author folder, uppercase)
- ❌ `my_company/clipboard_manager` (underscores not allowed)

### 4. Add `extension.json`

Create an `extension.json` file inside your folder. Here is the full template with all available fields:

```json
{
  "$schema": "../../../.github/schemas/extension.schema.json",
  "id": "publisher.my-extension",
  "title": "My Extension",
  "shortDescription": "A short description of what the extension does (max 200 characters).",
  "description": "A longer, detailed description of the extension. Typically sourced from the Store listing or project README.",
  "author": {
    "name": "Publisher Display Name",
    "url": "https://github.com/publisher"
  },
  "tags": ["tag1", "tag2"],
  "categories": ["productivity", "utilities-and-tools"],
  "icon": "icon.png",
  "installSources": [
    {
      "type": "winget",
      "id": "Publisher.PackageName"
    }
  ],
  "homepage": "https://github.com/publisher/extension"
}
```

#### Field reference

| Field | Required | Description |
|-------|----------|-------------|
| `$schema` | Optional | Path to the JSON schema. Enables editor autocompletion and validation. Use `"../../../.github/schemas/extension.schema.json"`. |
| `id` | **Required** | Unique identifier in `author.extension-name` format (e.g., `jiripolasek.media-controls`). **Must match your folder path** (`author/extension-name`). |
| `title` | **Required** | Human-readable display name (max 100 characters). |
| `shortDescription` | **Required** | Short one-line description of the extension (max 200 characters). |
| `description` | **Required** | Full description of the extension, typically sourced from the Store listing or README (max 3000 characters). |
| `author` | **Required** | Object with `name` (required, max 100 characters) and `url` (optional). |
| `tags` | Optional | Up to 5 freeform tags for filtering (each max 30 characters). |
| `categories` | Optional | Up to 3 categories from a fixed list. See [Allowed categories](#allowed-categories) below. |
| `icon` | **Required** | Filename of the icon in the same folder (e.g., `icon.png`). |
| `installSources` | **Required** | Array of install source objects. Each has a `type` and a type-specific identifier. See below. |
| `homepage` | Optional | URL to the project homepage or repository. |

#### Install source types

Each object in the `installSources` array has a `type` and a type-specific field:

| Type | Field | Description | Example |
|------|-------|-------------|---------|
| `winget` | `id` | The winget package identifier | `"Publisher.PackageName"` |
| `msstore` | `id` | Microsoft Store product ID | `"9n3bq81g19k7"` |
| `url` | `uri` | Direct download or release page URL | `"https://github.com/publisher/extension/releases"` |

#### Allowed categories

Choose up to 3 categories from the following fixed list:

| Category | Description |
|----------|-------------|
| `developer-tools` | Coding, debugging, developer utilities |
| `education` | Learning, study aids |
| `entertainment` | Streaming, media playback |
| `music` | Listening, creating, performing music |
| `news-and-weather` | News, forecasts |
| `personalization` | Themes, wallpaper, appearance |
| `photo-and-video` | Capture, editing, sharing |
| `productivity` | Task management, workflow, note-taking |
| `social` | Messaging, communication, collaboration |
| `utilities-and-tools` | Calculators, converters, file managers |

### 5. Add an icon

Place an icon file in your extension folder alongside `extension.json`.

- **Formats:** PNG (`.png`) or SVG (`.svg`)
- **Max file size:** 100 KB
- **Recommended dimensions:** 256×256 pixels for PNG files
- The filename must match the `icon` field in your `extension.json`

### 6. Add screenshots (optional)

To showcase your extension, add screenshots to a `screenshots/` folder inside your extension directory:

```
extensions/<author>/<extension-name>/
├── extension.json
├── icon.png
└── screenshots/
    ├── 01-main-view.png
    ├── 02-settings.png
    └── 03-search-results.jpg
```

**Screenshot rules:**

| Rule | Detail |
|------|--------|
| Folder name | `screenshots/` inside your extension folder |
| Formats | PNG (`.png`) or JPEG (`.jpg`, `.jpeg`) |
| Max file size | 1 MB per screenshot |
| Max count | 5 screenshots |
| Ordering | Alphabetical by filename — prefix with numbers to control order (e.g., `01-`, `02-`) |

Screenshots are automatically discovered by the gallery generation process when maintainers regenerate the gallery and update `extensions.json` with `screenshotUrls`. You do **not** need to reference them in `extension.json`.

### 7. Open a pull request

Push your branch to your fork and open a pull request targeting the `main` branch of this repository.

```bash
git add extensions/my-publisher/my-extension/
git commit -m "Add my-publisher.my-extension to gallery"
git push origin add-my-extension
```

Then open a PR on GitHub.

### 8. CI validation

Our CI pipeline automatically validates your submission. It checks that:

- Your `extension.json` conforms to the schema
- Required fields are present and correctly formatted
- The `id` matches the folder path (`author.extension-name` ↔ `author/extension-name/`)
- The icon file exists and is within size limits

If the CI reports errors, review the logs, fix the issues, and push updated commits to your PR branch.

### 9. Maintainer review and merge

A maintainer will review your PR. Once approved and merged, a maintainer will regenerate the gallery and open a separate PR to update `extensions.json`. After that PR is merged, your extension will appear in the Command Palette Extension Gallery.

> **Want to understand how the pipeline works?** See [Architecture](ARCHITECTURE.md) for full details.

## Updating an existing extension

To update an already-published extension (e.g., bump the version, update the description, or change the icon):

1. Create a new branch in your fork
2. Update the files in your existing `extensions/<author>/<extension-name>/` folder
3. Open a new pull request targeting `main`

The same CI validation and review process applies.

## Reference

See [`extensions/microsoft/sample-extension/`](../extensions/microsoft/sample-extension/) for a complete working example of a gallery submission.

## Schema reference

For editor autocompletion and inline validation, add the `$schema` property to the top of your `extension.json`:

```json
{
  "$schema": "../../../.github/schemas/extension.schema.json"
}
```

This enables IntelliSense in VS Code and other editors that support JSON Schema, giving you autocomplete suggestions, field descriptions, and real-time validation as you edit.
