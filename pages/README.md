# Command Palette Extensions Gallery

A static Astro gallery for community-built Microsoft PowerToys Command Palette extensions. The site reads the catalog directly from [`../extensions.json`](../extensions.json) and generates a searchable home page plus one detail page per extension.

## Run locally

```powershell
cd pages
npm install
npm run dev
```

Open `http://localhost:4321`.

## Production build

```powershell
npm run build
```

The build syncs referenced icons and screenshots from the parent catalog repository into `public/catalog`, then writes the static site to `dist`.

## GitHub Pages

The repository workflow builds this project with the repository name as Astro's base path and publishes it at `https://<owner>.github.io/<repository>/`.

On the fork, open **Settings → Pages** and select **GitHub Actions** as the source. Pushes to `main` that change the catalog, gallery, or deployment workflow will publish a new version automatically.
