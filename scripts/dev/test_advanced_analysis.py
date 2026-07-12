"""测试高级量化分析功能
Test script for the advanced quantitative analysis features
"""

import asyncio
import os
import sys


# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.advanced_analysis import AdvancedAnalysisEngine, AnalysisType
from src.core import MyStocksUnifiedManager


async def test_fundamental_analysis():
    """测试基本面分析"""
    print("🔍 测试基本面分析...")

    # 初始化分析引擎
    data_manager = MyStocksUnifiedManager()
    analysis_engine = AdvancedAnalysisEngine(data_manager)

    try:
        # 执行基本面分析
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            analysis_engine.comprehensive_analysis,
            "600000",  # 浦发银行
            [AnalysisType.FUNDAMENTAL],
            {"periods": 2, "include_valuation": True, "include_comparison": False, "include_raw_data": False},
        )

        print("✅ 基本面分析完成")
        if "fundamental" in result:
            fundamental = result["fundamental"]
            scores = fundamental.scores
            recommendations = fundamental.recommendations

            print(f"   📊 综合得分: {scores.get('fundamental_score', 0):.1f}")
            print(f"   🏷️  评级: {recommendations.get('rating', 'N/A')}")
            print(f"   💡 建议: {recommendations.get('investment_suggestion', 'N/A')}")

            # 显示维度得分
            dimension_scores = scores.get("dimension_scores", {})
            print("   📈 维度得分:")
            for dim, score in dimension_scores.items():
                print(f"      {dim}: {score:.1f}")

        return True

    except Exception as e:
        print(f"❌ 基本面分析失败: {e}")
        return False


async def test_technical_analysis():
    """测试技术分析"""
    print("\n📈 测试技术分析...")

    # 初始化分析引擎
    data_manager = MyStocksUnifiedManager()
    analysis_engine = AdvancedAnalysisEngine(data_manager)

    try:
        # 执行技术分析
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            analysis_engine.comprehensive_analysis,
            "600000",
            [AnalysisType.TECHNICAL],
            {
                "timeframes": ["1d"],
                "include_patterns": False,
                "include_regime": True,
                "signal_threshold": 0.5,
                "include_raw_data": False,
            },
        )

        print("✅ 技术分析完成")
        if "technical" in result:
            technical = result["technical"]
            scores = technical.scores
            recommendations = technical.recommendations

            print(f"   📊 信号强度: {scores.get('signal_strength', 0):.2f}")
            print(f"   🎯 主信号: {recommendations.get('primary_signal', 'hold')}")
            print(f"   📈 趋势强度: {scores.get('trend_strength', 0):.1f}")
            print(f"   🌊 波动率水平: {scores.get('volatility_level', 0):.1f}")

            # 显示信号
            signals = technical.signals
            print(f"   🔔 检测到 {len(signals)} 个信号")
            for signal in signals[:3]:  # 显示前3个
                print(f"      {signal.get('indicator', 'N/A')}: {signal.get('message', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ 技术分析失败: {e}")
        return False


async def test_comprehensive_analysis():
    """测试综合分析"""
    print("\n🎯 测试综合分析...")

    # 初始化分析引擎
    data_manager = MyStocksUnifiedManager()
    analysis_engine = AdvancedAnalysisEngine(data_manager)

    try:
        # 执行综合分析
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            analysis_engine.comprehensive_analysis,
            "600000",
            None,  # 所有分析类型
            {
                "periods": 2,
                "include_valuation": False,
                "include_comparison": False,
                "timeframes": ["1d"],
                "include_patterns": False,
                "include_regime": True,
                "signal_threshold": 0.5,
                "include_raw_data": False,
            },
        )

        print("✅ 综合分析完成")
        print(f"   📊 执行了 {len(result)} 种分析类型")

        # 显示每种分析的结果摘要
        for analysis_type, analysis_result in result.items():
            if hasattr(analysis_result, "scores") and analysis_result.scores:
                primary_score = list(analysis_result.scores.values())[0] if analysis_result.scores else 0
                print(f"   {analysis_type}: 得分 {primary_score}")

        return True

    except Exception as e:
        print(f"❌ 综合分析失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 MyStocks 高级量化分析功能测试")
    print("=" * 50)

    # 测试结果
    results = []

    # 测试基本面分析
    results.append(await test_fundamental_analysis())

    # 测试技术分析
    results.append(await test_technical_analysis())

    # 测试综合分析
    results.append(await test_comprehensive_analysis())

    # 输出测试总结
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    print(f"   ✅ 通过: {sum(results)}/{len(results)}")

    if all(results):
        print("🎉 所有测试通过！高级量化分析功能正常工作。")
        return True
    print("⚠️  部分测试失败，请检查配置和数据源。")
    return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
