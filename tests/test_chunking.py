from copilot.application.chunking import chunk_text, clean_text

SAMPLE = """Title line
1. Purpose
1.1 First rule.
1.2 Second rule.
2. Dosing
2.1 Start at 5 mg.
Table 1. Doses
Step\tDose
Standard\t5 mg
2.2 Maximum 20 mg.
"""


def test_one_chunk_per_section_with_clause_range():
    chunks = chunk_text(clean_text(SAMPLE))
    assert [c.section for c in chunks] == ["1. Purpose", "2. Dosing"]
    assert chunks[0].clauses == "1.1-1.2"
    assert chunks[1].clauses == "2.1-2.2"


def test_table_rows_stay_with_their_clause():
    dosing = chunk_text(clean_text(SAMPLE))[1]
    assert "Standard\t5 mg" in dosing.text


def test_long_section_splits_on_clause_boundaries():
    clauses = "\n".join(f"3.{i} " + "word " * 100 for i in range(1, 9))
    chunks = chunk_text("3. Long\n" + clauses)
    assert len(chunks) > 1
    assert all(c.text.startswith("3. Long") for c in chunks)
    assert all(c.clauses.startswith("3.") for c in chunks)
