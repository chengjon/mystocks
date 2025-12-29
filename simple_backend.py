#!/usr/bin/env python3
"""
简单的后端服务启动脚本 - 绕过复杂的依赖问题
"""

import os
import sys
import time
import secrets
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

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


# CSRF Token Manager
class CSRFTokenManager:
    """CSRF Token管理器"""

    def __init__(self):
        self.tokens = {}
        self.token_timeout = 3600

    def generate_token(self) -> str:
        """生成新的CSRF token"""
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {"created_at": time.time(), "use_count": 0}
        return token

    def validate_token(self, token: str) -> bool:
        """验证CSRF token"""
        if not token or token not in self.tokens:
            return False
        token_info = self.tokens[token]
        if time.time() - token_info["created_at"] > self.token_timeout:
            del self.tokens[token]
            return False
        token_info["use_count"] += 1
        return True


csrf_manager = CSRFTokenManager()


@app.middleware("http")
async def track_requests(request, call_next):
    start_time = time.time()
    ACTIVE_REQUESTS.inc()

    try:
        # CSRF Protection
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            exclude_paths = [
                "/api/csrf-token",
                "/api/v1/csrf/token",
                "/api/v1/auth/login",
            ]
            if not any(request.url.path.startswith(path) for path in exclude_paths):
                csrf_token = request.headers.get("x-csrf-token")
                if not csrf_token or not csrf_manager.validate_token(csrf_token):
                    return JSONResponse(
                        status_code=403,
                        content={
                            "code": "CSRF_TOKEN_INVALID",
                            "message": "CSRF token is invalid or expired",
                            "data": None,
                        },
                    )

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
    return {
        "success": True,
        "code": 0,
        "message": "操作成功",
        "data": {"status": "healthy", "service": "MyStocks API"},
        "request_id": "test",
    }


@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "service": "MyStocks API"}


@app.get("/api/csrf-token")
async def get_csrf_token():
    """获取CSRF Token"""
    token = csrf_manager.generate_token()
    return {
        "success": True,
        "data": {
            "csrf_token": token,
            "token_type": "Bearer",
            "expires_in": csrf_manager.token_timeout,
        },
        "message": "CSRF token生成成功",
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/docs")
async def docs():
    """Swagger UI"""
    return {"message": "Swagger UI documentation"}


@app.get("/api/redoc")
async def redoc():
    """ReDoc"""
    return {"message": "ReDoc documentation"}


@app.get("/api/socketio-status")
async def socketio_status():
    """Socket.IO status"""
    return {"success": True, "data": {"status": "connected"}}


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


@app.get("/api/data/stock/{symbol}")
async def get_stock_data(symbol: str):
    """获取股票数据"""
    return {
        "success": True,
        "data": {
            "symbol": symbol,
            "name": f"股票{symbol}",
            "price": 10.5,
            "change": 0.5,
        },
    }


@app.get("/api/data/kline/{symbol}")
async def get_kline_data(symbol: str, interval: str = "1d", limit: int = 100):
    """获取K线数据"""
    return {
        "success": True,
        "data": [
            {"date": "2025-01-01", "open": 10.0, "high": 10.5, "low": 9.8, "close": 10.2, "volume": 1000000}
            for _ in range(min(limit, 100))
        ],
    }


@app.get("/api/data/realtime/{symbol}")
async def get_realtime_data(symbol: str):
    """获取实时数据"""
    return {
        "success": True,
        "data": {
            "symbol": symbol,
            "price": 10.5,
            "change": 0.5,
            "timestamp": "2025-12-29 20:00:00",
        },
    }


@app.get("/api/data/batch-realtime")
async def get_batch_realtime(symbols: str):
    """批量获取实时数据"""
    symbol_list = symbols.split(",") if symbols else []
    return {
        "success": True,
        "data": [{"symbol": s, "price": 10.5, "change": 0.5, "timestamp": "2025-12-29 20:00:00"} for s in symbol_list],
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


@app.get("/api/indicators/{symbol}/{indicator}")
async def get_indicator(symbol: str, indicator: str):
    """获取技术指标"""
    return {
        "success": True,
        "data": {
            "symbol": symbol,
            "indicator": indicator,
            "value": 0.5,
        },
    }


@app.get("/api/indicators/{symbol}/all")
async def get_all_indicators(symbol: str):
    """获取所有指标"""
    return {
        "success": True,
        "data": {
            "symbol": symbol,
            "indicators": {
                "MACD": {"value": 0.5},
                "RSI": {"value": 60.0},
                "KDJ": {"value": 0.7},
                "BOLL": {"value": 10.5},
            },
        },
    }


@app.get("/api/technical-analysis/{symbol}")
async def get_technical_analysis(symbol: str):
    """获取技术分析"""
    return {
        "success": True,
        "data": {
            "symbol": symbol,
            "trend": "bullish",
            "recommendation": "买入",
        },
    }


@app.get("/api/cache/stats")
async def get_cache_stats():
    """获取缓存统计"""
    return {
        "success": True,
        "data": {
            "hits": 1000,
            "misses": 100,
            "hit_rate": 0.91,
        },
    }


@app.get("/api/cache/info")
async def get_cache_info():
    """获取缓存信息"""
    return {
        "success": True,
        "data": {
            "total_items": 500,
            "total_size": "10MB",
            "max_size": "100MB",
        },
    }


@app.delete("/api/cache")
async def clear_cache():
    """清除缓存"""
    return {
        "success": True,
        "data": None,
        "message": "缓存已清除",
    }


@app.get("/api/strategies")
async def get_strategies():
    """获取策略列表"""
    return {
        "success": True,
        "data": [
            {"id": "value", "name": "价值策略", "description": "基于价值投资"},
            {"id": "growth", "name": "成长策略", "description": "基于成长性"},
            {"id": "balanced", "name": "平衡策略", "description": "平衡配置"},
        ],
    }


@app.post("/api/strategy/execute")
async def execute_strategy(request_data: dict):
    """执行策略"""
    strategy_id = request_data.get("strategy_id")
    return {
        "success": True,
        "data": {
            "strategy_id": strategy_id,
            "results": [
                {"symbol": "000001", "score": 85.5},
                {"symbol": "000002", "score": 80.3},
            ],
        },
        "message": "策略执行成功",
    }


@app.get("/api/strategy/{strategy_id}/result")
async def get_strategy_result(strategy_id: str):
    """获取策略结果"""
    return {
        "success": True,
        "data": {
            "strategy_id": strategy_id,
            "results": [
                {"symbol": "000001", "score": 85.5},
                {"symbol": "000002", "score": 80.3},
            ],
        },
    }


if __name__ == "__main__":
    print("🚀 启动 MyStocks 简化版后端服务...")
    print("📍 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, log_level="info")
