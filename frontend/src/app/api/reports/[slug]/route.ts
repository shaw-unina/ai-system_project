import { NextResponse } from "next/server";
import { promises as fs } from "node:fs";
import path from "node:path";

const REPORTS_DIR = path.resolve(process.cwd(), "..", "reports", "_smoke");

export const dynamic = "force-dynamic";

export async function GET(_req: Request, ctx: { params: Promise<{ slug: string }> }) {
  const { slug } = await ctx.params;
  // Reject path traversal explicitly. We only serve filenames in REPORTS_DIR.
  if (slug.includes("/") || slug.includes("\\") || slug.includes("..")) {
    return NextResponse.json({ error: "bad slug" }, { status: 400 });
  }
  if (!slug.endsWith(".md")) {
    return NextResponse.json({ error: "only .md files" }, { status: 400 });
  }
  const target = path.resolve(REPORTS_DIR, slug);
  if (!target.startsWith(REPORTS_DIR + path.sep)) {
    return NextResponse.json({ error: "out of bounds" }, { status: 400 });
  }
  try {
    const text = await fs.readFile(target, "utf-8");
    return new NextResponse(text, {
      status: 200,
      headers: { "content-type": "text/markdown" },
    });
  } catch {
    return NextResponse.json({ error: "not found" }, { status: 404 });
  }
}
