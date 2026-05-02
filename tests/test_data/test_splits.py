import pytest

from misinfo.data.splits import (
    assert_disjoint,
    time_ordered_split,
    topic_slice_index,
)


def _items():
    return [
        {"id": 0, "claim_date": "2024-01-15", "topic": "politics"},
        {"id": 1, "claim_date": "2025-08-01", "topic": "health"},
        {"id": 2, "claim_date": "2023-06-30", "topic": "politics"},
        {"id": 3, "claim_date": "2025-12-12", "topic": "climate"},
        {"id": 4, "claim_date": "2024-09-09", "topic": "politics"},
    ]


def test_time_ordered_split_disjoint_and_late_is_latest() -> None:
    split = time_ordered_split(_items(), drift_fraction=0.4)
    assert set(split.early_indices) | set(split.late_indices) == {0, 1, 2, 3, 4}
    assert set(split.early_indices) & set(split.late_indices) == set()
    # the two latest dates are indices 1 (2025-08) and 3 (2025-12)
    assert set(split.late_indices) == {1, 3}


def test_time_ordered_split_deterministic() -> None:
    items = _items()
    a = time_ordered_split(items, drift_fraction=0.4)
    b = time_ordered_split(items, drift_fraction=0.4)
    assert a == b


def test_time_ordered_split_rejects_bad_fraction() -> None:
    with pytest.raises(ValueError):
        time_ordered_split(_items(), drift_fraction=0.0)
    with pytest.raises(ValueError):
        time_ordered_split(_items(), drift_fraction=1.0)


def test_topic_slice_drops_undersized() -> None:
    items = [{"topic": "a"}] * 35 + [{"topic": "b"}] * 10
    slices = topic_slice_index(items, min_size=30)
    assert "a" in slices and "b" not in slices
    assert len(slices["a"]) == 35


def test_assert_disjoint_raises_on_overlap() -> None:
    with pytest.raises(ValueError):
        assert_disjoint([1, 2, 3], [3, 4])
