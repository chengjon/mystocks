from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    负责数据源适配器的注册、查找和管理。
    """

    def __init__(self):
        self._adapters: Dict[str, Any] = {}

    def register(self, name: str, adapter: Any):
        """注册适配器"""
        if name in self._adapters:
            logger.warning(f"Adapter '{name}' already registered, overwriting.")
        self._adapters[name] = adapter
        logger.info(f"Registered adapter: {name}")

    def unregister(self, name: str) -> bool:
        """注销适配器"""
        if name in self._adapters:
            del self._adapters[name]
            logger.info(f"Unregistered adapter: {name}")
            return True
        return False

    def get(self, name: str) -> Optional[Any]:
        """获取适配器"""
        return self._adapters.get(name)

    def list_all(self) -> List[str]:
        """列出所有适配器名称"""
        return list(self._adapters.keys())
