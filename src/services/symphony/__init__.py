"""Legacy compatibility package for the in-repo Maestro runtime implementation."""

from .config import ServiceConfig, validate_dispatch_config
from .models import WorkflowDefinition
from .tracker_factory import create_tracker_client
from .workflow_loader import load_workflow_definition

__all__ = [
    "ServiceConfig",
    "WorkflowDefinition",
    "create_tracker_client",
    "load_workflow_definition",
    "validate_dispatch_config",
]
