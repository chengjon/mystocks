from __future__ import annotations

from typing import TYPE_CHECKING

from .profiles.mystocks import (
    LEGACY_RUNTIME_NAME,
    PROFILE_NAME,
    ROLE_MODEL,
    RUNTIME_FAMILY_NAME,
    THREE_LAYER_ARCHITECTURE,
)

if TYPE_CHECKING:
    from .collab import SQLiteCollaborationRegistry, WorkspaceManager
    from .kernel import (
        MaestroOrchestrator,
        MaestroService,
        ServiceConfig,
        TrackerConfig,
        WorkflowDefinition,
        create_status_app,
        create_tracker_client,
        load_workflow_definition,
        validate_dispatch_config,
    )

_COLLAB_EXPORTS = {"SQLiteCollaborationRegistry", "WorkspaceManager"}
_KERNEL_EXPORTS = {
    "MaestroOrchestrator",
    "MaestroService",
    "ServiceConfig",
    "TrackerConfig",
    "WorkflowDefinition",
    "create_status_app",
    "create_tracker_client",
    "load_workflow_definition",
    "validate_dispatch_config",
}

__all__ = [
    "LEGACY_RUNTIME_NAME",
    "MaestroOrchestrator",
    "MaestroService",
    "PROFILE_NAME",
    "ROLE_MODEL",
    "RUNTIME_FAMILY_NAME",
    "ServiceConfig",
    "SQLiteCollaborationRegistry",
    "THREE_LAYER_ARCHITECTURE",
    "TrackerConfig",
    "WorkflowDefinition",
    "WorkspaceManager",
    "create_status_app",
    "create_tracker_client",
    "load_workflow_definition",
    "validate_dispatch_config",
]


def __getattr__(name: str):
    if name in _COLLAB_EXPORTS:
        from . import collab

        value = getattr(collab, name)
    elif name in _KERNEL_EXPORTS:
        from . import kernel

        value = getattr(kernel, name)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
