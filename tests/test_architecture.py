import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "src" / "copilot"

# Third-party libraries that domain/application must never import.
FORBIDDEN_LIBS = {
    "fastapi", "starlette", "uvicorn", "pydantic", "sqlalchemy", "psycopg",
    "psycopg2", "asyncpg", "pgvector", "openai", "anthropic", "google",
    "groq", "ollama", "httpx", "requests", "pytesseract", "docx",
    "reportlab", "weasyprint", "redis",
}

# Internal layers each layer must not depend on.
FORBIDDEN_LAYERS = {
    "domain": {"copilot.application", "copilot.infrastructure", "copilot.api"},
    "application": {"copilot.infrastructure", "copilot.api"},
}


def imported_modules(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


@pytest.mark.parametrize("layer", ["domain", "application"])
def test_layer_respects_dependency_rule(layer):
    violations = []
    for path in (ROOT / layer).rglob("*.py"):
        for module in imported_modules(path):
            top_level = module.split(".")[0]
            forbidden_layer = any(
                module == m or module.startswith(m + ".")
                for m in FORBIDDEN_LAYERS[layer]
            )
            if top_level in FORBIDDEN_LIBS or forbidden_layer:
                violations.append(f"{path.relative_to(ROOT)} imports {module}")
    assert not violations, "Dependency rule violated:\n" + "\n".join(violations)