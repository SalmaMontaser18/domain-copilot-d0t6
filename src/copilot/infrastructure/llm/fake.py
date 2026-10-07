import hashlib
from collections.abc import Iterator

from copilot.application.ports.llm import LLMResponse, Message, ToolSpec, Usage


class FakeProvider:
    """Deterministic provider for tests and offline demos. No network."""

    name = "fake"
    DIM = 768

    def __init__(self, reply: str = "FAKE_REPLY") -> None:
        self.reply = reply

    def complete(
        self, messages: list[Message], tools: list[ToolSpec] | None = None
    ) -> LLMResponse:
        return LLMResponse(text=self.reply, usage=Usage(len(messages), 1))

    def stream(self, messages: list[Message]) -> Iterator[str]:
        yield from self.reply.split(" ")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def _vector(self, text: str) -> list[float]:
        values: list[float] = []
        counter = 0
        while len(values) < self.DIM:
            digest = hashlib.sha256(f"{counter}:{text}".encode()).digest()
            values.extend(byte / 255 for byte in digest)
            counter += 1
        return values[: self.DIM]
