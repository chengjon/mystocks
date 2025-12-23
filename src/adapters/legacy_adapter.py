"""
遗留适配器 - 模拟复杂遗留代码
用于演示AI测试优化器在重构支持中的应用
"""

from typing import Dict


class LegacyAdapter:
    """遗留适配器 - 需要重构的复杂代码"""

    def __init__(self):
        self.config = {}
        self.connection = None
        self.cache = {}
        self.metrics = {}

    def process_request(self, request_data: Dict) -> Dict:
        """复杂的方法，需要重构"""
        # 模拟复杂的业务逻辑
        try:
            # 验证输入
            if not request_data:
                raise ValueError("请求数据为空")

            if "type" not in request_data:
                raise ValueError("缺少请求类型")

            # 复杂的条件判断
            if request_data["type"] == "data_fetch":
                if "symbol" not in request_data:
                    raise ValueError("缺少symbol参数")

                if request_data["symbol"].startswith("6") or request_data[
                    "symbol"
                ].startswith("0"):
                    exchange = "SZSE"
                elif request_data["symbol"].startswith("6"):
                    exchange = "SSE"
                elif request_data["symbol"].startswith("3"):
                    exchange = "SZSE"
                else:
                    exchange = "OTHER"

                # 模拟数据处理
                result = self._process_data_fetch(request_data, exchange)

            elif request_data["type"] == "analysis":
                if "analysis_type" not in request_data:
                    raise ValueError("缺少analysis_type参数")

                result = self._process_analysis(request_data)

            elif request_data["type"] == "export":
                result = self._process_export(request_data)

            else:
                raise ValueError(f"不支持的请求类型: {request_data['type']}")

            # 后处理
            if result.get("success", False):
                self._update_metrics(request_data["type"], True)
            else:
                self._update_metrics(request_data["type"], False)

            return result

        except Exception as e:
            self._update_metrics("error", False)
            return {
                "success": False,
                "error": str(e),
                "error_code": self._get_error_code(e),
            }

    def _process_data_fetch(self, data: Dict, exchange: str) -> Dict:
        """数据处理方法 - 复杂度较高"""
        # 模拟数据获取
        try:
            # 检查缓存
            cache_key = f"{exchange}_{data['symbol']}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                # 检查缓存是否过期
                if time.time() - cached_data["timestamp"] < 300:  # 5分钟缓存
                    return {
                        "success": True,
                        "data": cached_data["data"],
                        "from_cache": True,
                    }

            # 模拟从不同交易所获取数据
            if exchange == "SZSE":
                data_result = self._fetch_from_szse(data["symbol"])
            elif exchange == "SSE":
                data_result = self._fetch_from_sse(data["symbol"])
            else:
                data_result = self._fetch_from_general(data["symbol"])

            # 处理数据
            processed_data = self._transform_data(data_result)

            # 更新缓存
            self.cache[cache_key] = {"data": processed_data, "timestamp": time.time()}

            return {"success": True, "data": processed_data, "from_cache": False}

        except Exception as e:
            return {"success": False, "error": f"数据处理失败: {str(e)}"}

    def _fetch_from_szse(self, symbol: str) -> Dict:
        """模拟从深交所获取数据"""
        # 复杂的API调用逻辑
        return {"symbol": symbol, "exchange": "SZSE", "price": 10.5, "volume": 1000000}

    def _fetch_from_sse(self, symbol: str) -> Dict:
        """模拟从上交所获取数据"""
        return {"symbol": symbol, "exchange": "SSE", "price": 15.2, "volume": 500000}

    def _fetch_from_general(self, symbol: str) -> Dict:
        """模拟从通用数据源获取数据"""
        return {"symbol": symbol, "exchange": "OTHER", "price": 12.8, "volume": 200000}

    def _transform_data(self, raw_data: Dict) -> Dict:
        """数据转换"""
        # 复杂的数据转换逻辑
        transformed = raw_data.copy()

        # 添加计算字段
        if "price" in raw_data:
            transformed["price_change"] = raw_data["price"] * 0.01
            transformed["price_change_percent"] = 1.0

        return transformed

    def _process_analysis(self, data: Dict) -> Dict:
        """分析处理"""
        # 复杂的分析逻辑
        analysis_type = data["analysis_type"]

        if analysis_type == "technical":
            return self._technical_analysis(data)
        elif analysis_type == "fundamental":
            return self._fundamental_analysis(data)
        else:
            raise ValueError(f"不支持的分析类型: {analysis_type}")

    def _technical_analysis(self, data: Dict) -> Dict:
        """技术分析"""
        return {"type": "technical", "signal": "BUY", "confidence": 0.85}

    def _fundamental_analysis(self, data: Dict) -> Dict:
        """基本面分析"""
        return {"type": "fundamental", "rating": "BUY", "score": 8.5}

    def _process_export(self, data: Dict) -> Dict:
        """导出处理"""
        return {
            "type": "export",
            "format": data.get("format", "json"),
            "status": "completed",
        }

    def _update_metrics(self, operation: str, success: bool):
        """更新指标"""
        if operation not in self.metrics:
            self.metrics[operation] = {"total": 0, "success": 0, "failed": 0}

        self.metrics[operation]["total"] += 1

        if success:
            self.metrics[operation]["success"] += 1
        else:
            self.metrics[operation]["failed"] += 1

    def _get_error_code(self, error: Exception) -> str:
        """获取错误代码"""
        if isinstance(error, ValueError):
            return "INVALID_INPUT"
        elif isinstance(error, KeyError):
            return "MISSING_PARAMETER"
        else:
            return "UNKNOWN_ERROR"

    def get_metrics(self) -> Dict:
        """获取指标"""
        return self.metrics.copy()
