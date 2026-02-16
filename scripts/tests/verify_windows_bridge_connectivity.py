"""
WSL2 to Windows Bridge Integration Test
验证从 WSL2 后端触发远程 Windows 节点的任务执行与 NAS 数据回填。
"""

import httpx
import asyncio
import sys
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# 配置对齐
NODES = {
    "WIND_QMT_CHOICE": "http://192.168.123.109:8001",
    "TDX": "http://192.168.123.74:8001"
}
NAS_POSTGRES = "postgresql://postgres:password@localhost:5438/mystocks"

async def test_node_health(name, url):
    print(f"🔍 Testing health for {name} ({url})...")
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            resp = await client.get(f"{url}/health")
            if resp.status_code == 200:
                print(f"  ✅ {name} is ONLINE. Data: {resp.json()}")
                return True
            else:
                print(f"  ❌ {name} returned status {resp.status_code}")
        except Exception as e:
            print(f"  ❌ {name} is UNREACHABLE: {e}")
    return False

async def trigger_mock_task(node_url):
    print(f"
🚀 Triggering mock Wind task on {node_url}...")
    payload = {
        "method": "wind_wsd",
        "params": {"symbol": "000001.SZ", "fields": "close"},
        "write_to_nas": True
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(f"{node_url}/api/v1/task/execute", json=payload)
            if resp.status_code == 200:
                task_data = resp.json()
                print(f"  ✅ Task Accepted! TaskID: {task_data['task_id']}")
                return task_data['task_id']
        except Exception as e:
            print(f"  ❌ Task Trigger Failed: {e}")
    return None

def verify_nas_data():
    print(f"
📥 Verifying data回填 in NAS PostgreSQL...")
    try:
        engine = create_engine(NAS_POSTGRES)
        query = "SELECT * FROM remote_fetch_cache ORDER BY timestamp DESC LIMIT 1"
        df = pd.read_sql(query, engine)
        if not df.empty:
            print(f"  ✅ Data Found in NAS!")
            print(df.iloc[0])
        else:
            print(f"  ⚠️ NAS table exists but no data found yet (task might be processing).")
    except Exception as e:
        print(f"  ❌ Database Access Failed: {e}")

async def main():
    print("=== MyStocks Multi-Node Bridge Integration Test ===
")
    
    # 1. 节点探测
    health_results = []
    for name, url in NODES.items():
        res = await test_node_health(name, url)
        health_results.append(res)
    
    if not any(health_results):
        print("
🛑 No nodes are online. Please start windows_task_node.py on target machines.")
        return

    # 2. 模拟触发 (选择第一个在线节点)
    target_url = NODES["WIND_QMT_CHOICE"]
    task_id = await trigger_mock_task(target_url)
    
    if task_id:
        print("
⏳ Waiting 3 seconds for async task to write to NAS...")
        await asyncio.sleep(3)
        # 3. 校验回填
        verify_nas_data()

if __name__ == "__main__":
    asyncio.run(main())
