import type { Context } from 'hono';
import { deleteCookie } from 'hono/cookie';
import type { CookieOptions } from 'hono/utils/cookie';

// Named for this service (multibench uses `mb_*`): cookies are scoped by host, not port, so two
// local services on `localhost` with the same cookie names would overwrite each other's session.
export const SESSION_COOKIE = 'st_session';
export const CSRF_COOKIE = 'st_csrf';
export const CSRF_HEADER = 'x-csrf-token';

// Cookie attributes are ported unchanged from multibench: SameSite=None (+Secure). Here the review
// UI and /api share one origin, so the cookies are first-party and work as-is; tightening to Lax
// is a deferred clean-up. The session cookie is httpOnly (JS can't read it); the CSRF cookie is the
// server-side half of the double-submit check (the client echoes the token in the CSRF header).
export function sessionCookieOptions(expires: Date, secure: boolean): CookieOptions {
  return { httpOnly: true, secure, sameSite: 'None', path: '/', expires };
}

export function csrfCookieOptions(expires: Date, secure: boolean): CookieOptions {
  return { httpOnly: false, secure, sameSite: 'None', path: '/', expires };
}

/**
 * Clear the session + CSRF cookies. The clear MUST carry the same `Secure`/`SameSite=None`/`Path`
 * attributes used when setting — a browser rejects a SameSite=None Set-Cookie clear that lacks
 * them, leaving stale cookies behind.
 */
export function clearAuthCookies(c: Context, secure: boolean): void {
  const opts = { path: '/', secure, sameSite: 'None' as const };
  deleteCookie(c, SESSION_COOKIE, opts);
  deleteCookie(c, CSRF_COOKIE, opts);
}
