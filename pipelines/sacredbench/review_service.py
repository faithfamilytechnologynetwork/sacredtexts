"""Read a reviewer's gold set from the review service (issue #157), for ``review-compare --from-service``.

It signs in through the service's own login endpoint with the reviewer's email and password, fetches
``GET /api/gold-set`` (the same bytes as the review page's download), and signs out again, so the
session it opened is deleted at once. The session token lives only in memory: nothing is written to
disk, and neither the credentials nor the token appear in any message. Standard library only.
"""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from sacredbench.review_compare import ReviewCompareError

SESSION_COOKIE = "st_session"
CSRF_COOKIE = "st_csrf"
CSRF_HEADER = "X-CSRF-Token"
# Plain http is allowed only to this machine, so a password never crosses a network unencrypted.
LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1")
TIMEOUT_S = 60


def service_base(url: str) -> str:
    """The base URL without a trailing ``/``: ``https://``, or ``http://`` to this machine only."""
    parts = urlsplit(url)
    if parts.scheme == "https" or (parts.scheme == "http" and parts.hostname in LOCAL_HOSTS):
        return url.rstrip("/")
    raise ReviewCompareError(f"--from-service {url!r}: the review service must be https:// (http:// only to localhost)")


def _send(request: Request) -> tuple[int, object, bytes]:
    try:
        with urlopen(request, timeout=TIMEOUT_S) as resp:
            return resp.status, resp.headers, resp.read()
    except HTTPError as exc:
        return exc.code, exc.headers, exc.read()
    except URLError as exc:
        raise ReviewCompareError(f"cannot reach the review service at {request.full_url} ({exc.reason})") from exc


def _json(what: str, status: int, headers, body: bytes) -> dict:
    content_type = headers.get_content_type()
    try:
        if content_type != "application/json":
            raise ValueError(content_type)
        value = json.loads(body)
    except ValueError as exc:
        raise ReviewCompareError(f"{what}: the review service answered {status} with {content_type}, not JSON") from exc
    if not isinstance(value, dict):
        raise ReviewCompareError(f"{what}: the review service answered {status} with JSON that is not an object")
    return value


def fetch_gold_set(base_url: str, email: str, password: str) -> str:
    """The signed-in reviewer's gold set for the service's active sample, as JSONL text."""
    base = service_base(base_url)
    credentials = json.dumps({"email": email, "password": password}).encode("utf-8")
    status, headers, body = _send(
        Request(f"{base}/api/auth/login", data=credentials, headers={"Content-Type": "application/json"}, method="POST")
    )
    login = _json(f"login to {base}", status, headers, body)
    if status != 200:
        raise ReviewCompareError(f"login to {base} failed ({status}: {login.get('error')})")
    cookies = dict(raw.split(";", 1)[0].strip().partition("=")[::2] for raw in headers.get_all("Set-Cookie") or [])
    token, csrf = cookies.get(SESSION_COOKIE), login.get("csrfToken")
    if not token or not isinstance(csrf, str) or cookies.get(CSRF_COOKIE) != csrf:
        raise ReviewCompareError(f"login to {base}: the response has no session cookie or CSRF token")
    signed_in = {"Cookie": f"{SESSION_COOKIE}={token}; {CSRF_COOKIE}={csrf}"}
    try:
        status, headers, body = _send(Request(f"{base}/api/gold-set", headers=signed_in))
    finally:
        out_status, out_headers, out_body = _send(
            Request(f"{base}/api/auth/logout", data=b"", headers={**signed_in, CSRF_HEADER: csrf}, method="POST")
        )
    if status != 200:
        raise ReviewCompareError(f"gold set from {base}: {status} ({_json('gold set', status, headers, body).get('error')})")
    if out_status != 200:
        raise ReviewCompareError(f"sign-out from {base} failed ({out_status}: {_json('sign-out', out_status, out_headers, out_body).get('error')})")
    if headers.get_content_type() != "application/jsonl":
        raise ReviewCompareError(f"gold set from {base}: the review service answered {headers.get_content_type()}, not JSONL")
    text = body.decode("utf-8")
    if not text.strip():
        raise ReviewCompareError(f"gold set from {base} is empty: this account has no labelled cells in the active sample")
    return text
