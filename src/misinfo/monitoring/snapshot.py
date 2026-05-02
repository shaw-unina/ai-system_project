"""JSON persistence for distribution snapshots."""
from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from misinfo.monitoring.drift import DistributionSnapshot


def save_snapshots(snapshots: Iterable[DistributionSnapshot], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = [s.to_dict() for s in snapshots]
    p.write_text(json.dumps(payload, indent=2))
    return p


def load_snapshots(path: str | Path) -> list[DistributionSnapshot]:
    payload = json.loads(Path(path).read_text())
    return [DistributionSnapshot.from_dict(d) for d in payload]
