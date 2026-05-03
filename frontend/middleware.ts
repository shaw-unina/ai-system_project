// Phase 11 — security headers on every response, plus a cookie gate on
// /operator. The user-facing /verify page stays open so the demo surface
// works without credentials. When OPERATOR_PASSWORD is unset the gate is
// disabled (local dev / unauthed deploys).

import { NextRequest, NextResponse } from "next/server";

const SECURITY_HEADERS: Record<string, string> = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
  "Content-Security-Policy": [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "connect-src 'self'",
    "frame-ancestors 'none'",
  ].join("; "),
};

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};

export function middleware(req: NextRequest): NextResponse {
  const url = req.nextUrl;
  const operatorPassword = process.env.OPERATOR_PASSWORD;
  const needsGate =
    Boolean(operatorPassword) &&
    (url.pathname === "/operator" || url.pathname.startsWith("/operator/"));

  if (needsGate) {
    const cookie = req.cookies.get("operator_session")?.value;
    if (cookie !== operatorPassword) {
      const dest = new URL("/login", req.url);
      dest.searchParams.set("next", url.pathname);
      const r = NextResponse.redirect(dest);
      applySecurityHeaders(r);
      return r;
    }
  }

  const res = NextResponse.next();
  applySecurityHeaders(res);
  return res;
}

function applySecurityHeaders(res: NextResponse): void {
  for (const [k, v] of Object.entries(SECURITY_HEADERS)) {
    res.headers.set(k, v);
  }
}
