from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from misinfo.repro import hash_file


@dataclass(frozen=True)
class ManifestEntry:
    artefact_id: str            # e.g. "averitec@v2/dev"
    path: str                   # path relative to repo root
    sha256: str
    size_bytes: int
    preprocessing_version: str
    notes: str = ""


@dataclass
class DataManifest:
    entries: list[ManifestEntry] = field(default_factory=list)

    def add(self, entry: ManifestEntry) -> None:
        if any(e.artefact_id == entry.artefact_id for e in self.entries):
            raise ValueError(f"duplicate artefact_id: {entry.artefact_id}")
        self.entries.append(entry)

    def to_dict(self) -> dict:
        return {"entries": [asdict(e) for e in self.entries]}

    def write(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True))

    @classmethod
    def read(cls, path: str | Path) -> "DataManifest":
        data = json.loads(Path(path).read_text())
        return cls(entries=[ManifestEntry(**e) for e in data["entries"]])

    def verify(self, repo_root: str | Path = ".") -> list[str]:
        """Return a list of artefact_ids whose on-disk hash no longer matches."""
        root = Path(repo_root)
        broken: list[str] = []
        for e in self.entries:
            p = root / e.path
            if not p.exists() or hash_file(p) != e.sha256:
                broken.append(e.artefact_id)
        return broken


def make_entry(artefact_id: str, path: str | Path, preprocessing_version: str, notes: str = "") -> ManifestEntry:
    p = Path(path)
    return ManifestEntry(
        artefact_id=artefact_id,
        path=str(p),
        sha256=hash_file(p),
        size_bytes=p.stat().st_size,
        preprocessing_version=preprocessing_version,
        notes=notes,
    )
