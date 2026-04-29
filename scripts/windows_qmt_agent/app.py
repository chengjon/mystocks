from __future__ import annotations

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse

from .config import WindowsQmtAgentSettings, load_settings_from_env
from .models import ExecuteTaskRequest, HealthResponse
from .service import BRIDGE_CONTRACT_VERSION_HEADER, WindowsQmtReferenceService


def create_app(settings: WindowsQmtAgentSettings | None = None) -> FastAPI:
    resolved_settings = settings or load_settings_from_env()
    service = WindowsQmtReferenceService(resolved_settings)

    app = FastAPI(title=f"MyStocks Windows qmt Reference Service [{resolved_settings.node_name}]")
    app.state.windows_qmt_reference_service = service

    @app.get("/health", response_model=HealthResponse)
    async def health() -> dict[str, object]:
        return service.health_payload()

    @app.post("/api/v1/task/execute")
    async def execute_task(
        request: ExecuteTaskRequest,
        authorization: str | None = Header(default=None),
        bridge_contract_version: str | None = Header(default=None, alias=BRIDGE_CONTRACT_VERSION_HEADER),
    ) -> JSONResponse:
        boundary_failure = service.validate_boundary(
            authorization=authorization,
            contract_version=bridge_contract_version,
            provider=request.provider,
            method=request.method,
        )
        if boundary_failure is not None:
            status_code, payload = boundary_failure
            return JSONResponse(status_code=status_code, content=payload, headers=service.contract_headers())

        target_failure = service.validate_execute_target(request)
        if target_failure is not None:
            status_code, payload = target_failure
            return JSONResponse(status_code=status_code, content=payload, headers=service.contract_headers())

        status_code, payload = service.create_task(request)
        return JSONResponse(status_code=status_code, content=payload, headers=service.contract_headers())

    @app.get("/api/v1/task/result/{task_id}")
    async def get_task_result(
        task_id: str,
        authorization: str | None = Header(default=None),
        bridge_contract_version: str | None = Header(default=None, alias=BRIDGE_CONTRACT_VERSION_HEADER),
    ) -> JSONResponse:
        boundary_failure = service.validate_boundary(
            authorization=authorization,
            contract_version=bridge_contract_version,
            provider="qmt",
            method="task_result",
        )
        if boundary_failure is not None:
            status_code, payload = boundary_failure
            return JSONResponse(status_code=status_code, content=payload, headers=service.contract_headers())

        status_code, payload = service.get_task_result(task_id)
        return JSONResponse(status_code=status_code, content=payload, headers=service.contract_headers())

    return app


app = create_app()
