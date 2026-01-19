#!/usr/bin/env python3
"""
MyStocks Backend Startup Script for PM2
This script properly sets up the Python path and starts uvicorn
"""

import os
import sys


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    backend_dir = os.path.dirname(os.path.abspath(__file__))

    sys.path.insert(0, project_root)
    sys.path.insert(0, backend_dir)
    os.environ["PYTHONPATH"] = f"{project_root}:{backend_dir}"

    os.chdir(backend_dir)

    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

    print(f"🚀 Starting MyStocks backend on port 8000...")
    print(f"📁 Project root: {project_root}")
    print(f"📁 Backend dir: {backend_dir}")
    print(f"🐍 Python path: {os.environ.get('PYTHONPATH')}")

    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
