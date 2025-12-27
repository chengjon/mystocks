"""
AI测试工具包

提供全面的AI辅助测试功能，包括：
- 智能测试生成
- 数据分析
- 数据管理
- 测试集成
"""

from .test_ai_assisted_testing import (
    AITestGenerator,
    IntelligentTestOptimizer,
    AITestAssistant,
)
from .test_data_analyzer import AITestDataAnalyzer, AnomalyDetection, TrendPrediction
from .test_data_manager import AITestDataManager, TestDataProfile, DataGenerationRequest
from .test_integration_system import (
    AITestIntegrationSystem,
    TestOrchestrationConfig,
    TestExecutionPlan,
    TestExecutionResult,
    TestPhase,
    IntelligentTestPlanner,
    SmartTestExecutor,
)

# 导出所有主要类和函数
__all__ = [
    # 核心AI测试组件
    "AITestGenerator",
    "IntelligentTestOptimizer",
    "AITestAssistant",
    "AITestDataAnalyzer",
    "AITestDataManager",
    "AITestIntegrationSystem",
    # 数据模型
    "TestDataProfile",
    "DataGenerationRequest",
    "TestOrchestrationConfig",
    "TestExecutionPlan",
    "TestExecutionResult",
    "AnomalyDetection",
    "TrendPrediction",
    # 枚举
    "TestPhase",
    # 便捷函数
    "create_ai_testing_session",
    "run_ai_test_suite",
]


def create_ai_testing_session(config: dict = None) -> AITestIntegrationSystem:
    """创建AI测试会话"""
    if config is None:
        config = {
            "max_concurrent_tests": 5,
            "enable_ai_enhancement": True,
            "auto_optimize": True,
            "report_format": "comprehensive",
        }

    orchestration_config = TestOrchestrationConfig(**config)
    return AITestIntegrationSystem(orchestration_config)


async def run_ai_test_suite(project_context: dict, test_executors: dict = None, config: dict = None) -> dict:
    """运行AI测试套件

    Args:
        project_context: 项目上下文信息
        test_executors: 测试执行器字典
        config: 配置参数

    Returns:
        测试结果字典
    """
    if test_executors is None:
        test_executors = {}

    # 创建测试会话
    session = create_ai_testing_session(config)

    # 运行智能测试
    results = await session.run_intelligent_testing(project_context, test_executors)

    return results


def quick_test_analysis(test_results: list) -> dict:
    """快速测试分析

    Args:
        test_results: 测试结果列表

    Returns:
        分析结果字典
    """
    analyzer = AITestDataAnalyzer()

    # 检测异常
    anomalies = analyzer.detect_test_anomalies(test_results)

    # 预测趋势
    trends = analyzer.predict_test_trends(test_results)

    # 生成洞察
    insights = analyzer.generate_test_insights(test_results)

    return {
        "anomalies": [a.dict() for a in anomalies],
        "trends": [t.dict() for t in trends],
        "insights": insights,
    }


def generate_test_data(profile_name: str, data_schema: dict, request_params: dict = None) -> dict:
    """生成测试数据

    Args:
        profile_name: 数据档案名称
        data_schema: 数据模式
        request_params: 请求参数

    Returns:
        生成的测试数据
    """
    data_manager = AITestDataManager()

    try:
        return data_manager.generate_test_data(profile_name, data_schema, request_params)
    except ValueError as e:
        print(f"错误: {e}")
        return {}


def optimize_test_plan(plan_id: str = None) -> dict:
    """优化测试计划

    Args:
        plan_id: 计划ID（可选）

    Returns:
        优化结果
    """
    # 这里可以实现更复杂的优化逻辑
    return {
        "plan_id": plan_id,
        "optimizations_applied": [],
        "estimated_improvements": {},
    }


# 便捷配置模板
DEFAULT_CONFIG = {
    "max_concurrent_tests": 10,
    "enable_ai_enhancement": True,
    "auto_optimize": True,
    "enable_performance_monitoring": True,
    "report_format": "comprehensive",
    "data_retention_days": 30,
}

PERFORMANCE_CONFIG = {
    "max_concurrent_tests": 5,
    "enable_ai_enhancement": True,
    "auto_optimize": False,
    "enable_performance_monitoring": True,
    "report_format": "detailed",
    "data_retention_days": 7,
}

QUICK_CONFIG = {
    "max_concurrent_tests": 3,
    "enable_ai_enhancement": False,
    "auto_optimize": False,
    "enable_performance_monitoring": False,
    "report_format": "basic",
    "data_retention_days": 1,
}


def get_config_template(template_name: str = "default") -> dict:
    """获取配置模板

    Args:
        template_name: 模板名称 (default, performance, quick)

    Returns:
        配置字典
    """
    templates = {
        "default": DEFAULT_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "quick": QUICK_CONFIG,
    }

    return templates.get(template_name, DEFAULT_CONFIG)


# 项目示例用法
def create_my_stocks_test_context():
    """创建MyStocks项目测试上下文"""
    return {
        "project_name": "MyStocks",
        "project_type": "web_application",
        "modules_count": 15,
        "modules": [
            "authentication",
            "database",
            "api",
            "trading",
            "market_data",
            "user_management",
            "monitoring",
            "reporting",
        ],
        "features": ["api", "database", "ui", "realtime_data", "security"],
        "complexity_level": "medium",
        "critical_components": ["authentication", "database", "api"],
        "testing_requirements": {
            "coverage": 80,
            "performance_threshold": 2.0,
            "security_tests": True,
        },
    }


def create_my_stocks_test_executors():
    """创建MyStocks测试执行器"""
    return {
        "unit_tests": run_unit_tests,
        "integration_tests": run_integration_tests,
        "api_contract_tests": run_api_contract_tests,
        "e2e_tests": run_e2e_tests,
        "performance_tests": run_performance_tests,
    }


async def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    await asyncio.sleep(2)  # 模拟执行
    return {"passed": 25, "failed": 1, "skipped": 0}


async def run_integration_tests():
    """运行集成测试"""
    print("🔗 运行集成测试...")
    await asyncio.sleep(5)
    return {"passed": 18, "failed": 2, "skipped": 0}


async def run_api_contract_tests():
    """运行API契约测试"""
    print("📋 运行API契约测试...")
    await asyncio.sleep(3)
    return {"passed": 12, "failed": 0, "skipped": 0}


async def run_e2e_tests():
    """运行端到端测试"""
    print("🌐 运行端到端测试...")
    await asyncio.sleep(10)
    return {"passed": 8, "failed": 1, "skipped": 1}


async def run_performance_tests():
    """运行性能测试"""
    print("⚡ 运行性能测试...")
    await asyncio.sleep(15)
    return {"passed": 5, "failed": 0, "skipped": 0}


# 使用示例
async def demo_ai_testing():
    """演示AI测试功能"""
    print("🤖 AI测试演示")

    # 1. 创建测试上下文
    context = create_my_stocks_test_context()

    # 2. 创建测试执行器
    executors = create_my_stocks_test_executors()

    # 3. 运行AI测试
    results = await run_ai_test_suite(context, executors)

    # 4. 显示结果
    print("\n=== 测试结果 ===")
    print(f"计划名称: {results['metadata']['plan_name']}")
    print(f"总执行时间: {results['execution_summary']['total_duration']}s")
    print(f"通过率: {results['execution_summary']['success_rate']}%")
    print(f"建议数量: {len(results['recommendations'])}")

    for i, rec in enumerate(results["recommendations"], 1):
        print(f"{i}. {rec}")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_ai_testing())
