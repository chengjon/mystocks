RUNTIME_FAMILY_NAME = "Maestro"
LEGACY_RUNTIME_NAME = "Symphony"
PROFILE_NAME = "mystocks"

COLLAB_CONTROL_PLANE_DEFAULTS = {
    "backend": "sqlite",
    "mongo_uri": "mongodb://localhost:27017",
    "mongo_db": "mystocks_coord",
    "cutover_mode": "project-first",
    "promote_new_tasks_to_mongo": True,
}

ROLE_MODEL = {
    "human": {
        "label": "Human",
        "responsibilities": (
            "define goals and direction",
            "define total task scope",
            "define high-level constraints",
        ),
    },
    "main_cli": {
        "label": "Main CLI",
        "responsibilities": (
            "decompose the total task",
            "assign owner and worker CLI",
            "define acceptance criteria",
            "export TASK.md snapshots from Mongo state",
            "review exported TASK-REPORT.md snapshots and human evidence",
        ),
    },
    "worker_cli": {
        "label": "Worker CLI",
        "responsibilities": (
            "execute within assigned scope",
            "respect file ownership boundaries",
            "update Mongo coordination state",
            "append human evidence to exported TASK-REPORT.md when needed",
            "provide verification evidence",
        ),
    },
    "runtime": {
        "label": "Maestro Runtime",
        "responsibilities": (
            "automate dispatch after task activation",
            "create or reuse workspaces",
            "monitor session heartbeat and stale state",
            "retry and surface runtime visibility",
        ),
    },
}

THREE_LAYER_ARCHITECTURE = [
    {
        "key": "kernel",
        "name": "Maestro Kernel",
        "responsibility": "generic orchestration runtime, tracker wiring, agent execution, and status APIs",
    },
    {
        "key": "collab",
        "name": "Maestro Collab",
        "responsibility": "multi-CLI coordination core such as workspace, ownership, task-contract, and worktree automation",
    },
    {
        "key": "profiles",
        "name": "Maestro Profiles",
        "responsibility": "repository-specific policy, prompts, defaults, and workflow bindings such as MyStocks",
    },
]
