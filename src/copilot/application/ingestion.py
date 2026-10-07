import hashlib
from dataclasses import dataclass

from copilot.application.chunking import chunk_text, clean_text
from copilot.application.ports.documents import (
    DocumentRepository,
    ExtractedDocument,
    IndexedChunk,
    TextExtractor,
)
from copilot.application.ports.llm import LLMProvider
from copilot.domain.errors import DomainError, InvalidDocumentError, UnsupportedFormatError

EMBED_BATCH = 32


@dataclass(frozen=True)
class IngestionResult:
    path: str
    status: str  # indexed | unchanged | failed
    chunks: int = 0
    error: str = ""


class IngestDocument:
    """Pipeline: extract -> clean -> chunk -> embed -> index. Idempotent by content hash."""

    def __init__(
        self,
        extractors: list[TextExtractor],
        embedder: LLMProvider,
        repository: DocumentRepository,
    ) -> None:
        self.extractors = extractors
        self.embedder = embedder
        self.repository = repository

    def run(self, path: str) -> IngestionResult:
        document: ExtractedDocument | None = None
        try:
            document = self._extract(path)
            text = clean_text(document.text)
            meta = document.meta
            content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if self.repository.get_hash(meta.doc_id, meta.version) == content_hash:
                return IngestionResult(path, "unchanged")
            drafts = chunk_text(text)
            if not drafts:
                raise InvalidDocumentError(f"no numbered sections found in {path}")
            vectors = self._embed([draft.text for draft in drafts])
            chunks = [
                IndexedChunk(i, draft, vector)
                for i, (draft, vector) in enumerate(zip(drafts, vectors, strict=True))
            ]
            self.repository.save(meta, content_hash, chunks)
            return IngestionResult(path, "indexed", len(chunks))
        except DomainError as error:
            if document is not None:
                self.repository.mark_failed(document.meta, str(error))
            return IngestionResult(path, "failed", error=str(error))

    def _extract(self, path: str) -> ExtractedDocument:
        for extractor in self.extractors:
            if extractor.supports(path):
                return extractor.extract(path)
        raise UnsupportedFormatError(f"no extractor for {path}")

    def _embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), EMBED_BATCH):
            vectors.extend(self.embedder.embed(texts[start : start + EMBED_BATCH]))
        return vectors
