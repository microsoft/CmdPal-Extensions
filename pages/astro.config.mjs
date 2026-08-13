import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const site = process.env.ASTRO_SITE;
const base = process.env.ASTRO_BASE ?? '/';

export default defineConfig({
  ...(site ? { site } : {}),
  base,
  integrations: site ? [sitemap({
    filter: (page) => !page.endsWith('/404') && !page.endsWith('/404.html'),
  })] : [],
  output: 'static',
  trailingSlash: 'always',
  devToolbar: {
    enabled: false,
  },
});
