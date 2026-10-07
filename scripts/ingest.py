"""Ingest documents. Usage: PYTHONPATH=src python scripts/ingest.py data/corpus/source"""
import os
import sys
from pathlib import Path

from copilot.application.ingestion import IngestDocument
from copilot.infrastructure.db.repository import PostgresDocumentRepository
from copilot.infrastructure.extractors.markdown import MarkdownExtractor
from copilot.infrastructure.llm.factory import build_provider


def main(folder: str) -> int:
    use_case = IngestDocument(
        [MarkdownExtractor()],
        build_provider(os.environ.get("LLM_PROVIDER", "fake")),
        PostgresDocumentRepository(os.environ["DATABASE_URL"]),
    )
    failures = 0
    for path in sorted(p for p in Path(folder).iterdir() if p.is_file()):
        result = use_case.run(str(path))
        failures += result.status == "failed"
        print(f"{result.status:10} {path.name} chunks={result.chunks} {result.error}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
