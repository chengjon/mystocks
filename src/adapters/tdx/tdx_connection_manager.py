"""
Compatibility shim for TDX connection manager.

The implementation lives in src.adapters.tdx_connection_manager; this module
keeps the legacy import path used by tests and older code.
"""

from src.adapters.tdx_connection_manager import TdxConnectionManager

__all__ = ["TdxConnectionManager"]
