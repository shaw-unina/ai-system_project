import { NextResponse } from "next/server";
import { BACKEND_URL, backendHeaders } from "@/lib/backend";

export async function POST(req: Request) {
  const body = await req.text();
  const upstream = await fetch(`${BACKEND_URL}/v1/verify`, {
    method: "POST",
    headers: backendHeaders({ "content-type": "application/json" }),
    body,
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "content-type": upstream.headers.get("content-type") ?? "application/json" },
  });
}
