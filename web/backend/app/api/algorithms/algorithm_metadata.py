"""
算法元数据辅助函数
"""

from __future__ import annotations

from typing import Any, Dict, List


def get_algorithm_description(algorithm: Any) -> str:
    """获取算法描述"""
    descriptions = {
        "svm": "支持向量机 - 基于间隔最大化原理的分类算法，适用于高维特征空间",
        "decision_tree": "决策树 - 基于特征分裂的树形分类算法，具有良好的可解释性",
        "naive_bayes": "朴素贝叶斯 - 基于概率统计的分类算法，适用于文本和特征独立的场景",
        "brute_force": "暴力匹配 - 基础字符串匹配算法，作为性能基准",
        "knuth_morris_pratt": "KMP算法 - 高效的单模式字符串匹配算法",
        "boyer_moore_horspool": "BMH算法 - 启发式字符串匹配算法，适合长文本",
        "aho_corasick": "Aho-Corasick - 多模式字符串匹配算法，支持同时查找多个模式",
        "hidden_markov_model": "隐马尔可夫模型 - 用于市场状态识别和转移预测",
        "bayesian_network": "贝叶斯网络 - 概率图模型，用于分析市场变量间的因果关系",
        "n_gram": "N-gram模型 - 序列分析模型，用于预测市场走势模式",
        "neural_network": "神经网络 - 深度学习模型，用于复杂的时间序列预测",
    }
    return descriptions.get(algorithm.value, "量化交易算法")


def get_algorithm_parameters(algorithm: Any) -> Dict[str, Any]:
    """获取算法参数规格"""
    base_params = {
        "gpu_accelerated": True,
        "input_format": "numerical_features",
        "output_format": "predictions_with_confidence",
    }

    specific_params = {
        "svm": {
            "kernel": ["linear", "rbf", "poly", "sigmoid"],
            "C": "float (0.1-100)",
            "gamma": ["scale", "auto", "float"],
            "max_iter": "int (-1 for unlimited)",
        },
        "decision_tree": {
            "max_depth": "int (None for unlimited)",
            "min_samples_split": "int",
            "criterion": ["gini", "entropy", "log_loss"],
        },
        "hmm": {
            "n_states": "int (2-10)",
            "n_features": "int",
            "covariance_type": ["full", "tied", "diag", "spherical"],
        },
        "neural_network": {
            "architecture": ["lstm", "gru", "cnn", "transformer"],
            "layers": "int (1-10)",
            "units": "int (32-1024)",
            "dropout": "float (0.0-0.5)",
        },
    }

    params = base_params.copy()
    if algorithm.value in specific_params:
        params["specific_parameters"] = specific_params[algorithm.value]

    return params


def get_algorithm_use_cases(algorithm: Any) -> List[str]:
    """获取算法应用场景"""
    use_cases = {
        "svm": ["股票买卖点预测", "市场趋势分类", "风险水平评估", "多资产配置决策"],
        "decision_tree": ["交易规则生成", "市场条件判断", "投资组合筛选", "风险控制策略"],
        "naive_bayes": ["市场情绪分析", "新闻事件分类", "基本面数据处理", "快速信号筛选"],
        "aho_corasick": ["多模式走势识别", "技术形态检测", "市场异常模式发现", "实时信号监控"],
        "hmm": ["牛熊市状态识别", "市场波动周期分析", "趋势转变预测", "风险状态监控"],
        "bayesian_network": ["市场因果关系分析", "多因子影响评估", "联动效应预测", "投资组合优化"],
        "n_gram": ["价格序列模式识别", "交易量变化预测", "市场周期分析", "短期走势预测"],
        "neural_network": ["长期趋势预测", "高频交易信号", "复杂市场模式学习", "自适应策略优化"],
    }

    return use_cases.get(algorithm.value, ["量化交易分析"])


def get_algorithm_performance(algorithm: Any) -> Dict[str, Any]:
    """获取算法性能特征"""
    performance = {
        "svm": {
            "gpu_speedup": "50-80x",
            "typical_accuracy": "75-90%",
            "training_time": "seconds to minutes",
            "memory_usage": "moderate",
        },
        "decision_tree": {
            "gpu_speedup": "10-20x",
            "typical_accuracy": "70-85%",
            "training_time": "seconds",
            "memory_usage": "low",
        },
        "hmm": {
            "gpu_speedup": "30-50x",
            "typical_accuracy": "80-95%",
            "training_time": "minutes",
            "memory_usage": "moderate",
        },
        "neural_network": {
            "gpu_speedup": "100-200x",
            "typical_accuracy": "85-95%",
            "training_time": "minutes to hours",
            "memory_usage": "high",
        },
    }

    return performance.get(
        algorithm.value,
        {
            "gpu_speedup": "varies",
            "typical_accuracy": "70-90%",
            "training_time": "varies",
            "memory_usage": "moderate",
        },
    )
