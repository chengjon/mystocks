class AttributionAnalysisError(Exception):
    """Base error for attribution analysis failures."""


class AttributionInputError(AttributionAnalysisError):
    """Raised when attribution input payloads are invalid."""
