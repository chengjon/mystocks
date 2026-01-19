from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseValidator(ABC):
    """验证器基类"""

    @abstractmethod
    def validate(self, data: Any, rules: List[str]) -> Dict[str, Any]:
        """
        执行验证

        Args:
            data: 待验证数据（DataFrame or GPU DataFrame）
            rules: 需要执行的规则列表

        Returns:
            验证结果，包含异常行的索引或掩码
        """
        pass
