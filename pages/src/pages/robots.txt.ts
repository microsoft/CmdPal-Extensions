import type { APIRoute } from 'astro';

export const prerender = true;

export const GET: APIRoute = ({ site }) => {
  const base = import.meta.env.BASE_URL.endsWith('/')
    ? import.meta.env.BASE_URL
    : `${import.meta.env.BASE_URL}/`;
  const sitemap = site
    ? `Sitemap: ${new URL(`${base}sitemap-index.xml`, site)}\n`
    : '';

  return new Response(`# Squirrels welcome. Please crawl responsibly.
User-agent: *
Allow: /

${sitemap}`, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
    },
  });
};
