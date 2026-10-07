from copilot.application.ports.llm import LLMProvider
from copilot.domain.errors import ConfigurationError
from copilot.infrastructure.llm.fake import FakeProvider


def build_provider(name: str) -> LLMProvider:
    if name == "fake":
        return FakeProvider()
    raise ConfigurationError(f"unknown LLM_PROVIDER: {name}")
