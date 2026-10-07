import re
from dataclasses import dataclass, field

from copilot.application.ports.llm import LLMProvider
from copilot.application.ports.retrieval import ChunkSearch, RetrievedChunk

STOPWORDS = {
    "the", "and", "for", "what", "which", "who", "how", "when", "does", "with",
    "that", "this", "from", "are", "was", "were", "can", "should", "his", "her",
    "into", "than", "then", "there", "their", "have", "has", "had", "not", "any",
    "per", "its", "your", "you", "about", "after", "before", "between", "give",
}
MIN_COVERAGE = 0.75  # initial value, tuned with the evaluation harness
STEM_LENGTH = 5  # "treated" and "treatment" both match on "treat"


@dataclass(frozen=True)
class RetrievalResult:
    answerable: bool
    chunks: list[RetrievedChunk] = field(default_factory=list)
    reason: str = ""
    coverage: float = 0.0


def query_terms(question: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", question.lower())
    terms: list[str] = []
    for word in words:
        if len(word) > 2 and word not in STOPWORDS and word not in terms:
            terms.append(word)
    return terms


def coverage(terms: list[str], text: str) -> float:
    """Share of the question's terms (matched on their stem) that appear in the passage."""
    lowered = text.lower()
    return sum(term[:STEM_LENGTH] in lowered for term in terms) / len(terms)


class RetrieveEvidence:
    """Hybrid search (keywords + vectors). Refuses when the evidence does not cover the question."""

    def __init__(self, embedder: LLMProvider, search: ChunkSearch, limit: int = 5) -> None:
        self.embedder = embedder
        self.search = search
        self.limit = limit

    def run(self, question: str, include_superseded: bool = False) -> RetrievalResult:
        terms = query_terms(question)
        if not terms:
            return RetrievalResult(False, reason="question has no searchable terms")
        embedding = self.embedder.embed([question])[0]
        found = self.search.search(terms, embedding, self.limit, include_superseded)
        if not found:
            return RetrievalResult(False, reason="no matching passages in the corpus")
        scored = [(coverage(terms, chunk.text), chunk) for chunk in found]
        best = max(value for value, _ in scored)
        if best < MIN_COVERAGE:
            return RetrievalResult(
                False,
                reason=f"evidence does not cover the question (best coverage {best:.2f})",
                coverage=best,
            )
        relevant = [chunk for value, chunk in scored if value >= MIN_COVERAGE]
        return RetrievalResult(True, relevant, coverage=best)
