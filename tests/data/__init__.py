"""
测试数据管理模块

提供全面的测试数据管理功能，包括：
- 数据生成和管理
- 数据质量分析
- 数据优化和压缩
- 数据生命周期管理
"""

from .test_data_optimizer import (
    DataQualityMetrics,
    CompressionResult,
    DataOptimizationStrategy,
    TestDataOptimizer,
)

# 导出主要类和函数
__all__ = [
    "TestDataOptimizer",
    "DataQualityMetrics",
    "CompressionResult",
    "DataOptimizationStrategy",
    # 便捷函数
    "create_data_optimization_session",
    "optimize_test_data_profile",
    "analyze_data_quality",
]


def create_data_optimization_session(data_manager=None) -> TestDataOptimizer:
    """创建数据优化会话"""
    from ..ai.test_data_manager import AITestDataManager

    if data_manager is None:
        data_manager = AITestDataManager()

    return TestDataOptimizer(data_manager)


async def optimize_test_data_profile(profile_name: str, data_manager=None) -> dict:
    """优化测试数据档案

    Args:
        profile_name: 数据档案名称
        data_manager: 数据管理器实例

    Returns:
        优化结果字典
    """
    optimizer = create_data_optimization_session(data_manager)
    return await optimizer.optimize_test_data(profile_name)


async def analyze_data_quality(profile_name: str, data_manager=None) -> dict:
    """分析数据质量

    Args:
        profile_name: 数据档案名称
        data_manager: 数据管理器实例

    Returns:
        质量分析结果
    """
    from ..ai.test_data_manager import AITestDataManager

    if data_manager is None:
        data_manager = AITestDataManager()

    optimizer = TestDataOptimizer(data_manager)
    metrics = await optimizer.analyze_data_quality(profile_name)

    return {
        "profile_name": profile_name,
        "metrics": metrics.__dict__,
        "quality_grade": _get_quality_grade(metrics.overall_quality),
        "recommendations": _get_quality_recommendations(metrics),
    }


def _get_quality_grade(overall_quality: float) -> str:
    """获取质量等级"""
    if overall_quality >= 0.9:
        return "优秀"
    elif overall_quality >= 0.8:
        return "良好"
    elif overall_quality >= 0.7:
        return "中等"
    elif overall_quality >= 0.6:
        return "待改进"
    else:
        return "较差"


def _get_quality_recommendations(metrics: DataQualityMetrics) -> list:
    """获取质量建议"""
    recommendations = []

    if metrics.completeness_score < 0.8:
        recommendations.append("数据完整性不足，建议补充缺失字段")

    if metrics.consistency_score < 0.8:
        recommendations.append("数据一致性较差，建议统一数据格式")

    if metrics.accuracy_score < 0.8:
        recommendations.append("数据准确性需要提升，建议添加验证规则")

    if metrics.timeliness_score < 0.8:
        recommendations.append("数据时效性有待提高，建议优化更新频率")

    if metrics.duplicate_ratio > 0.1:
        recommendations.append("检测到重复数据，建议进行去重处理")

    return recommendations


# 项目示例用法
def create_my_stocks_data_context():
    """创建MyStocks项目数据上下文"""
    return {
        "project_name": "MyStocks",
        "data_profiles": [
            {
                "name": "market_data",
                "description": "市场测试数据",
                "size": 1000,
                "constraints": {
                    "symbols": ["AAPL", "GOOGL", "MSFT"],
                    "date_range": "2025-01-01:2025-12-12",
                    "data_types": ["price", "volume", "timestamp"],
                },
            },
            {
                "name": "trading_data",
                "description": "交易测试数据",
                "size": 500,
                "constraints": {
                    "account_types": ["cash", "margin"],
                    "order_types": ["market", "limit"],
                    "status_codes": [0, 1, 2, 3],
                },
            },
            {
                "name": "user_data",
                "description": "用户测试数据",
                "size": 100,
                "constraints": {
                    "user_roles": ["admin", "trader", "viewer"],
                    "account_status": ["active", "inactive", "suspended"],
                },
            },
        ],
        "optimization_goals": {
            "storage_reduction": 0.3,  # 30%存储空间减少
            "quality_improvement": 0.2,  # 20%质量提升
            "performance_optimization": True,
        },
    }


async def demo_data_optimization():
    """演示数据优化功能"""
    print("📊 测试数据优化演示")

    # 1. 创建数据上下文
    context = create_my_stocks_data_context()

    # 2. 创建优化器
    optimizer = create_data_optimization_session()

    # 3. 优化每个数据档案
    results = {}
    for profile in context["data_profiles"]:
        print(f"\n🔧 优化数据档案: {profile['name']}")
        result = await optimizer.optimize_test_data(profile["name"])
        results[profile["name"]] = result

        # 显示优化结果
        if "quality_improvement" in result:
            print(f"  质量改进: {result['quality_improvement']:.2%}")
        if "compression_ratio" in result:
            print(f"  压缩比率: {result['compression_ratio']:.2%}")

    # 4. 显示总体统计
    print("\n=== 优化统计 ===")
    stats = await optimizer.get_optimization_statistics()
    print(f"总优化次数: {stats['total_optimizations']}")
    print(f"成功率: {stats['success_rate']:.2%}")
    print(f"平均质量改进: {stats['average_quality_improvement']:.2%}")

    # 5. 清理缓存
    cleanup_result = await optimizer.cleanup_optimization_cache()
    print(f"缓存清理: 清理了 {cleanup_result['cleaned_entries']} 个条目")


if __name__ == "__main__":
    # 运行演示
    import asyncio

    asyncio.run(demo_data_optimization())
