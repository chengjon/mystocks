#!/bin/bash
# MyStocks Backend启动脚本

# 设置PYTHONPATH
export PYTHONPATH=/opt/claude/mystocks_spec/web/backend:/opt/claude/mystocks_spec

# 启动uvicorn
cd /opt/claude/mystocks_spec/web/backend
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
