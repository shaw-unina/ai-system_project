from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class TimeOrderedSplit:
    early_indices: tuple[int, ...]
    late_indices: tuple[int, ...]

    def __post_init__(self) -> None:
        early = set(self.early_indices)
        late = set(self.late_indices)
        if early & late:
            raise ValueError("early and late indices must be disjoint")


def _to_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        # Accept YYYY-MM-DD or full ISO
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    raise TypeError(f"unsupported date type: {type(value).__name__}")


def time_ordered_split(
    items: Sequence[dict[str, Any]],
    date_field: str = "claim_date",
    drift_fraction: float = 0.20,
) -> TimeOrderedSplit:
    """Sort items by date_field; reserve the latest `drift_fraction` as the drift slice.

    Stable: ties resolved by original index. Disjoint, deterministic.
    """
    if not 0.0 < drift_fraction < 1.0:
        raise ValueError("drift_fraction must be in (0, 1)")

    indexed = list(enumerate(items))
    indexed.sort(key=lambda pair: (_to_date(pair[1][date_field]), pair[0]))
    n = len(indexed)
    cut = n - max(1, int(round(n * drift_fraction)))
    early = tuple(idx for idx, _ in indexed[:cut])
    late = tuple(idx for idx, _ in indexed[cut:])
    return TimeOrderedSplit(early_indices=early, late_indices=late)


def topic_slice_index(
    items: Sequence[dict[str, Any]],
    topic_field: str = "topic",
    min_size: int = 30,
) -> dict[str, tuple[int, ...]]:
    """Return topic -> indices, dropping topics with fewer than `min_size` items."""
    buckets: dict[str, list[int]] = {}
    for i, item in enumerate(items):
        topic = item.get(topic_field)
        if topic is None:
            continue
        buckets.setdefault(str(topic), []).append(i)
    return {
        topic: tuple(idxs)
        for topic, idxs in sorted(buckets.items())
        if len(idxs) >= min_size
    }


def assert_disjoint(*groups: Iterable[int]) -> None:
    seen: set[int] = set()
    for g in groups:
        s = set(g)
        overlap = seen & s
        if overlap:
            raise ValueError(f"index overlap detected: {sorted(overlap)[:5]}")
        seen |= s
