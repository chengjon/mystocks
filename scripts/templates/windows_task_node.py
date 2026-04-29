"""Compatibility wrapper for the repo-owned Windows qmt reference service."""

from __future__ import annotations

from scripts.windows_qmt_agent.app import app
from scripts.windows_qmt_agent.main import main

__all__ = ["app", "main"]


if __name__ == "__main__":
    main()
