#!/bin/bash
cd /opt/claude/mystocks_spec/web/backend
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload