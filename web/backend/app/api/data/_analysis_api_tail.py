"""Analysis API tail helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


class AnalysisDataServiceTailMixin:
    """Shared tail helpers for `AnalysisDataService`."""

    async def validate_data(self, data: Any, data_type: str) -> Dict:
        """验证数据质量"""
        try:
            result = {
                "is_valid": True,
                "data_type": data_type,
                "validation_time": datetime.now().isoformat(),
                "errors": [],
                "warnings": [],
            }

            if data_type == "price":
                if not data or data <= 0:
                    result["is_valid"] = False
                    result["errors"].append("价格数据无效")

            elif data_type == "volume":
                if not data or data <= 0:
                    result["is_valid"] = False
                    result["errors"].append("成交量数据无效")

            elif data_type == "ratio":
                if not data or data <= 0:
                    result["is_valid"] = False
                    result["errors"].append("比率数据无效")
                elif data == 0:
                    result["warnings"].append("比率为0可能导致除零错误")

            return result

        except Exception as error:
            self.logger.error(f"数据验证失败: {error}")
            return {
                "is_valid": False,
                "data_type": data_type,
                "validation_time": datetime.now().isoformat(),
                "errors": [str(error)],
                "warnings": [],
            }

    def _log_request_start(self, method: str, params: Dict) -> None:
        """记录请求开始"""
        self.logger.info(f"开始{method}: {params}")

    def _log_request_success(self, method: str, result: Dict) -> None:
        """记录请求成功"""
        self.logger.info(f"{method}成功: {result}")

    def _log_request_error(self, method: str, error: Exception) -> None:
        """记录请求错误"""
        self.logger.error(f"{method}失败: {error}")
