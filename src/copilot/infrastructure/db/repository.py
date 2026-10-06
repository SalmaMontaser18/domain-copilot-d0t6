import psycopg

from copilot.application.ports.documents import IndexedChunk
from copilot.domain.documents import DocumentMeta

UPSERT_DOCUMENT = """
INSERT INTO documents
    (doc_id, version, title, doc_type, effective_date, status, source_path,
     content_hash, ingest_status, error)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (doc_id, version) DO UPDATE SET
    title = EXCLUDED.title, doc_type = EXCLUDED.doc_type,
    effective_date = EXCLUDED.effective_date, status = EXCLUDED.status,
    source_path = EXCLUDED.source_path,
    content_hash = COALESCE(EXCLUDED.content_hash, documents.content_hash),
    ingest_status = EXCLUDED.ingest_status, error = EXCLUDED.error, updated_at = now()
RETURNING id
"""

INSERT_CHUNK = (
    "INSERT INTO chunks (document_id, chunk_index, section, clauses, text, embedding) "
    "VALUES (%s, %s, %s, %s, %s, %s::vector)"
)


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.6f}" for value in values) + "]"


class PostgresDocumentRepository:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def get_hash(self, doc_id: str, version: str) -> str | None:
        with psycopg.connect(self.dsn) as conn:
            row = conn.execute(
                "SELECT content_hash FROM documents "
                "WHERE doc_id = %s AND version = %s AND ingest_status = 'indexed'",
                (doc_id, version),
            ).fetchone()
        return row[0] if row else None

    def save(
        self, meta: DocumentMeta, content_hash: str, chunks: list[IndexedChunk]
    ) -> None:
        with psycopg.connect(self.dsn) as conn:
            document_id = self._upsert(conn, meta, content_hash, "indexed", None)
            conn.execute("DELETE FROM chunks WHERE document_id = %s", (document_id,))
            with conn.cursor() as cur:
                cur.executemany(
                    INSERT_CHUNK,
                    [
                        (
                            document_id,
                            chunk.index,
                            chunk.draft.section,
                            chunk.draft.clauses,
                            chunk.draft.text,
                            _vector_literal(chunk.embedding),
                        )
                        for chunk in chunks
                    ],
                )

    def mark_failed(self, meta: DocumentMeta, error: str) -> None:
        with psycopg.connect(self.dsn) as conn:
            self._upsert(conn, meta, None, "failed", error)

    @staticmethod
    def _upsert(conn, meta, content_hash, ingest_status, error) -> int:
        row = conn.execute(
            UPSERT_DOCUMENT,
            (
                meta.doc_id,
                meta.version,
                meta.title,
                meta.doc_type,
                meta.effective_date,
                meta.status,
                meta.source_path,
                content_hash,
                ingest_status,
                error,
            ),
        ).fetchone()
        return row[0]
