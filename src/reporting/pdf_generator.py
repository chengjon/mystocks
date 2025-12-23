"""
PDF报告生成器 (PDF Report Generator)

功能说明:
- 自动生成专业的策略回测报告
- 包含性能指标、风险指标、图表
- 支持中文字体
- 自定义模板和样式

使用ReportLab库生成PDF报告

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional
from datetime import datetime
import logging

# 尝试导入ReportLab
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
        Image,
        KeepTogether,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("警告: ReportLab未安装，PDF功能不可用")
    print("安装: pip install reportlab")


class PDFReportGenerator:
    """
    PDF报告生成器

    功能:
    - 策略回测报告
    - 性能分析报告
    - 月度/季度报告
    - 自定义模板
    """

    def __init__(self, font_path: Optional[str] = None, page_size=None):
        """
        初始化PDF生成器

        参数:
            font_path: 中文字体路径（可选）
            page_size: 页面大小（默认A4）
        """
        self.logger = logging.getLogger(f"{__name__}.PDFReportGenerator")

        if not REPORTLAB_AVAILABLE:
            self.logger.error("ReportLab未安装，无法使用PDF功能")
            return

        self.page_size = page_size or A4
        self.width, self.height = self.page_size

        # 尝试注册中文字体
        self._register_chinese_font(font_path)

        # 样式
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _register_chinese_font(self, font_path: Optional[str] = None):
        """注册中文字体"""
        self.chinese_font_available = False

        if font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont("SimSun", font_path))
                self.chinese_font_available = True
                self.logger.info(f"已加载中文字体: {font_path}")
            except Exception as e:
                self.logger.warning(f"无法加载中文字体: {e}")

        # 如果没有中文字体，使用默认字体
        if not self.chinese_font_available:
            self.logger.warning("未加载中文字体，中文可能显示为方框")

    def _setup_styles(self):
        """设置样式"""
        # 标题样式
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1f77b4"),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName="SimSun" if self.chinese_font_available else "Helvetica-Bold",
            )
        )

        # 章节标题
        self.styles.add(
            ParagraphStyle(
                name="SectionTitle",
                parent=self.styles["Heading2"],
                fontSize=16,
                textColor=colors.HexColor("#2c3e50"),
                spaceAfter=12,
                spaceBefore=12,
                fontName="SimSun" if self.chinese_font_available else "Helvetica-Bold",
            )
        )

        # 正文
        self.styles.add(
            ParagraphStyle(
                name="CustomBody",
                parent=self.styles["Normal"],
                fontSize=10,
                leading=14,
                fontName="SimSun" if self.chinese_font_available else "Helvetica",
            )
        )

    def generate_backtest_report(
        self,
        result: Dict,
        strategy_name: str,
        output_path: str,
        chart_paths: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        生成回测报告PDF

        参数:
            result: 回测结果字典
            strategy_name: 策略名称
            output_path: 输出路径
            chart_paths: 图表路径字典

        返回:
            str: 生成的PDF路径
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab未安装，无法生成PDF")

        self.logger.info(f"开始生成PDF报告: {output_path}")

        # 创建PDF文档
        doc = SimpleDocTemplate(
            output_path,
            pagesize=self.page_size,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        # 构建内容
        story = []

        # 1. 封面
        story.extend(self._build_cover(strategy_name, result))
        story.append(PageBreak())

        # 2. 执行摘要
        story.extend(self._build_executive_summary(result))
        story.append(Spacer(1, 0.5 * inch))

        # 3. 性能指标
        story.extend(self._build_performance_section(result))
        story.append(Spacer(1, 0.5 * inch))

        # 4. 风险指标
        story.extend(self._build_risk_section(result))
        story.append(Spacer(1, 0.5 * inch))

        # 5. 交易统计
        story.extend(self._build_trading_section(result))

        # 6. 图表（如果提供）
        if chart_paths:
            story.append(PageBreak())
            story.extend(self._build_charts_section(chart_paths))

        # 7. 页脚
        story.append(PageBreak())
        story.extend(self._build_footer())

        # 生成PDF
        doc.build(story)

        self.logger.info(f"✓ PDF报告已生成: {output_path}")
        return output_path

    def _build_cover(self, strategy_name: str, result: Dict) -> List:
        """构建封面"""
        elements = []

        # 标题
        title = Paragraph(
            f"Strategy Backtest Report<br/>{strategy_name}", self.styles["CustomTitle"]
        )
        elements.append(Spacer(1, 2 * inch))
        elements.append(title)
        elements.append(Spacer(1, 0.5 * inch))

        # 日期
        report_date = datetime.now().strftime("%Y-%m-%d")
        date_text = Paragraph(
            f"<para align=center>Report Date: {report_date}</para>",
            self.styles["CustomBody"],
        )
        elements.append(date_text)
        elements.append(Spacer(1, 1 * inch))

        # 关键指标预览
        metrics = result.get("performance", {})
        preview_data = [
            ["Metric", "Value"],
            ["Total Return", f"{metrics.get('total_return', 0) * 100:.2f}%"],
            ["Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}"],
            ["Max Drawdown", f"{metrics.get('max_drawdown', 0) * 100:.2f}%"],
        ]

        preview_table = Table(preview_data, colWidths=[3 * inch, 2 * inch])
        preview_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        elements.append(preview_table)

        return elements

    def _build_executive_summary(self, result: Dict) -> List:
        """构建执行摘要"""
        elements = []

        elements.append(Paragraph("Executive Summary", self.styles["SectionTitle"]))

        metrics = result.get("performance", {})
        risk = result.get("risk", {})

        summary_text = f"""
        The strategy achieved a total return of {metrics.get("total_return", 0) * 100:.2f}%
        with a Sharpe ratio of {metrics.get("sharpe_ratio", 0):.2f}.
        The maximum drawdown was {metrics.get("max_drawdown", 0) * 100:.2f}%,
        indicating {self._assess_risk(metrics.get("max_drawdown", 0))} risk level.

        Annual volatility: {metrics.get("annual_volatility", 0) * 100:.2f}%<br/>
        Win rate: {metrics.get("win_rate", 0) * 100:.2f}%<br/>
        Profit factor: {metrics.get("profit_factor", 0):.2f}
        """

        elements.append(Paragraph(summary_text, self.styles["CustomBody"]))

        return elements

    def _build_performance_section(self, result: Dict) -> List:
        """构建性能指标部分"""
        elements = []

        elements.append(Paragraph("Performance Metrics", self.styles["SectionTitle"]))

        metrics = result.get("performance", {})

        perf_data = [
            ["Metric", "Value"],
            ["Total Return", f"{metrics.get('total_return', 0) * 100:.2f}%"],
            ["Annual Return", f"{metrics.get('annual_return', 0) * 100:.2f}%"],
            ["Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}"],
            ["Sortino Ratio", f"{metrics.get('sortino_ratio', 0):.2f}"],
            ["Calmar Ratio", f"{metrics.get('calmar_ratio', 0):.2f}"],
            ["Omega Ratio", f"{metrics.get('omega_ratio', 0):.2f}"],
            ["Annual Volatility", f"{metrics.get('annual_volatility', 0) * 100:.2f}%"],
        ]

        perf_table = Table(perf_data, colWidths=[3 * inch, 2 * inch])
        perf_table.setStyle(self._get_table_style())

        elements.append(perf_table)

        return elements

    def _build_risk_section(self, result: Dict) -> List:
        """构建风险指标部分"""
        elements = []

        elements.append(Paragraph("Risk Metrics", self.styles["SectionTitle"]))

        risk = result.get("risk", {})

        risk_data = [
            ["Metric", "Value"],
            ["Max Drawdown", f"{risk.get('max_drawdown', 0) * 100:.2f}%"],
            ["Max Drawdown Duration", f"{risk.get('max_drawdown_duration', 0)} days"],
            ["Value at Risk (95%)", f"{risk.get('var_95', 0) * 100:.2f}%"],
            ["Conditional VaR (95%)", f"{risk.get('cvar_95', 0) * 100:.2f}%"],
            ["Downside Deviation", f"{risk.get('downside_deviation', 0) * 100:.2f}%"],
        ]

        risk_table = Table(risk_data, colWidths=[3 * inch, 2 * inch])
        risk_table.setStyle(self._get_table_style())

        elements.append(risk_table)

        return elements

    def _build_trading_section(self, result: Dict) -> List:
        """构建交易统计部分"""
        elements = []

        elements.append(Paragraph("Trading Statistics", self.styles["SectionTitle"]))

        backtest = result.get("backtest", {})

        trading_data = [
            ["Metric", "Value"],
            ["Total Trades", str(backtest.get("total_trades", 0))],
            ["Win Rate", f"{backtest.get('win_rate', 0) * 100:.2f}%"],
            ["Profit Factor", f"{backtest.get('profit_factor', 0):.2f}"],
            ["Average Win", f"{backtest.get('avg_win', 0) * 100:.2f}%"],
            ["Average Loss", f"{backtest.get('avg_loss', 0) * 100:.2f}%"],
            ["Largest Win", f"{backtest.get('largest_win', 0) * 100:.2f}%"],
            ["Largest Loss", f"{backtest.get('largest_loss', 0) * 100:.2f}%"],
        ]

        trading_table = Table(trading_data, colWidths=[3 * inch, 2 * inch])
        trading_table.setStyle(self._get_table_style())

        elements.append(trading_table)

        return elements

    def _build_charts_section(self, chart_paths: Dict[str, str]) -> List:
        """构建图表部分"""
        elements = []

        elements.append(
            Paragraph("Charts and Visualizations", self.styles["SectionTitle"])
        )

        for chart_name, chart_path in chart_paths.items():
            if os.path.exists(chart_path):
                # 添加图表标题
                elements.append(
                    Paragraph(
                        chart_name.replace("_", " ").title(), self.styles["Heading3"]
                    )
                )

                # 添加图表图片
                try:
                    img = Image(chart_path, width=6 * inch, height=4 * inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.3 * inch))
                except Exception as e:
                    self.logger.warning(f"无法加载图表 {chart_name}: {e}")

        return elements

    def _build_footer(self) -> List:
        """构建页脚"""
        elements = []

        footer_text = f"""
        <para align=center>
        This report was generated by MyStocks Quantitative Trading System<br/>
        Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br/>
        <br/>
        Disclaimer: Past performance does not guarantee future results.
        </para>
        """

        elements.append(Paragraph(footer_text, self.styles["CustomBody"]))

        return elements

    def _get_table_style(self) -> TableStyle:
        """获取表格样式"""
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ecf0f1")),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#ecf0f1")],
                ),
            ]
        )

    def _assess_risk(self, max_drawdown: float) -> str:
        """评估风险等级"""
        if max_drawdown < 0.1:
            return "low"
        elif max_drawdown < 0.2:
            return "moderate"
        elif max_drawdown < 0.3:
            return "high"
        else:
            return "very high"

    def generate_monthly_report(self, data: Dict, output_path: str) -> str:
        """
        生成月度报告

        参数:
            data: 月度数据
            output_path: 输出路径

        返回:
            str: PDF路径
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab未安装")

        doc = SimpleDocTemplate(output_path, pagesize=self.page_size)
        story = []

        # 标题
        story.append(Paragraph("Monthly Report", self.styles["CustomTitle"]))
        story.append(Spacer(1, 0.5 * inch))

        # 月度摘要
        summary_text = f"""
        Month: {data.get("month", "N/A")}<br/>
        Total Return: {data.get("return", 0) * 100:.2f}%<br/>
        Total Trades: {data.get("trades", 0)}<br/>
        Win Rate: {data.get("win_rate", 0) * 100:.2f}%
        """
        story.append(Paragraph(summary_text, self.styles["CustomBody"]))

        # 构建PDF
        doc.build(story)

        return output_path


if __name__ == "__main__":
    # 测试代码
    print("PDF报告生成器测试")
    print("=" * 70)

    if not REPORTLAB_AVAILABLE:
        print("✗ ReportLab未安装，无法测试PDF功能")
        print("  请安装: pip install reportlab")
        exit(1)

    # 设置日志
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 创建生成器
    generator = PDFReportGenerator()

    # 模拟回测结果
    mock_result = {
        "performance": {
            "total_return": 0.35,
            "annual_return": 0.15,
            "sharpe_ratio": 1.8,
            "sortino_ratio": 2.1,
            "calmar_ratio": 1.2,
            "omega_ratio": 1.5,
            "annual_volatility": 0.12,
            "max_drawdown": -0.15,
            "win_rate": 0.58,
            "profit_factor": 1.8,
        },
        "risk": {
            "max_drawdown": -0.15,
            "max_drawdown_duration": 45,
            "var_95": -0.025,
            "cvar_95": -0.035,
            "downside_deviation": 0.08,
        },
        "backtest": {
            "total_trades": 150,
            "win_rate": 0.58,
            "profit_factor": 1.8,
            "avg_win": 0.025,
            "avg_loss": -0.015,
            "largest_win": 0.085,
            "largest_loss": -0.042,
        },
    }

    # 生成报告
    output_path = "/tmp/backtest_report.pdf"

    try:
        generator.generate_backtest_report(
            result=mock_result,
            strategy_name="Momentum Strategy",
            output_path=output_path,
        )

        print(f"\n✓ PDF报告已生成: {output_path}")
        print(f"  文件大小: {os.path.getsize(output_path)} bytes")

    except Exception as e:
        print(f"\n✗ 生成失败: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 70)
    print("测试完成")
