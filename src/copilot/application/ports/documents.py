from dataclasses import dataclass
from typing import Protocol

from copilot.domain.documents import ChunkDraft, DocumentMeta


@dataclass(frozen=True)
class ExtractedDocument:
    meta: DocumentMeta
    text: str


@dataclass(frozen=True)
class IndexedChunk:
    index: int
    draft: ChunkDraft
    embedding: list[float]


class TextExtractor(Protocol):
    def supports(self, path: str) -> bool: ...

    def extract(self, path: str) -> ExtractedDocument: ...


class DocumentRepository(Protocol):
    def get_hash(self, doc_id: str, version: str) -> str | None: ...

    def save(
        self, meta: DocumentMeta, content_hash: str, chunks: list[IndexedChunk]
    ) -> None: ...

    def mark_failed(self, meta: DocumentMeta, error: str) -> None: ...
