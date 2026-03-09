"""Shared methods for `capital_flow_cluster.py`."""

from __future__ import annotations

import logging
import warnings
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.advanced_analysis import AnalysisResult, AnalysisType
from src.advanced_analysis.capital_flow_analyzer._capital_flow_cluster_tail import CapitalFlowClusterTailMixin
from src.advanced_analysis.capital_flow_analyzer._generate_capital_flow_signals import CapitalFlowSignalMixin
from src.advanced_analysis.capital_flow_analyzer.capital_flow_models import (
    CapitalFlowCluster,
    MainForceControl,
)

try:
    import cudf

    GPU_AVAILABLE = True
except ImportError:
    cudf = None
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Capital flow clustering will run on CPU.")

logger = logging.getLogger(__name__)


class CapitalFlowClusterMixin(CapitalFlowSignalMixin, CapitalFlowClusterTailMixin):
    def __init__(self, data_manager, gpu_manager=None):
        super().__init__(data_manager, gpu_manager)
    
        # 聚类参数配置
        self.clustering_params = {
            "n_clusters_range": range(2, 8),  # 聚类数量范围
            "min_samples_dbscan": 3,  # DBSCAN最小样本数
            "eps_dbscan": 0.3,  # DBSCAN邻域半径
            "random_state": 42,
        }
    
        # 主力控盘阈值
        self.control_thresholds = {
            "high_control": 0.7,  # 高控盘阈值
            "medium_control": 0.5,  # 中等控盘阈值
            "low_control": 0.3,  # 低控盘阈值
            "concentration_threshold": 0.6,  # 集中度阈值
            "sustained_period": 10,  # 持续周期阈值
        }
    
        # 聪明钱识别参数
        self.smart_money_params = {
            "institutional_threshold": 0.7,  # 机构资金占比阈值
            "accumulation_threshold": 0.6,  # 建仓强度阈值
            "divergence_threshold": 0.5,  # 背离程度阈值
            "timing_window": 20,  # 择时窗口
        }
    
        # 分析时间窗口
        self.analysis_windows = {
            "short_term": 5,  # 短期：5天
            "medium_term": 20,  # 中期：20天
            "long_term": 60,  # 长期：60天
        }
    
    
    def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
        """
        执行资金流向分析
    
        Args:
            stock_code: 股票代码
            **kwargs: 分析参数
                - analysis_period: 分析周期 (默认: 30天)
                - include_clustering: 是否包含聚类分析 (默认: True)
                - include_control_analysis: 是否包含控盘分析 (默认: True)
                - include_smart_money: 是否包含聪明钱分析 (默认: True)
                - market_context: 是否包含市场背景分析 (默认: True)
    
        Returns:
            AnalysisResult: 分析结果
        """
        analysis_period = kwargs.get("analysis_period", 30)
        include_clustering = kwargs.get("include_clustering", True)
        include_control_analysis = kwargs.get("include_control_analysis", True)
        include_smart_money = kwargs.get("include_smart_money", True)
        market_context = kwargs.get("market_context", True)
    
        try:
            # 获取资金流向数据
            capital_flow_data = self._get_capital_flow_data(stock_code, analysis_period)
    
            if capital_flow_data.empty:
                return self._create_error_result(stock_code, "No capital flow data available for analysis")
    
            # 资金流向聚类分析
            flow_clusters = []
            if include_clustering:
                flow_clusters = self._analyze_flow_clustering(capital_flow_data)
    
            # 主力控盘分析
            main_force_control = None
            if include_control_analysis:
                main_force_control = self._analyze_main_force_control(stock_code, capital_flow_data)
    
            # 聪明钱分析
            smart_money_indicator = None
            if include_smart_money:
                smart_money_indicator = self._analyze_smart_money(stock_code, capital_flow_data)
    
            # 市场背景分析
            market_context_data = {}
            if market_context:
                market_context_data = self._analyze_market_context(capital_flow_data)
    
            # 计算综合得分
            scores = self._calculate_capital_flow_scores(
                capital_flow_data, flow_clusters, main_force_control, smart_money_indicator
            )
    
            # 生成信号
            signals = self._generate_capital_flow_signals(
                capital_flow_data, flow_clusters, main_force_control, smart_money_indicator
            )
    
            # 投资建议
            recommendations = self._generate_capital_flow_recommendations(
                main_force_control, smart_money_indicator, market_context_data
            )
    
            # 风险评估
            risk_assessment = self._assess_capital_flow_risk(capital_flow_data, main_force_control, smart_money_indicator)
    
            # 元数据
            metadata = {
                "analysis_period_days": analysis_period,
                "data_points": len(capital_flow_data),
                "clusters_identified": len(flow_clusters),
                "main_force_control_degree": main_force_control.control_degree if main_force_control else 0,
                "smart_money_score": smart_money_indicator.smart_money_score if smart_money_indicator else 0,
                "flow_volatility": capital_flow_data["net_flow"].std() if "net_flow" in capital_flow_data.columns else 0,
                "dominant_force_type": main_force_control.main_force_type if main_force_control else "unknown",
                "analysis_timestamp": datetime.now(),
            }
    
            return AnalysisResult(
                analysis_type=AnalysisType.CAPITAL_FLOW,
                stock_code=stock_code,
                timestamp=datetime.now(),
                scores=scores,
                signals=signals,
                recommendations=recommendations,
                risk_assessment=risk_assessment,
                metadata=metadata,
                raw_data=capital_flow_data if kwargs.get("include_raw_data", False) else None,
            )
    
        except Exception as e:
            return self._create_error_result(stock_code, str(e))
    
    
    def _get_capital_flow_data(self, stock_code: str, days: int) -> pd.DataFrame:
        """获取资金流向数据"""
        try:
            from src.data_sources.factory import get_timeseries_source
    
            timeseries_source = get_timeseries_source(source_type="mock")
    
            # 获取资金流向数据
            capital_flow_data = timeseries_source.get_fund_flow(stock_code, days=days)
    
            if capital_flow_data.empty:
                # 如果没有真实数据，生成模拟数据
                capital_flow_data = self._generate_mock_capital_flow_data(stock_code, days)
    
            return capital_flow_data
    
        except Exception as e:
            logger.error("Error getting capital flow data for %s: %s", stock_code, e)
            # 返回模拟数据作为fallback
            return self._generate_mock_capital_flow_data(stock_code, days)
    
    
    def _generate_mock_capital_flow_data(self, stock_code: str, days: int) -> pd.DataFrame:
        """生成模拟资金流向数据"""
        np.random.seed(hash(stock_code) % 2**32)
    
        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        data = []
    
        base_flow = np.random.uniform(100000, 1000000)  # 基础资金量
    
        for i, date in enumerate(dates):
            # 生成有趋势的资金流向
            trend_factor = 1 + 0.1 * np.sin(i / 10)  # 周期性趋势
            random_factor = np.random.normal(1, 0.3)  # 随机波动
    
            main_inflow = base_flow * trend_factor * random_factor * np.random.uniform(0.3, 0.8)
            main_outflow = base_flow * trend_factor * random_factor * np.random.uniform(0.2, 0.7)
            retail_inflow = base_flow * trend_factor * random_factor * np.random.uniform(0.4, 1.0)
            retail_outflow = base_flow * trend_factor * random_factor * np.random.uniform(0.3, 0.9)
    
            net_flow = (main_inflow + retail_inflow) - (main_outflow + retail_outflow)
    
            data.append(
                {
                    "date": date,
                    "main_inflow": main_inflow,
                    "main_outflow": main_outflow,
                    "retail_inflow": retail_inflow,
                    "retail_outflow": retail_outflow,
                    "net_flow": net_flow,
                    "total_flow": main_inflow + main_outflow + retail_inflow + retail_outflow,
                    "flow_ratio": net_flow / (main_inflow + main_outflow + retail_inflow + retail_outflow + 1e-8),
                }
            )
    
        return pd.DataFrame(data).set_index("date")
    
    
    def _analyze_flow_clustering(self, capital_flow_data: pd.DataFrame) -> List[CapitalFlowCluster]:
        """分析资金流向聚类"""
        if capital_flow_data.empty or len(capital_flow_data) < 10:
            return []
    
        try:
            # 准备聚类特征
            features = self._extract_clustering_features(capital_flow_data)
    
            if features.empty or len(features) < 5:
                return []
    
            # 数据标准化
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features.values)
    
            # 使用K-means聚类
            clusters = self._perform_kmeans_clustering(scaled_features, features)
    
            # 转换为聚类结果
            flow_clusters = []
            for cluster_id, cluster_data in clusters.items():
                if len(cluster_data) > 0:
                    cluster = CapitalFlowCluster(
                        cluster_id=cluster_id,
                        cluster_size=len(cluster_data),
                        centroid_flow=cluster_data["net_flow"].mean(),
                        avg_institutional_flow=cluster_data["main_net_flow"].mean(),
                        avg_retail_flow=cluster_data["retail_net_flow"].mean(),
                        cluster_stocks=[f"stock_{i}" for i in range(len(cluster_data))],  # 模拟股票列表
                        flow_pattern=self._classify_flow_pattern(cluster_data),
                        confidence=self._calculate_cluster_confidence(cluster_data),
                    )
                    flow_clusters.append(cluster)
    
            return flow_clusters
    
        except Exception as e:
            logger.error("Error in flow clustering analysis: %s", e)
            return []
    
    
    def _extract_clustering_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """提取聚类特征"""
        features = pd.DataFrame(index=data.index)
    
        # 资金流向特征
        features["net_flow"] = data["net_flow"]
        features["flow_volatility"] = data["net_flow"].rolling(window=5).std()
        features["flow_trend"] = data["net_flow"].rolling(window=10).mean()
        features["main_net_flow"] = data["main_inflow"] - data["main_outflow"]
        features["retail_net_flow"] = data["retail_inflow"] - data["retail_outflow"]
        features["concentration_ratio"] = abs(features["main_net_flow"]) / (
            abs(features["main_net_flow"]) + abs(features["retail_net_flow"]) + 1e-8
        )
    
        # 流向模式特征
        features["flow_momentum"] = data["net_flow"].pct_change().rolling(window=3).mean()
        features["flow_persistence"] = (
            (np.sign(data["net_flow"]) == np.sign(data["net_flow"].shift(1))).astype(int).rolling(window=5).mean()
        )
    
        return features.dropna()
    
    
    def _perform_kmeans_clustering(
        self, scaled_features: np.ndarray, original_features: pd.DataFrame
    ) -> Dict[int, pd.DataFrame]:
        """执行K-means聚类"""
        best_clusters = {}
        best_score = -1
    
        for n_clusters in self.clustering_params["n_clusters_range"]:
            try:
                if GPU_AVAILABLE:
                    kmeans = KMeans(n_clusters=n_clusters, random_state=self.clustering_params["random_state"])
                    labels = kmeans.fit_predict(cudf.DataFrame(scaled_features))
                    labels = labels.to_numpy()
                else:
                    kmeans = KMeans(n_clusters=n_clusters, random_state=self.clustering_params["random_state"])
                    labels = kmeans.fit_predict(scaled_features)
    
                # 计算轮廓系数
                if len(set(labels)) > 1:
                    score = silhouette_score(scaled_features, labels)
                    if score > best_score:
                        best_score = score
    
                        # 分组数据
                        clusters = {}
                        for i, label in enumerate(labels):
                            if label not in clusters:
                                clusters[label] = []
                            clusters[label].append(original_features.iloc[i])
    
                        best_clusters = {label: pd.DataFrame(data) for label, data in clusters.items()}
    
            except Exception as e:
                logger.error("Error in K-means clustering with %s clusters: %s", n_clusters, e)
                continue
    
        return best_clusters
    
    
    def _classify_flow_pattern(self, cluster_data: pd.DataFrame) -> str:
        """分类资金流向模式"""
        avg_flow = cluster_data["net_flow"].mean()
        flow_volatility = cluster_data["net_flow"].std()
        concentration = cluster_data["concentration_ratio"].mean()
    
        if avg_flow > 0 and concentration > 0.6:
            return "institutional_accumulation"  # 机构建仓
        elif avg_flow > 0 and concentration < 0.4:
            return "retail_driven_rally"  # 散户推动反弹
        elif avg_flow < 0 and concentration > 0.6:
            return "institutional_distribution"  # 机构出货
        elif avg_flow < 0 and flow_volatility > abs(avg_flow) * 0.5:
            return "panic_selling"  # 恐慌性抛售
        elif abs(avg_flow) < flow_volatility * 0.3:
            return "consolidation"  # 震荡整理
        else:
            return "mixed_flow"  # 混合流向
    
    
    def _calculate_cluster_confidence(self, cluster_data: pd.DataFrame) -> float:
        """计算聚类置信度"""
        # 基于数据一致性和大小计算置信度
        size_confidence = min(len(cluster_data) / 20, 1.0)  # 样本大小置信度
        consistency_confidence = 1 - cluster_data["net_flow"].std() / (abs(cluster_data["net_flow"].mean()) + 1e-8)
    
        return min(size_confidence * consistency_confidence, 1.0)
    
    
    def _analyze_main_force_control(self, stock_code: str, capital_flow_data: pd.DataFrame) -> MainForceControl:
        """分析主力控盘情况"""
        try:
            # 计算控盘程度
            control_degree = self._calculate_control_degree(capital_flow_data)
    
            # 识别主力类型
            main_force_type = self._identify_main_force_type(capital_flow_data)
    
            # 计算资金集中度
            concentration_ratio = self._calculate_concentration_ratio(capital_flow_data)
    
            # 计算持续控盘周期
            sustained_period = self._calculate_sustained_period(capital_flow_data)
    
            # 计算控盘稳定性
            control_stability = self._calculate_control_stability(capital_flow_data)
    
            # 计算资金流向可预测性
            flow_predictability = self._calculate_flow_predictability(capital_flow_data)
    
            # 计算机构主导程度
            institutional_dominance = self._calculate_institutional_dominance(capital_flow_data)
    
            # 生成控盘信号
            control_signals = self._generate_control_signals(
                control_degree, concentration_ratio, sustained_period, control_stability
            )
    
            return MainForceControl(
                stock_code=stock_code,
                control_degree=control_degree,
                main_force_type=main_force_type,
                concentration_ratio=concentration_ratio,
                sustained_period=sustained_period,
                control_stability=control_stability,
                flow_predictability=flow_predictability,
                institutional_dominance=institutional_dominance,
                control_signals=control_signals,
            )
    
        except Exception as e:
            logger.error("Error in main force control analysis: %s", e)
            return MainForceControl(
                stock_code=stock_code,
                control_degree=0.0,
                main_force_type="unknown",
                concentration_ratio=0.0,
                sustained_period=0,
                control_stability=0.0,
                flow_predictability=0.0,
                institutional_dominance=0.0,
                control_signals=[],
            )
    
    
    def _calculate_control_degree(self, data: pd.DataFrame) -> float:
        """计算控盘程度"""
        if data.empty:
            return 0.0
    
        # 基于资金流向的一致性和强度计算控盘程度
        net_flows = data["net_flow"].values
    
        # 流向一致性
        flow_direction = np.sign(net_flows)
        direction_consistency = abs(np.mean(flow_direction))
    
        # 流向强度
        avg_flow = np.mean(np.abs(net_flows))
        flow_volatility = np.std(net_flows)
        flow_intensity = avg_flow / (flow_volatility + 1e-8)
    
        # 控盘程度 = 一致性 * 强度 * 时间权重
        control_degree = direction_consistency * min(flow_intensity / 10, 1.0)
    
        return min(control_degree, 1.0)
    
    
    def _identify_main_force_type(self, data: pd.DataFrame) -> str:
        """识别主力类型"""
        if data.empty:
            return "unknown"
    
        main_flow = data["main_inflow"].sum() - data["main_outflow"].sum()
        retail_flow = data["retail_inflow"].sum() - data["retail_outflow"].sum()
    
        main_ratio = abs(main_flow) / (abs(main_flow) + abs(retail_flow) + 1e-8)
    
        if main_ratio > 0.7:
            return "institutional_dominant"  # 机构主导
        elif main_ratio > 0.5:
            return "mixed_institutional"  # 混合机构
        elif main_ratio > 0.3:
            return "retail_influenced"  # 散户影响
        else:
            return "retail_dominant"  # 散户主导
    
    
    def _calculate_concentration_ratio(self, data: pd.DataFrame) -> float:
        """计算资金集中度"""
        if data.empty:
            return 0.0
    
        # 计算每日资金集中度
        main_total = data["main_inflow"] + data["main_outflow"]
        retail_total = data["retail_inflow"] + data["retail_outflow"]
        total_flow = main_total + retail_total
    
        concentration_ratios = main_total / (total_flow + 1e-8)
        return concentration_ratios.mean()
    
    
    def _calculate_sustained_period(self, data: pd.DataFrame) -> int:
        """计算持续控盘周期"""
        if data.empty:
            return 0
    
        # 计算连续同向资金流向的天数
        net_flows = data["net_flow"].values
        directions = np.sign(net_flows)
    
        # 找到最长的连续同向周期
        max_streak = 0
        current_streak = 1
    
        for i in range(1, len(directions)):
            if directions[i] == directions[i - 1] and directions[i] != 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
    
        return max_streak
    
    
    def _calculate_control_stability(self, data: pd.DataFrame) -> float:
        """计算控盘稳定性"""
        if data.empty:
            return 0.0
    
        # 计算资金流向的标准差相对平均值
        net_flows = data["net_flow"].values
        avg_flow = np.mean(np.abs(net_flows))
        flow_std = np.std(net_flows)
    
        stability = 1 - min(flow_std / (avg_flow + 1e-8), 1.0)
        return stability
    
    
    def _calculate_flow_predictability(self, data: pd.DataFrame) -> float:
        """计算资金流向可预测性"""
        if len(data) < 5:
            return 0.0
    
        # 使用自相关系数衡量可预测性
        net_flows = data["net_flow"].values
        autocorr = np.correlate(net_flows, net_flows, mode="full")
        center_idx = len(autocorr) // 2
    
        # 计算短期自相关强度
        short_term_autocorr = np.mean(autocorr[center_idx + 1 : center_idx + 6])  # 1-5天自相关
    
        predictability = min(abs(short_term_autocorr) / np.var(net_flows), 1.0)
        return predictability
    
    
    def _calculate_institutional_dominance(self, data: pd.DataFrame) -> float:
        """计算机构主导程度"""
        if data.empty:
            return 0.0
    
        # 计算机构资金占比
        main_total = (data["main_inflow"] + data["main_outflow"]).sum()
        retail_total = (data["retail_inflow"] + data["retail_outflow"]).sum()
        total_flow = main_total + retail_total
    
        return main_total / (total_flow + 1e-8) if total_flow > 0 else 0.0
    
    
    def _generate_control_signals(
        self, control_degree: float, concentration_ratio: float, sustained_period: int, control_stability: float
    ) -> List[str]:
        """生成控盘信号"""
        signals = []
    
        if control_degree > self.control_thresholds["high_control"]:
            signals.append("高度控盘")
        elif control_degree > self.control_thresholds["medium_control"]:
            signals.append("中等控盘")
        elif control_degree > self.control_thresholds["low_control"]:
            signals.append("轻度控盘")
    
        if concentration_ratio > self.control_thresholds["concentration_threshold"]:
            signals.append("资金高度集中")
    
        if sustained_period > self.control_thresholds["sustained_period"]:
            signals.append(f"持续控盘{sustained_period}天")
    
        if control_stability > 0.8:
            signals.append("控盘稳定性高")
        elif control_stability < 0.4:
            signals.append("控盘稳定性低")
    
        return signals
