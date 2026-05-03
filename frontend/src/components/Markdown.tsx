"use client";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";

export function Markdown({ children, className }: { children: string; className?: string }) {
  return (
    <div
      className={cn(
        "prose prose-sm max-w-none dark:prose-invert",
        "prose-headings:font-display prose-headings:tracking-tight",
        "prose-p:my-2 prose-p:leading-relaxed",
        "prose-li:my-1 prose-ul:my-2 prose-ol:my-2",
        "prose-a:text-accent-700 prose-a:no-underline hover:prose-a:underline",
        "prose-code:rounded prose-code:bg-muted prose-code:px-1 prose-code:py-0.5",
        "prose-code:font-mono prose-code:text-[0.85em] prose-code:before:content-none prose-code:after:content-none",
        "prose-blockquote:border-l-brand-500 prose-blockquote:bg-muted/50",
        "prose-blockquote:py-0.5 prose-blockquote:not-italic",
        "prose-strong:text-foreground prose-p:text-foreground prose-li:text-foreground",
        className
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children, ...rest }) => (
            <a href={href} target="_blank" rel="noreferrer noopener" {...rest}>
              {children}
            </a>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

export default Markdown;
