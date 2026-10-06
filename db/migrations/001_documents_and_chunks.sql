CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    doc_id TEXT NOT NULL,
    version TEXT NOT NULL,
    title TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    effective_date DATE,
    status TEXT NOT NULL DEFAULT 'current',
    source_path TEXT NOT NULL,
    content_hash TEXT,
    ingest_status TEXT NOT NULL DEFAULT 'pending',
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (doc_id, version)
);

CREATE TABLE chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    section TEXT NOT NULL,
    clauses TEXT NOT NULL,
    page INT,
    text TEXT NOT NULL,
    embedding vector(768),
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX chunks_tsv_idx ON chunks USING gin (tsv);
CREATE INDEX chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops);
