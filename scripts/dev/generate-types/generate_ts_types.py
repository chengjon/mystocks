#!/usr/bin/env python3
"""Compatibility wrapper for canonical frontend type generation.

The repository standardizes frontend API type generation on:

    python scripts/generate_frontend_types.py

This legacy path is kept only so older automation gets a clear, compatible
entrypoint while the implementation remains single-sourced.
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_RELATIVE_PATH = "scripts/generate_frontend_types.py"
LEGACY_FLAGS = ("--contracts-dir", "--output-dir", "--tool")


def _first_legacy_flag(args: list[str]) -> str | None:
    for arg in args:
        for flag in LEGACY_FLAGS:
            if arg == flag or arg.startswith(f"{flag}="):
                return flag
    return None


def _ensure_project_root_on_path() -> None:
    project_root = str(PROJECT_ROOT)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def _print_legacy_flag_error(flag: str) -> None:
    print(
        f"{Path(__file__).as_posix()} is a compatibility wrapper. "
        f"Use `python {CANONICAL_RELATIVE_PATH}`. "
        f"Legacy flag `{flag}` is no longer supported by the canonical frontend type generation path.",
        file=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    legacy_flag = _first_legacy_flag(args)
    if legacy_flag is not None:
        _print_legacy_flag_error(legacy_flag)
        return 2

    _ensure_project_root_on_path()
    from scripts import generate_frontend_types

    original_argv = sys.argv[:]
    sys.argv = [str(PROJECT_ROOT / CANONICAL_RELATIVE_PATH), *args]
    try:
        result = generate_frontend_types.main()
    except SystemExit as exc:
        if exc.code is None:
            return 0
        if isinstance(exc.code, int):
            return exc.code
        print(exc.code, file=sys.stderr)
        return 1
    finally:
        sys.argv = original_argv

    return 0 if result is None else int(result)


if __name__ == "__main__":
    raise SystemExit(main())
