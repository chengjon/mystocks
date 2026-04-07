"""数据访问层 - 向后兼容入口"""
import warnings
warnings.warn(
    "src.data_access is a compatibility shim. Import directly from src.data_access.{module} instead.",
    DeprecationWarning,
    stacklevel=2
)

# Compatibility shim: keep the legacy module path while routing all exports
# to the canonical src.data_access package.
from src.data_access import *  # noqa: F401, F403
