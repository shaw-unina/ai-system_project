"""Zero-shot NLI encoder baseline using DeBERTa-v3-MNLI.

No fine-tuning. Lazy-imports `transformers` so the base install doesn't pay.
"""
from __future__ import annotations

from typing import Any

from misinfo.config import get_settings
from misinfo.observability import current_trace_id, traced
from misinfo.pipeline.interfaces import Retriever
from misinfo.repro import git_sha
from misinfo.schemas import EvidenceRef, Verdict, VerdictMetadata

DEFAULT_MODEL = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"


def _evidence_text(ev: list[EvidenceRef], max_chars: int = 2000) -> str:
    return " ".join(e.span for e in ev)[:max_chars]


class EncoderBaseline:
    def __init__(
        self,
        retriever: Retriever,
        *,
        model_name: str = DEFAULT_MODEL,
        zero_shot_pipeline: Any | None = None,
        top_k: int = 5,
    ) -> None:
        self._retriever = retriever
        self._top_k = top_k
        self._model_name = model_name
        self._pipe = zero_shot_pipeline or self._load_pipeline(model_name)

    @staticmethod
    def _load_pipeline(model_name: str) -> Any:
        from transformers import pipeline  # type: ignore[import-not-found]

        return pipeline("zero-shot-classification", model=model_name, device=-1)

    @traced("verify_encoder_baseline")
    def verify(self, claim: str) -> Verdict:
        s = get_settings()
        evidence = self._retriever.retrieve(claim, top_k=self._top_k)
        premise = _evidence_text(evidence) or "(no evidence)"
        hypothesis_template = "This text {} the claim: " + claim
        result = self._pipe(
            premise,
            candidate_labels=["supports", "refutes", "is unrelated to"],
            hypothesis_template=hypothesis_template,
        )
        # result has 'labels' (sorted desc by score) and 'scores'
        label_map = {
            "supports": "Supported",
            "refutes": "Refuted",
            "is unrelated to": "NotEnoughEvidence",
        }
        top = result["labels"][0]
        verdict_label = label_map[top]
        confidence = float(result["scores"][0])
        return Verdict(
            verdict=verdict_label,  # type: ignore[arg-type]
            confidence=confidence,
            evidence=evidence,
            rationale=f"Zero-shot NLI classified evidence as {top!r} the claim "
                      f"(p={confidence:.3f}).",
            metadata=VerdictMetadata(
                backend="encoder",
                model_id=self._model_name,
                model_version=None,
                seed=s.random_seed,
                temperature=None,
                config_hash=str(git_sha() or ""),
                langfuse_trace_id=current_trace_id(),
            ),
        )

    def batch_verify(self, claims: list[str]) -> list[Verdict]:
        return [self.verify(c) for c in claims]
