import { access, cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const sourceRoot = dirname(root);
const targetRoot = join(root, 'public', 'catalog');
const authorAvatarRoot = join(root, 'public', 'authors');
const catalog = JSON.parse(await readFile(join(sourceRoot, 'extensions.json'), 'utf8'));

const slugify = (value) => value
  .normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLocaleLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

const githubAuthors = new Map();
for (const extension of catalog.extensions) {
  try {
    const profileUrl = new URL(extension.author.url);
    if (profileUrl.hostname.toLocaleLowerCase() !== 'github.com') continue;
    const owner = profileUrl.pathname.split('/').filter(Boolean)[0];
    if (owner) githubAuthors.set(slugify(owner), owner);
  } catch { /* Non-URL publisher values keep the glyph fallback. */ }
}

const urls = catalog.extensions.flatMap((extension) => [
  extension.iconUrl,
  ...(extension.screenshotUrls ?? []),
]);

await rm(targetRoot, { recursive: true, force: true });

for (const url of urls) {
  const marker = '/main/';
  const markerIndex = url.indexOf(marker);
  if (markerIndex === -1) continue;

  const relativePath = decodeURIComponent(url.slice(markerIndex + marker.length));
  const source = join(sourceRoot, relativePath);
  const target = join(targetRoot, relativePath);
  await mkdir(dirname(target), { recursive: true });
  await cp(source, target);
}

await mkdir(authorAvatarRoot, { recursive: true });
let downloadedAvatars = 0;
for (const [slug, owner] of githubAuthors) {
  const target = join(authorAvatarRoot, `${slug}.png`);
  try {
    await access(target);
    continue;
  } catch { /* Download only avatars that are not already cached. */ }

  try {
    const response = await fetch(`https://github.com/${encodeURIComponent(owner)}.png?size=160`, {
      headers: { 'User-Agent': 'CmdPal-Web-Gallery catalog sync' },
    });
    if (!response.ok || !response.headers.get('content-type')?.startsWith('image/')) {
      throw new Error(`HTTP ${response.status}`);
    }
    await writeFile(target, Buffer.from(await response.arrayBuffer()));
    downloadedAvatars += 1;
  } catch (error) {
    console.warn(`Could not cache the GitHub avatar for ${owner}: ${error.message}`);
  }
}

console.log(`Synced ${urls.length} catalog assets and ${githubAuthors.size} author avatars (${downloadedAvatars} downloaded) for ${catalog.extensionCount} extensions.`);
