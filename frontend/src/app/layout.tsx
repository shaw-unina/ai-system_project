import type { Metadata } from "next";
import "@/styles/globals.css";
import DisclosureBanner from "@/components/DisclosureBanner";
import QueryProvider from "@/components/QueryProvider";

export const metadata: Metadata = {
  title: "misinfo · dashboard",
  description: "Misinformation detector dashboard (local-deploy only).",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <DisclosureBanner />
        <header className="px-4 py-3 border-b bg-white flex items-center gap-4">
          <a href="/" className="font-semibold">
            misinfo
          </a>
          <nav className="flex gap-3 text-sm">
            <a href="/verify" className="text-slate-700 hover:underline">
              Verify
            </a>
            <a href="/operator" className="text-slate-700 hover:underline">
              Operator
            </a>
          </nav>
        </header>
        <QueryProvider>
          <main className="max-w-4xl mx-auto px-4 py-6">{children}</main>
        </QueryProvider>
        <footer className="px-4 py-3 text-xs text-slate-500 text-center">
          Local deploy only · auth + rate-limiting deferred to Phase 11. The dashboard
          stores low-confidence rows in your browser only — no server-side persistence.
        </footer>
      </body>
    </html>
  );
}
