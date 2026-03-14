from src.services.maestro import (
    ActorIdentity,
    CoordinationService,
    DualWriteCollaborationRegistry,
    MaestroService,
    MongoCollaborationRegistry,
    MongoCollaborationStore,
)
from src.services.maestro.collab import WorkItemRecord, WorkspaceManager
from src.services.maestro.kernel import MaestroOrchestrator
from src.services.maestro.profiles.mystocks import PROFILE_NAME, ROLE_MODEL, THREE_LAYER_ARCHITECTURE
from src.services.symphony.orchestrator import SymphonyOrchestrator
from src.services.symphony.service import SymphonyService


def test_maestro_namespace_exposes_compatibility_runtime() -> None:
    assert MaestroService is SymphonyService
    assert MaestroOrchestrator is SymphonyOrchestrator
    assert WorkspaceManager.__name__ == "WorkspaceManager"
    assert ActorIdentity.__name__ == "ActorIdentity"
    assert CoordinationService.__name__ == "CoordinationService"
    assert MongoCollaborationStore.__name__ == "MongoCollaborationStore"
    assert MongoCollaborationRegistry.__name__ == "MongoCollaborationRegistry"
    assert DualWriteCollaborationRegistry.__name__ == "DualWriteCollaborationRegistry"


def test_maestro_collab_namespace_exposes_control_plane_models() -> None:
    assert WorkItemRecord.__name__ == "WorkItemRecord"


def test_mystocks_profile_defines_role_model_and_three_layers() -> None:
    assert PROFILE_NAME == "mystocks"
    assert set(ROLE_MODEL) == {"human", "main_cli", "worker_cli", "runtime"}
    assert [layer["key"] for layer in THREE_LAYER_ARCHITECTURE] == ["kernel", "collab", "profiles"]
