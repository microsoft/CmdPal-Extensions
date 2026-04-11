<p align="center">
  <img src="docs/images/gallery.png" alt="Extension Gallery in Command Palette" width="700" />
</p>

<h1 align="center">🎨 Command Palette Extensions Gallery</h1>
<p align="center">
  The official community gallery for <a href="https://github.com/microsoft/PowerToys">Command Palette</a> extensions.
</p>
<h3 align="center">
  <a href="#-submit-your-extension">Submit an extension</a>
  <span> · </span>
  <a href="https://learn.microsoft.com/windows/powertoys/command-palette/extensibility-overview">Create your own extension</a>
</h3>

🔍 **Discoverable by millions** — your extension shows up right inside Command Palette, where users are already looking

📦 **Host it your way** — publish through winget, the Microsoft Store, or your own download link — you stay in control

🌍 **Open-source & community-driven** — join a growing ecosystem of developers extending Windows productivity

## 🛠️ Submit your extension

New to building Command Palette extensions? Check out the [Extension Development docs](https://learn.microsoft.com/windows/powertoys/command-palette/extensibility-overview) to get started.

Once your extension is ready, follow these steps to list it in the gallery:

1. **Fork** this repository
2. **Create a folder** at `extensions/<your-name>/<extension-name>/` (lowercase, hyphens only)
3. **Add an `extension.json`** with your extension metadata — see the [Contributing Guide](docs/CONTRIBUTING.md) for the full field reference and template
4. **Add an icon** (PNG or SVG, max 100 KB, 256×256 recommended) in the same folder
5. **Publish your extension** to at least one install source: [winget](https://learn.microsoft.com/windows/powertoys/command-palette/publish-extension), [Microsoft Store](https://learn.microsoft.com/windows/powertoys/command-palette/publish-extension), or a direct download URL (e.g. a [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) page)
6. **Open a pull request** targeting `main`

CI will validate your submission automatically and the Command Palette team will review your PR. Once merged, your extension will show up in the Command Palette Extension Gallery.

See [`extensions/microsoft/sample-extension/`](extensions/microsoft/sample-extension/) for a complete example.

<p align="center">
  <img src="docs/images/details.png" alt="Extension details page" width="700" />
</p>

## 🤝 Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit the [Microsoft CLA site](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information, see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## ⚖️ Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.
