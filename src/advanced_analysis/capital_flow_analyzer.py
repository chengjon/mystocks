"""
Capital Flow Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台资金流向与主力控盘分析功能

This module provides comprehensive capital flow analysis including:
- Capital flow clustering and pattern analysis
- Main force control detection and analysis
- Capital flow correlation and network analysis
- Institutional vs retail flow dynamics
- Smart money tracking and identification
"""

import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType, BaseAnalyzer

# GPU acceleration support
try:
    import cudf
    from cuml import KMeans

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    try:
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        warnings.warn("Neither GPU nor CPU clustering libraries available. Capital flow analysis will be limited.")


@dataclass
class CapitalFlowCluster:
    """资金流向聚类结果"""

    cluster_id: int
    cluster_size: int  # 聚类中股票数量
    centroid_flow: float  # 聚类中心资金流向
    avg_institutional_flow: float  # 平均机构资金流向
    avg_retail_flow: float  # 平均散户资金流向
    cluster_stocks: List[str]  # 聚类中的股票列表
    flow_pattern: str  # 资金流向模式
    confidence: float  # 聚类置信度


@dataclass
class MainForceControl:
    """主力控盘分析"""

    stock_code: str
    control_degree: float  # 控盘程度 (0-1)
    main_force_type: str  # 主力类型
    concentration_ratio: float  # 资金集中度
    sustained_period: int  # 持续控盘周期
    control_stability: float  # 控盘稳定性
    flow_predictability: float  # 资金流向可预测性
    institutional_dominance: float  # 机构主导程度
    control_signals: List[str]  # 控盘信号列表


@dataclass
class FlowCorrelationNetwork:
    """资金流向相关性网络"""

    correlation_matrix: pd.DataFrame
    strong_correlations: List[Tuple[str, str, float]]  # (stock1, stock2, correlation)
    flow_clusters: List[CapitalFlowCluster]
    network_density: float  # 网络密度
    dominant_flows: List[str]  # 主要资金流向方向
    risk_contagion_potential: float  # 风险传染潜力


@dataclass
class SmartMoneyIndicator:
    """聪明钱指标"""

    stock_code: str
    smart_money_score: float  # 聪明钱评分 (0-1)
    institutional_accumulation: float  # 机构建仓强度
    insider_activity: float  # 内部人活动强度
    whale_transactions: float  # 大户交易占比
    flow_divergence: float  # 资金流背离程度
    timing_quality: float  # 择时质量
    conviction_signals: List[str]  # 坚定信号


class CapitalFlowAnalyzer(BaseAnalyzer):
    """
    资金流向分析器

    提供全面的资金流向与主力控盘分析，包括：
    - 资金流向聚类和模式分析
    - 主力控盘能力检测
    - 资金流向相关性和网络分析
    - 机构vs散户资金动态
    - 聪明钱追踪和识别
    """


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
        print(f"Error getting capital flow data for {stock_code}: {e}")
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
        print(f"Error in flow clustering analysis: {e}")
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
            print(f"Error in K-means clustering with {n_clusters} clusters: {e}")
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
        print(f"Error in main force control analysis: {e}")
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


def _analyze_smart_money(self, stock_code: str, capital_flow_data: pd.DataFrame) -> SmartMoneyIndicator:
    """分析聪明钱指标"""
    try:
        # 计算聪明钱评分
        smart_money_score = self._calculate_smart_money_score(capital_flow_data)

        # 计算机构建仓强度
        institutional_accumulation = self._calculate_institutional_accumulation(capital_flow_data)

        # 计算内部人活动强度
        insider_activity = self._calculate_insider_activity(capital_flow_data)

        # 计算大户交易占比
        whale_transactions = self._calculate_whale_transactions(capital_flow_data)

        # 计算资金流背离程度
        flow_divergence = self._calculate_flow_divergence(capital_flow_data)

        # 计算择时质量
        timing_quality = self._calculate_timing_quality(capital_flow_data)

        # 生成坚定信号
        conviction_signals = self._generate_conviction_signals(
            smart_money_score, institutional_accumulation, flow_divergence, timing_quality
        )

        return SmartMoneyIndicator(
            stock_code=stock_code,
            smart_money_score=smart_money_score,
            institutional_accumulation=institutional_accumulation,
            insider_activity=insider_activity,
            whale_transactions=whale_transactions,
            flow_divergence=flow_divergence,
            timing_quality=timing_quality,
            conviction_signals=conviction_signals,
        )

    except Exception as e:
        print(f"Error in smart money analysis: {e}")
        return SmartMoneyIndicator(
            stock_code=stock_code,
            smart_money_score=0.0,
            institutional_accumulation=0.0,
            insider_activity=0.0,
            whale_transactions=0.0,
            flow_divergence=0.0,
            timing_quality=0.0,
            conviction_signals=[],
        )


def _calculate_smart_money_score(self, data: pd.DataFrame) -> float:
    """计算聪明钱评分"""
    if data.empty:
        return 0.0

    # 综合多个指标计算聪明钱评分
    institutional_score = self._calculate_institutional_accumulation(data)
    divergence_score = 1 - self._calculate_flow_divergence(data)  # 背离程度取反
    timing_score = self._calculate_timing_quality(data)
    concentration_score = self._calculate_concentration_ratio(data)

    # 加权计算
    weights = [0.4, 0.3, 0.2, 0.1]  # 机构、背离、择时、集中度
    scores = [institutional_score, divergence_score, timing_score, concentration_score]

    smart_money_score = sum(w * s for w, s in zip(weights, scores))
    return min(smart_money_score, 1.0)


def _calculate_institutional_accumulation(self, data: pd.DataFrame) -> float:
    """计算机构建仓强度"""
    if data.empty:
        return 0.0

    # 计算机构资金净流入占比
    main_net_flow = data["main_inflow"] - data["main_outflow"]
    total_net_flow = data["net_flow"]

    accumulation_ratio = (main_net_flow > 0).sum() / len(main_net_flow)
    accumulation_strength = main_net_flow[main_net_flow > 0].mean() / (abs(total_net_flow).mean() + 1e-8)

    return min(accumulation_ratio * accumulation_strength, 1.0)


def _calculate_insider_activity(self, data: pd.DataFrame) -> float:
    """计算内部人活动强度"""
    # 简化的内部人活动计算
    # 实际应该基于股东增减持数据
    flow_volatility = data["net_flow"].std() / (abs(data["net_flow"].mean()) + 1e-8)
    return min(flow_volatility, 1.0)


def _calculate_whale_transactions(self, data: pd.DataFrame) -> float:
    """计算大户交易占比"""
    # 计算主力资金占比
    main_total = data["main_inflow"] + data["main_outflow"]
    retail_total = data["retail_inflow"] + data["retail_outflow"]
    total_flow = main_total + retail_total

    whale_ratio = main_total.sum() / (total_flow.sum() + 1e-8)
    return min(whale_ratio, 1.0)


def _calculate_flow_divergence(self, data: pd.DataFrame) -> float:
    """计算资金流背离程度"""
    if len(data) < 10:
        return 0.0

    # 计算价格趋势和资金流向的背离
    price_trend = data["close"].pct_change().rolling(window=5).mean()
    flow_trend = data["net_flow"].rolling(window=5).mean()

    # 计算相关系数
    correlation = price_trend.corr(flow_trend) if len(price_trend.dropna()) > 1 else 0

    # 背离程度 = 1 - |相关系数|
    divergence = 1 - abs(correlation)
    return min(divergence, 1.0)


def _calculate_timing_quality(self, data: pd.DataFrame) -> float:
    """计算择时质量"""
    if len(data) < 10:
        return 0.0

    # 计算资金流入时机与价格变动的关系
    price_changes = data["close"].pct_change()
    net_flows = data["net_flow"]

    # 计算流入时机与后续价格变动的相关性
    inflow_timing = net_flows.shift(-1)  # 次日价格变动
    timing_correlation = price_changes.corr(net_flows) if len(price_changes.dropna()) > 1 else 0

    timing_quality = (timing_correlation + 1) / 2  # 转换为0-1范围
    return timing_quality


def _generate_conviction_signals(
    self, smart_money_score: float, institutional_accumulation: float, flow_divergence: float, timing_quality: float
) -> List[str]:
    """生成坚定信号"""
    signals = []

    if smart_money_score > 0.8:
        signals.append("聪明钱高度认可")
    elif smart_money_score > 0.6:
        signals.append("聪明钱较为认可")

    if institutional_accumulation > self.smart_money_params["accumulation_threshold"]:
        signals.append("机构持续建仓")

    if flow_divergence < 0.3:
        signals.append("资金流与价格趋势一致")

    if timing_quality > 0.7:
        signals.append("择时质量优秀")

    return signals


def _analyze_market_context(self, capital_flow_data: pd.DataFrame) -> Dict[str, Any]:
    """分析市场背景"""
    # 简化的市场背景分析
    return {"market_sentiment": "neutral", "sector_rotation": "balanced", "risk_appetite": "moderate"}


def _calculate_capital_flow_scores(
    self,
    data: pd.DataFrame,
    clusters: List[CapitalFlowCluster],
    control: MainForceControl,
    smart_money: SmartMoneyIndicator,
) -> Dict[str, float]:
    """计算资金流向分析得分"""
    scores = {}

    try:
        # 资金流向强度得分
        if not data.empty:
            avg_net_flow = abs(data["net_flow"].mean())
            flow_volatility = data["net_flow"].std()
            flow_strength_score = min(avg_net_flow / (flow_volatility + 1e-8) / 5, 1.0)
            scores["flow_strength"] = flow_strength_score

        # 聚类有效性得分
        if clusters:
            avg_cluster_confidence = np.mean([c.confidence for c in clusters])
            scores["clustering_effectiveness"] = avg_cluster_confidence

        # 主力控盘得分
        if control:
            scores["control_degree"] = control.control_degree
            scores["control_stability"] = control.control_stability

        # 聪明钱得分
        if smart_money:
            scores["smart_money_score"] = smart_money.smart_money_score
            scores["timing_quality"] = smart_money.timing_quality

        # 综合得分
        weights = {
            "flow_strength": 0.3,
            "clustering_effectiveness": 0.2,
            "control_degree": 0.25,
            "smart_money_score": 0.25,
        }

        overall_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        scores["overall_score"] = overall_score

    except Exception as e:
        print(f"Error calculating capital flow scores: {e}")
        scores = {"overall_score": 0.0, "error": True}

    return scores


def _generate_capital_flow_signals(
    self,
    data: pd.DataFrame,
    clusters: List[CapitalFlowCluster],
    control: MainForceControl,
    smart_money: SmartMoneyIndicator,
) -> List[Dict[str, Any]]:
    """生成资金流向信号"""
    signals = []

    # 主力控盘信号
    if control and control.control_degree > 0.6:
        severity = "high" if control.control_degree > 0.8 else "medium"
        signals.append(
            {
                "type": "main_force_control",
                "severity": severity,
                "message": f"主力控盘程度高 ({control.control_degree:.2f}) - {control.main_force_type}",
                "details": {
                    "control_degree": control.control_degree,
                    "concentration_ratio": control.concentration_ratio,
                    "sustained_period": control.sustained_period,
                    "control_signals": control.control_signals[:3],
                },
            }
        )

    # 聪明钱信号
    if smart_money and smart_money.smart_money_score > 0.7:
        signals.append(
            {
                "type": "smart_money_signal",
                "severity": "high",
                "message": f"聪明钱高度认可 ({smart_money.smart_money_score:.2f})",
                "details": {
                    "institutional_accumulation": smart_money.institutional_accumulation,
                    "timing_quality": smart_money.timing_quality,
                    "conviction_signals": smart_money.conviction_signals[:3],
                },
            }
        )

    # 聚类信号
    if clusters:
        dominant_cluster = max(clusters, key=lambda c: c.cluster_size)
        if dominant_cluster.confidence > 0.7:
            signals.append(
                {
                    "type": "flow_clustering",
                    "severity": "medium",
                    "message": f"资金流向聚类模式: {dominant_cluster.flow_pattern}",
                    "details": {
                        "cluster_size": dominant_cluster.cluster_size,
                        "flow_pattern": dominant_cluster.flow_pattern,
                        "confidence": dominant_cluster.confidence,
                    },
                }
            )

    # 资金流向强度信号
    if not data.empty:
        recent_flow = data["net_flow"].iloc[-1] if len(data) > 0 else 0
        avg_flow = data["net_flow"].mean() if len(data) > 0 else 0

        if abs(recent_flow) > abs(avg_flow) * 2:
            direction = "流入" if recent_flow > 0 else "流出"
            severity = "high" if abs(recent_flow) > abs(avg_flow) * 3 else "medium"
            signals.append(
                {
                    "type": "flow_intensity",
                    "severity": severity,
                    "message": f"资金大幅{direction} ({recent_flow:,.0f})",
                    "details": {
                        "recent_flow": recent_flow,
                        "avg_flow": avg_flow,
                        "intensity_ratio": abs(recent_flow) / abs(avg_flow),
                    },
                }
            )

    return signals


def _generate_capital_flow_recommendations(
    self, control: MainForceControl, smart_money: SmartMoneyIndicator, market_context: Dict[str, Any]
) -> Dict[str, Any]:
    """生成资金流向投资建议"""
    recommendations = {}

    try:
        # 基于控盘情况的建议
        if control:
            if control.control_degree > 0.8:
                primary_signal = "hold"
                action = "主力高度控盘，观望为主"
                confidence = "high"
            elif control.control_degree > 0.6:
                primary_signal = "follow"
                action = "主力控盘明显，跟随主力操作"
                confidence = "medium"
            else:
                primary_signal = "normal"
                action = "控盘程度正常，可按常规策略操作"
                confidence = "medium"
        else:
            primary_signal = "unknown"
            action = "控盘情况不明，谨慎操作"
            confidence = "low"

        # 考虑聪明钱因素
        if smart_money and smart_money.smart_money_score > 0.8:
            action += " (聪明钱高度认可，可适当乐观)"
            confidence = "high"
        elif smart_money and smart_money.smart_money_score < 0.3:
            action += " (聪明钱认可度低，需谨慎)"
            confidence = "low"

        # 考虑市场背景
        market_sentiment = market_context.get("market_sentiment", "neutral")
        if market_sentiment == "bullish":
            action += " (市场情绪乐观)"
        elif market_sentiment == "bearish":
            action += " (市场情绪谨慎)"

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "control_analysis": {
                    "control_degree": control.control_degree if control else 0,
                    "main_force_type": control.main_force_type if control else "unknown",
                },
                "smart_money_analysis": {
                    "smart_money_score": smart_money.smart_money_score if smart_money else 0,
                    "timing_quality": smart_money.timing_quality if smart_money else 0,
                },
                "market_context": market_context,
            }
        )

    except Exception as e:
        print(f"Error generating capital flow recommendations: {e}")
        recommendations = {
            "primary_signal": "hold",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_capital_flow_risk(
    self, data: pd.DataFrame, control: MainForceControl, smart_money: SmartMoneyIndicator
) -> Dict[str, Any]:
    """评估资金流向风险"""
    risk_assessment = {}

    try:
        # 流向波动风险
        if not data.empty:
            flow_volatility = data["net_flow"].std() / (abs(data["net_flow"].mean()) + 1e-8)
            if flow_volatility > 1.0:
                flow_volatility_risk = "high"
            elif flow_volatility > 0.5:
                flow_volatility_risk = "medium"
            else:
                flow_volatility_risk = "low"
        else:
            flow_volatility_risk = "unknown"

        # 控盘风险
        if control:
            if control.control_degree > 0.8:
                control_risk = "high"  # 过度控盘可能存在风险
            elif control.control_stability < 0.4:
                control_risk = "high"  # 控盘不稳定
            else:
                control_risk = "low"
        else:
            control_risk = "medium"

        # 聪明钱风险
        if smart_money:
            if smart_money.smart_money_score < 0.3:
                smart_money_risk = "high"  # 聪明钱不认可
            elif smart_money.flow_divergence > 0.7:
                smart_money_risk = "medium"  # 存在背离
            else:
                smart_money_risk = "low"
        else:
            smart_money_risk = "medium"

        # 综合风险等级
        risk_scores = {"high": 3, "medium": 2, "low": 1, "unknown": 2}
        avg_risk_score = np.mean(
            [
                risk_scores.get(flow_volatility_risk, 2),
                risk_scores.get(control_risk, 2),
                risk_scores.get(smart_money_risk, 2),
            ]
        )

        if avg_risk_score > 2.5:
            overall_risk = "high"
        elif avg_risk_score > 1.5:
            overall_risk = "medium"
        else:
            overall_risk = "low"

        risk_assessment.update(
            {
                "overall_risk_level": overall_risk,
                "flow_volatility_risk": flow_volatility_risk,
                "control_risk": control_risk,
                "smart_money_risk": smart_money_risk,
                "risk_factors": [
                    "资金流向波动大" if flow_volatility_risk == "high" else None,
                    "主力过度控盘" if control_risk == "high" else None,
                    "聪明钱认可度低" if smart_money_risk == "high" else None,
                ],
                "risk_factors": [
                    f
                    for f in [
                        "资金流向波动大" if flow_volatility_risk == "high" else None,
                        "主力过度控盘" if control_risk == "high" else None,
                        "聪明钱认可度低" if smart_money_risk == "high" else None,
                    ]
                    if f is not None
                ],
            }
        )

    except Exception as e:
        print(f"Error assessing capital flow risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.CAPITAL_FLOW,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"资金流向分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )
