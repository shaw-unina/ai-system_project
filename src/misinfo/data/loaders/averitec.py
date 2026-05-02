from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from misinfo.data.preprocessing import preprocess_claim

REQUIRED_FIELDS = ("claim_id", "claim", "label")


def _iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_averitec_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load AVeriTeC v2 JSONL split, validate schema, preprocess claim text.

    Expected per-line keys: claim_id, claim, label, claim_date (optional), topic (optional),
    questions (optional). Unknown keys are preserved.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"AVeriTeC split not found: {path}")

    out: list[dict[str, Any]] = []
    for i, row in enumerate(_iter_jsonl(path)):
        for f in REQUIRED_FIELDS:
            if f not in row:
                raise ValueError(f"row {i} missing required field {f!r}")
        row = dict(row)
        row["claim"] = preprocess_claim(row["claim"])
        out.append(row)
    return out
