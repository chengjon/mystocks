"""适配器加载器 - 统一管理外部适配器导入

解决问题：
- 移除硬编码的 sys.path.insert()
- 提供统一的适配器导入接口
- 支持适配器健康检查
- 支持依赖注入

使用方式：
    from app.core.adapter_loader import get_akshare_adapter, get_tdx_adapter

    ak = get_akshare_adapter()
    tdx = get_tdx_adapter()
"""

import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)

# 自动计算项目根目录（向上3级：app -> backend -> web -> mystocks_spec）
BACKEND_DIR = Path(__file__).parent.parent  # app/
WEB_DIR = BACKEND_DIR.parent  # web/
PROJECT_ROOT = WEB_DIR.parent  # mystocks_spec/

# 确保项目根目录在 sys.path 中（只添加一次）
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class AdapterLoader:
    """适配器加载器单例"""

    _adapters: Dict[str, Any] = {}
    _health_status: Dict[str, Dict] = {}

    @classmethod
    @lru_cache(maxsize=1)
    def get_akshare_adapter(cls):
        """获取 AkShare 适配器实例（单例）"""
        if "akshare" not in cls._adapters:
            try:
                from src.adapters.akshare_adapter import AkshareDataSource

                cls._adapters["akshare"] = AkshareDataSource()
                cls._health_status["akshare"] = {
                    "healthy": True,
                    "status": "initialized",
                }
                logger.info("✅ AkShare adapter loaded successfully")
            except Exception as e:
                logger.error("❌ Failed to load AkShare adapter: %(e)s")
                cls._health_status["akshare"] = {
                    "healthy": False,
                    "status": "failed",
                    "error": str(e),
                }
                raise
        return cls._adapters["akshare"]

    @classmethod
    @lru_cache(maxsize=1)
    def get_tdx_adapter(cls):
        """获取 TDX 适配器实例（单例）"""
        if "tdx" not in cls._adapters:
            try:
                from src.adapters.tdx import TdxDataSource

                cls._adapters["tdx"] = TdxDataSource()
                cls._health_status["tdx"] = {"healthy": True, "status": "initialized"}
                logger.info("✅ TDX adapter loaded successfully")
            except Exception as e:
                logger.error("❌ Failed to load TDX adapter: %(e)s")
                cls._health_status["tdx"] = {
                    "healthy": False,
                    "status": "failed",
                    "error": str(e),
                }
                raise
        return cls._adapters["tdx"]

    @classmethod
    @lru_cache(maxsize=1)
    def get_financial_adapter(cls):
        """获取 Financial 适配器实例（单例）"""
        if "financial" not in cls._adapters:
            try:
                from src.adapters.financial_adapter import FinancialDataSource

                cls._adapters["financial"] = FinancialDataSource()
                cls._health_status["financial"] = {
                    "healthy": True,
                    "status": "initialized",
                }
                logger.info("✅ Financial adapter loaded successfully")
            except Exception as e:
                logger.error("❌ Failed to load Financial adapter: %(e)s")
                cls._health_status["financial"] = {
                    "healthy": False,
                    "status": "failed",
                    "error": str(e),
                }
                raise
        return cls._adapters["financial"]

    @classmethod
    def get_health_status(cls, adapter_name: Optional[str] = None) -> Dict:
        """获取适配器健康状态"""
        if adapter_name:
            return cls._health_status.get(adapter_name, {"healthy": False, "status": "unknown"})
        return cls._health_status

    @classmethod
    def check_adapter_health(cls, adapter_name: str) -> bool:
        """检查适配器是否健康"""
        try:
            if adapter_name == "akshare":
                adapter = cls.get_akshare_adapter()
            elif adapter_name == "tdx":
                adapter = cls.get_tdx_adapter()
            elif adapter_name == "financial":
                adapter = cls.get_financial_adapter()
            else:
                return False

            # 执行健康检查（如果适配器有 health_check 方法）
            if hasattr(adapter, "health_check"):
                return adapter.health_check()

            # 默认：如果能加载就认为健康
            return True
        except Exception:
            logger.error("❌ Health check failed for %(adapter_name)s: %(e)s")
            return False


# 便捷函数（向后兼容旧代码）
def get_akshare_adapter():
    """获取 AkShare 适配器（便捷函数）"""
    return AdapterLoader.get_akshare_adapter()


def get_tdx_adapter():
    """获取 TDX 适配器（便捷函数）"""
    return AdapterLoader.get_tdx_adapter()


def get_financial_adapter():
    """获取 Financial 适配器（便捷函数）"""
    return AdapterLoader.get_financial_adapter()


def get_adapter_health_status(adapter_name: Optional[str] = None) -> Dict:
    """获取适配器健康状态"""
    return AdapterLoader.get_health_status(adapter_name)


def check_all_adapters() -> Dict[str, bool]:
    """检查所有适配器健康状态"""
    return {
        "akshare": AdapterLoader.check_adapter_health("akshare"),
        "tdx": AdapterLoader.check_adapter_health("tdx"),
        "financial": AdapterLoader.check_adapter_health("financial"),
    }


# 初始化日志
logger.info("📁 Project root: %(PROJECT_ROOT)s")
logger.info("📁 Adapters directory: {PROJECT_ROOT / 'adapters'}")
