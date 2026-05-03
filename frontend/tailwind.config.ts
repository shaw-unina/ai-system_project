import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        display: ['"Newsreader"', "ui-serif", "Georgia", "serif"],
        sans: ['"Roboto"', "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      colors: {
        // shadcn-style semantic tokens (HSL via CSS vars)
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        // Brand + accent (theme-aware)
        ink: {
          DEFAULT: "hsl(var(--foreground))",
          muted: "hsl(var(--muted-foreground))",
        },
        paper: "hsl(var(--background))",
        surface: "hsl(var(--card))",
        brand: {
          50: "hsl(var(--brand-50))",
          100: "hsl(var(--brand-100))",
          500: "hsl(var(--brand-500))",
          600: "hsl(var(--brand-600))",
          700: "hsl(var(--brand-700))",
          800: "hsl(var(--brand-800))",
          900: "hsl(var(--brand-900))",
        },
        accent: {
          500: "hsl(var(--accent-500))",
          600: "hsl(var(--accent-600))",
          700: "hsl(var(--accent-700))",
        },
        // Verdict tones — reference vars so they flip in dark mode
        verdict: {
          supported: "hsl(var(--verdict-supported))",
          "supported-bg": "hsl(var(--verdict-supported-bg))",
          "supported-ring": "hsl(var(--verdict-supported-ring))",
          refuted: "hsl(var(--verdict-refuted))",
          "refuted-bg": "hsl(var(--verdict-refuted-bg))",
          "refuted-ring": "hsl(var(--verdict-refuted-ring))",
          unknown: "hsl(var(--verdict-unknown))",
          "unknown-bg": "hsl(var(--verdict-unknown-bg))",
          "unknown-ring": "hsl(var(--verdict-unknown-ring))",
          abstain: "hsl(var(--verdict-abstain))",
          "abstain-bg": "hsl(var(--verdict-abstain-bg))",
          "abstain-ring": "hsl(var(--verdict-abstain-ring))",
        },
      },
      boxShadow: {
        soft: "0 1px 2px hsl(var(--shadow-soft) / 0.5), 0 4px 12px hsl(var(--shadow-soft) / 0.4)",
        ring: "0 0 0 4px hsl(var(--brand-700) / 0.18)",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};

export default config;
