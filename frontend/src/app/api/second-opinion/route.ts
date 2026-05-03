import { NextResponse } from "next/server";
import { BACKEND_URL, backendHeaders } from "@/lib/backend";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const claim = url.searchParams.get("claim") ?? "";
  const max_results = url.searchParams.get("max_results") ?? "5";
  const upstream = await fetch(
    `${BACKEND_URL}/v1/second-opinion?claim=${encodeURIComponent(claim)}&max_results=${encodeURIComponent(max_results)}`,
    { headers: backendHeaders(), cache: "no-store" },
  );
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "content-type": upstream.headers.get("content-type") ?? "application/json" },
  });
}
