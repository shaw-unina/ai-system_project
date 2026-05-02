"""Evidence corpus loading + a simple in-memory document store."""
from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Document:
    source_id: str
    text: str
    url: str | None = None


@dataclass
class EvidenceCorpus:
    documents: list[Document] = field(default_factory=list)

    @classmethod
    def from_jsonl(cls, path: str | Path) -> "EvidenceCorpus":
        p = Path(path)
        docs: list[Document] = []
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                docs.append(
                    Document(
                        source_id=str(row["source_id"]),
                        text=str(row["text"]),
                        url=row.get("url"),
                    )
                )
        return cls(documents=docs)

    @classmethod
    def from_iterable(cls, items: Iterable[dict]) -> "EvidenceCorpus":
        return cls(
            documents=[
                Document(
                    source_id=str(it["source_id"]),
                    text=str(it["text"]),
                    url=it.get("url"),
                )
                for it in items
            ]
        )

    def __len__(self) -> int:
        return len(self.documents)

    def texts(self) -> list[str]:
        return [d.text for d in self.documents]
