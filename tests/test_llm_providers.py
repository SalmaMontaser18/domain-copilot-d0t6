import pytest

from copilot.application.llm_fallback import FallbackLLM
from copilot.application.ports.llm import Message
from copilot.domain.errors import ProviderUnavailableError
from copilot.infrastructure.llm.fake import FakeProvider


class BrokenProvider(FakeProvider):
    name = "broken"

    def complete(self, messages, tools=None):
        raise ProviderUnavailableError("down")


MSG = [Message("user", "hi")]


def test_fake_embeddings_are_deterministic():
    p = FakeProvider()
    assert p.embed(["a"]) == p.embed(["a"])
    assert p.embed(["a"]) != p.embed(["b"])


def test_fake_stream_yields_tokens():
    assert list(FakeProvider("a b c").stream(MSG)) == ["a", "b", "c"]


def test_fallback_uses_next_provider_when_first_fails():
    chain = FallbackLLM([BrokenProvider(), FakeProvider("ok")])
    assert chain.complete(MSG).text == "ok"


def test_fallback_raises_when_all_fail():
    chain = FallbackLLM([BrokenProvider()])
    with pytest.raises(ProviderUnavailableError):
        chain.complete(MSG)