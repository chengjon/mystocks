"""
健康检查 API 端点
"""

import json
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, Optional

import psycopg2
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from app.core.responses import (
    ErrorCodes,
    ResponseMessages,
    create_error_response,
    create_health_response,
    create_success_response,
)
from app.core.security import get_current_user, User

router = APIRouter(tags=["health"])


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


@router.get("/health")
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
            "timestamp": datetime.utcnow().isoformat(),
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
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:3000", timeout=aiohttp.ClientTimeout(total=5)) as response:
                response_time = (time.time() - start_time) * 1000  # 转换为毫秒

                if response.status == 200:
                    return HealthStatus(service="frontend", status="normal", response_time=response_time)
                else:
                    return HealthStatus(
                        service="frontend",
                        status="warning",
                        details=f"服务响应异常: {response.status}",
                        response_time=response_time,
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
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'http://localhost:{os.getenv("BACKEND_PORT", "8000")}/api/health',
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                response_time = (time.time() - start_time) * 1000  # 转换为毫秒

                if response.status == 200:
                    return HealthStatus(service="api", status="normal", response_time=response_time)
                else:
                    return HealthStatus(
                        service="api",
                        status="warning",
                        details=f"服务响应异常: {response.status}",
                        response_time=response_time,
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
        report_dir = "/opt/mystocks/logs/health_reports"
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
        print(f"生成健康报告失败: {str(e)}")
        return None


@router.get("/health/detailed")
async def detailed_health_check(
    current_user: User = Depends(get_current_user)
):
    """
    详细健康检查

    返回系统各个组件的详细健康状态
    """
    try:
        # 执行健康检查脚本
        health_script = "/opt/claude/mystocks_spec/scripts/automation/health_check_simple.sh"

        if os.path.exists(health_script):
            # 设置脚本可执行权限
            os.chmod(health_script, 0o755)

            # 执行脚本
            result = subprocess.run(health_script, shell=True, capture_output=True, text=True, timeout=30)

            # 检查执行结果
            if result.returncode == 0:
                return {"status": "success", "output": result.stdout, "error": result.stderr}
            else:
                raise Exception(f"脚本执行失败，返回码: {result.returncode}, 错误: {result.stderr}")
        else:
            raise Exception(f"健康检查脚本不存在: {health_script}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"详细健康检查失败: {str(e)}")


@router.get("/reports/health/{timestamp}")
async def get_health_report(
    timestamp: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取健康检查报告

    参数:
    - timestamp: 报告时间戳
    """
    try:
        report_file = f"/opt/mystocks/logs/health_reports/health_report_{timestamp}.json"

        if not os.path.exists(report_file):
            raise HTTPException(status_code=404, detail="报告不存在")

        with open(report_file, "r", encoding="utf-8") as f:
            report_data = json.load(f)

        return report_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取报告失败: {str(e)}")
