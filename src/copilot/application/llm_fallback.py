from typing import Iterator

from copilot.application.ports.llm import LLMProvider, LLMResponse, Message, ToolSpec
from copilot.domain.errors import ProviderUnavailableError


class FallbackLLM:
    """Tries providers in order; moves on when one is unavailable."""

    name = "fallback-chain"

    def __init__(self, providers: list[LLMProvider]) -> None:
        self.providers = providers

    def complete(self, messages: list[Message],
                 tools: list[ToolSpec] | None = None) -> LLMResponse:
        return self._first(lambda p: p.complete(messages, tools))

    def stream(self, messages: list[Message]) -> Iterator[str]:
        return self._first(lambda p: p.stream(messages))

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._first(lambda p: p.embed(texts))

    def _first(self, call):
        for provider in self.providers:
            try:
                return call(provider)
            except ProviderUnavailableError:
                continue
        raise ProviderUnavailableError("all providers in the chain failed")