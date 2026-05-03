import type { Metadata } from "next";
import { Newsreader, Roboto } from "next/font/google";
import "@/styles/globals.css";
import DisclosureBadge from "@/components/DisclosureBadge";
import QueryProvider from "@/components/QueryProvider";
import ThemeProvider from "@/components/ThemeProvider";
import ThemeToggle from "@/components/ThemeToggle";

const newsreader = Newsreader({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-display",
  display: "swap",
});

const roboto = Roboto({
  subsets: ["latin"],
  weight: ["300", "400", "500", "700"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "misinfo · verification dashboard",
  description: "Closed-book verification for short factual claims.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${newsreader.variable} ${roboto.variable}`}>
      <body className="min-h-screen bg-background text-foreground antialiased">
        <ThemeProvider>
          <header className="sticky top-0 z-30 border-b border-border bg-background/80 backdrop-blur">
            <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
              <a
                href="/"
                className="font-display text-lg font-semibold tracking-tight text-foreground"
              >
                misinfo
              </a>
              <nav className="flex flex-1 items-center gap-5 text-sm">
                <a
                  href="/verify"
                  className="text-muted-foreground transition-colors hover:text-foreground"
                >
                  Verify
                </a>
                <a
                  href="/operator"
                  className="text-muted-foreground transition-colors hover:text-foreground"
                >
                  Operator
                </a>
              </nav>
              <ThemeToggle />
              <DisclosureBadge />
            </div>
          </header>
          <QueryProvider>
            <main className="mx-auto max-w-6xl px-4 py-10">{children}</main>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
