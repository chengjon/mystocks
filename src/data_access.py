"""数据访问层 - 向后兼容入口"""

# Compatibility shim: keep the legacy module path while routing all exports
# to the canonical src.data_access package.
from src.data_access import *  # noqa: F401, F403
