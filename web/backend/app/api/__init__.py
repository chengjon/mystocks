"""Lightweight API package entrypoint.

Submodules are imported on demand by callers such as ``router_registry``.
Keeping this package init side-effect free avoids startup failures from
optional route dependencies during unrelated imports.
"""

__all__: list[str] = []
