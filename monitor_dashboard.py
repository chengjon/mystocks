#!/usr/bin/env python3
"""
简单的监控状态页面 - 替代Grafana/Prometheus
"""

import os
import time
import psutil
from datetime import datetime
from fastapi import FastAPI
import uvicorn

# 创建监控API
monitor_app = FastAPI(title="MyStocks Monitor", description="系统监控面板")


@monitor_app.get("/")
async def monitor_root():
    return {"service": "MyStocks Monitor", "status": "running"}


@monitor_app.get("/status")
async def get_system_status():
    """获取系统状态"""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
        "uptime": time.time() - psutil.boot_time(),
    }


@monitor_app.get("/services")
async def get_services_status():
    """获取服务状态"""
    services = {}

    # 检查前端服务
    try:
        import requests

        response = requests.get("http://localhost:3000", timeout=2)
        services["frontend"] = {"status": "running", "port": 3000}
    except:
        services["frontend"] = {"status": "stopped", "port": 3000}

    # 检查后端服务
    try:
        import requests

        response = requests.get("http://localhost:8000/health", timeout=2)
        services["backend"] = {"status": "running", "port": 8000}
    except:
        services["backend"] = {"status": "stopped", "port": 8000}

    return services


@monitor_app.get("/metrics")
async def get_metrics():
    """简单的指标端点"""
    return {
        "system_cpu": psutil.cpu_percent(),
        "system_memory": psutil.virtual_memory().percent,
        "api_requests": 1234,  # 模拟数据
        "active_connections": 56,  # 模拟数据
    }


if __name__ == "__main__":
    print("📊 启动 MyStocks 监控服务...")
    print("📍 监控面板: http://localhost:3101")

    uvicorn.run(
        "monitor_dashboard:monitor_app",
        host="0.0.0.0",
        port=3101,
        reload=False,
        log_level="info",
    )
