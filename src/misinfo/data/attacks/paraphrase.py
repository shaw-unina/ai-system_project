from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Style = Literal["newswire", "tabloid", "social"]
STYLES: tuple[Style, ...] = ("newswire", "tabloid", "social")

PROMPTS_DIR = Path(__file__).parent / "prompts"

_TOKEN_RE = re.compile(r"\w+")

# Quality-gate thresholds (Phase 3 §3)
NLI_ENTAILMENT_THRESHOLD = 0.70
NEAR_DUPLICATE_MAX = 0.85
LENGTH_RATIO_MIN = 0.5
LENGTH_RATIO_MAX = 2.0


def load_prompt(style: Style) -> str:
    if style not in STYLES:
        raise ValueError(f"unknown style: {style!r}; expected one of {STYLES}")
    return (PROMPTS_DIR / f"{style}.txt").read_text(encoding="utf-8")


def _tokens(s: str) -> list[str]:
    return _TOKEN_RE.findall(s.lower())


def near_duplicate_score(original: str, paraphrase: str) -> float:
    """Token-level Jaccard overlap. Used as a cheap stand-in for BLEU; values in [0, 1].

    Higher = more similar. We reject paraphrases above NEAR_DUPLICATE_MAX.
    """
    a, b = set(_tokens(original)), set(_tokens(paraphrase))
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def length_ratio_ok(original: str, paraphrase: str) -> bool:
    if not original:
        return False
    ratio = len(paraphrase) / len(original)
    return LENGTH_RATIO_MIN <= ratio <= LENGTH_RATIO_MAX


@dataclass(frozen=True)
class QualityGateResult:
    passed: bool
    nli_score: float
    duplicate_score: float
    length_ok: bool
    reasons: tuple[str, ...]


# Default NLI predictor protocol: callable(premise, hypothesis) -> float in [0, 1].
NliPredictor = Callable[[str, str], float]


def _default_nli_predictor(_premise: str, _hypothesis: str) -> float:
    raise RuntimeError(
        "No NLI predictor configured. Pass `nli_predictor=` from a real model "
        "(e.g. DeBERTa-v3-MNLI) or a mock in tests."
    )


def check_quality_gates(
    original: str,
    paraphrase: str,
    nli_predictor: NliPredictor = _default_nli_predictor,
) -> QualityGateResult:
    """Apply the three Phase 3 quality gates.

    A paraphrase passes iff:
      - NLI(original ⇒ paraphrase) ≥ NLI_ENTAILMENT_THRESHOLD (label preservation), and
      - near_duplicate_score < NEAR_DUPLICATE_MAX (not a near-copy), and
      - length ratio in [LENGTH_RATIO_MIN, LENGTH_RATIO_MAX].
    """
    reasons: list[str] = []
    dup = near_duplicate_score(original, paraphrase)
    if dup >= NEAR_DUPLICATE_MAX:
        reasons.append(f"near_duplicate({dup:.2f}>={NEAR_DUPLICATE_MAX})")
    len_ok = length_ratio_ok(original, paraphrase)
    if not len_ok:
        reasons.append("length_out_of_band")
    nli = float(nli_predictor(original, paraphrase))
    if nli < NLI_ENTAILMENT_THRESHOLD:
        reasons.append(f"nli({nli:.2f}<{NLI_ENTAILMENT_THRESHOLD})")
    return QualityGateResult(
        passed=not reasons,
        nli_score=nli,
        duplicate_score=dup,
        length_ok=len_ok,
        reasons=tuple(reasons),
    )
