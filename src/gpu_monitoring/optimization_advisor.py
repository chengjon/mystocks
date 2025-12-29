from typing import List, Dict
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class OptimizationRecommendation(BaseModel):
    title: str
    category: str
    severity: str
    description: str
    expected_improvement: str
    action_steps: List[str]


class OptimizationAdvisor:
    def __init__(self):
        pass

    def analyze_and_recommend(self, gpu_metrics, perf_metrics, stats_24h: Dict) -> List[OptimizationRecommendation]:
        recommendations = []

        if stats_24h["avg_utilization"] < 30:
            recommendations.append(
                OptimizationRecommendation(
                    title="GPU利用率过低",
                    category="efficiency",
                    severity="warning",
                    description=f"过去24小时平均GPU利用率仅{stats_24h['avg_utilization']:.1f}%,存在资源浪费",
                    expected_improvement="提升利用率可降低每GFLOP成本",
                    action_steps=[
                        "增加批处理大小 (batch_size)",
                        "并行执行多个回测任务",
                        "检查是否有CPU瓶颈限制GPU性能",
                    ],
                )
            )

        if stats_24h["max_temperature"] > 85:
            recommendations.append(
                OptimizationRecommendation(
                    title="温度过高警告",
                    category="temperature",
                    severity="critical",
                    description=f"GPU最高温度达到{stats_24h['max_temperature']:.1f}°C,可能影响性能和寿命",
                    expected_improvement="降温可提升3-5%性能并延长硬件寿命",
                    action_steps=[
                        "检查机箱风扇运行状态",
                        "清理GPU散热器灰尘",
                        "降低GPU功耗限制 (power_limit)",
                        "考虑增加机箱散热风扇",
                    ],
                )
            )

        if gpu_metrics.memory_utilization < 50:
            recommendations.append(
                OptimizationRecommendation(
                    title="显存利用率较低",
                    category="memory",
                    severity="info",
                    description=f"当前显存利用率{gpu_metrics.memory_utilization:.1f}%,可增加数据批处理大小",
                    expected_improvement="提升显存利用率可提高10-20%吞吐量",
                    action_steps=["增加batch_size (当前可能偏小)", "减少内存池预留空间", "预加载更多数据到显存"],
                )
            )

        if perf_metrics.overall_speedup < 50:
            recommendations.append(
                OptimizationRecommendation(
                    title="加速比低于预期",
                    category="performance",
                    severity="warning",
                    description=f"当前综合加速比{perf_metrics.overall_speedup:.2f}x,远低于目标68.58x",
                    expected_improvement="优化算法可达到目标加速比",
                    action_steps=[
                        "检查是否使用Strassen算法 (O(n^2.807))",
                        "启用CUDA流并行",
                        "使用分块矩阵乘法优化大矩阵",
                        "检查GPU驱动版本是否最新",
                    ],
                )
            )

        if perf_metrics.cache_hit_rate < 80:
            recommendations.append(
                OptimizationRecommendation(
                    title="缓存命中率偏低",
                    category="performance",
                    severity="info",
                    description=f"内存池缓存命中率{perf_metrics.cache_hit_rate:.1f}%,存在优化空间",
                    expected_improvement="提升缓存命中率可减少30%内存分配开销",
                    action_steps=["增加内存池大小", "优化内存块重用策略", "预分配常用尺寸内存块"],
                )
            )

        return recommendations
