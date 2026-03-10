"""Demo helpers for `test_trend_analysis.py`."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import numpy as np


def run_trend_analysis_demo(analyzer_cls, point_cls):
    """运行趋势分析演示并输出日志。"""
    logging.info("📈 演示趋势分析功能")

    analyzer = analyzer_cls()
    success_rates = []
    timestamps = []
    base_rate = 95.0

    for index in range(100):
        timestamp = datetime.now() - timedelta(hours=100 - index)
        trend = -0.05 * index
        noise = np.random.normal(0, 2)
        rate = max(80, min(100, base_rate + trend + noise))
        success_rates.append(rate)
        timestamps.append(timestamp)

    test_success_data = [
        point_cls(timestamp=timestamp, value=value, category="test_success")
        for timestamp, value in zip(timestamps, success_rates)
    ]
    analyzer.add_historical_data("test_success_rate", test_success_data)

    response_times = []
    for index in range(80):
        timestamp = datetime.now() - timedelta(hours=100 - index)
        trend = 2.0 * index
        noise = np.random.normal(0, 10)
        response_time = max(50, 100 + trend + noise)
        response_times.append(response_time)
        timestamps.append(timestamp)

    api_response_data = [
        point_cls(timestamp=timestamp, value=value, category="api_response")
        for timestamp, value in zip(timestamps[:80], response_times)
    ]
    analyzer.add_historical_data("api_response_time", api_response_data)

    logging.info("📊 测试成功率趋势分析:")
    success_result = analyzer.analyze_trend("test_success_rate")
    logging.info(f"  趋势方向: {success_result.direction.value}")
    logging.info(f"  置信度: {success_result.confidence.value}")
    logging.info(f"  斜率: {success_result.slope:.4f}")
    logging.info(f"  R²: {success_result.r_squared:.4f}")
    logging.info(f"  p值: {success_result.p_value:.4f}")
    logging.info(f"  预测下一值: {success_result.prediction:.2f}")
    logging.info(f"  异常值数量: {len(success_result.anomalies)}")
    logging.info(f"  模式数量: {len(success_result.patterns)}")
    logging.info("  洞察:")
    for insight in success_result.insights:
        logging.info(f"    - {insight}")

    logging.info("⚡ API响应时间趋势分析:")
    api_result = analyzer.analyze_trend("api_response_time")
    logging.info(f"  趋势方向: {api_result.direction.value}")
    logging.info(f"  置信度: {api_result.confidence.value}")
    logging.info(f"  斜率: {api_result.slope:.4f}")
    logging.info(f"  R²: {api_result.r_squared:.4f}")
    logging.info(f"  p值: {api_result.p_value:.4f}")
    logging.info(f"  预测下一值: {api_result.prediction:.2f}")
    logging.info("  洞察:")
    for insight in api_result.insights:
        logging.info(f"    - {insight}")

    logging.info("🎨 创建可视化图表:")
    try:
        success_chart = analyzer.create_visualization("test_success_rate")
        logging.info(f"  ✅ 测试成功率图表已生成 (包含 {len(success_chart.get('data', []))} 个数据系列)")

        api_chart = analyzer.create_visualization("api_response_time")
        logging.info(f"  ✅ API响应时间图表已生成 (包含 {len(api_chart.get('data', []))} 个数据系列)")
    except Exception as error:
        logging.info(f"  ❌ 图表生成失败: {error}")

    logging.info("📋 总体趋势摘要:")
    summary = analyzer.get_trend_summary(["test_success_rate", "api_response_time"])
    logging.info(f"  指标数量: {summary['metrics_count']}")
    logging.info(f"  高置信度指标比例: {summary['confidence_ratio']:.2f}")
    logging.info("  总体洞察:")
    for insight in summary["overall_insights"]:
        logging.info(f"    - {insight}")

    logging.info("✅ 趋势分析演示完成")
    return analyzer
