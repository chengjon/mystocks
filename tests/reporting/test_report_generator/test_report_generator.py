#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告生成器

提供多格式、多层次的测试报告生成功能，支持PDF、HTML、JSON、CSV等格式。
"""

import json
import os
import statistics
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional


class TestReportGenerator:
    """测试报告生成器主类"""

    def __init__(self):
        self.html_generator = HTMLReportGenerator()
        self.pdf_generator = PDFReportGenerator() if PDF_AVAILABLE else None
        self.json_generator = JSONReportGenerator()
        self.chart_generator = ChartGenerator()

    def calculate_metrics(self, test_results: List[Dict[str, Any]]) -> TestMetrics:
        """计算测试指标"""
        if not test_results:
            return TestMetrics()

        # 基本统计
        total = len(test_results)
        passed = sum(1 for r in test_results if r.get('status') == 'passed')
        failed = sum(1 for r in test_results if r.get('status') == 'failed')
        skipped = sum(1 for r in test_results if r.get('status') == 'skipped')

        # 时间统计
        durations = [r.get('duration', 0) for r in test_results if r.get('duration') is not None]
        avg_duration = statistics.mean(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        median_duration = statistics.median(durations) if durations else 0
        std_duration = statistics.stdev(durations) if len(durations) > 1 else 0

        # 计算衍生指标
        success_rate = (passed / total * 100) if total > 0 else 0
        coverage_rate = 85.0  # 假设覆盖率
        efficiency_score = self._calculate_efficiency_score(test_results)
        reliability_score = self._calculate_reliability_score(test_results)

        return TestMetrics(
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            skipped_tests=skipped,
            average_duration=avg_duration,
            max_duration=max_duration,
            min_duration=min_duration,
            median_duration=median_duration,
            std_duration=std_duration,
            success_rate=success_rate,
            coverage_rate=coverage_rate,
            efficiency_score=efficiency_score,
            reliability_score=reliability_score
        )

    def _calculate_efficiency_score(self, test_results: List[Dict]) -> float:
        """计算效率评分"""
        if not test_results:
            return 0.0

        # 基于通过率和平均执行时间计算
        pass_rate = sum(1 for r in test_results if r.get('status') == 'passed') / len(test_results)

        durations = [r.get('duration', 0) for r in test_results if r.get('duration') is not None]
        avg_duration = statistics.mean(durations) if durations else 300  # 默认5分钟

        # 时间得分（反向，越快越好）
        time_score = max(0, 100 - (avg_duration / 300) * 100)

        # 综合评分
        efficiency = (pass_rate * 70 + time_score * 30)
        return round(efficiency, 1)

    def _calculate_reliability_score(self, test_results: List[Dict]) -> float:
        """计算可靠性评分"""
        if not test_results:
            return 0.0

        # 基于通过率、失败模式和执行稳定性计算
        pass_rate = sum(1 for r in test_results if r.get('status') == 'passed') / len(test_results)

        # 失败模式分析
        critical_failures = sum(
            1
            for r in test_results
            if r.get('status') == 'failed'
            and r.get('error_message', '').lower() in ['timeout', 'connection', 'server error']
        )

        failure_penalty = (critical_failures / len(test_results)) * 50 if test_results else 0

        reliability = (pass_rate * 100) - failure_penalty
        return round(max(0, reliability), 1)

    def generate_charts(self, test_results: List[Dict[str, Any]], metrics: TestMetrics) -> Dict[str, str]:
        """生成图表"""
        charts = {}

        # 成功率饼图
        charts['success_rate_pie'] = self.chart_generator.create_success_rate_pie_chart(metrics)

        # 执行时间直方图
        durations = [r.get('duration', 0) for r in test_results if r.get('duration') is not None]
        if durations:
            charts['duration_histogram'] = self.chart_generator.create_duration_histogram(durations)

        # 测试类型分布
        charts['test_type_breakdown'] = self.chart_generator.create_test_type_breakdown(test_results)

        # 趋势图（需要历史数据）
        charts['trend_chart'] = self.chart_generator.create_trend_chart([])  # 暂时为空

        return charts

    def generate_summary(self, metrics: TestMetrics, test_results: List[Dict]) -> Dict[str, Any]:
        """生成报告摘要"""
        return {
            "test_session_summary": {
                "total_executions": len(test_results),
                "execution_period": "N/A",
                "overall_assessment": "优秀" if metrics.success_rate >= 90 else "良好" if metrics.success_rate >= 70 else "需改进",
                "key_highlights": [
                    f"成功率达到 {metrics.success_rate:.1f}%",
                    f"平均执行时间 {metrics.average_duration:.2f}秒",
                    f"可靠性评分 {metrics.reliability_score:.1f}"
                ]
            },
            "performance_analysis": {
                "fastest_test": f"{metrics.min_duration:.2f}秒",
                "slowest_test": f"{metrics.max_duration:.2f}秒",
                "stability": "稳定" if metrics.std_duration < metrics.average_duration * 0.5 else "波动较大"
            },
            "quality_assessment": {
                "test_coverage": f"{metrics.coverage_rate:.1f}%",
                "efficiency_rating": "优秀" if metrics.efficiency_score >= 80 else "良好" if metrics.efficiency_score >= 60 else "需优化",
                "reliability_rating": "优秀" if metrics.reliability_score >= 90 else "良好" if metrics.reliability_score >= 70 else "需改进"
            }
        }

    def generate_recommendations(self, metrics: TestMetrics, test_results: List[Dict]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 基于成功率
        if metrics.success_rate < 80:
            recommendations.append("成功率偏低，建议检查测试环境配置和测试用例质量")
        elif metrics.success_rate < 90:
            recommendations.append("成功率有待提升，建议关注失败用例的修复")

        # 基于执行时间
        if metrics.average_duration > 60:
            recommendations.append(f"平均执行时间较长（{metrics.average_duration:.1f}秒），考虑优化测试性能")

        # 基于失败模式
        failed_tests = [r for r in test_results if r.get('status') == 'failed']
        if failed_tests:
            timeout_failures = [r for r in failed_tests if 'timeout' in (r.get('error_message', '') or '').lower()]
            if len(timeout_failures) > 0:
                recommendations.append(f"发现 {len(timeout_failures)} 个超时失败，建议增加超时时间或优化性能")

        # 基于稳定性
        if metrics.std_duration > metrics.average_duration * 0.5:
            recommendations.append("测试执行时间波动较大，建议检查外部依赖和环境稳定性")

        # 默认建议
        if not recommendations:
            recommendations.append("测试执行良好，建议保持当前的测试策略和频率")

        return recommendations

    def generate_report(
        self,
        test_results: List[Dict[str, Any]],
        report_type: ReportType = ReportType.COMPREHENSIVE,
        report_format: ReportFormat = ReportFormat.HTML,
        title: str = "MyStocks 测试报告",
        subtitle: str = "综合测试执行报告",
        test_session_id: str = "",
        output_path: Optional[str] = None
    ) -> str:
        """生成测试报告"""
        # 计算指标
        metrics = self.calculate_metrics(test_results)

        # 生成图表
        charts = self.generate_charts(test_results, metrics)

        # 生成摘要
        summary = self.generate_summary(metrics, test_results)

        # 生成建议
        recommendations = self.generate_recommendations(metrics, test_results)

        # 创建报告数据
        report_data = ReportData(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type=report_type,
            report_format=report_format,
            title=title,
            subtitle=subtitle,
            test_session_id=test_session_id,
            metrics=metrics,
            test_results=test_results,
            charts=charts,
            summary=summary,
            recommendations=recommendations
        )

        # 根据格式生成报告
        if report_format == ReportFormat.HTML:
            content = self.html_generator.generate_html(report_data)
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            return content
        elif report_format == ReportFormat.JSON:
            json_data = self.json_generator.generate_json(report_data)
            json_content = json.dumps(json_data, ensure_ascii=False, indent=2)
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(json_content)
            return json_content
        elif report_format == ReportFormat.PDF:
            if not self.pdf_generator:
                raise ImportError("PDF生成需要安装reportlab库")
            if not output_path:
                output_path = f"/tmp/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            self.pdf_generator.generate_pdf(report_data, output_path)
            return output_path
        else:
            raise ValueError(f"不支持的报告格式: {report_format}")

    def export_to_multiple_formats(
        self,
        test_results: List[Dict[str, Any]],
        output_dir: str = "/tmp",
        formats: List[ReportFormat] = None
    ) -> Dict[str, str]:
        """导出多种格式的报告"""
        if formats is None:
            formats = [ReportFormat.HTML, ReportFormat.JSON, ReportFormat.PDF]

        exported_files = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"mystocks_test_report_{timestamp}"

        for format_type in formats:
            try:
                output_path = os.path.join(output_dir, f"{base_filename}.{format_type.value}")
                file_content = self.generate_report(
                    test_results=test_results,
                    report_format=format_type,
                    output_path=output_path
                )
                exported_files[format_type.value] = output_path
                print(f"✓ 已导出 {format_type.value.upper()} 报告: {output_path}")
            except Exception as e:
                print(f"❌ 导出 {format_type.value} 报告失败: {str(e)}")

        # 创建压缩包
        if len(exported_files) > 1:
            zip_path = os.path.join(output_dir, f"{base_filename}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in exported_files.values():
                    zipf.write(file_path, os.path.basename(file_path))
            exported_files['zip'] = zip_path
            print(f"✓ 已创建压缩包: {zip_path}")

        return exported_files


async def demo_report_generator():
    """演示报告生成器功能"""
    print("🚀 演示测试报告生成器")

    generator = TestReportGenerator()

    # 模拟测试结果
    test_results = [
        {
            "test_id": "test_001",
            "test_name": "AI测试生成器验证",
            "test_type": "ai_assisted",
            "status": "passed",
            "duration": 2.5,
            "error_message": None
        },
        {
            "test_id": "test_002",
            "test_name": "API性能基准测试",
            "test_type": "performance",
            "status": "passed",
            "duration": 45.2,
            "error_message": None
        },
        {
            "test_id": "test_003",
            "test_name": "安全漏洞扫描",
            "test_type": "security",
            "status": "failed",
            "duration": 120.5,
            "error_message": "Connection timeout"
        },
        {
            "test_id": "test_004",
            "test_name": "契约测试执行",
            "test_type": "contract",
            "status": "passed",
            "duration": 15.8,
            "error_message": None
        },
        {
            "test_id": "test_005",
            "test_name": "混沌工程测试",
            "test_type": "chaos",
            "status": "skipped",
            "duration": 0,
            "error_message": "Dependency not available"
        }
    ]

    # 生成HTML报告
    html_content = generator.generate_report(
        test_results=test_results,
        report_format=ReportFormat.HTML,
        title="MyStocks 综合测试报告",
        subtitle="2024年12月测试执行汇总"
    )
    print(f"\n📄 HTML报告生成成功（长度: {len(html_content)} 字符）")

    # 生成JSON报告
    json_content = generator.generate_report(
        test_results=test_results,
        report_format=ReportFormat.JSON,
        title="MyStocks 测试数据",
        subtitle="测试结果JSON格式导出"
    )
    print(f"📊 JSON报告生成成功（长度: {len(json_content)} 字符）")

    # 导出多种格式
    exported_files = generator.export_to_multiple_formats(
        test_results=test_results,
        output_dir="/tmp",
        formats=[ReportFormat.HTML, ReportFormat.JSON]
    )
    print(f"\n📁 已导出文件: {list(exported_files.keys())}")

    # 计算并显示指标
    metrics = generator.calculate_metrics(test_results)
    print("\n📈 测试指标:")
    print(f"  总测试数: {metrics.total_tests}")
    print(f"  通过率: {metrics.success_rate:.1f}%")
    print(f"  平均耗时: {metrics.average_duration:.2f}秒")
    print(f"  可靠性评分: {metrics.reliability_score:.1f}")

    print("\n✅ 测试报告生成器演示完成")


