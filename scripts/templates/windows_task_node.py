"""
MyStocks Windows Task Node (Provider)
用于在 Windows 环境下封装 Wind, Choice, MiniQMT 接口并回填数据至 NAS。
"""

import os
import uuid
import time
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, BackgroundTasks
import uvicorn
import pandas as pd
from sqlalchemy import create_engine

# ==================== 配置区 (建议通过 .env 或 环境变量管理) ====================
NODE_NAME = os.getenv("NODE_NAME", "WIN-QUANT-01")
NAS_POSTGRES_URL = os.getenv("NAS_POSTGRES_URL", "postgresql://postgres:password@localhost:5438/mystocks")
NAS_TDENGINE_REST = os.getenv("NAS_TDENGINE_REST", "http://root:password@localhost:6041")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(f"Node-{NODE_NAME}")

app = FastAPI(title=f"MyStocks Task Provider [{NODE_NAME}]")

# ==================== 数据模型 ====================
class TaskRequest(BaseModel):
    method: str  # 格式如: "wind_wsd", "qmt_get_position", "choice_css"
    params: Dict[str, Any]
    write_to_nas: bool = True

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    node: str

# ==================== 接口实现区 (按需安装对应的 SDK) ====================

def fetch_wind_data(method: str, params: Dict[str, Any]) -> pd.DataFrame:
    """Wind 数据采集实现 (需安装 WindPy)"""
    # from WindPy import w
    # w.start()
    logger.info(f"Executing Wind task: {method} with {params}")
    # 模拟数据
    return pd.DataFrame([{"symbol": params.get("symbol"), "price": 100.5, "source": "Wind"}])

def fetch_qmt_data(method: str, params: Dict[str, Any]) -> pd.DataFrame:
    """MiniQMT 实时数据实现 (需安装 xtquant)"""
    # from xtquant import xtdata
    logger.info(f"Executing QMT task: {method}")
    return pd.DataFrame([{"symbol": params.get("symbol"), "pos": 1000, "source": "MiniQMT"}])

def fetch_choice_data(method: str, params: Dict[str, Any]) -> pd.DataFrame:
    """Choice 数据采集实现"""
    logger.info(f"Executing Choice task: {method}")
    return pd.DataFrame([{"symbol": params.get("symbol"), "eps": 1.2, "source": "Choice"}])

# ==================== 核心逻辑 ====================

def process_and_store(task_id: str, request: TaskRequest):
    """后台执行任务并回填 NAS"""
    try:
        # 1. 路由至对应的 SDK
        if request.method.startswith("wind"):
            df = fetch_wind_data(request.method, request.params)
        elif request.method.startswith("qmt"):
            df = fetch_qmt_data(request.method, request.params)
        elif request.method.startswith("choice"):
            df = fetch_choice_data(request.method, request.params)
        else:
            raise ValueError(f"Unknown method prefix: {request.method}")

        # 2. 写入 NAS 数据库 (PostgreSQL 示例)
        if request.write_to_nas and not df.empty:
            engine = create_engine(NAS_POSTGRES_URL)
            # 根据业务逻辑自动匹配表名
            table_name = "remote_fetch_cache"
            df.to_sql(table_name, con=engine, if_exists="append", index=False)
            logger.info(f"✅ Task {task_id} data written to NAS table: {table_name}")

    except Exception as e:
        logger.error(f"❌ Task {task_id} failed: {str(e)}")

# ==================== API 端点 ====================

@app.get("/health")
async def health():
    return {
        "status": "online", 
        "node": NODE_NAME, 
        "time": datetime.now().isoformat(),
        "capabilities": ["wind", "qmt", "choice"]
    }

@app.post("/api/v1/task/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    # 将耗时的采集任务放入后台，立即返回 HTTP 202
    background_tasks.add_task(process_and_store, task_id, request)
    
    return TaskResponse(
        task_id=task_id,
        status="accepted",
        message="Task started in background",
        node=NODE_NAME
    )

if __name__ == "__main__":
    # 建议生产环境使用: uvicorn windows_task_node:app --host 0.0.0.0 --port 8001
    uvicorn.run(app, host="0.0.0.0", port=8001)
