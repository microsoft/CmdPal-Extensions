# Command Palette Extensions Gallery

The community gallery of extensions for [Microsoft Command Palette](https://github.com/microsoft/PowerToys). This repository provides a curated list of extensions that users can discover and install directly from within Command Palette.

## How it works

Each extension is represented by a folder under `extensions/` containing an `extension.json` metadata file and an icon. A CI pipeline aggregates all individual submissions into a single [`generated/extensions.json`](generated/extensions.json) file that the Command Palette app fetches at runtime to populate its extension gallery.

## For extension developers

Want to list your extension in the gallery? We'd love to have you! Check out the **[Contributing Guide](docs/CONTRIBUTING.md)** for step-by-step instructions on how to submit your extension.

## Gallery JSON endpoint

The Command Palette app fetches the gallery from:

```
https://raw.githubusercontent.com/microsoft/CmdPal-Extensions/main/generated/extensions.json
```

## Repository structure

```
CmdPal-Extensions/
├── extensions/                  # One folder per extension submission
│   └── <publisher>.<ext-id>/
│       ├── extension.json       # Extension metadata
│       └── icon.png             # Extension icon
├── generated/
│   └── extensions.json          # Auto-generated aggregate (do not edit)
├── schemas/
│   └── extension.schema.json    # JSON Schema for extension.json
├── scripts/                     # CI/build scripts
└── docs/
    └── CONTRIBUTING.md          # Submission guide for developers
```

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit the [Microsoft CLA site](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information, see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.
