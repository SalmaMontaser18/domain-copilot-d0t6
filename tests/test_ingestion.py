from copilot.application.ingestion import IngestDocument
from copilot.application.ports.documents import ExtractedDocument
from copilot.domain.documents import DocumentMeta
from copilot.infrastructure.llm.fake import FakeProvider

META = DocumentMeta("GL-01", "2.0", "Test", "guideline", "2025-03-01", "current", "a.md")
TEXT = "1. Scope\n1.1 Rule one.\n2. Dose\n2.1 Five mg."


class StubExtractor:
    def __init__(self, text: str, supported: bool = True) -> None:
        self.text = text
        self.supported = supported

    def supports(self, path):
        return self.supported

    def extract(self, path):
        return ExtractedDocument(META, self.text)


class MemoryRepo:
    def __init__(self):
        self.hashes, self.saved, self.failed = {}, [], []

    def get_hash(self, doc_id, version):
        return self.hashes.get((doc_id, version))

    def save(self, meta, content_hash, chunks):
        self.hashes[(meta.doc_id, meta.version)] = content_hash
        self.saved.append(len(chunks))

    def mark_failed(self, meta, error):
        self.failed.append(error)


def make(text, supported=True):
    repo = MemoryRepo()
    return IngestDocument([StubExtractor(text, supported)], FakeProvider(), repo), repo


def test_reingesting_unchanged_document_is_a_no_op():
    use_case, repo = make(TEXT)
    assert use_case.run("a.md").status == "indexed"
    assert use_case.run("a.md").status == "unchanged"
    assert repo.saved == [2]


def test_changed_content_is_reindexed():
    use_case, repo = make(TEXT)
    use_case.run("a.md")
    use_case.extractors[0].text = TEXT + "\n2.2 Maximum ten mg."
    assert use_case.run("a.md").status == "indexed"
    assert len(repo.saved) == 2


def test_document_without_sections_fails_and_failure_is_recorded():
    use_case, repo = make("just some text")
    assert use_case.run("a.md").status == "failed"
    assert repo.failed


def test_unsupported_format_fails_without_touching_the_repository():
    use_case, repo = make(TEXT, supported=False)
    assert use_case.run("a.xyz").status == "failed"
    assert repo.saved == [] and repo.failed == []
