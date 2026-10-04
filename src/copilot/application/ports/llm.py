from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Message:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict  # JSON schema


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict


@dataclass(frozen=True)
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0


@dataclass(frozen=True)
class LLMResponse:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: Usage = Usage()


class LLMProvider(Protocol):
    name: str

    def complete(self, messages: list[Message],
                 tools: list[ToolSpec] | None = None) -> LLMResponse: ...

    def stream(self, messages: list[Message]) -> Iterator[str]: ...

    def embed(self, texts: list[str]) -> list[list[float]]: ...