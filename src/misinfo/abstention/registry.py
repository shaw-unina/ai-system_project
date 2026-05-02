"""Head name → class lookup. Used by the CLI."""
from __future__ import annotations

from typing import Literal

from misinfo.abstention.fusion import LogisticFusionHead
from misinfo.abstention.identity import IdentityAbstentionHead
from misinfo.abstention.isotonic import IsotonicCalibrationHead
from misinfo.abstention.retrieval_gated import RetrievalGatedHead
from misinfo.abstention.temperature import TemperatureScalingHead

HeadName = Literal["identity", "temperature", "isotonic", "retrieval_gated", "fusion"]

_HEADS: dict[str, type] = {
    "identity": IdentityAbstentionHead,
    "temperature": TemperatureScalingHead,
    "isotonic": IsotonicCalibrationHead,
    "retrieval_gated": RetrievalGatedHead,
    "fusion": LogisticFusionHead,
}


def head_class(name: str) -> type:
    if name not in _HEADS:
        raise ValueError(f"Unknown head: {name!r}. Known: {sorted(_HEADS)}")
    return _HEADS[name]


def make_head(name: str):
    return head_class(name)()


def load_head(name: str, path: str):
    cls = head_class(name)
    if not hasattr(cls, "load"):
        raise ValueError(f"Head {name!r} does not support load()")
    return cls.load(path)  # type: ignore[attr-defined]
