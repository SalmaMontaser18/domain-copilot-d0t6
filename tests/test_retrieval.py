from copilot.application.ports.retrieval import RetrievedChunk
from copilot.application.retrieval import RetrieveEvidence, coverage, query_terms
from copilot.infrastructure.llm.fake import FakeProvider


def chunk(text: str) -> RetrievedChunk:
    return RetrievedChunk("GL-01", "2.0", "T", "4. Dosing", "4.1", text, 0.03)


class StubSearch:
    def __init__(self, chunks):
        self.chunks = chunks

    def search(self, terms, embedding, limit, include_superseded):
        return self.chunks


def make(chunks):
    return RetrieveEvidence(FakeProvider(), StubSearch(chunks))


def test_query_terms_drop_stopwords_and_duplicates():
    assert query_terms("What is the starting dose of Cardiolan? Cardiolan!") == [
        "starting",
        "dose",
        "cardiolan",
    ]


def test_refuses_when_nothing_found():
    result = make([]).run("pediatric dose of Zentavir")
    assert not result.answerable
    assert result.reason


def test_refuses_when_passages_do_not_cover_the_question():
    result = make([chunk("4.1 The dose is 5 mg once daily.")]).run("pediatric dose of Zentavir")
    assert not result.answerable


def test_answers_when_passage_covers_the_question():
    result = make([chunk("4.1 Cardiolan starting dose is 5 mg.")]).run(
        "starting dose of Cardiolan"
    )
    assert result.answerable
    assert len(result.chunks) == 1


def test_returns_only_relevant_passages():
    chunks = [chunk("Cardiolan starting dose is 5 mg."), chunk("Unrelated text about asthma.")]
    result = make(chunks).run("starting dose of Cardiolan")
    assert [c.text for c in result.chunks] == ["Cardiolan starting dose is 5 mg."]


def test_refuses_question_without_searchable_terms():
    assert not make([chunk("anything")]).run("what is the").answerable


def test_refuses_when_only_some_terms_match_even_if_the_drug_is_mentioned():
    text = "7.7 No interaction between Zentavir and Cardiolan. The combined dose is 10 mg."
    result = make([chunk(text)]).run("pediatric dose of Zentavir")
    assert not result.answerable


def test_stem_matching_treats_treated_and_treatment_as_the_same_term():
    assert coverage(["treated"], "the treatment course") == 1.0