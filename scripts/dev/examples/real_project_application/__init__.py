"""real_project_application 拆分包"""
from .real_project_application import RealProjectApplication  # noqa: F401
from .utils import main  # noqa: F401

__all__ = ['RealProjectApplication', 'main']
