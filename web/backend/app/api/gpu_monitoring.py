"""
GPU监控API路由 (CLI-5: Phase 6 - T5.2)

提供GPU硬件状态、性能指标和监控数据的API端点。
优先返回真实运行时状态；当运行时未接入或宿主机无GPU时，返回诚实的可用性结果。
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.core.responses import UnifiedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gpu", tags=["gpu-monitoring"])

GPU_STATUS_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "GPU运行状态获取成功",
    "data": {
        "status": "available",
        "device_id": 0,
        "gpus": [
            {
                "device_id": 0,
                "name": "NVIDIA RTX 4090",
                "gpu_utilization": 75.5,
                "memory_used": 18000,
                "memory_total": 24576,
                "memory_utilization": 73.2,
                "temperature": 68.0,
                "power_usage": 320.0,
                "health_status": "healthy",
                "allocated_strategies": 0,
            }
        ],
    },
    "request_id": "demo-request-id",
}

GPU_PERFORMANCE_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "GPU性能指标获取成功",
    "data": {
        "status": "available",
        "device_id": 0,
        "metrics": [
            {
                "device_id": 0,
                "gpu_utilization": 75.5,
                "memory_utilization": 73.2,
                "temperature": 68.0,
                "power_usage": 320.0,
                "timestamp": 1713052800.0,
                "health_status": "healthy",
            }
        ],
    },
    "request_id": "demo-request-id",
}

GPU_MONITORING_ERROR_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 500,
    "message": "GPU监控服务不可用",
    "request_id": "demo-request-id",
}

GPU_METRICS_ERROR_RESPONSE_EXAMPLE = "# GPU runtime unavailable\nmystocks_gpu_available 0\n"

GPU_METRICS_SUCCESS_RESPONSE_EXAMPLE = """# HELP mystocks_gpu_available GPU runtime availability
# TYPE mystocks_gpu_available gauge
mystocks_gpu_available 1
# HELP mystocks_gpu_utilization_percent GPU utilization percentage
# TYPE mystocks_gpu_utilization_percent gauge
mystocks_gpu_utilization_percent{device_id="0"} 75.5
"""

GPU_HISTORY_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "GPU历史监控尚未持久化，返回当前运行时快照",
    "data": {
        "status": "runtime_snapshot_only",
        "device_id": 0,
        "records": [
            {
                "timestamp": 1713052800.0,
                "device_id": 0,
                "gpu_utilization": 75.5,
                "memory_utilization": 73.2,
                "temperature": 68.0,
                "power_usage": 320.0,
            }
        ],
        "total": 1,
    },
    "request_id": "demo-request-id",
}


def _json_response_spec(description: str, example: object) -> dict[int, dict]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


def _runtime_gpu_response(message: str, request_id: Optional[str], data: dict, *, success: bool = True) -> UnifiedResponse:
    return UnifiedResponse(
        success=success,
        code=200 if success else 503,
        message=message,
        data=data,
        request_id=request_id,
    )


GPU_HISTORY_RESPONSES = {
    **_json_response_spec("GPU 历史监控数据", GPU_HISTORY_RESPONSE_EXAMPLE),
    500: {
        "description": "GPU 历史数据查询失败",
        "content": {"application/json": {"example": GPU_MONITORING_ERROR_RESPONSE_EXAMPLE}},
    },
}

GPU_PROMETHEUS_METRICS_RESPONSES = {
    200: {
        "description": "Prometheus GPU 指标文本",
        "content": {"text/plain": {"example": GPU_METRICS_SUCCESS_RESPONSE_EXAMPLE}},
    },
    500: {
        "description": "Prometheus GPU 指标导出失败",
        "content": {"text/plain": {"example": GPU_METRICS_ERROR_RESPONSE_EXAMPLE}},
    },
}


class GPUStatus(BaseModel):
    """GPU硬件状态模型"""

    device_id: int = Field(..., description="GPU设备ID")
    name: str = Field(..., description="GPU名称")
    gpu_utilization: float = Field(..., description="GPU利用率 (%)", ge=0, le=100)
    memory_used: int = Field(..., description="已用显存 (MB)")
    memory_total: int = Field(..., description="总显存 (MB)")
    memory_utilization: float = Field(..., description="显存利用率 (%)", ge=0, le=100)
    temperature: float = Field(..., description="GPU温度 (°C)")
    power_usage: float = Field(..., description="功耗 (W)")
    sm_clock: int = Field(0, description="SM时钟频率 (MHz)")
    memory_clock: int = Field(0, description="显存时钟频率 (MHz)")


class GPUPerformanceMetrics(BaseModel):
    """GPU性能指标模型"""

    device_id: int = Field(..., description="GPU设备ID")
    matrix_gflops: Optional[float] = Field(None, description="矩阵运算性能 (GFLOPS)")
    matrix_speedup: Optional[float] = Field(None, description="矩阵运算加速比")
    memory_gflops: Optional[float] = Field(None, description="内存操作性能 (GFLOPS)")
    memory_speedup: Optional[float] = Field(None, description="内存操作加速比")
    throughput: Optional[float] = Field(None, description="吞吐量 (ops/s)")
    timestamp: Optional[float] = Field(None, description="时间戳")


def _safe_percentage(value: Any) -> float:
    return round(float(value or 0) * 100, 2)


async def _get_gpu_runtime_snapshot(device_id: Optional[int] = None) -> dict[str, Any]:
    from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager, NVML_AVAILABLE

    if not NVML_AVAILABLE:
        return {
            "status": "unavailable",
            "reason": "nvml_unavailable",
            "device_id": device_id,
            "gpus": [],
        }

    manager = GPUResourceManager()
    initialized = await manager.initialize()
    if not initialized:
        return {
            "status": "unavailable",
            "reason": "initialization_failed",
            "device_id": device_id,
            "gpus": [],
        }

    await manager.update_device_metrics()

    devices = [manager.get_device_health(gpu_id) for gpu_id in manager.devices.keys()]
    if device_id is not None:
        devices = [device for device in devices if device.get("device_id") == device_id]

    gpus = [
        {
            "device_id": device["device_id"],
            "name": device["name"],
            "gpu_utilization": _safe_percentage(device.get("compute_utilization")),
            "memory_used": int(device.get("memory_used_mb") or 0),
            "memory_total": int(device.get("memory_total_mb") or 0),
            "memory_utilization": _safe_percentage(device.get("memory_utilization")),
            "temperature": 0.0,
            "power_usage": 0.0,
            "health_status": device.get("health_status", "unknown"),
            "allocated_strategies": int(device.get("allocated_strategies") or 0),
            "timestamp": time.time(),
        }
        for device in devices
        if "error" not in device
    ]

    status = "available" if gpus else "unavailable"
    return {
        "status": status,
        "reason": None if gpus else "device_not_found" if device_id is not None else "no_gpu_devices",
        "device_id": device_id,
        "gpus": gpus,
    }


def _build_gpu_metrics_payload(runtime_snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "device_id": gpu["device_id"],
            "gpu_utilization": gpu["gpu_utilization"],
            "memory_utilization": gpu["memory_utilization"],
            "temperature": gpu["temperature"],
            "power_usage": gpu["power_usage"],
            "timestamp": gpu["timestamp"],
            "health_status": gpu["health_status"],
        }
        for gpu in runtime_snapshot["gpus"]
    ]


def _build_gpu_history_payload(runtime_snapshot: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    return [
        {
            "timestamp": gpu["timestamp"],
            "device_id": gpu["device_id"],
            "gpu_utilization": gpu["gpu_utilization"],
            "memory_utilization": gpu["memory_utilization"],
            "temperature": gpu["temperature"],
            "power_usage": gpu["power_usage"],
            "source": "runtime_snapshot",
        }
        for gpu in runtime_snapshot["gpus"][:limit]
    ]


def _build_prometheus_metrics(runtime_snapshot: dict[str, Any]) -> str:
    lines = [
        "# HELP mystocks_gpu_available GPU runtime availability",
        "# TYPE mystocks_gpu_available gauge",
        f"mystocks_gpu_available {1 if runtime_snapshot['status'] == 'available' else 0}",
    ]

    for gpu in runtime_snapshot["gpus"]:
        device_id = gpu["device_id"]
        lines.extend(
            [
                "# HELP mystocks_gpu_utilization_percent GPU utilization percentage",
                "# TYPE mystocks_gpu_utilization_percent gauge",
                f'mystocks_gpu_utilization_percent{{device_id="{device_id}"}} {gpu["gpu_utilization"]}',
                "# HELP mystocks_gpu_memory_utilization_percent GPU memory utilization percentage",
                "# TYPE mystocks_gpu_memory_utilization_percent gauge",
                f'mystocks_gpu_memory_utilization_percent{{device_id="{device_id}"}} {gpu["memory_utilization"]}',
                "# HELP mystocks_gpu_allocated_strategies Active strategies allocated to GPU",
                "# TYPE mystocks_gpu_allocated_strategies gauge",
                f'mystocks_gpu_allocated_strategies{{device_id="{device_id}"}} {gpu["allocated_strategies"]}',
            ]
        )

    return "\n".join(lines) + "\n"


@router.get(
    "/status",
    summary="获取 GPU 运行状态",
    description="返回当前 GPU 运行时可用性、设备指标和降级原因，用于控制面状态检查与运维监控。",
    responses={
        200: {
            "description": "GPU 实时状态",
            "content": {"application/json": {"example": GPU_STATUS_RESPONSE_EXAMPLE}},
        },
        500: {
            "description": "GPU 状态查询失败",
            "content": {"application/json": {"example": GPU_MONITORING_ERROR_RESPONSE_EXAMPLE}},
        },
    },
)
async def get_gpu_status(
    request: Request,
    device_id: Optional[int] = Query(None, description="GPU设备ID（可选，不指定则返回所有GPU）"),
):
    request_id = getattr(request.state, "request_id", None)
    runtime_snapshot = await _get_gpu_runtime_snapshot(device_id)

    if runtime_snapshot["status"] != "available":
        logger.info("GPU运行时不可用: device_id=%s, reason=%s", device_id, runtime_snapshot.get("reason"))
        return _runtime_gpu_response(
            message="未检测到可用GPU运行时",
            request_id=request_id,
            data=runtime_snapshot,
        )

    return _runtime_gpu_response(
        message="GPU运行状态获取成功",
        request_id=request_id,
        data=runtime_snapshot,
    )


@router.get(
    "/performance",
    summary="获取 GPU 性能指标",
    description="返回当前 GPU 利用率、显存利用率和策略分配指标，用于性能面板与监控采集。",
    responses={
        200: {
            "description": "GPU 性能指标",
            "content": {"application/json": {"example": GPU_PERFORMANCE_RESPONSE_EXAMPLE}},
        },
        500: {
            "description": "GPU 性能指标查询失败",
            "content": {"application/json": {"example": GPU_MONITORING_ERROR_RESPONSE_EXAMPLE}},
        },
    },
)
async def get_gpu_performance(
    request: Request,
    device_id: Optional[int] = Query(None, description="GPU设备ID（可选，不指定则返回所有GPU）"),
):
    request_id = getattr(request.state, "request_id", None)
    runtime_snapshot = await _get_gpu_runtime_snapshot(device_id)
    metrics = _build_gpu_metrics_payload(runtime_snapshot)

    return _runtime_gpu_response(
        message="GPU性能指标获取成功" if metrics else "未检测到可用GPU运行时",
        request_id=request_id,
        data={
            "status": runtime_snapshot["status"],
            "device_id": device_id,
            "metrics": metrics,
            "reason": runtime_snapshot.get("reason"),
        },
    )


@router.get(
    "/metrics",
    summary="导出 GPU Prometheus 指标",
    description="以 Prometheus 文本格式导出当前 GPU 监控指标，供监控系统按固定周期抓取。",
    response_class=PlainTextResponse,
    responses=GPU_PROMETHEUS_METRICS_RESPONSES,
)
async def get_prometheus_metrics(request: Request):
    runtime_snapshot = await _get_gpu_runtime_snapshot()
    return PlainTextResponse(content=_build_prometheus_metrics(runtime_snapshot), media_type="text/plain")


@router.get(
    "/history",
    summary="查询 GPU 历史监控数据",
    description="按设备和时间范围返回 GPU 历史监控记录，当前仅接入运行时快照，尚未持久化。",
    responses=GPU_HISTORY_RESPONSES,
)
async def get_gpu_history(
    request: Request,
    device_id: int = Query(..., description="GPU设备ID"),
    start_time: Optional[float] = Query(None, description="开始时间戳"),
    end_time: Optional[float] = Query(None, description="结束时间戳"),
    limit: int = Query(100, description="返回记录数", ge=1, le=1000),
):
    request_id = getattr(request.state, "request_id", None)
    runtime_snapshot = await _get_gpu_runtime_snapshot(device_id)
    records = _build_gpu_history_payload(runtime_snapshot, limit)

    if start_time is not None:
        records = [record for record in records if record["timestamp"] >= start_time]
    if end_time is not None:
        records = [record for record in records if record["timestamp"] <= end_time]

    return _runtime_gpu_response(
        message="GPU历史监控尚未持久化，返回当前运行时快照" if records else "未检测到可用GPU运行时",
        request_id=request_id,
        data={
            "status": "runtime_snapshot_only" if records else runtime_snapshot["status"],
            "device_id": device_id,
            "records": records,
            "total": len(records),
            "reason": runtime_snapshot.get("reason"),
        },
    )


logger.info("✅ GPU监控API路由已加载 (CLI-5 Phase 6)")
