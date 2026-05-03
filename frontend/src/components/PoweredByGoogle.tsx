// Inline Google "G" mark (per Google brand guidelines: official 4-color G).
// Used solely as attribution for Fact Check Tools API results.
export function PoweredByGoogle({ className = "" }: { className?: string }) {
  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <svg viewBox="0 0 48 48" className="h-4 w-4" aria-hidden>
        <path
          fill="#FFC107"
          d="M43.6 20.5H42V20H24v8h11.3c-1.6 4.5-5.9 8-11.3 8-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34 6.5 29.3 4.5 24 4.5 13.2 4.5 4.5 13.2 4.5 24S13.2 43.5 24 43.5 43.5 34.8 43.5 24c0-1.2-.1-2.3-.4-3.5z"
        />
        <path
          fill="#FF3D00"
          d="M6.3 14.7l6.6 4.8C14.7 16 19 13 24 13c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34 6.5 29.3 4.5 24 4.5 16.4 4.5 9.8 8.7 6.3 14.7z"
        />
        <path
          fill="#4CAF50"
          d="M24 43.5c5.2 0 9.9-2 13.4-5.2l-6.2-5.2c-2 1.4-4.5 2.4-7.2 2.4-5.4 0-10-3.5-11.5-8.4l-6.6 5.1C9.6 39.2 16.2 43.5 24 43.5z"
        />
        <path
          fill="#1976D2"
          d="M43.6 20.5H42V20H24v8h11.3c-.7 2-2 3.8-3.6 5.1l6.2 5.2c-.4.4 6.6-4.8 6.6-14.3 0-1.2-.1-2.3-.4-3.5z"
        />
      </svg>
      <span className="text-[11px] font-medium uppercase tracking-wider text-ink-muted">
        Powered by Google Fact Check Tools
      </span>
    </div>
  );
}

export default PoweredByGoogle;
