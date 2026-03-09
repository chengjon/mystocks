from __future__ import annotations


class SymphonyError(Exception):
    """Base error for Symphony runtime failures."""


class MissingWorkflowFileError(SymphonyError):
    """Raised when the configured workflow file does not exist."""


class WorkflowParseError(SymphonyError):
    """Raised when workflow front matter cannot be parsed."""


class WorkflowFrontMatterNotAMapError(SymphonyError):
    """Raised when workflow front matter is valid YAML but not a mapping."""


class ConfigurationValidationError(SymphonyError):
    """Raised when the effective Symphony config is invalid for dispatch."""

    def __init__(self, message: str, code: str = "invalid_configuration") -> None:
        super().__init__(message)
        self.code = code


class HookExecutionError(SymphonyError):
    """Raised when a fatal workspace hook fails."""


class WorkspaceSafetyError(SymphonyError):
    """Raised when a workspace path violates root-containment rules."""


class TrackerRequestError(SymphonyError):
    """Raised when tracker transport or GraphQL requests fail."""
