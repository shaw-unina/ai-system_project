"""Command-line entry point for the misinformation detector.

Subcommands:
    info             Print effective Settings + backend metadata.
    verify           Verify a single claim from the command line.
    batch            Verify a JSONL file of claims, write Verdicts to JSONL.
    eval             Run an eval over a JSONL dataset, write a markdown report.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from misinfo.config import get_settings
from misinfo.observability import flush


def _cmd_info(_: argparse.Namespace) -> int:
    s = get_settings()
    from misinfo.inference.factory import get_backend

    backend = get_backend(cache=False)
    payload = {
        "env": s.env,
        "backend": s.misinfo_backend,
        "cache_enabled": s.misinfo_cache,
        "model_id": backend.model_id,
        "model_version": backend.model_version,
        "langfuse_enabled": bool(
            s.langfuse_host and s.langfuse_public_key and s.langfuse_secret_key
        ),
    }
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _build_factchecker_from_corpus(corpus_path: Path | None) -> Any:
    """Wire up a RAGFactChecker over an optional JSONL corpus.

    If corpus_path is None, uses an empty corpus — the pipeline still runs but
    every retrieval returns []. Useful for smoke tests.
    """
    from misinfo.decompose.llm_decomposer import LLMDecomposer
    from misinfo.inference.factory import get_backend
    from misinfo.pipeline.orchestrator import RAGFactChecker
    from misinfo.retrieve.bm25 import BM25Retriever
    from misinfo.retrieve.corpus import EvidenceCorpus
    from misinfo.verify.aggregator import LLMAggregator
    from misinfo.verify.answerer import LLMAnswerer

    corpus = (
        EvidenceCorpus.from_jsonl(corpus_path) if corpus_path else EvidenceCorpus()
    )
    retriever = BM25Retriever(corpus)
    llm = get_backend()
    return RAGFactChecker(
        decomposer=LLMDecomposer(llm),
        retriever=retriever,
        answerer=LLMAnswerer(llm),
        aggregator=LLMAggregator(llm),
        backend_id=get_settings().misinfo_backend,
        model_id=llm.model_id,
        model_version=llm.model_version,
    )


def _cmd_verify(args: argparse.Namespace) -> int:
    fc = _build_factchecker_from_corpus(args.corpus)
    verdict = fc.verify(args.claim)
    sys.stdout.write(verdict.model_dump_json(indent=2) + "\n")
    flush()
    return 0


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _cmd_batch(args: argparse.Namespace) -> int:
    fc = _build_factchecker_from_corpus(args.corpus)
    rows = _read_jsonl(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as out:
        for row in rows:
            verdict = fc.verify(row["claim"])
            out.write(
                json.dumps({"claim_id": row.get("claim_id"), "verdict": verdict.model_dump()})
                + "\n"
            )
    flush()
    return 0


def _cmd_eval(args: argparse.Namespace) -> int:
    from misinfo.eval.harness import run_eval
    from misinfo.eval.reports import write_report

    fc = _build_factchecker_from_corpus(args.corpus)
    dataset = _read_jsonl(args.input)
    results = run_eval(
        fc, dataset, system=args.system, dataset_name=args.input.stem
    )
    write_report(results, args.report)
    if args.results_json:
        args.results_json.parent.mkdir(parents=True, exist_ok=True)
        args.results_json.write_text(results.model_dump_json(indent=2))
    flush()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="misinfo", description="Misinformation detector CLI.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("info", help="Print runtime configuration").set_defaults(func=_cmd_info)

    pv = sub.add_parser("verify", help="Verify a single claim")
    pv.add_argument("claim", type=str)
    pv.add_argument("--corpus", type=Path, default=None, help="JSONL evidence corpus")
    pv.set_defaults(func=_cmd_verify)

    pb = sub.add_parser("batch", help="Verify a JSONL file of claims")
    pb.add_argument("--input", type=Path, required=True)
    pb.add_argument("--output", type=Path, required=True)
    pb.add_argument("--corpus", type=Path, default=None)
    pb.set_defaults(func=_cmd_batch)

    pe = sub.add_parser("eval", help="Evaluate against a labelled JSONL dataset")
    pe.add_argument("--input", type=Path, required=True)
    pe.add_argument("--report", type=Path, required=True, help="Markdown report path")
    pe.add_argument("--results-json", type=Path, default=None)
    pe.add_argument("--corpus", type=Path, default=None)
    pe.add_argument("--system", type=str, default="rag")
    pe.set_defaults(func=_cmd_eval)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
