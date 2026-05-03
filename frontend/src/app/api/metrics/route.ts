import { NextResponse } from "next/server";
import { BACKEND_URL, metricsHeaders } from "@/lib/backend";

export const dynamic = "force-dynamic";

export async function GET() {
  const upstream = await fetch(`${BACKEND_URL}/metrics`, {
    cache: "no-store",
    headers: metricsHeaders(),
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "content-type": "text/plain" },
  });
}
