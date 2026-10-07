import re

import psycopg

from copilot.application.ports.retrieval import RetrievedChunk

HYBRID_SQL = """
WITH kw AS (
    SELECT c.id,
           row_number() OVER (ORDER BY ts_rank_cd(c.tsv, q) DESC) AS rnk
    FROM chunks c
    JOIN documents d ON d.id = c.document_id,
         to_tsquery('english', %(tsquery)s) q
    WHERE c.tsv @@ q AND (d.status = 'current' OR %(old)s)
    ORDER BY ts_rank_cd(c.tsv, q) DESC
    LIMIT 20
),
vec AS (
    SELECT c.id,
           row_number() OVER (ORDER BY c.embedding <=> %(vec)s::vector) AS rnk
    FROM chunks c
    JOIN documents d ON d.id = c.document_id
    WHERE d.status = 'current' OR %(old)s
    ORDER BY c.embedding <=> %(vec)s::vector
    LIMIT 20
)
SELECT d.doc_id, d.version, d.title, c.section, c.clauses, c.text,
       COALESCE(1.0 / (60 + kw.rnk), 0) + COALESCE(1.0 / (60 + vec.rnk), 0) AS rrf
FROM chunks c
JOIN documents d ON d.id = c.document_id
LEFT JOIN kw ON kw.id = c.id
LEFT JOIN vec ON vec.id = c.id
WHERE kw.id IS NOT NULL OR vec.id IS NOT NULL
ORDER BY rrf DESC
LIMIT %(limit)s
"""


class PostgresChunkSearch:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def search(
        self,
        terms: list[str],
        embedding: list[float],
        limit: int,
        include_superseded: bool,
    ) -> list[RetrievedChunk]:
        safe = [re.sub(r"[^a-z0-9]", "", term) for term in terms]
        safe = [term for term in safe if term]
        if not safe:
            return []
        params = {
            "tsquery": " | ".join(safe),
            "old": include_superseded,
            "vec": "[" + ",".join(f"{value:.6f}" for value in embedding) + "]",
            "limit": limit,
        }
        with psycopg.connect(self.dsn) as conn:
            rows = conn.execute(HYBRID_SQL, params).fetchall()
        return [
            RetrievedChunk(
                doc_id=row[0],
                version=row[1],
                title=row[2],
                section=row[3],
                clauses=row[4],
                text=row[5],
                score=float(row[6]),
            )
            for row in rows
        ]
