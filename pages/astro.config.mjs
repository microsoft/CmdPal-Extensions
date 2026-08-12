import { defineConfig } from 'astro/config';

const site = process.env.ASTRO_SITE;
const base = process.env.ASTRO_BASE ?? '/';

export default defineConfig({
  ...(site ? { site } : {}),
  base,
  output: 'static',
  trailingSlash: 'never',
  devToolbar: {
    enabled: false,
  },
});
