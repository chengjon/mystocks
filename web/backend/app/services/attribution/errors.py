class AttributionAnalysisError(Exception):
    """Base error for attribution analysis failures."""


class AttributionInputError(AttributionAnalysisError):
    """Raised when attribution input payloads are invalid."""


class AttributionDependencyError(AttributionAnalysisError):
    """Raised when benchmark, industry, or factor dependencies are unavailable."""


class AttributionStaleError(AttributionAnalysisError):
    """Raised when attribution can only be served with stale enrichment."""


class AttributionUnsupportedSnapshotError(AttributionAnalysisError):
    """Raised when a snapshot payload cannot be normalized into canonical attribution inputs."""
