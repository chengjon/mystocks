"""Compat redirect: /api/strategy-mgmt/* → /api/v1/strategy/*"""
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/api/strategy-mgmt", tags=["strategy-mgmt-compat"])


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    operation_id="redirect_to_strategy_mgmt_compat",
    include_in_schema=False,
)
async def redirect_to_canonical(path: str):
    return RedirectResponse(url=f"/api/v1/strategy/{path}", status_code=307)
