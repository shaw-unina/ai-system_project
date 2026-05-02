from misinfo.eval.folds import select, three_way_split


def test_three_way_split_partitions_input():
    f = three_way_split(100, seed=42)
    all_idx = set(f.calibration) | set(f.threshold) | set(f.eval)
    assert all_idx == set(range(100))
    assert len(f.calibration) + len(f.threshold) + len(f.eval) == 100


def test_three_way_split_disjoint():
    f = three_way_split(100, seed=42)
    assert not (set(f.calibration) & set(f.threshold))
    assert not (set(f.calibration) & set(f.eval))
    assert not (set(f.threshold) & set(f.eval))


def test_three_way_split_deterministic():
    a = three_way_split(50, seed=7)
    b = three_way_split(50, seed=7)
    assert a == b


def test_select_returns_subset():
    items = list(range(10))
    assert select(items, [3, 1, 4]) == [3, 1, 4]
