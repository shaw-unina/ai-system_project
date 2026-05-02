"""Build slice-membership indices over a dataset."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def by_field(
    items: Sequence[dict[str, Any]],
    field: str,
    *,
    min_size: int = 30,
) -> dict[str, list[int]]:
    """Return name → row-indices for each distinct value of `field`,
    dropping slices with fewer than `min_size` rows.
    """
    buckets: dict[str, list[int]] = {}
    for i, item in enumerate(items):
        v = item.get(field)
        if v is None:
            continue
        buckets.setdefault(str(v), []).append(i)
    return {k: v for k, v in sorted(buckets.items()) if len(v) >= min_size}
