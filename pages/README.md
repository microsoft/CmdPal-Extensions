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

## Privacy and cookie audit

Last reviewed: **August 13, 2026**.

The gallery is intentionally static and does not include analytics, advertising, tracking scripts, or code that writes cookies. A code audit and a response-header check of the GitHub Pages deployment found no `Set-Cookie` headers from the gallery itself.

The site stores two user-selected appearance preferences in browser local storage:

- `cmdpal-gallery-theme` restores light, dark, or automatic theme selection.
- `cmdpal-gallery-style` restores Aero, teal, or legacy visual style selection.

These values are used only in the browser to restore the requested interface and are not transmitted by the gallery.

Author images use the direct `https://avatars.githubusercontent.com/<username>?s=160` endpoint. The earlier `https://github.com/<username>.png` shortcut was removed because it redirects and can emit GitHub cookies before returning the image. The direct avatar request was checked without finding a `Set-Cookie` response, but it is still a third-party request: normal connection data such as the visitor's IP address and user agent is available to GitHub.

### Banner decision

The gallery does **not** show a cookie-consent banner because the current implementation has no non-essential cookies or tracking technologies. The two local-storage values provide appearance customization explicitly requested by the visitor. A banner would therefore interrupt the experience without presenting a meaningful consent choice.

This decision must be reviewed before introducing analytics, advertising, embedded media, social widgets, or any other non-essential storage or tracking. The public-facing disclosure is maintained in [`src/pages/privacy.astro`](src/pages/privacy.astro) and is linked from the shared site footer.

The assessment considered:

- [EU ePrivacy Directive, Article 5(3)](https://eur-lex.europa.eu/eli/dir/2002/58/art_5/par_3/oj/eng)
- [EDPB Guidelines 2/2023 on the technical scope of Article 5(3)](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-22023-technical-scope-art-53-eprivacy-directive_en)
- [CNIL guidance on cookies and other trackers](https://www.cnil.fr/fr/cookies-et-autres-traceurs/regles/cookies/comment-mettre-mon-site-web-en-conformite)
- [Czech Office for Personal Data Protection cookie guidance](https://uoou.gov.cz/novinky/vse/cookies-od-zacatku-roku-2022-pouze-se-souhlasem)

This is a practical engineering audit, not legal advice.
