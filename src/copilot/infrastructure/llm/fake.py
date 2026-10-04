import hashlib
from collections.abc import Iterator

from copilot.application.ports.llm import LLMResponse, Message, ToolSpec, Usage


class FakeProvider:
    """Deterministic provider for tests and offline demos. No network."""

    name = "fake"
    DIM = 64

    def __init__(self, reply: str = "FAKE_REPLY") -> None:
        self.reply = reply

    def complete(self, messages: list[Message],
                 tools: list[ToolSpec] | None = None) -> LLMResponse:
        return LLMResponse(text=self.reply, usage=Usage(len(messages), 1))

    def stream(self, messages: list[Message]) -> Iterator[str]:
        yield from self.reply.split(" ")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def _vector(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [b / 255 for b in (digest * 2)[: self.DIM]]