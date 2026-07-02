"""ExtraSource adapter contract.

Defines the Protocol, metadata, and result types that consumer-side
auxiliary data sources MUST implement to register with the
ExtraSource registry. See
``openspec/changes/add-extra-source-adapter-contract/`` for the
authoritative contract and Layer 1/2/3 division of labor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class ExtraSourceMeta:
    name: str
    category: str
    expires_on: Optional[str] = None


@dataclass(frozen=True)
class ExtraSourceResult:
    data: Any
    provider_used: str


@runtime_checkable
class ExtraSourceAdapter(Protocol):
    def get_meta(self) -> ExtraSourceMeta: ...

    def fetch(self, params: dict[str, Any]) -> ExtraSourceResult: ...


class ExtraSourceCategoryConflictError(RuntimeError):
    """Raised when an ExtraSource adapter declares a category that
    overlaps with OpenStock's static 70-category inventory."""


class ExtraSourceNameConflictError(RuntimeError):
    """Raised when an ExtraSource adapter is registered with a ``name``
    that is already present in the registry. Names MUST be globally
    unique so that logs, metrics, and CI attribution remain
    unambiguous."""
