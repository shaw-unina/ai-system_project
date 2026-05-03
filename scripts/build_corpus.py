"""Phase 11.1 — corpus builder.

Builds the JSONL evidence corpora consumed by the BM25 retriever.

Usage::

    python scripts/build_corpus.py averitec --out data/processed/averitec_corpus.jsonl
    python scripts/build_corpus.py wiki     --out data/processed/wiki_corpus.jsonl --max 50000
    python scripts/build_corpus.py union    --out data/processed/union_corpus.jsonl

The web retriever (default) does not need any of these — they're only used
when ``MISINFO_RETRIEVER=bm25`` so the calibrated metrics in the model card
remain reproducible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _emit(path: Path, rows) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            text = (row.get("text") or "").strip()
            if not text:
                continue
            key = hashlib.sha256(
                ((row.get("url") or "") + "|" + text[:200]).encode("utf-8")
            ).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


def _averitec(max_docs: int | None) -> list[dict]:
    """Reads HF dataset chenxwh/AVeriTeC and flattens to evidence docs."""
    try:
        from datasets import load_dataset  # type: ignore
    except ImportError:
        sys.exit(
            "averitec ingester needs the `datasets` package. "
            "Install with: pip install datasets"
        )

    rows: list[dict] = []
    for split in ("train", "dev"):
        try:
            ds = load_dataset("chenxwh/AVeriTeC", split=split)
        except Exception as exc:
            print(f"skip averitec/{split}: {exc}", file=sys.stderr)
            continue
        for example in ds:
            cid = example.get("claim_id") or example.get("id") or ""
            for qi, q in enumerate(example.get("questions") or []):
                for ai, ans in enumerate(q.get("answers") or []):
                    text = (
                        ans.get("source_text")
                        or ans.get("answer")
                        or ""
                    )
                    url = ans.get("source_url")
                    if not text:
                        continue
                    rows.append(
                        {
                            "source_id": f"averitec-{cid}-{qi}-{ai}",
                            "text": text,
                            "url": url,
                        }
                    )
                    if max_docs is not None and len(rows) >= max_docs:
                        return rows
    return rows


def _wiki(max_docs: int) -> list[dict]:
    """Simple-English Wikipedia lead paragraphs from HF datasets."""
    try:
        from datasets import load_dataset  # type: ignore
    except ImportError:
        sys.exit(
            "wiki ingester needs the `datasets` package. "
            "Install with: pip install datasets"
        )
    ds = load_dataset("wikipedia", "20220301.simple", split="train", streaming=True)
    rows: list[dict] = []
    for art in ds:
        text = (art.get("text") or "").strip()
        if not text:
            continue
        lead = text.split("\n\n", 1)[0][:1000]
        title = art.get("title") or ""
        slug = title.replace(" ", "_")
        rows.append(
            {
                "source_id": f"wiki-{slug}",
                "text": lead,
                "url": f"https://simple.wikipedia.org/wiki/{slug}",
            }
        )
        if len(rows) >= max_docs:
            break
    return rows


def _union(out: Path, max_wiki: int) -> int:
    averitec = REPO_ROOT / "data/processed/averitec_corpus.jsonl"
    wiki = REPO_ROOT / "data/processed/wiki_corpus.jsonl"
    if not averitec.exists():
        sys.exit(f"missing {averitec}; run `build_corpus.py averitec` first")
    if not wiki.exists():
        sys.exit(f"missing {wiki}; run `build_corpus.py wiki` first")
    out.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for src in (averitec, wiki):
            with src.open("r", encoding="utf-8") as r:
                for line in r:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    key = obj.get("source_id") or hashlib.sha256(line.encode()).hexdigest()
                    if key in seen:
                        continue
                    seen.add(key)
                    f.write(line + "\n")
                    n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=("averitec", "wiki", "union"))
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--max", type=int, default=None)
    args = ap.parse_args()

    out = args.out or (REPO_ROOT / f"data/processed/{args.which}_corpus.jsonl")

    if args.which == "averitec":
        n = _emit(out, _averitec(args.max))
    elif args.which == "wiki":
        n = _emit(out, _wiki(args.max or 50_000))
    else:
        n = _union(out, args.max or 50_000)

    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"wrote {n} docs to {out}")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
