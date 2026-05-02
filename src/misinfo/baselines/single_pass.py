"""Single-pass RAG: one LLM call, all evidence stuffed in. Phase 7 ablation."""
from __future__ import annotations

from misinfo.config import get_settings
from misinfo.inference.base import LanguageModel
from misinfo.observability import current_trace_id, traced
from misinfo.pipeline.interfaces import Retriever
from misinfo.repro import git_sha
from misinfo.schemas import AggregatorOutput, EvidenceRef, Verdict, VerdictMetadata


_PROMPT = """\
You are a fact-checking assistant. Given a CLAIM and a list of EVIDENCE
passages, produce a verdict. Allowed verdicts: "Supported", "Refuted",
"NotEnoughEvidence". Confidence is in [0, 1]. Cite the evidence ids.

CLAIM: {claim}

EVIDENCE:
{evidence_block}
"""


def _evidence_block(ev: list[EvidenceRef]) -> str:
    if not ev:
        return "(no evidence retrieved)"
    return "\n".join(f"[{e.source_id}] {e.span}" for e in ev)


class SinglePassRAGFactChecker:
    def __init__(
        self,
        retriever: Retriever,
        llm: LanguageModel,
        *,
        backend_id: str = "groq",
        top_k: int = 5,
    ) -> None:
        self._retriever = retriever
        self._llm = llm
        self._backend_id = backend_id
        self._top_k = top_k

    @traced("verify_single_pass")
    def verify(self, claim: str) -> Verdict:
        s = get_settings()
        evidence = self._retriever.retrieve(claim, top_k=self._top_k)
        prompt = _PROMPT.format(claim=claim, evidence_block=_evidence_block(evidence))
        out = self._llm.generate_structured(
            prompt, AggregatorOutput, max_tokens=400, temperature=0.0
        )
        return Verdict(
            verdict=out.verdict,
            confidence=out.confidence,
            evidence=evidence,
            rationale=out.rationale,
            metadata=VerdictMetadata(
                backend=self._backend_id,
                model_id=self._llm.model_id,
                model_version=self._llm.model_version,
                seed=s.random_seed,
                temperature=0.0,
                config_hash=str(git_sha() or ""),
                langfuse_trace_id=current_trace_id(),
            ),
        )

    def batch_verify(self, claims: list[str]) -> list[Verdict]:
        return [self.verify(c) for c in claims]
