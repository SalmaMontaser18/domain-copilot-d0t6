"""Search the corpus. Usage: python scripts/search.py "question" [--old]"""
import os
import sys

from copilot.application.retrieval import RetrieveEvidence
from copilot.infrastructure.db.search import PostgresChunkSearch
from copilot.infrastructure.llm.factory import build_provider


def main(question: str, include_old: bool) -> None:
    use_case = RetrieveEvidence(
        build_provider(os.environ.get("LLM_PROVIDER", "fake")),
        PostgresChunkSearch(os.environ["DATABASE_URL"]),
    )
    result = use_case.run(question, include_old)
    if not result.answerable:
        print(f"REFUSE: {result.reason}")
        return
    print(f"ANSWERABLE (coverage {result.coverage:.2f})")
    for item in result.chunks:
        print(f"  {item.doc_id} v{item.version} clauses {item.clauses:9} {item.section}")


if __name__ == "__main__":
    main(sys.argv[1], "--old" in sys.argv)
