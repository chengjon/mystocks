"""
健康检查 API 端点
"""

import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import psycopg2
from fastapi import APIRouter, Depends, Path, Request
from pydantic import BaseModel

from app.core.readiness import check_mongodb_readiness
from app.core.exceptions import BusinessException, NotFoundException
from app.core.responses import (
    ErrorCodes,
    UnifiedResponse,
    create_error_response,
    create_health_response,
    create_unified_success_response,
)
from app.core.security import User, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

SYSTEM_SERVICES_HEALTH_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "服务mystocks-web-api状态检查",
    "data": {
        "status": "healthy",
        "service": "mystocks-web-api",
        "timestamp": "2026-04-03T00:00:00+00:00",
        "overall_status": "healthy",
        "services": {
            "postgresql": {"service": "postgresql", "status": "normal"},
            "tdengine": {"service": "tdengine", "status": "normal"},
            "mongodb": {"service": "mongodb", "status": "normal"},
            "contract": {"service": "contract", "status": "normal"},
            "disk": {"service": "disk", "status": "normal"},
            "system": {"service": "system", "status": "normal"},
        },
    },
    "request_id": "demo-request-id",
}

SYSTEM_SERVICES_HEALTH_ERROR_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 500,
    "message": "健康检查失败: database unavailable",
    "request_id": "demo-request-id",
}

DETAILED_HEALTH_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "详细健康检查完成",
    "data": {
        "status": "success",
        "output": "[OK] backend: running\n[OK] frontend: running\n",
        "error": "",
    },
    "request_id": "req-health-detailed-001",
}

DETAILED_HEALTH_ERROR_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 500,
    "message": "详细健康检查失败: 健康检查脚本不存在: /opt/claude/mystocks_spec/scripts/dev/automation/health_check_simple.sh",
    "error_code": "HEALTH_CHECK_FAILED",
    "request_id": "req-health-detailed-001",
}

HEALTH_REPORT_RESPONSE_EXAMPLE = {
    "timestamp": "2026-04-03T00:00:00+00:00",
    "services": {
        "postgresql": {
            "service": "postgresql",
            "status": "normal",
            "details": "连接正常",
            "response_time": 0.02,
        },
        "tdengine": {
            "service": "tdengine",
            "status": "normal",
            "details": "连接正常",
            "response_time": 0.03,
        },
    },
}

HEALTH_REPORT_NOT_FOUND_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 404,
    "message": "健康检查报告不存在: 20260403_000000",
    "error_code": "RESOURCE_NOT_FOUND",
    "request_id": "req-health-report-001",
}

HEALTH_REPORT_ERROR_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 500,
    "message": "获取报告失败: [Errno 13] Permission denied",
    "error_code": "REPORT_RETRIEVAL_FAILED",
    "request_id": "req-health-report-001",
}


class HealthStatus(BaseModel):
    """健康检查状态响应模型"""

    service: str
    status: str  # 'normal', 'warning', 'error'
    details: Optional[str] = None
    response_time: Optional[float] = None


class HealthResponse(BaseModel):
    """健康检查综合响应模型"""

    timestamp: str
    overall_status: str  # 'normal', 'warning', 'error'
    services: Dict[str, HealthStatus]
    report_url: Optional[str] = None


def _resolve_ports(*env_keys: str) -> list[int]:
    ports: list[int] = []
    for key in env_keys:
        value = os.getenv(key, "").strip()
        if not value:
            continue
        try:
            port = int(value)
        except ValueError:
            continue
        if port > 0:
            ports.append(port)
    return ports


@router.get(
    "/health/services",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="系统服务健康检查",
    responses={
        200: {
            "description": "系统服务级健康检查结果",
            "content": {"application/json": {"example": SYSTEM_SERVICES_HEALTH_RESPONSE_EXAMPLE}},
        },
        500: {
            "description": "系统服务健康检查失败",
            "content": {"application/json": {"example": SYSTEM_SERVICES_HEALTH_ERROR_RESPONSE_EXAMPLE}},
        },
    },
)
async def check_system_health(request: Request):
    """
    系统健康检查API端点

    返回系统各个组件的健康状态
    """
    try:
        # 获取请求ID
        request_id = getattr(request.state, "request_id", None)

        # 创建健康检查结果
        services = {}

        # 检查PostgreSQL
        services["postgresql"] = await check_postgresql_service()

        # 检查TDengine
        services["tdengine"] = await check_tdengine_service()

        # 检查MongoDB（默认可选基础设施）
        services["mongodb"] = await check_mongodb_service()

        # 检查API契约治理健康状态
        services["contract"] = await check_contract_health()

        # 检查磁盘空间
        services["disk"] = await check_disk_space()

        # 检查系统资源
        services["system"] = await check_system_resources()

        # 确定整体状态
        overall_status = "healthy"
        for service_status in services.values():
            if service_status.status == "error":
                overall_status = "unhealthy"
                break
            elif service_status.status == "warning" and overall_status == "healthy":
                overall_status = "degraded"

        # 创建健康数据
        health_data = {
            "overall_status": overall_status,
            "services": services,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return create_health_response(
            service="mystocks-web-api", status=overall_status, details=health_data, request_id=request_id
        )

    except Exception as e:
        return create_error_response(
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            message=f"健康检查失败: {str(e)}",
            request_id=getattr(request.state, "request_id", None),
        )


async def check_frontend_service() -> HealthStatus:
    """检查前端服务状态"""
    import time

    import aiohttp

    start_time = time.time()
    frontend_ports = _resolve_ports("FRONTEND_PORT", "FRONTEND_BACKUP_PORT")
    if not frontend_ports:
        return HealthStatus(
            service="frontend",
            status="error",
            details="缺少 FRONTEND_PORT/FRONTEND_BACKUP_PORT 环境变量",
            response_time=(time.time() - start_time) * 1000,
        )

    try:
        async with aiohttp.ClientSession() as session:
            for port in frontend_ports:
                try:
                    async with session.get(
                        f"http://localhost:{port}", timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
                        if response.status == 200:
                            return HealthStatus(service="frontend", status="normal", response_time=response_time)
                        return HealthStatus(
                            service="frontend",
                            status="warning",
                            details=f"服务响应异常: {response.status} (port={port})",
                            response_time=response_time,
                        )
                except Exception:
                    continue

            return HealthStatus(
                service="frontend",
                status="error",
                details=f"服务不可访问: 已尝试端口 {frontend_ports}",
                response_time=(time.time() - start_time) * 1000,
            )
    except Exception as e:
        return HealthStatus(
            service="frontend",
            status="error",
            details=f"服务不可访问: {str(e)}",
            response_time=(time.time() - start_time) * 1000,
        )


async def check_api_service() -> HealthStatus:
    """检查API服务状态"""
    import time

    import aiohttp

    start_time = time.time()
    backend_ports = _resolve_ports("BACKEND_PORT", "BACKEND_BACKUP_PORT")
    if not backend_ports:
        return HealthStatus(
            service="api",
            status="error",
            details="缺少 BACKEND_PORT/BACKEND_BACKUP_PORT 环境变量",
            response_time=(time.time() - start_time) * 1000,
        )

    try:
        async with aiohttp.ClientSession() as session:
            for port in backend_ports:
                try:
                    async with session.get(
                        f"http://localhost:{port}/api/health",
                        timeout=aiohttp.ClientTimeout(total=5),
                    ) as response:
                        response_time = (time.time() - start_time) * 1000  # 转换为毫秒

                        if response.status == 200:
                            return HealthStatus(service="api", status="normal", response_time=response_time)
                        return HealthStatus(
                            service="api",
                            status="warning",
                            details=f"服务响应异常: {response.status} (port={port})",
                            response_time=response_time,
                        )
                except Exception:
                    continue

            return HealthStatus(
                service="api",
                status="error",
                details=f"服务不可访问: 已尝试端口 {backend_ports}",
                response_time=(time.time() - start_time) * 1000,
            )
    except Exception as e:
        return HealthStatus(
            service="api",
            status="error",
            details=f"服务不可访问: {str(e)}",
            response_time=(time.time() - start_time) * 1000,
        )


async def check_postgresql_service() -> HealthStatus:
    """检查PostgreSQL服务状态"""
    try:
        # 从环境变量中获取PostgreSQL连接信息
        pg_host = os.getenv("POSTGRESQL_HOST", "localhost")
        pg_port = os.getenv("POSTGRESQL_PORT", "5438")
        pg_user = os.getenv("POSTGRESQL_USER", "postgres")
        pg_password = os.getenv("POSTGRESQL_PASSWORD", "postgres")
        pg_database = os.getenv("POSTGRESQL_DATABASE", "mystocks")

        conn = psycopg2.connect(
            host=pg_host, port=pg_port, user=pg_user, password=pg_password, database=pg_database, connect_timeout=5
        )

        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()

        cursor.close()
        conn.close()

        return HealthStatus(service="postgresql", status="normal", details="数据库连接正常")
    except Exception as e:
        return HealthStatus(service="postgresql", status="error", details=f"数据库连接失败: {str(e)}")


async def check_tdengine_service() -> HealthStatus:
    """检查TDengine服务状态"""
    try:
        import socket

        # 尝试连接到TDengine端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("localhost", 6030))
        sock.close()

        if result == 0:
            return HealthStatus(service="tdengine", status="normal", details="端口可访问")
        else:
            return HealthStatus(service="tdengine", status="warning", details="端口不可访问")
    except Exception as e:
        return HealthStatus(service="tdengine", status="error", details=f"连接检查失败: {str(e)}")


async def check_mongodb_service() -> HealthStatus:
    """检查 MongoDB 服务状态（默认可见但不作为硬阻塞项）。"""
    result = check_mongodb_readiness()
    status = result.get("status", "optional_unavailable")
    details = result.get("detail")
    latency = result.get("latency_ms")

    if status in {"ready", "optional_unconfigured"}:
        return HealthStatus(service="mongodb", status="normal", details=details, response_time=latency)

    if status == "optional_unavailable":
        return HealthStatus(service="mongodb", status="warning", details=details, response_time=latency)

    return HealthStatus(service="mongodb", status="error", details=details, response_time=latency)


async def check_contract_health() -> HealthStatus:
    """检查 API 契约治理健康状态。"""
    try:
        from app.api.contract.services.drift_incidents import list_contract_drift_incidents

        open_incidents = list_contract_drift_incidents()
        if not open_incidents:
            return HealthStatus(
                service="contract",
                status="normal",
                details="contract validation ok; open drift incidents=0",
            )

        status = "error" if any(incident.severity == "error" for incident in open_incidents) else "warning"
        return HealthStatus(
            service="contract",
            status=status,
            details=f"contract validation drift incidents open={len(open_incidents)}",
        )
    except Exception as e:
        return HealthStatus(service="contract", status="warning", details=f"contract health check failed: {str(e)}")


async def check_disk_space() -> HealthStatus:
    """检查磁盘空间"""
    try:
        import shutil

        # 获取根目录的磁盘使用情况
        total, used, free = shutil.disk_usage("/")

        # 计算使用百分比
        percent_used = (used / total) * 100

        if percent_used > 90:
            status = "error"
            details = f"磁盘使用率过高: {percent_used:.1f}%"
        elif percent_used > 80:
            status = "warning"
            details = f"磁盘使用率较高: {percent_used:.1f}%"
        else:
            status = "normal"
            details = f"磁盘使用率正常: {percent_used:.1f}%"

        return HealthStatus(
            service="disk",
            status=status,
            details=f"{details}, 总计: {total // (1024**3)}GB, 可用: {free // (1024**3)}GB",
        )
    except Exception as e:
        return HealthStatus(service="disk", status="warning", details=f"检查失败: {str(e)}")


async def check_system_resources() -> HealthStatus:
    """检查系统资源"""
    try:
        import psutil

        # 获取CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # 获取内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        if cpu_percent > 90 or memory_percent > 90:
            status = "error"
            details = f"资源使用率过高 - CPU: {cpu_percent:.1f}%, 内存: {memory_percent:.1f}%"
        elif cpu_percent > 80 or memory_percent > 80:
            status = "warning"
            details = f"资源使用率较高 - CPU: {cpu_percent:.1f}%, 内存: {memory_percent:.1f}%"
        else:
            status = "normal"
            details = f"资源使用率正常 - CPU: {cpu_percent:.1f}%, 内存: {memory_percent:.1f}%"

        return HealthStatus(service="system", status=status, details=details)
    except ImportError:
        return HealthStatus(service="system", status="warning", details="psutil模块未安装，跳过资源检查")
    except Exception as e:
        return HealthStatus(service="system", status="warning", details=f"检查失败: {str(e)}")


async def generate_health_report(services: Dict[str, HealthStatus]) -> Optional[str]:
    """生成健康检查报告并返回URL"""
    try:
        # 创建报告目录
        report_dir = "/var/log/mystocks/health_reports"
        os.makedirs(report_dir, exist_ok=True)

        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(report_dir, f"health_report_{timestamp}.json")

        # 构建报告数据
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "services": {name: service.dict() for name, service in services.items()},
        }

        # 写入报告文件
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        # 返回报告URL
        return f"/api/reports/health/{timestamp}"
    except Exception as e:
        logger.exception("生成健康报告失败: %s", e)
        return None


@router.get(
    "/health/detailed",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="详细健康检查",
    description="执行详细健康检查脚本并返回组件级输出，用于运维排障、发布验收和环境巡检。",
    responses={
        200: {
            "description": "详细健康检查执行完成",
            "content": {"application/json": {"example": DETAILED_HEALTH_RESPONSE_EXAMPLE}},
        },
        500: {
            "description": "详细健康检查执行失败",
            "content": {"application/json": {"example": DETAILED_HEALTH_ERROR_RESPONSE_EXAMPLE}},
        },
    },
)
async def detailed_health_check(current_user: User = Depends(get_current_user)):
    """
    详细健康检查

    返回系统各个组件的详细健康状态
    """
    try:
        # 执行健康检查脚本
        health_script = "/opt/claude/mystocks_spec/scripts/dev/automation/health_check_simple.sh"

        if os.path.exists(health_script):
            # 直接通过 bash 执行，避免只读文件系统上的 chmod 失败
            result = subprocess.run(["bash", health_script], capture_output=True, text=True, timeout=30)

            # 检查执行结果
            if result.returncode == 0:
                return create_unified_success_response(
                    data={"status": "success", "output": result.stdout, "error": result.stderr},
                    message="详细健康检查完成",
                )
            if result.stdout.strip():
                return create_unified_success_response(
                    data={
                        "status": "warning",
                        "output": result.stdout,
                        "error": result.stderr,
                        "returncode": result.returncode,
                    },
                    message="详细健康检查完成（存在非阻塞警告）",
                )
            raise Exception(f"脚本执行失败，返回码: {result.returncode}, 错误: {result.stderr}")
        else:
            raise Exception(f"健康检查脚本不存在: {health_script}")
    except Exception as e:
        raise BusinessException(detail=f"详细健康检查失败: {str(e)}", status_code=500, error_code="HEALTH_CHECK_FAILED")


@router.get(
    "/reports/health/{timestamp}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="获取健康检查报告",
    description="按报告时间戳读取历史健康检查结果，便于排查某次巡检、发布窗口或告警时段的系统状态。",
    responses={
        200: {
            "description": "指定时间点的健康检查报告",
            "content": {"application/json": {"example": HEALTH_REPORT_RESPONSE_EXAMPLE}},
        },
        404: {
            "description": "指定健康检查报告不存在",
            "content": {"application/json": {"example": HEALTH_REPORT_NOT_FOUND_RESPONSE_EXAMPLE}},
        },
        500: {
            "description": "健康检查报告读取失败",
            "content": {"application/json": {"example": HEALTH_REPORT_ERROR_RESPONSE_EXAMPLE}},
        },
    },
)
async def get_health_report(
    timestamp: str = Path(..., description="健康检查报告时间戳，例如 20260405_183000。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取健康检查报告

    参数:
    - timestamp: 报告时间戳
    """
    try:
        report_file = f"/var/log/mystocks/health_reports/health_report_{timestamp}.json"

        if not os.path.exists(report_file):
            raise NotFoundException(resource="健康检查报告", identifier=timestamp)

        with open(report_file, "r", encoding="utf-8") as f:
            report_data = json.load(f)

        return create_unified_success_response(data=report_data, message="健康检查报告获取成功")
    except NotFoundException:
        raise
    except Exception as e:
        raise BusinessException(detail=f"获取报告失败: {str(e)}", status_code=500, error_code="REPORT_RETRIEVAL_FAILED")
