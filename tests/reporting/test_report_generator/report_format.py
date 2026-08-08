#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告生成器

提供多格式、多层次的测试报告生成功能，支持PDF、HTML、JSON、CSV等格式。
"""

import base64
import io
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from jinja2 import Template
from plotly.subplots import make_subplots

class ReportFormat(Enum):
    """报告格式枚举"""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    XML = "xml"
    MARKDOWN = "markdown"
    EXCEL = "excel"


class ReportType(Enum):
    """报告类型枚举"""
    SUMMARY = "summary"  # 总结报告
    DETAILED = "detailed"  # 详细报告
    DASHBOARD = "dashboard"  # 仪表板报告
    TREND = "trend"  # 趋势报告
    COMPLIANCE = "compliance"  # 合规报告
    PERFORMANCE = "performance"  # 性能报告
    SECURITY = "security"  # 安全报告
    COMPREHENSIVE = "comprehensive"  # 综合报告


@dataclass
class TestMetrics:
    """测试指标数据"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    flaky_tests: int = 0
    average_duration: float = 0.0
    max_duration: float = 0.0
    min_duration: float = 0.0
    median_duration: float = 0.0
    std_duration: float = 0.0
    success_rate: float = 0.0
    coverage_rate: float = 0.0
    efficiency_score: float = 0.0
    reliability_score: float = 0.0


@dataclass
class ReportData:
    """报告数据结构"""
    report_id: str
    report_type: ReportType
    report_format: ReportFormat
    title: str
    subtitle: str = ""
    generated_at: datetime = field(default_factory=datetime.now)
    test_session_id: str = ""
    metrics: TestMetrics = field(default_factory=TestMetrics)
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    charts: Dict[str, str] = field(default_factory=dict)  # chart_name -> base64_image
    tables: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # table_name -> table_data
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChartGenerator:
    """图表生成器"""

    def __init__(self):
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

    def create_success_rate_pie_chart(self, metrics: TestMetrics) -> str:
        """创建成功率饼图"""
        labels = ['通过', '失败', '跳过']
        sizes = [metrics.passed_tests, metrics.failed_tests, metrics.skipped_tests]
        colors = ['#2ecc71', '#e74c3c', '#f39c12']

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title('测试结果分布', fontsize=16, fontweight='bold', pad=20)

        # 添加成功率文本
        success_rate_text = f"成功率: {metrics.success_rate:.1f}%"
        ax.text(0.5, -1.2, success_rate_text, ha='center', va='center',
                fontsize=14, fontweight='bold', transform=ax.transAxes)

        # 转换为base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.read()).decode()
        plt.close()

        return chart_data

    def create_duration_histogram(self, durations: List[float]) -> str:
        """创建执行时间直方图"""
        fig, ax = plt.subplots(figsize=(12, 6))

        if durations:
            ax.hist(durations, bins=30, color='#3498db', alpha=0.7, edgecolor='black')
            ax.axvline(statistics.mean(durations), color='red', linestyle='--',
                      label=f'平均值: {statistics.mean(durations):.2f}s')
            ax.axvline(statistics.median(durations), color='green', linestyle='--',
                      label=f'中位数: {statistics.median(durations):.2f}s')

        ax.set_xlabel('执行时间 (秒)', fontsize=12)
        ax.set_ylabel('频次', fontsize=12)
        ax.set_title('测试执行时间分布', fontsize=16, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.read()).decode()
        plt.close()

        return chart_data

    def create_test_type_breakdown(self, test_results: List[Dict]) -> str:
        """创建测试类型分布图"""
        from collections import Counter

        test_types = [result.get('test_type', 'unknown') for result in test_results]
        type_counts = Counter(test_types)

        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(type_counts.keys(), type_counts.values(), color=plt.cm.Set3(np.linspace(0, 1, len(type_counts))))

        ax.set_xlabel('测试类型', fontsize=12)
        ax.set_ylabel('数量', fontsize=12)
        ax.set_title('按测试类型分类', fontsize=16, fontweight='bold')

        # 在条形上添加数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom')

        plt.xticks(rotation=45)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.read()).decode()
        plt.close()

        return chart_data

    def create_trend_chart(self, historical_data: List[Dict[str, Any]]) -> str:
        """创建趋势分析图"""
        if not historical_data:
            return ""

        dates = [pd.to_datetime(d['date']) for d in historical_data]
        success_rates = [d['success_rate'] for d in historical_data]
        total_tests = [d['total_tests'] for d in historical_data]

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('成功率趋势', '测试数量趋势'),
            vertical_spacing=0.08
        )

        # 成功率趋势
        fig.add_trace(
            go.Scatter(x=dates, y=success_rates, mode='lines+markers',
                      name='成功率', line=dict(color='#2ecc71', width=3)),
            row=1, col=1
        )

        # 测试数量趋势
        fig.add_trace(
            go.Scatter(x=dates, y=total_tests, mode='lines+markers',
                      name='测试数量', line=dict(color='#3498db', width=3)),
            row=2, col=1
        )

        fig.update_layout(
            title="测试趋势分析",
            height=600,
            showlegend=True
        )

        fig.update_yaxes(title_text="成功率 (%)", row=1, col=1)
        fig.update_yaxes(title_text="测试数量", row=2, col=1)
        fig.update_xaxes(title_text="日期", row=2, col=1)

        # 转换为base64
        buffer = io.BytesIO()
        fig.write_image(buffer, format='png', width=1200, height=600, scale=2)
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.read()).decode()

        return chart_data


class HTMLReportGenerator:
    """HTML报告生成器"""

    def __init__(self):
        self.chart_generator = ChartGenerator()
        self.template = self._load_template()

    def _load_template(self) -> Template:
        """加载HTML模板"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header .subtitle {
            margin: 10px 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        .metric-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .chart-container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chart-title {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #2c3e50;
        }
        .chart-image {
            width: 100%;
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }
        .test-results {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .test-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .test-table th,
        .test-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .test-table th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        .status-passed {
            color: #27ae60;
            font-weight: bold;
        }
        .status-failed {
            color: #e74c3c;
            font-weight: bold;
        }
        .status-skipped {
            color: #f39c12;
            font-weight: bold;
        }
        .recommendations {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            border-radius: 5px;
            margin: 30px 0;
        }
        .recommendations h3 {
            margin-top: 0;
            color: #856404;
        }
        .recommendations ul {
            margin-bottom: 0;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #eee;
            margin-top: 30px;
        }
        @media (max-width: 768px) {
            .metric-cards {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <div class="subtitle">{{ subtitle }}</div>
        <div class="subtitle">生成时间: {{ generated_at }}</div>
    </div>

    <!-- 指标卡片 -->
    <div class="metric-cards">
        <div class="metric-card">
            <div class="metric-label">总测试数</div>
            <div class="metric-value">{{ metrics.total_tests }}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">通过率</div>
            <div class="metric-value status-passed">{{ "%.1f"|format(metrics.success_rate) }}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">平均耗时</div>
            <div class="metric-value">{{ "%.1f"|format(metrics.average_duration) }}s</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">可靠性评分</div>
            <div class="metric-value">{{ "%.1f"|format(metrics.reliability_score) }}</div>
        </div>
    </div>

    <!-- 图表区域 -->
    {% if charts.success_rate_pie %}
    <div class="chart-container">
        <div class="chart-title">测试结果分布</div>
        <img src="data:image/png;base64,{{ charts.success_rate_pie }}" alt="测试结果分布" class="chart-image">
    </div>
    {% endif %}

    {% if charts.duration_histogram %}
    <div class="chart-container">
        <div class="chart-title">执行时间分布</div>
        <img src="data:image/png;base64,{{ charts.duration_histogram }}" alt="执行时间分布" class="chart-image">
    </div>
    {% endif %}

    {% if charts.test_type_breakdown %}
    <div class="chart-container">
        <div class="chart-title">测试类型分布</div>
        <img src="data:image/png;base64,{{ charts.test_type_breakdown }}" alt="测试类型分布" class="chart-image">
    </div>
    {% endif %}

    <!-- 测试结果表格 -->
    {% if test_results %}
    <div class="test-results">
        <h2>详细测试结果</h2>
        <table class="test-table">
            <thead>
                <tr>
                    <th>测试ID</th>
                    <th>测试名称</th>
                    <th>测试类型</th>
                    <th>状态</th>
                    <th>耗时 (秒)</th>
                    <th>错误信息</th>
                </tr>
            </thead>
            <tbody>
                {% for result in test_results %}
                <tr>
                    <td>{{ result.test_id }}</td>
                    <td>{{ result.test_name }}</td>
                    <td>{{ result.test_type }}</td>
                    <td class="status-{{ result.status }}">{{ result.status }}</td>
                    <td>{{ "%.2f"|format(result.duration or 0) }}</td>
                    <td>{{ result.error_message or "" }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}

    <!-- 改进建议 -->
    {% if recommendations %}
    <div class="recommendations">
        <h3>改进建议</h3>
        <ul>
            {% for rec in recommendations %}
            <li>{{ rec }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    <!-- 页脚 -->
    <div class="footer">
        <p>MyStocks 测试报告 | 生成时间: {{ generated_at }}</p>
    </div>

</body>
</html>
        """
        return Template(html_template)

    def generate_html(self, report_data: ReportData) -> str:
        """生成HTML报告"""
        html_content = self.template.render(
            title=report_data.title,
            subtitle=report_data.subtitle,
            generated_at=report_data.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
            metrics=report_data.metrics,
            charts=report_data.charts,
            test_results=report_data.test_results,
            recommendations=report_data.recommendations
        )
        return html_content


class PDFReportGenerator:
    """PDF报告生成器"""

    def __init__(self):
        if not PDF_AVAILABLE:
            raise ImportError("PDF生成功能需要安装reportlab库")

    def generate_pdf(self, report_data: ReportData, output_path: str):
        """生成PDF报告"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # 样式设置
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # 居中
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )

        # 标题
        story.append(Paragraph(report_data.title, title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(report_data.subtitle, styles['Normal']))
        story.append(Spacer(1, 20))

        # 指标汇总
        story.append(Paragraph("测试指标汇总", heading_style))

        # 创建指标表格
        metrics_data = [
            ['指标名称', '数值'],
            ['总测试数', str(report_data.metrics.total_tests)],
            ['通过数', str(report_data.metrics.passed_tests)],
            ['失败数', str(report_data.metrics.failed_tests)],
            ['跳过数', str(report_data.metrics.skipped_tests)],
            ['成功率', f"{report_data.metrics.success_rate:.1f}%"],
            ['平均耗时', f"{report_data.metrics.average_duration:.2f}s"],
            ['最大耗时', f"{report_data.metrics.max_duration:.2f}s"],
            ['可靠性评分', f"{report_data.metrics.reliability_score:.1f}"]
        ]

        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(metrics_table)
        story.append(Spacer(1, 20))

        # 图表（如果提供base64图像）
        if report_data.charts:
            story.append(Paragraph("图表分析", heading_style))
            for chart_name, chart_base64 in report_data.charts.items():
                try:
                    image_data = base64.b64decode(chart_base64)
                    img_buffer = io.BytesIO(image_data)
                    img = Image(img_buffer, width=6*inch, height=4*inch)
                    story.append(img)
                    story.append(Spacer(1, 20))
                except Exception:
                    story.append(Paragraph(f"图表 {chart_name} 解析失败", styles['Normal']))
                    story.append(Spacer(1, 10))

        # 改进建议
        if report_data.recommendations:
            story.append(Paragraph("改进建议", heading_style))
            for rec in report_data.recommendations:
                story.append(Paragraph(f"• {rec}", styles['Normal']))
            story.append(Spacer(1, 20))

        # 生成PDF
        doc.build(story)


class JSONReportGenerator:
    """JSON报告生成器"""

    def generate_json(self, report_data: ReportData) -> Dict[str, Any]:
        """生成JSON报告"""
        # 转换dataclass为字典
        json_data = {
            "report_id": report_data.report_id,
            "report_type": report_data.report_type.value,
            "report_format": report_data.report_format.value,
            "title": report_data.title,
            "subtitle": report_data.subtitle,
            "generated_at": report_data.generated_at.isoformat(),
            "test_session_id": report_data.test_session_id,
            "metrics": {
                "total_tests": report_data.metrics.total_tests,
                "passed_tests": report_data.metrics.passed_tests,
                "failed_tests": report_data.metrics.failed_tests,
                "skipped_tests": report_data.metrics.skipped_tests,
                "average_duration": report_data.metrics.average_duration,
                "max_duration": report_data.metrics.max_duration,
                "min_duration": report_data.metrics.min_duration,
                "median_duration": report_data.metrics.median_duration,
                "std_duration": report_data.metrics.std_duration,
                "success_rate": report_data.metrics.success_rate,
                "coverage_rate": report_data.metrics.coverage_rate,
                "efficiency_score": report_data.metrics.efficiency_score,
                "reliability_score": report_data.metrics.reliability_score
            },
            "test_results": report_data.test_results,
            "charts": report_data.charts,
            "tables": report_data.tables,
            "summary": report_data.summary,
            "recommendations": report_data.recommendations,
            "artifacts": report_data.artifacts,
            "metadata": report_data.metadata
        }
        return json_data


