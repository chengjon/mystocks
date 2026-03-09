from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse


def create_status_app(orchestrator) -> FastAPI:
    """Create the optional Symphony status API."""

    app = FastAPI(title="Symphony Status API")

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        snapshot = orchestrator.snapshot()
        return (
            "<html><body>"
            "<h1>Symphony</h1>"
            f"<p>Running: {snapshot['counts']['running']}</p>"
            f"<p>Retrying: {snapshot['counts']['retrying']}</p>"
            "</body></html>"
        )

    @app.get("/api/v1/state")
    def state() -> dict:
        return orchestrator.snapshot()

    @app.get("/api/v1/{issue_identifier}")
    def issue(issue_identifier: str):
        snapshot = orchestrator.get_issue_snapshot(issue_identifier)
        if snapshot is None:
            return JSONResponse(
                status_code=404,
                content={"error": {"code": "issue_not_found", "message": f"Unknown issue: {issue_identifier}"}},
            )
        return snapshot

    @app.post("/api/v1/refresh", status_code=202)
    def refresh() -> dict:
        orchestrator.queue_refresh()
        return {
            "queued": True,
            "coalesced": False,
            "requested_at": orchestrator.snapshot()["generated_at"],
            "operations": ["poll", "reconcile"],
        }

    @app.get("/api/v1/collab/issues/{issue_identifier}")
    def collab_issue(issue_identifier: str):
        snapshot = orchestrator.get_collab_issue_state(issue_identifier)
        if snapshot is None or all(snapshot.get(key) is None for key in ("assignment", "workspace", "heartbeat")):
            return JSONResponse(
                status_code=404,
                content={
                    "error": {"code": "collab_issue_not_found", "message": f"Unknown collab issue: {issue_identifier}"}
                },
            )
        return snapshot

    @app.get("/api/v1/collab/workspaces")
    def collab_workspaces() -> dict:
        return {"items": orchestrator.list_collab_workspaces()}

    @app.get("/api/v1/collab/stale")
    def collab_stale() -> dict:
        return {"items": orchestrator.list_collab_stale()}

    return app
