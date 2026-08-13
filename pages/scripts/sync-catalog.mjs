import { cp, mkdir, readFile, rm } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const sourceRoot = dirname(root);
const targetRoot = join(root, 'public', 'catalog');
const catalog = JSON.parse(await readFile(join(sourceRoot, 'extensions.json'), 'utf8'));

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

console.log(`Synced ${urls.length} catalog assets for ${catalog.extensionCount} extensions.`);
