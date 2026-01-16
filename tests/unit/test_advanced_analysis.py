"""
Tests for Advanced Quantitative Analysis Modules
A股量化分析平台高级分析模块测试

This module contains comprehensive tests for all advanced analysis modules:
- Fundamental Analyzer
- Technical Analyzer
- Trading Signals Analyzer
- Time Series Analyzer
- Market Panorama Analyzer
- Capital Flow Analyzer
- Chip Distribution Analyzer
- Anomaly Tracking Analyzer
- Financial Valuation Analyzer
- Sentiment Analyzer
- Decision Models Analyzer
- Multidimensional Radar Analyzer
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.advanced_analysis import AnalysisType, AnalysisResult, AdvancedAnalysisEngine, MultidimensionalRadarAnalyzer
from src.core import MyStocksUnifiedManager, DataClassification


class TestMultidimensionalRadarAnalyzer:
    """多维度雷达分析器测试"""

    @pytest.fixture
    def mock_data_manager(self):
        """模拟数据管理器"""
        manager = Mock(spec=MyStocksUnifiedManager)
        return manager

    @pytest.fixture
    def mock_gpu_manager(self):
        """模拟GPU管理器"""
        gpu_manager = Mock()
        return gpu_manager

    @pytest.fixture
    def radar_analyzer(self, mock_data_manager, mock_gpu_manager):
        """雷达分析器实例"""
        return MultidimensionalRadarAnalyzer(mock_data_manager, mock_gpu_manager)

    @pytest.fixture
    def mock_analysis_results(self):
        """模拟各维度分析结果"""
        results = {}

        # 创建模拟的AnalysisResult对象
        for analysis_type in [
            AnalysisType.FUNDAMENTAL,
            AnalysisType.TECHNICAL,
            AnalysisType.TRADING_SIGNALS,
            AnalysisType.TIME_SERIES,
            AnalysisType.MARKET_PANORAMA,
            AnalysisType.CAPITAL_FLOW,
            AnalysisType.CHIP_DISTRIBUTION,
            AnalysisType.ANOMALY_TRACKING,
        ]:
            result = Mock(spec=AnalysisResult)
            result.analysis_type = analysis_type
            result.stock_code = "600000"
            result.timestamp = datetime.now()
            result.scores = {"score": 75.0, "confidence": 0.8}
            result.signals = [{"type": "BUY", "strength": 0.7, "description": "Test signal"}]
            result.recommendations = {"action": "BUY", "confidence": 0.75}
            result.risk_assessment = {"level": "medium", "factors": ["volatility"]}
            result.metadata = {"version": "1.0"}
            results[analysis_type] = result

        return results

    def test_initialization(self, radar_analyzer):
        """测试初始化"""
        assert radar_analyzer is not None
        assert hasattr(radar_analyzer, "analyzers")
        assert len(radar_analyzer.analyzers) == 8  # 8 core analyzers

    def test_dimension_weights(self, radar_analyzer):
        """测试维度权重配置"""
        weights = radar_analyzer.dimension_weights
        assert isinstance(weights, dict)
        assert len(weights) == 8
        assert sum(weights.values()) == pytest.approx(1.0)  # Should sum to 1

    def test_calculate_overall_score(self, radar_analyzer):
        """测试综合评分计算"""
        # Create mock dimensions
        dimensions = [Mock(score=80.0, weight=0.2), Mock(score=70.0, weight=0.3), Mock(score=60.0, weight=0.5)]

        score = radar_analyzer._calculate_overall_score(dimensions)
        expected = (80 * 0.2 + 70 * 0.3 + 60 * 0.5) / (0.2 + 0.3 + 0.5)
        assert score == pytest.approx(expected)

    def test_determine_risk_level(self, radar_analyzer):
        """测试风险等级确定"""
        assert radar_analyzer._determine_risk_level(85) == "low"
        assert radar_analyzer._determine_risk_level(75) == "medium"
        assert radar_analyzer._determine_risk_level(55) == "high"
        assert radar_analyzer._determine_risk_level(25) == "extreme"

    @patch("src.advanced_analysis.multidimensional_radar.FundamentalAnalyzer")
    @patch("src.advanced_analysis.multidimensional_radar.TechnicalAnalyzer")
    @patch("src.advanced_analysis.multidimensional_radar.TradingSignalAnalyzer")
    @patch("src.advanced_analysis.multidimensional_radar.TimeSeriesAnalyzer")
    @patch("src.advanced_analysis.multidimensional_radar.MarketPanoramaAnalyzer")
    @patch("src.advanced_analysis.multidimensional_radar.CapitalFlowAnalyzer")
    @patch("src.advanced_analysis.multidimensional_radar.ChipDistributionAnalyzer")
    @patch("src.advanced_analysis.multidimensional_radar.AnomalyTrackingAnalyzer")
    def test_analyze_with_mocked_analyzers(
        self,
        mock_anomaly,
        mock_chip,
        mock_capital,
        mock_market,
        mock_timeseries,
        mock_trading,
        mock_technical,
        mock_fundamental,
        radar_analyzer,
        mock_analysis_results,
    ):
        """测试完整分析流程（使用模拟分析器）"""
        # Setup mocks
        mock_fundamental.return_value.analyze.return_value = mock_analysis_results[AnalysisType.FUNDAMENTAL]
        mock_technical.return_value.analyze.return_value = mock_analysis_results[AnalysisType.TECHNICAL]
        mock_trading.return_value.analyze.return_value = mock_analysis_results[AnalysisType.TRADING_SIGNALS]
        mock_timeseries.return_value.analyze.return_value = mock_analysis_results[AnalysisType.TIME_SERIES]
        mock_market.return_value.analyze.return_value = mock_analysis_results[AnalysisType.MARKET_PANORAMA]
        mock_capital.return_value.analyze.return_value = mock_analysis_results[AnalysisType.CAPITAL_FLOW]
        mock_chip.return_value.analyze.return_value = mock_analysis_results[AnalysisType.CHIP_DISTRIBUTION]
        mock_anomaly.return_value.analyze.return_value = mock_analysis_results[AnalysisType.ANOMALY_TRACKING]

        # Execute analysis
        result = radar_analyzer.analyze("600000")

        # Verify result structure
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == AnalysisType.MULTIDIMENSIONAL_RADAR
        assert result.stock_code == "600000"
        assert isinstance(result.scores, dict)
        assert isinstance(result.signals, list)
        assert isinstance(result.recommendations, dict)
        assert isinstance(result.risk_assessment, dict)

    def test_generate_radar_chart_data(self, radar_analyzer):
        """测试雷达图数据生成"""
        dimensions = [
            Mock(name="基本面", score=75.0, weight=0.2),
            Mock(name="技术面", score=80.0, weight=0.15),
            Mock(name="资金流", score=70.0, weight=0.15),
        ]

        chart_data = radar_analyzer._generate_radar_chart_data(dimensions)

        assert "labels" in chart_data
        assert "datasets" in chart_data
        assert "options" in chart_data
        assert len(chart_data["labels"]) == 3
        assert len(chart_data["datasets"][0]["data"]) == 3

    def test_assess_overall_risk(self, radar_analyzer):
        """测试整体风险评估"""
        radar_result = Mock()
        radar_result.dimensions = [Mock(risk_level="low"), Mock(risk_level="medium"), Mock(risk_level="high")]

        risk_assessment = radar_analyzer._assess_overall_risk(radar_result)

        assert "overall_risk_level" in risk_assessment
        assert "risk_distribution" in risk_assessment
        assert "high_risk_dimensions" in risk_assessment

    def test_generate_recommendation(self, radar_analyzer):
        """测试投资建议生成"""
        assert radar_analyzer._generate_recommendation(85, {"overall_risk_level": "low"}) == "强烈推荐买入"
        assert radar_analyzer._generate_recommendation(65, {"overall_risk_level": "medium"}) == "推荐买入"
        assert radar_analyzer._generate_recommendation(45, {"overall_risk_level": "high"}) == "观望"
        assert radar_analyzer._generate_recommendation(25, {"overall_risk_level": "extreme"}) == "建议卖出"

    def test_error_handling(self, radar_analyzer):
        """测试错误处理"""
        # Test with empty dimensions
        score = radar_analyzer._calculate_overall_score([])
        assert score == 50.0

        # Test with zero weights
        dimensions = [Mock(score=80.0, weight=0.0)]
        score = radar_analyzer._calculate_overall_score(dimensions)
        assert score == 50.0


class TestAdvancedAnalysisEngine:
    """高级分析引擎测试"""

    @pytest.fixture
    def mock_data_manager(self):
        """模拟数据管理器"""
        manager = Mock(spec=MyStocksUnifiedManager)
        return manager

    @pytest.fixture
    def analysis_engine(self, mock_data_manager):
        """分析引擎实例"""
        return AdvancedAnalysisEngine(mock_data_manager)

    def test_initialization(self, analysis_engine):
        """测试初始化"""
        assert analysis_engine is not None
        assert hasattr(analysis_engine, "analyzers")
        assert len(analysis_engine.analyzers) == 12  # All analysis types

    def test_comprehensive_analysis_types(self, analysis_engine):
        """测试支持的分析类型"""
        expected_types = [
            AnalysisType.FUNDAMENTAL,
            AnalysisType.TECHNICAL,
            AnalysisType.TRADING_SIGNALS,
            AnalysisType.TIME_SERIES,
            AnalysisType.MARKET_PANORAMA,
            AnalysisType.CAPITAL_FLOW,
            AnalysisType.CHIP_DISTRIBUTION,
            AnalysisType.ANOMALY_TRACKING,
            AnalysisType.FINANCIAL_VALUATION,
            AnalysisType.SENTIMENT_ANALYSIS,
            AnalysisType.DECISION_MODELS,
            AnalysisType.MULTIDIMENSIONAL_RADAR,
        ]

        assert set(analysis_engine.analyzers.keys()) == set(expected_types)

    @patch("src.advanced_analysis.MultidimensionalRadarAnalyzer")
    def test_comprehensive_analysis_execution(self, mock_radar_analyzer, analysis_engine):
        """测试综合分析执行"""
        # Setup mock
        mock_result = Mock(spec=AnalysisResult)
        mock_result.analysis_type = AnalysisType.MULTIDIMENSIONAL_RADAR
        mock_radar_analyzer.return_value.analyze.return_value = mock_result

        # Execute analysis
        results = analysis_engine.comprehensive_analysis("600000", [AnalysisType.MULTIDIMENSIONAL_RADAR])

        assert AnalysisType.MULTIDIMENSIONAL_RADAR.value in results
        assert results[AnalysisType.MULTIDIMENSIONAL_RADAR.value] == mock_result

    def test_get_market_overview(self, analysis_engine):
        """测试市场概览获取"""
        with patch.object(
            analysis_engine.analyzers[AnalysisType.MARKET_PANORAMA], "analyze_market_overview"
        ) as mock_method:
            mock_method.return_value = {"market_health": 75.0}

            result = analysis_engine.get_market_overview()
            assert result == {"market_health": 75.0}

    def test_get_realtime_alerts(self, analysis_engine):
        """测试实时预警获取"""
        with (
            patch.object(analysis_engine.analyzers[AnalysisType.TRADING_SIGNALS], "analyze") as mock_trading,
            patch.object(analysis_engine.analyzers[AnalysisType.ANOMALY_TRACKING], "analyze") as mock_anomaly,
        ):
            mock_trading_result = Mock()
            mock_trading_result.signals = [{"type": "BUY", "severity": 8}]

            mock_anomaly_result = Mock()
            mock_anomaly_result.signals = [{"type": "WARNING", "severity": 9}]

            mock_trading.return_value = mock_trading_result
            mock_anomaly.return_value = mock_anomaly_result

            alerts = analysis_engine.get_realtime_alerts("600000")

            assert len(alerts) == 2
            assert alerts[0]["severity"] >= alerts[1]["severity"]  # Should be sorted by severity


# Integration Tests
class TestAdvancedAnalysisIntegration:
    """高级分析集成测试"""

    def test_all_analyzers_can_be_imported(self):
        """测试所有分析器可以正常导入"""
        # This test ensures all analyzer modules can be imported without errors
        from src.advanced_analysis import (
            FundamentalAnalyzer,
            TechnicalAnalyzer,
            TradingSignalAnalyzer,
            TimeSeriesAnalyzer,
            MarketPanoramaAnalyzer,
            CapitalFlowAnalyzer,
            ChipDistributionAnalyzer,
            AnomalyTrackingAnalyzer,
            FinancialValuationAnalyzer,
            SentimentAnalyzer,
            DecisionModelsAnalyzer,
            MultidimensionalRadarAnalyzer,
        )

        # If we reach this point, all imports were successful
        assert True

    def test_analysis_types_enum_complete(self):
        """测试分析类型枚举完整性"""
        # Ensure all implemented analyzers have corresponding enum values
        implemented_types = [
            "fundamental",
            "technical",
            "trading_signals",
            "time_series",
            "market_panorama",
            "capital_flow",
            "chip_distribution",
            "anomaly_tracking",
            "financial_valuation",
            "sentiment_analysis",
            "decision_models",
            "multidimensional_radar",
        ]

        enum_values = [atype.value for atype in AnalysisType]
        for impl_type in implemented_types:
            assert impl_type in enum_values, f"Missing enum value for {impl_type}"

    def test_weight_configuration_valid(self):
        """测试权重配置有效性"""
        analyzer = MultidimensionalRadarAnalyzer(Mock(), Mock())

        weights = analyzer.dimension_weights
        total_weight = sum(weights.values())

        # Weights should sum to approximately 1.0
        assert abs(total_weight - 1.0) < 0.001, f"Total weight {total_weight} should be 1.0"

        # All weights should be positive
        for weight in weights.values():
            assert weight > 0, "All weights should be positive"
