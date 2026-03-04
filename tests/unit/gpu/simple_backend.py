#!/usr/bin/env python3
"""
简单的后端服务启动脚本 - 绕过复杂的依赖问题
"""

import os
import sys
import time

import uvicorn
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

# 设置项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 创建简单的FastAPI应用
app = FastAPI(title="MyStocks API", description="量化交易数据管理系统 API", version="1.0.0")

# Prometheus Metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])

REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])

ACTIVE_REQUESTS = Gauge("http_requests_active", "Number of active HTTP requests")

API_ERROR_COUNT = Counter("api_errors_total", "Total API errors", ["endpoint", "error_type"])


@app.middleware("http")
async def track_requests(request, call_next):
    start_time = time.time()
    ACTIVE_REQUESTS.inc()

    try:
        response = await call_next(request)

        # Record metrics
        method = request.method
        path = request.url.path
        status = response.status_code
        latency = time.time() - start_time

        REQUEST_COUNT.labels(method=method, endpoint=path, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(latency)

        return response
    except Exception as e:
        # Record error metrics
        path = request.url.path
        API_ERROR_COUNT.labels(endpoint=path, error_type=type(e).__name__).inc()
        raise
    finally:
        ACTIVE_REQUESTS.dec()


@app.get("/")
async def root():
    return {"message": "MyStocks API is running", "status": "active"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "MyStocks API"}


@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "service": "MyStocks API"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# 基础的模拟数据端点
@app.get("/api/data/stocks/basic")
async def get_stocks_basic():
    """获取股票基本信息 - 模拟数据"""
    return {
        "success": True,
        "data": [
            {"symbol": "600000", "name": "浦发银行", "industry": "银行"},
            {"symbol": "000001", "name": "平安银行", "industry": "银行"},
            {"symbol": "000002", "name": "万科A", "industry": "房地产"},
        ],
        "total": 3,
    }


@app.get("/api/monitoring/realtime")
async def get_realtime_data():
    """获取实时数据 - 模拟数据"""
    return {
        "success": True,
        "data": {
            "market_status": "open",
            "timestamp": "2025-12-20 23:40:00",
            "indices": {
                "sh000001": {"name": "上证指数", "value": 3000.0, "change": 1.2},
                "sz399001": {"name": "深证成指", "value": 10000.0, "change": -0.8},
            },
        },
    }


if __name__ == "__main__":
    print("🚀 启动 MyStocks 简化版后端服务...")
    print("📍 服务地址: http://localhost:8020")
    print("📖 API文档: http://localhost:8020/docs")

    uvicorn.run("simple_backend:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
