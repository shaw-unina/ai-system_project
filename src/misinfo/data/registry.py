from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    version: str
    license: str
    homepage: str
    splits: tuple[str, ...] = field(default_factory=tuple)
    text_only: bool = True
    notes: str = ""

    @property
    def key(self) -> str:
        return f"{self.name}@{self.version}"


REGISTRY: dict[str, DatasetSpec] = {}


def register(spec: DatasetSpec) -> DatasetSpec:
    if spec.key in REGISTRY:
        raise ValueError(f"DatasetSpec already registered: {spec.key}")
    REGISTRY[spec.key] = spec
    return spec


def get_spec(name: str, version: str) -> DatasetSpec:
    key = f"{name}@{version}"
    if key not in REGISTRY:
        raise KeyError(f"Unknown dataset: {key}. Known: {sorted(REGISTRY)}")
    return REGISTRY[key]


# Static registrations
register(
    DatasetSpec(
        name="averitec",
        version="v2",
        license="CC-BY-SA-4.0",
        homepage="https://fever.ai/2025/task.html",
        splits=("train", "dev", "test"),
        notes="Real-world claims with web evidence. Primary benchmark.",
    )
)

register(
    DatasetSpec(
        name="fakenewsnet",
        version="politifact-text",
        license="MIT (code); publisher terms (data)",
        homepage="https://github.com/KaiDMML/FakeNewsNet",
        splits=("all",),
        notes="Text-only PolitiFact slice (titles+URLs). Tweet rehydration unsupported.",
    )
)

register(
    DatasetSpec(
        name="attack-set",
        version="v0",
        license="CC-BY-SA-4.0 (derivative of AVeriTeC fake-claim subset)",
        homepage="local",
        splits=("newswire", "tabloid", "social"),
        notes="LLM-paraphrase attack set generated from AVeriTeC v2 dev fakes.",
    )
)
