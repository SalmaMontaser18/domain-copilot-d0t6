from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RetrievedChunk:
    doc_id: str
    version: str
    title: str
    section: str
    clauses: str
    text: str
    score: float


class ChunkSearch(Protocol):
    def search(
        self,
        terms: list[str],
        embedding: list[float],
        limit: int,
        include_superseded: bool,
    ) -> list[RetrievedChunk]: ...
