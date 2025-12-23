"""
测试标记系统

为不同类型的测试提供统一的标记定义和管理。
"""

import pytest


# 单元测试标记
def pytest_configure(config):
    """配置测试标记"""

    # 注册自定义标记
    config.addinivalue_line("markers", "unit: 单元测试，测试单个组件或函数的独立功能")
    config.addinivalue_line("markers", "integration: 集成测试，测试多个组件之间的交互")
    config.addinivalue_line("markers", "e2e: 端到端测试，测试完整的用户流程")
    config.addinivalue_line("markers", "performance: 性能测试，测试系统性能指标")
    config.addinivalue_line("markers", "security: 安全测试，测试系统安全性")
    config.addinivalue_line("markers", "ai: AI辅助测试，使用AI辅助的测试功能")
    config.addinivalue_line("markers", "contract: 契约测试，测试API契约符合性")
    config.addinivalue_line("markers", "chaos: 混沌工程测试，测试系统容错能力")
    config.addinivalue_line("markers", "slow: 慢速测试，用于长时间运行的测试")
    config.addinivalue_line("markers", "smoke: 冒烟测试，快速的基本功能验证")


# 标记检查器
class MarkerChecker:
    """标记检查器"""

    @staticmethod
    def has_marker(test_item, marker_name):
        """检查测试是否具有指定标记"""
        return marker_name in test_item.keywords

    @staticmethod
    def get_marker_value(test_item, marker_name):
        """获取标记的值"""
        marker = test_item.get_closest_marker(marker_name)
        return marker.args[0] if marker and marker.args else None

    @staticmethod
    def get_all_markers(test_item):
        """获取测试的所有标记"""
        return list(test_item.iter_markers())


# 标记过滤器
class MarkerFilter:
    """标记过滤器"""

    @staticmethod
    def by_type(test_items, marker_type):
        """根据标记类型过滤测试"""
        return [
            item for item in test_items if MarkerChecker.has_marker(item, marker_type)
        ]

    @staticmethod
    def by_priority(test_items, priority):
        """根据优先级过滤测试"""
        priority_mapping = {
            "high": ["unit", "integration", "contract"],
            "medium": ["performance", "security", "ai"],
            "low": ["e2e", "chaos", "slow"],
        }

        if priority not in priority_mapping:
            return test_items

        high_priority_markers = priority_mapping[priority]
        return [
            item
            for item in test_items
            if any(
                MarkerChecker.has_marker(item, marker)
                for marker in high_priority_markers
            )
        ]


# 标记统计器
class MarkerStatistics:
    """标记统计器"""

    @staticmethod
    def count_by_type(test_items):
        """统计各类型测试的数量"""
        statistics = {}

        for marker in [
            "unit",
            "integration",
            "e2e",
            "performance",
            "security",
            "ai",
            "contract",
            "chaos",
            "slow",
            "smoke",
        ]:
            count = len(MarkerFilter.by_type(test_items, marker))
            if count > 0:
                statistics[marker] = count

        return statistics

    @staticmethod
    def get_test_distribution(test_items):
        """获取测试分布"""
        return {
            "total": len(test_items),
            "by_type": MarkerStatistics.count_by_type(test_items),
            "high_priority": len(MarkerFilter.by_priority(test_items, "high")),
            "medium_priority": len(MarkerFilter.by_priority(test_items, "medium")),
            "low_priority": len(MarkerFilter.by_priority(test_items, "low")),
        }


# 测试分类器
class TestClassifier:
    """测试分类器"""

    @staticmethod
    def classify_test(test_item):
        """分类测试"""
        markers = MarkerChecker.get_all_markers(test_item)

        if not markers:
            return "unclassified"

        # 返回第一个匹配的标记类型
        marker_names = [m.name for m in markers]
        priority_types = ["unit", "integration", "contract", "e2e"]

        for marker in marker_names:
            if marker in priority_types:
                return marker

        return marker_names[0] if marker_names else "unclassified"

    @staticmethod
    def get_test_suite_config():
        """获取测试套件配置"""
        return {
            "unit": {
                "description": "单元测试",
                "priority": "high",
                "timeout": 30,
                "retry": 0,
            },
            "integration": {
                "description": "集成测试",
                "priority": "high",
                "timeout": 60,
                "retry": 1,
            },
            "e2e": {
                "description": "端到端测试",
                "priority": "medium",
                "timeout": 300,
                "retry": 1,
            },
            "performance": {
                "description": "性能测试",
                "priority": "medium",
                "timeout": 600,
                "retry": 0,
            },
            "security": {
                "description": "安全测试",
                "priority": "high",
                "timeout": 180,
                "retry": 0,
            },
            "ai": {
                "description": "AI辅助测试",
                "priority": "medium",
                "timeout": 120,
                "retry": 1,
            },
            "contract": {
                "description": "契约测试",
                "priority": "high",
                "timeout": 90,
                "retry": 1,
            },
            "chaos": {
                "description": "混沌工程测试",
                "priority": "low",
                "timeout": 240,
                "retry": 0,
            },
        }


# 使用示例
if __name__ == "__main__":
    # 示例测试函数
    @pytest.mark.unit
    @pytest.mark.smoke
    def test_basic_functionality():
        """基础功能测试"""
        assert True

    @pytest.mark.integration
    @pytest.mark.slow
    def test_component_integration():
        """组件集成测试"""
        assert True

    @pytest.mark.e2e
    def test_user_workflow():
        """用户工作流测试"""
        assert True

    # 创建测试示例
    test_examples = [
        test_basic_functionality,
        test_component_integration,
        test_user_workflow,
    ]

    # 统计测试分布
    distribution = MarkerStatistics.get_test_distribution(test_examples)
    print(f"测试分布: {distribution}")

    # 分类测试
    for test in test_examples:
        classification = TestClassifier.classify_test(test)
        print(f"测试 {test.__name__} 分类: {classification}")
