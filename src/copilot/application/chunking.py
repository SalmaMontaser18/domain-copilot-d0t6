import re

from copilot.domain.documents import ChunkDraft

SECTION_RE = re.compile(r"^(\d{1,2})\.\s+(\S.*)$")
CLAUSE_RE = re.compile(r"^(\d{1,2}\.\d{1,2})\s")
MAX_CHARS = 1500


def clean_text(raw: str) -> str:
    text = "\n".join(line.rstrip() for line in raw.replace("\r\n", "\n").split("\n"))
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()


def chunk_text(text: str) -> list[ChunkDraft]:
    sections: list[tuple[str, list[str]]] = []
    for line in text.split("\n"):
        match = SECTION_RE.match(line)
        if match:
            sections.append((f"{match.group(1)}. {match.group(2)}", []))
        elif sections:
            sections[-1][1].append(line)
    chunks: list[ChunkDraft] = []
    for title, lines in sections:
        chunks.extend(_chunk_section(title, lines))
    return chunks


def _units(lines: list[str]) -> list[tuple[str, list[str]]]:
    """Group lines by clause; table rows and continuation lines stay with their clause."""
    units: list[tuple[str, list[str]]] = []
    for line in lines:
        if not line.strip():
            continue
        match = CLAUSE_RE.match(line)
        if match or not units:
            units.append((match.group(1) if match else "", [line]))
        else:
            units[-1][1].append(line)
    return units


def _chunk_section(title: str, lines: list[str]) -> list[ChunkDraft]:
    chunks: list[ChunkDraft] = []
    body: list[str] = []
    labels: list[str] = []
    size = 0
    for label, unit_lines in _units(lines):
        unit = "\n".join(unit_lines)
        if body and size + len(unit) > MAX_CHARS:
            chunks.append(_make(title, labels, body))
            body, labels, size = [], [], 0
        body.append(unit)
        if label:
            labels.append(label)
        size += len(unit)
    if body:
        chunks.append(_make(title, labels, body))
    return chunks


def _make(title: str, labels: list[str], body: list[str]) -> ChunkDraft:
    if not labels:
        clauses = ""
    elif len(labels) == 1:
        clauses = labels[0]
    else:
        clauses = f"{labels[0]}-{labels[-1]}"
    return ChunkDraft(section=title, clauses=clauses, text=f"{title}\n" + "\n".join(body))
