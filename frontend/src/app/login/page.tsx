// Operator login. Posts to /api/login which sets the session cookie and
// redirects back to ?next. No accounts, no users — a single shared password
// from the OPERATOR_PASSWORD env var. Auth.proper lands post-Phase 11.

import { Suspense } from "react";

export const dynamic = "force-dynamic";

function LoginForm({ next }: { next: string }) {
  return (
    <form
      method="post"
      action="/api/login"
      className="mx-auto mt-16 max-w-sm space-y-4 rounded border p-6"
    >
      <h1 className="text-lg font-semibold">Operator login</h1>
      <p className="text-sm text-gray-600">
        The operator dashboard is gated. Enter the shared password set by
        your deployment&apos;s <code>OPERATOR_PASSWORD</code>.
      </p>
      <input type="hidden" name="next" value={next} />
      <input
        type="password"
        name="password"
        required
        autoFocus
        autoComplete="current-password"
        className="w-full rounded border px-3 py-2"
        data-testid="login-password"
      />
      <button
        type="submit"
        className="w-full rounded bg-black px-3 py-2 text-white"
        data-testid="login-submit"
      >
        Sign in
      </button>
    </form>
  );
}

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const sp = await searchParams;
  const next = sp.next ?? "/operator";
  return (
    <Suspense>
      <LoginForm next={next} />
    </Suspense>
  );
}
