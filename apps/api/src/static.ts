import { existsSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import type { Context, Hono, MiddlewareHandler } from 'hono';
import { serveStatic } from '@hono/node-server/serve-static';

/** One rule of the dist's `_headers` file: a path (exact, or a prefix ending in `*`) and its headers. */
export interface HeaderRule {
  path: string;
  headers: Array<[string, string]>;
}

/**
 * The built viewer: its directory, the SPA shell (read once for the history fallback) and the
 * `_headers` rules its Cloudflare Pages build carries (`public/_headers`).
 */
export interface ViewerDist {
  root: string;
  indexHtml: string;
  headers: HeaderRule[];
}

/** `/api` and everything under it belongs to the API and never falls back to the SPA. */
export const isApiPath = (path: string): boolean => path === '/api' || path.startsWith('/api/');

/**
 * Vite's hashed bundles. A missing one is a real 404, not a client route: after a redeploy a stale
 * tab asks for bundles the new build no longer has, and an HTML shell served as JavaScript fails
 * opaquely where a 404 is plain in the network panel.
 */
export const isAssetPath = (path: string): boolean => path.startsWith('/assets/');

const isRead = (c: Context): boolean => c.req.method === 'GET' || c.req.method === 'HEAD';

/**
 * Parse a Pages `_headers` file: an unindented line is a path, the indented `Name: value` lines under
 * it are its headers, `#` starts a comment. Only exact paths and a trailing `*` splat are supported;
 * anything else throws, so a rule this service would misread stops startup.
 */
export function parseHeaders(text: string): HeaderRule[] {
  const rules: HeaderRule[] = [];
  for (const [i, line] of text.split('\n').entries()) {
    if (line.trim() === '' || line.trim().startsWith('#')) continue;
    if (!/^\s/.test(line)) {
      const path = line.trim();
      if (!path.startsWith('/') || /[:]|\*(?!$)/.test(path)) throw new Error(`_headers line ${i + 1}: unsupported path ${path}`);
      rules.push({ path, headers: [] });
      continue;
    }
    const colon = line.indexOf(':');
    const rule = rules.at(-1);
    if (!rule || colon < 0) throw new Error(`_headers line ${i + 1}: a header must be \`Name: value\` under a path`);
    rule.headers.push([line.slice(0, colon).trim(), line.slice(colon + 1).trim()]);
  }
  return rules;
}

/** The headers every rule matching `path` sets, in file order. */
export function headersFor(rules: HeaderRule[], path: string): Array<[string, string]> {
  return rules
    .filter((r) => (r.path.endsWith('*') ? path.startsWith(r.path.slice(0, -1)) : path === r.path))
    .flatMap((r) => r.headers);
}

/**
 * Resolve `dir` and read its `index.html` and `_headers` (absent ⇒ no rules). A missing shell throws,
 * so the service fails fast.
 */
export function loadViewerDist(dir: string): ViewerDist {
  const root = resolve(dir);
  let indexHtml: string;
  try {
    indexHtml = readFileSync(join(root, 'index.html'), 'utf8');
  } catch (err) {
    throw new Error(`VIEWER_DIST ${root} has no readable index.html (${(err as Error).message})`);
  }
  const headersFile = join(root, '_headers');
  const headers = existsSync(headersFile) ? parseHeaders(readFileSync(headersFile, 'utf8')) : [];
  return { root, indexHtml, headers };
}

/**
 * Serve the built viewer, porting the in-repo static host (`apps/viewer/server/index.mjs`): static
 * files from the dist, then `index.html` for any unmatched path so client routes deep-link. The
 * additions: `/api/*` is never served from the dist or given the fallback, and only GET/HEAD are.
 * Mount AFTER the API routes so they take precedence.
 *
 * The run data a `build:pages` dist bakes under `runs/` is served as Cloudflare Pages serves it: a
 * found file gets the headers `_headers` gives its path (`/runs/*` as `text/plain`, so it is
 * compressed), and an encoded run id (`/runs/archive%2Fx/summary.json`, as the client asks for it)
 * gets a 307 to the decoded path, as Pages' asset server answers it.
 */
export function mountViewer(app: Hono<any>, viewer: ViewerDist): void {
  const files = serveStatic({ root: viewer.root });
  const staticFiles: MiddlewareHandler = async (c, next) => {
    if (isApiPath(c.req.path) || !isRead(c)) return next();
    const url = new URL(c.req.url);
    if (url.pathname.startsWith('/runs/') && /%2f/i.test(url.pathname)) {
      return c.redirect(`${url.pathname.replace(/%2f/gi, '/')}${url.search}`, 307);
    }
    const res = await files(c, next);
    if (res) for (const [name, value] of headersFor(viewer.headers, c.req.path)) res.headers.set(name, value);
    return res;
  };
  app.use('/*', staticFiles);
}

/**
 * The not-found handler. An unmatched `/api/*` or `/assets/*` path is always a JSON 404. With a viewer
 * mounted, any other GET/HEAD is a client route and gets the SPA shell.
 */
export function notFoundHandler(viewer: ViewerDist | undefined) {
  return (c: Context) => {
    const path = c.req.path;
    if (viewer && !isApiPath(path) && !isAssetPath(path) && isRead(c)) return c.html(viewer.indexHtml);
    return c.json({ error: 'not found' }, 404);
  };
}
