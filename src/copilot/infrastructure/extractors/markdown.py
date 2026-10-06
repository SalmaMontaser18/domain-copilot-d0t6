import re
from pathlib import Path

import yaml

from copilot.application.ports.documents import ExtractedDocument
from copilot.domain.documents import DocumentMeta
from copilot.domain.errors import InvalidDocumentError

REQUIRED = ("doc_id", "version", "title", "doc_type", "effective_date", "status")


class MarkdownExtractor:
    def supports(self, path: str) -> bool:
        return path.lower().endswith(".md")

    def extract(self, path: str) -> ExtractedDocument:
        raw = Path(path).read_text(encoding="utf-8-sig")
        parts = raw.split("---", 2)
        if len(parts) < 3 or parts[0].strip():
            raise InvalidDocumentError(f"{path}: missing front-matter")
        try:
            front = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError as error:
            raise InvalidDocumentError(f"{path}: bad front-matter ({error})") from error
        missing = [key for key in REQUIRED if key not in front]
        if missing:
            raise InvalidDocumentError(f"{path}: missing fields {missing}")
        body = parts[2].split("---QA---")[0]
        body = re.sub(r"^#{1,6}\s+", "", body, flags=re.MULTILINE)
        meta = DocumentMeta(
            doc_id=str(front["doc_id"]),
            version=str(front["version"]),
            title=str(front["title"]),
            doc_type=str(front["doc_type"]),
            effective_date=str(front["effective_date"]),
            status=str(front["status"]),
            source_path=path,
        )
        return ExtractedDocument(meta, body)
