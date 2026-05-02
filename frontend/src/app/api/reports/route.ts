import { NextResponse } from "next/server";
import { promises as fs } from "node:fs";
import path from "node:path";

// Lists Phase 7 smoke reports. Resolves a path relative to the repo root so
// it works in both `next dev` (frontend/) and the standalone build (mounted
// at the same depth).
const REPORTS_DIR = path.resolve(process.cwd(), "..", "reports", "_smoke");

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const entries = await fs.readdir(REPORTS_DIR);
    const md = entries.filter((f) => f.endsWith(".md")).sort();
    return NextResponse.json(md);
  } catch {
    return NextResponse.json([], { status: 200 });
  }
}
