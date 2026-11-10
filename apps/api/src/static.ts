import { readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import type { Context, Hono, MiddlewareHandler } from 'hono';
import { serveStatic } from '@hono/node-server/serve-static';

/** The built viewer: its directory and the SPA shell, read once for the history fallback. */
export interface ViewerDist {
  root: string;
  indexHtml: string;
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

/** Resolve `dir` and read its `index.html`. A missing shell throws, so the service fails fast. */
export function loadViewerDist(dir: string): ViewerDist {
  const root = resolve(dir);
  let indexHtml: string;
  try {
    indexHtml = readFileSync(join(root, 'index.html'), 'utf8');
  } catch (err) {
    throw new Error(`VIEWER_DIST ${root} has no readable index.html (${(err as Error).message})`);
  }
  return { root, indexHtml };
}

/**
 * Serve the built viewer, porting the in-repo static host (`apps/viewer/server/index.mjs`): static
 * files from the dist, then `index.html` for any unmatched path so client routes deep-link. The
 * additions: `/api/*` is never served from the dist or given the fallback, and only GET/HEAD are.
 * Mount AFTER the API routes so they take precedence.
 */
export function mountViewer(app: Hono<any>, viewer: ViewerDist): void {
  const files = serveStatic({ root: viewer.root });
  const staticFiles: MiddlewareHandler = async (c, next) => {
    if (isApiPath(c.req.path) || !isRead(c)) return next();
    return files(c, next);
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
