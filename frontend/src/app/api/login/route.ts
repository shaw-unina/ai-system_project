import { NextResponse } from "next/server";

export async function POST(req: Request): Promise<NextResponse> {
  const expected = process.env.OPERATOR_PASSWORD;
  const form = await req.formData();
  const password = String(form.get("password") ?? "");
  const next = sanitizeNext(String(form.get("next") ?? "/operator"));

  if (!expected) {
    return NextResponse.redirect(new URL(next, req.url));
  }
  if (password !== expected) {
    const back = new URL("/login", req.url);
    back.searchParams.set("next", next);
    back.searchParams.set("error", "1");
    return NextResponse.redirect(back);
  }

  const res = NextResponse.redirect(new URL(next, req.url));
  res.cookies.set("operator_session", expected, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 8,
  });
  return res;
}

function sanitizeNext(next: string): string {
  if (!next.startsWith("/")) return "/operator";
  if (next.startsWith("//")) return "/operator";
  return next;
}
