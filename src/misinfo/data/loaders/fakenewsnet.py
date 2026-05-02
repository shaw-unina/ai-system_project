from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from misinfo.data.preprocessing import preprocess_claim


def load_politifact_text(
    fake_csv: str | Path,
    real_csv: str | Path,
) -> list[dict[str, Any]]:
    """Load FakeNewsNet PolitiFact title-only CSVs (no rehydrated tweets).

    Each CSV is expected to have at least columns: id, news_url, title.
    Returns a list of dicts with keys: claim_id, claim, label, source_url, label_source.
    """
    rows: list[dict[str, Any]] = []
    for path, label in ((fake_csv, "fake"), (real_csv, "real")):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"FakeNewsNet split not found: {p}")
        with p.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                title = r.get("title") or ""
                if not title.strip():
                    continue
                rows.append(
                    {
                        "claim_id": f"politifact-{label}-{r.get('id', '')}",
                        "claim": preprocess_claim(title),
                        "label": label,
                        "source_url": r.get("news_url", ""),
                        "label_source": "politifact",
                    }
                )
    return rows
