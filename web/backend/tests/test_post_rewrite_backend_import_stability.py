from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_app_main_imports_on_origin_main_recovery_path() -> None:
    env = os.environ.copy()
    env.update(
        {
            "POSTGRESQL_HOST": "localhost",
            "POSTGRESQL_PORT": "5432",
            "POSTGRESQL_USER": "tester",
            "POSTGRESQL_PASSWORD": "tester",
            "POSTGRESQL_DATABASE": "tester",
            "JWT_SECRET_KEY": "test-secret-key",
            "BACKEND_PORT": "8134",
            "BACKEND_BACKUP_PORT": "8135",
            "TESTING": "true",
            "PYTHONPATH": ".:web/backend",
        }
    )

    completed = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
        env=env,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
