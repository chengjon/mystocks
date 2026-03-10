"""AlgorithmService 历史查询方法集。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class AlgorithmServiceHistoryMixin:
    """训练/预测历史查询能力。"""

    async def get_training_history(
        self,
        model_id: Optional[str] = None,
        algorithm_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """获取训练历史记录。"""
        if not self.repository:
            return []

        return await self.repository.list_training_history(model_id, algorithm_type, limit)

    async def get_prediction_history(
        self,
        model_id: Optional[str] = None,
        algorithm_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取预测历史记录。"""
        if not self.repository:
            return []

        return await self.repository.list_prediction_history(model_id, algorithm_type, limit)

    async def get_model_statistics(self) -> Dict[str, Any]:
        """获取模型统计信息。"""
        if not self.repository:
            return {}

        return await self.repository.get_model_statistics()
