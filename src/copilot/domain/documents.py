from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentMeta:
    doc_id: str
    version: str
    title: str
    doc_type: str
    effective_date: str
    status: str
    source_path: str


@dataclass(frozen=True)
class ChunkDraft:
    section: str
    clauses: str
    text: str
