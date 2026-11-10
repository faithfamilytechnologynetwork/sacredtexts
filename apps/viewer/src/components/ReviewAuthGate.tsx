import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { CenteredSpinner } from "./Loading";
import { initReview, loginReview, logoutReview, signupReview, useReviewStatus } from "../lib/review";
import { UNAVAILABLE_MESSAGE } from "../lib/reviewApi";

// Auth gate for the /review pages, ported from multibench (its Spec 92). Labels persist to the review
// service per signed-in reviewer, so the pages need a session. `initReview` runs once to resolve the
// session (and a CSRF token). Until it resolves we show a spinner; signed out, the sign-in /
// create-account form; signed in, the page. One state multibench didn't have: "unavailable", when
// there is no review service at this origin at all (the static viewer build). That shows a notice,
// never a sign-in form nobody could use.

export function ReviewAuthGate({ children }: { children: ReactNode }) {
  const status = useReviewStatus();

  // `initReview` is idempotent (coalesces concurrent calls) and re-arms after a reset, so calling it
  // whenever the session is still "unknown" is safe and survives test remounts.
  useEffect(() => {
    if (status.auth === "unknown") void initReview();
  }, [status.auth]);

  if (status.auth === "unknown") return <CenteredSpinner label="Checking your session…" />;
  if (status.auth === "unavailable") return <ReviewUnavailable />;
  if (status.auth === "out") return <ReviewAuthForm initError={status.error} />;
  return <>{children}</>;
}

/** No review service at this origin: say so plainly. */
export function ReviewUnavailable() {
  return (
    <div role="alert" className="mx-auto max-w-xl py-12 text-center" data-testid="review-unavailable">
      <h1 className="text-xl font-semibold">{capitalize(UNAVAILABLE_MESSAGE)}</h1>
      <p className="mt-2 text-sm text-default-500">
        Reviewing needs the review service, and this copy of the viewer doesn&rsquo;t have one. The
        benchmark&rsquo;s scores and verses are still here to browse.
      </p>
    </div>
  );
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** "Signed in as …" strip + sign-out, for the top of a review page. */
export function ReviewerBadge() {
  const status = useReviewStatus();
  // A refused sign-out leaves the reviewer signed in (the server session is still live); say so.
  const [signOutError, setSignOutError] = useState<string | null>(null);
  if (!status.reviewer) return null;
  const signOut = () => {
    setSignOutError(null);
    logoutReview().catch((e: unknown) => setSignOutError(e instanceof Error ? e.message : "sign-out failed"));
  };
  return (
    <div
      className="rounded-lg border border-default-200 bg-surface-secondary px-3 py-2 text-sm"
      data-testid="reviewer-badge"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-default-600">
          Signed in as <strong>{status.reviewer.name || status.reviewer.email}</strong>
        </span>
        <button type="button" onClick={signOut} className="text-xs text-accent hover:underline">
          Sign out
        </button>
      </div>
      {signOutError && (
        <p className="mt-1 text-xs text-danger" role="alert" data-testid="sign-out-error">
          Couldn&rsquo;t sign out ({signOutError}). You&rsquo;re still signed in; try again.
        </p>
      )}
    </div>
  );
}

/** A small banner for the async save state: saving, an error, or a reconcile with another device. */
export function ReviewSaveStatus() {
  const status = useReviewStatus();
  if (status.error) {
    const msg =
      status.errorKind === "load"
        ? `Couldn't load your saved labels (${status.error}). Editing stays off until they load.`
        : status.errorKind === "rejected"
          ? `Not saved: ${status.error}. Your labels stay on this device; your next change will try again.`
          : `Couldn't save your last change (${status.error}). It stays on this device and will retry.`;
    return (
      <p className="text-xs text-danger" role="status" data-testid="review-save-status">
        {msg}
      </p>
    );
  }
  if (status.reconciled) {
    return (
      <p className="text-xs text-warning" role="status" data-testid="review-save-status">
        Your labels were changed on another device — this page now shows the latest version.
      </p>
    );
  }
  if (status.saving) {
    return (
      <p className="text-xs text-default-400" role="status" data-testid="review-save-status">
        Saving…
      </p>
    );
  }
  // Idle with nothing pending — say nothing rather than a premature "Saved".
  return null;
}

function ReviewAuthForm({ initError }: { initError?: string | null }) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [background, setBackground] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "login") {
        await loginReview(email, password);
      } else {
        await signupReview({ email, password, name, background, inviteCode });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  const input = "rounded border border-default-200 bg-background px-2 py-1.5 text-sm text-default-800";

  return (
    <form
      onSubmit={submit}
      className="mx-auto flex w-full max-w-sm flex-col gap-3 rounded-lg border border-default-200 p-5"
      data-testid="review-auth-form"
    >
      <h2 className="text-lg font-semibold">{mode === "login" ? "Sign in to review" : "Create a reviewer account"}</h2>
      <p className="text-sm text-default-500">
        Your labels are saved privately to your account and sync across your devices.
      </p>

      {initError && (
        <p className="text-sm text-danger" role="alert" data-testid="review-service-error">
          {initError}
        </p>
      )}

      {mode === "signup" && (
        <>
          <label className="flex flex-col gap-1 text-xs font-medium text-default-500">
            Name
            <input className={input} value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <label className="flex flex-col gap-1 text-xs font-medium text-default-500">
            Background (the texts you know, and how)
            <input
              className={input}
              value={background}
              onChange={(e) => setBackground(e.target.value)}
              placeholder="e.g. reads Qur'anic Arabic; hafiz"
            />
          </label>
          <label className="flex flex-col gap-1 text-xs font-medium text-default-500">
            Invite code
            <input className={input} value={inviteCode} onChange={(e) => setInviteCode(e.target.value)} required />
          </label>
        </>
      )}

      <label className="flex flex-col gap-1 text-xs font-medium text-default-500">
        Email
        <input className={input} type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </label>
      <label className="flex flex-col gap-1 text-xs font-medium text-default-500">
        Password
        <input
          className={input}
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
        />
      </label>

      {error && (
        <p className="text-sm text-danger" role="alert" data-testid="review-auth-error">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={busy}
        className="rounded bg-accent px-3 py-1.5 text-sm font-medium text-accent-foreground disabled:opacity-60"
      >
        {busy ? "…" : mode === "login" ? "Sign in" : "Create account"}
      </button>

      <button
        type="button"
        onClick={() => {
          setMode(mode === "login" ? "signup" : "login");
          setError(null);
        }}
        className="text-xs text-accent hover:underline"
      >
        {mode === "login" ? "Need an account? Create one" : "Have an account? Sign in"}
      </button>
    </form>
  );
}
