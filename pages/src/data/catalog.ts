import catalogJson from '../../../extensions.json';

export interface InstallSource {
  type: 'msstore' | 'winget' | string;
  id: string;
}

export interface ExtensionAuthor {
  name: string;
  url: string;
}

export interface Extension {
  id: string;
  title: string;
  shortDescription: string;
  description: string;
  author: ExtensionAuthor;
  homepage: string;
  tags: string[];
  categories: string[];
  installSources: InstallSource[];
  iconUrl: string;
  screenshotUrls?: string[];
  addedAt: string;
}

export interface Catalog {
  version: string;
  generatedAt: string;
  extensionCount: number;
  extensions: Extension[];
}

export interface CatalogAuthor extends ExtensionAuthor {
  slug: string;
  extensions: Extension[];
}

const rawCatalog = catalogJson as Catalog;

export const catalog: Catalog = {
  ...rawCatalog,
  extensions: rawCatalog.extensions.map((extension) => ({
    ...extension,
    tags: extension.tags ?? [],
    categories: extension.categories ?? [],
    installSources: extension.installSources ?? [],
    screenshotUrls: extension.screenshotUrls ?? [],
  })),
};

const slugify = (value: string) => value
  .normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLocaleLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

const basePath = import.meta.env.BASE_URL === '/'
  ? ''
  : import.meta.env.BASE_URL.replace(/\/$/, '');

export const withBase = (path: string) => `${basePath}${path}` || '/';

export const toAuthorSlug = (author: ExtensionAuthor) => {
  try {
    const url = new URL(author.url);
    if (url.hostname.toLocaleLowerCase() === 'github.com') {
      const owner = url.pathname.split('/').filter(Boolean)[0];
      if (owner) return slugify(owner);
    }
  } catch { /* Fall back to the publisher name for non-URL values. */ }

  return slugify(author.name);
};

export const toAuthorPageUrl = (author: ExtensionAuthor) => withBase(`/authors/${toAuthorSlug(author)}`);

export const toAuthorAvatarUrl = (author: ExtensionAuthor) => {
  try {
    const url = new URL(author.url);
    if (url.hostname.toLocaleLowerCase() === 'github.com' && url.pathname.split('/').filter(Boolean)[0]) {
      return withBase(`/authors/${toAuthorSlug(author)}.png`);
    }
  } catch { /* Non-URL publisher values use the glyph fallback. */ }

  return undefined;
};

const authorMap = new Map<string, CatalogAuthor>();
catalog.extensions.forEach((extension) => {
  const slug = toAuthorSlug(extension.author);
  const existing = authorMap.get(slug);
  if (existing) {
    existing.extensions.push(extension);
  } else {
    authorMap.set(slug, { ...extension.author, slug, extensions: [extension] });
  }
});

export const authors = [...authorMap.values()]
  .map((author) => ({
    ...author,
    extensions: author.extensions.sort((left, right) =>
      right.addedAt.localeCompare(left.addedAt) || left.title.localeCompare(right.title),
    ),
  }))
  .sort((left, right) => left.name.localeCompare(right.name));

export const categoryLabels: Record<string, string> = {
  'developer-tools': 'Developer tools',
  'education': 'Education',
  'entertainment': 'Entertainment',
  'music': 'Music',
  'news-and-weather': 'News & weather',
  'personalization': 'Personalization',
  'productivity': 'Productivity',
  'social': 'Social',
  'utilities-and-tools': 'Utilities & tools',
};

export const toLocalAsset = (url: string) => {
  const marker = '/main/';
  const markerIndex = url.indexOf(marker);
  if (markerIndex === -1) return url;

  return withBase(`/catalog/${url
    .slice(markerIndex + marker.length)
    .split('/')
    .map((segment) => encodeURIComponent(decodeURIComponent(segment)))
    .join('/')}`);
};

export const toExtensionPageUrl = (extensionId: string) => withBase(`/extensions/${extensionId}`);

export const toStoreUrl = (id: string) => `https://apps.microsoft.com/detail/${id}`;

export const toCmdPalGalleryUrl = (extensionId?: string) =>
  extensionId
    ? `x-cmdpal://extensions/gallery/${encodeURIComponent(extensionId)}`
    : 'x-cmdpal://extensions/gallery';

export const categoryEntries = Object.entries(
  catalog.extensions.reduce<Record<string, number>>((counts, extension) => {
    extension.categories.forEach((category) => {
      counts[category] = (counts[category] ?? 0) + 1;
    });
    return counts;
  }, {}),
).sort(([, left], [, right]) => right - left);
