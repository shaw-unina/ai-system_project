import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export const dynamic = "force-dynamic";

export async function GET() {
  const upstream = await fetch(`${BACKEND_URL}/metrics`, { cache: "no-store" });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "content-type": "text/plain" },
  });
}
