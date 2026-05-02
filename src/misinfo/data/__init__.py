"""Data layer for misinfo: registry, loaders, splits, preprocessing, attacks, manifest."""

from misinfo.data.registry import DatasetSpec, REGISTRY, register, get_spec
from misinfo.data.manifest import DataManifest, ManifestEntry

__all__ = [
    "DatasetSpec",
    "REGISTRY",
    "register",
    "get_spec",
    "DataManifest",
    "ManifestEntry",
]
