class DomainError(Exception):
    """Base class for explicit domain errors."""


class ProviderUnavailableError(DomainError):
    """An LLM or embedding provider failed or is unreachable."""