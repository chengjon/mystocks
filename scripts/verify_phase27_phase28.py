#!/usr/bin/env python3
"""
API验证脚本 - Phase 2.7 & 2.8
Technical Analysis API & Monitoring API
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Any, List

# ==================== 配置 ====================

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "dev-mock-token-for-development"

headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"}

# ==================== 验证函数 ====================


class APIValidator:
    """API验证器"""

    def __init__(self):
        self.results = []

    def test_endpoint(
        self,
        api_name: str,
        endpoint: str,
        method: str = "GET",
        params: Dict = None,
        data: Dict = None,
        expected_fields: List[str] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        验证API端点

        Args:
            api_name: API名称
            endpoint: 端点路径
            method: HTTP方法
            params: URL参数
            data: 请求体数据
            expected_fields: 预期返回的字段
            timeout: 超时时间(秒)

        Returns:
            验证结果字典
        """
        url = f"{BASE_URL}{endpoint}"
        result = {
            "api_name": api_name,
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "http_status": None,
            "response_time_ms": None,
            "error": None,
            "data_size": 0,
            "expected_fields_found": [],
        }

        try:
            # Layer 3: 性能验证 - 记录开始时间
            start_time = time.time()

            # Layer 1: 端点存在性验证
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            # 计算响应时间
            response_time_ms = (time.time() - start_time) * 1000
            result["response_time_ms"] = round(response_time_ms, 2)
            result["http_status"] = response.status_code

            # Layer 1: 检查HTTP状态码
            if response.status_code in [404, 405]:
                result["status"] = "FAILED"
                result["error"] = f"端点不存在或方法不支持 (HTTP {response.status_code})"
                return result
            elif response.status_code >= 500:
                result["status"] = "FAILED"
                result["error"] = f"服务器内部错误 (HTTP {response.status_code})"
                return result

            # Layer 2: 契约格式验证
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                result["status"] = "FAILED"
                result["error"] = f"响应不是有效的JSON: {e}"
                return result

            # 检查统一响应格式
            if "code" in response_data or "success" in response_data:
                result["status"] = "SUCCESS"
            else:
                result["status"] = "PARTIAL"
                result["error"] = "响应缺少code或success字段"

            # Layer 4: 数据完整性验证
            data_field = response_data.get("data", response_data)

            if isinstance(data_field, (list, dict)):
                if isinstance(data_field, list):
                    result["data_size"] = len(data_field)
                elif isinstance(data_field, dict):
                    result["data_size"] = len(data_field)

                # 检查预期字段
                if expected_fields:
                    if isinstance(data_field, list) and len(data_field) > 0:
                        sample = data_field[0]
                    elif isinstance(data_field, dict):
                        sample = data_field
                    else:
                        sample = {}

                    for field in expected_fields:
                        if field in sample:
                            result["expected_fields_found"].append(field)

            # 保存响应数据用于调试
            result["response_sample"] = str(response_data)[:500]

        except requests.exceptions.Timeout:
            result["status"] = "FAILED"
            result["error"] = f"请求超时 (>{timeout}秒)"
        except requests.exceptions.ConnectionError:
            result["status"] = "FAILED"
            result["error"] = "连接失败"
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)

        self.results.append(result)
        return result

    def print_result(self, result: Dict[str, Any]):
        """打印验证结果"""
        status_icon = "✅" if result["status"] == "SUCCESS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
        print(f"\n{status_icon} {result['api_name']}")
        print(f"   端点: {result['method']} {result['endpoint']}")
        print(f"   HTTP状态: {result['http_status']}")
        print(f"   响应时间: {result['response_time_ms']}ms")
        print(f"   数据量: {result['data_size']}")

        if result["error"]:
            print(f"   错误: {result['error']}")

        if result["expected_fields_found"]:
            print(f"   预期字段: {', '.join(result['expected_fields_found'])}")

    def generate_report(self) -> str:
        """生成验证报告"""
        report_lines = [
            "# API验证报告 - Phase 2.7 & 2.8",
            f"\n**验证时间**: {datetime.now().isoformat()}",
            f"**API总数**: {len(self.results)}",
            "\n---\n",
            "## 验证结果汇总\n",
            f"| API名称 | 状态 | HTTP状态 | 响应时间 | 数据量 |",
            f"|---------|------|----------|----------|--------|",
        ]

        for result in self.results:
            status_emoji = "✅" if result["status"] == "SUCCESS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
            report_lines.append(
                f"| {result['api_name']} | {status_emoji} {result['status']} | {result['http_status']} | {result['response_time_ms']}ms | {result['data_size']} |"
            )

        # 统计信息
        success_count = sum(1 for r in self.results if r["status"] == "SUCCESS")
        partial_count = sum(1 for r in self.results if r["status"] == "PARTIAL")
        failed_count = sum(1 for r in self.results if r["status"] == "FAILED")

        report_lines.extend(
            [
                "\n---\n",
                "## 统计信息\n",
                f"- ✅ 成功: {success_count}",
                f"- ⚠️ 部分成功: {partial_count}",
                f"- ❌ 失败: {failed_count}",
                f"- 📊 成功率: {success_count / len(self.results) * 100:.1f}%",
            ]
        )

        # 错误详情
        failed_results = [r for r in self.results if r["status"] in ["FAILED", "PARTIAL"]]
        if failed_results:
            report_lines.extend(
                [
                    "\n---\n",
                    "## 错误详情\n",
                ]
            )
            for result in failed_results:
                report_lines.extend(
                    [
                        f"\n### {result['api_name']}",
                        f"- **状态**: {result['status']}",
                        f"- **端点**: {result['method']} {result['endpoint']}",
                        f"- **HTTP状态**: {result['http_status']}",
                        f"- **错误**: {result['error']}",
                        f"- **响应时间**: {result['response_time_ms']}ms",
                    ]
                )

        return "\n".join(report_lines)


# ==================== Phase 2.7: Technical Analysis API ====================


def verify_phase27(validator: APIValidator, test_symbol: str = "600000.SH"):
    """验证Phase 2.7: Technical Analysis API"""

    print("=" * 80)
    print("Phase 2.7: Technical Analysis API (7个API)")
    print("=" * 80)

    # API 2.7.1: 技术指标
    validator.test_endpoint(
        api_name="2.7.1 - 技术指标",
        endpoint=f"/api/v1/technical/{test_symbol}/indicators",
        method="GET",
        params={"limit": 100},
        expected_fields=["symbol", "latest_price", "trend", "momentum", "volatility"],
    )

    # API 2.7.2: 批量指标
    validator.test_endpoint(
        api_name="2.7.2 - 批量指标",
        endpoint="/api/v1/technical/batch/indicators",
        method="POST",
        data={"symbols": ["600000.SH", "600519.SH"], "indicators": ["MA", "MACD", "RSI"], "period": "daily"},
        expected_fields=["results"],
    )

    # API 2.7.3: 趋势分析
    validator.test_endpoint(
        api_name="2.7.3 - 趋势分析",
        endpoint=f"/api/v1/technical/{test_symbol}/trend",
        method="GET",
        params={"period": "daily", "ma_periods": [5, 10, 20, 60]},
        expected_fields=["ma5", "ma10", "ma20", "ma60"],
    )

    # API 2.7.4: 动量指标
    validator.test_endpoint(
        api_name="2.7.4 - 动量指标",
        endpoint=f"/api/v1/technical/{test_symbol}/momentum",
        method="GET",
        params={"period": "daily"},
        expected_fields=["rsi", "kdj", "cci"],
    )

    # API 2.7.5: 波动率
    validator.test_endpoint(
        api_name="2.7.5 - 波动率",
        endpoint=f"/api/v1/technical/{test_symbol}/volatility",
        method="GET",
        params={"period": "daily"},
        expected_fields=["bb_upper", "bb_middle", "bb_lower", "atr"],
    )

    # API 2.7.6: 成交量分析
    validator.test_endpoint(
        api_name="2.7.6 - 成交量分析",
        endpoint=f"/api/v1/technical/{test_symbol}/volume",
        method="GET",
        params={"period": "daily"},
        expected_fields=["obv", "vwap", "volume_ma5"],
    )

    # API 2.7.7: 交易信号
    validator.test_endpoint(
        api_name="2.7.7 - 交易信号",
        endpoint=f"/api/v1/technical/{test_symbol}/signals",
        method="GET",
        params={"period": "daily"},
        expected_fields=["buy_signals", "sell_signals", "signals_count"],
    )


# ==================== Phase 2.8: Monitoring API ====================


def verify_phase28(validator: APIValidator, test_symbol: str = "600000.SH"):
    """验证Phase 2.8: Monitoring API"""

    print("\n" + "=" * 80)
    print("Phase 2.8: Monitoring API (6个API)")
    print("=" * 80)

    # API 2.8.1: 监控摘要
    validator.test_endpoint(
        api_name="2.8.1 - 监控摘要",
        endpoint="/api/v1/monitoring/summary",
        method="GET",
        expected_fields=["total_symbols", "active_rules", "alert_count"],
    )

    # API 2.8.2: 实时监控
    validator.test_endpoint(
        api_name="2.8.2 - 实时监控",
        endpoint="/api/v1/monitoring/realtime",
        method="GET",
        params={"limit": 10},
        expected_fields=["symbol", "price", "change", "signals"],
    )

    # API 2.8.3: 告警列表
    validator.test_endpoint(
        api_name="2.8.3 - 告警列表",
        endpoint="/api/v1/monitoring/alerts",
        method="GET",
        params={"limit": 10, "is_read": False},
        expected_fields=["symbol", "alert_type", "alert_level", "created_at"],
    )

    # API 2.8.4: 龙虎榜
    validator.test_endpoint(
        api_name="2.8.4 - 龙虎榜",
        endpoint="/api/v1/monitoring/dragon-tiger",
        method="GET",
        params={"limit": 10},
        expected_fields=["date", "stock_name", "department", "amount"],
    )

    # API 2.8.5: 停止监控
    validator.test_endpoint(
        api_name="2.8.5 - 停止监控",
        endpoint="/api/v1/monitoring/control/stop",
        method="POST",
        data={"symbol": test_symbol},
        expected_fields=["success", "message"],
    )

    # API 2.8.6: 开始监控
    validator.test_endpoint(
        api_name="2.8.6 - 开始监控",
        endpoint="/api/v1/monitoring/control/start",
        method="POST",
        data={
            "symbol": test_symbol,
            "monitoring_type": "price",
            "conditions": {"price_limit": {"above": 100.0, "below": 90.0}},
        },
        expected_fields=["success", "monitoring_id"],
    )


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 API验证 - Phase 2.7 & 2.8")
    print("=" * 80)

    # 创建验证器
    validator = APIValidator()

    # 执行Phase 2.7验证
    test_symbol = "600000.SH"
    verify_phase27(validator, test_symbol)

    # 执行Phase 2.8验证
    verify_phase28(validator, test_symbol)

    # 打印所有结果
    print("\n" + "=" * 80)
    print("验证结果汇总")
    print("=" * 80)

    for result in validator.results:
        validator.print_result(result)

    # 生成报告
    report = validator.generate_report()

    # 保存报告
    report_path = "/opt/claude/mystocks_spec/docs/reports/api_verification/PHASE_2.7_2.8_VERIFICATION_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n" + "=" * 80)
    print(f"✅ 验证报告已保存: {report_path}")
    print("=" * 80)

    # 打印报告预览
    print("\n报告预览:")
    print(report[:1000])


if __name__ == "__main__":
    main()
