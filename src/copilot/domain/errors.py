class DomainError(Exception):
    """Base class for explicit domain errors."""


class ProviderUnavailableError(DomainError):
    """An LLM or embedding provider failed or is unreachable."""


class UnsupportedFormatError(DomainError):
    """No extractor can read this file type."""


class InvalidDocumentError(DomainError):
    """The document is malformed, for example missing front-matter or sections."""


class ConfigurationError(DomainError):
    """Configuration names something that does not exist."""
