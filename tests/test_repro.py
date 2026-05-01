import numpy as np

from misinfo.repro import hash_file, seed_everything


def test_seed_determinism() -> None:
    seed_everything(7)
    a = np.random.rand(5)
    seed_everything(7)
    b = np.random.rand(5)
    assert np.allclose(a, b)


def test_hash_file_stable(tmp_path) -> None:
    p = tmp_path / "x.txt"
    p.write_bytes(b"hello world")
    assert hash_file(p) == hash_file(p)
    assert len(hash_file(p)) == 64
