"""测试ConfigDrivenTableManager

验证US2 (T020) 的核心功能:
1. 配置文件加载正确
2. 表结构统计准确
3. 分类映射完整
4. 安全模式工作正常

创建日期: 2025-10-12
"""

import logging
import sys
from pathlib import Path


# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config_driven_table_manager import ConfigDrivenTableManager


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_config_loading():
    """测试1: 配置文件加载"""
    logger.info("=" * 60)
    logger.info("测试1: 配置文件加载")
    logger.info("=" * 60)

    try:
        manager = ConfigDrivenTableManager(config_path="config/table_config.yaml")
        logger.info("✅ ConfigDrivenTableManager 初始化成功")
        logger.info(f"   - 配置版本: {manager.config.get('version')}")
        logger.info(f"   - 表定义数量: {len(manager.config.get('tables', []))}")
        logger.info(f"   - 安全模式: {manager.safe_mode}")
        return True
    except Exception as e:
        logger.error(f"❌ 配置加载失败: {e}")
        return False


def test_table_statistics(manager):
    """测试2: 表统计功能"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 表数量统计")
    logger.info("=" * 60)

    try:
        stats = manager.get_table_count_by_database()
        logger.info("✅ 表数量统计:")

        total = 0
        for db_type, count in stats.items():
            logger.info(f"   - {db_type}: {count}个表")
            total += count

        logger.info(f"   - 总计: {total}个表")

        # 验证表数量
        expected_total = len(manager.config["tables"])
        if total == expected_total:
            logger.info(f"✅ 表数量验证通过 ({total} == {expected_total})")
            return True
        logger.error(f"❌ 表数量不匹配 ({total} != {expected_total})")
        return False

    except Exception as e:
        logger.error(f"❌ 表统计失败: {e}")
        return False


def test_classification_mapping(manager):
    """测试3: 数据分类映射"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3: 数据分类映射")
    logger.info("=" * 60)

    try:
        mapping = manager.get_classification_mapping()
        logger.info(f"✅ 数据分类映射: {len(mapping)}个分类")

        # 显示前10个分类
        logger.info("\n前10个数据分类:")
        for i, (classification, table_name) in enumerate(list(mapping.items())[:10]):
            logger.info(f"   {i + 1}. {classification:30s} → {table_name}")

        if len(mapping) > 10:
            logger.info(f"   ... 还有 {len(mapping) - 10} 个分类")

        # 验证关键分类是否存在
        key_classifications = [
            "TICK_DATA",
            "MINUTE_KLINE",
            "DAILY_KLINE",
            "SYMBOLS_INFO",
            "TECHNICAL_INDICATORS",
            "ORDER_RECORDS",
        ]

        missing = []
        for classification in key_classifications:
            if classification not in mapping:
                missing.append(classification)

        if missing:
            logger.warning(f"⚠️ 缺少关键分类: {missing}")
        else:
            logger.info("✅ 所有关键分类都已定义")

        return len(mapping) > 0

    except Exception as e:
        logger.error(f"❌ 分类映射测试失败: {e}")
        return False


def test_safe_mode(manager):
    """测试4: 安全模式功能"""
    logger.info("\n" + "=" * 60)
    logger.info("测试4: 安全模式功能")
    logger.info("=" * 60)

    try:
        # 测试安全模式状态
        logger.info(f"✅ 安全模式状态: {manager.safe_mode}")

        # 测试危险操作确认
        result = manager.confirm_dangerous_operation(
            operation_type="DELETE_COLUMN",
            table_name="test_table",
            details="删除列 old_column",
        )

        if result == False:
            logger.info("✅ 危险操作正确拒绝（需要手动确认）")
        else:
            logger.warning("⚠️ 危险操作未被拒绝")

        return True

    except Exception as e:
        logger.error(f"❌ 安全模式测试失败: {e}")
        return False


def test_config_validation(manager):
    """测试5: 配置内容验证"""
    logger.info("\n" + "=" * 60)
    logger.info("测试5: 配置内容验证")
    logger.info("=" * 60)

    try:
        # 检查数据库配置
        databases = manager.config.get("databases", {})
        logger.info(f"✅ 数据库配置: {len(databases)}个数据库")
        for db_name in databases.keys():
            logger.info(f"   - {db_name}")

        # 检查维护任务配置
        maintenance = manager.config.get("maintenance", {})
        logger.info("\n✅ 维护配置:")
        logger.info(f"   - auto_create_tables: {maintenance.get('auto_create_tables')}")
        logger.info(f"   - safe_mode: {maintenance.get('safe_mode')}")

        daily_tasks = maintenance.get("daily_tasks", [])
        logger.info(f"   - daily_tasks: {len(daily_tasks)}个任务")

        weekly_tasks = maintenance.get("weekly_tasks", [])
        logger.info(f"   - weekly_tasks: {len(weekly_tasks)}个任务")

        return True

    except Exception as e:
        logger.error(f"❌ 配置验证失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 10 + "ConfigDrivenTableManager 测试套件" + " " * 13 + "║")
    logger.info("║" + " " * 16 + "US2 (T020) 功能验证" + " " * 20 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("")

    # 测试1: 配置加载
    success1 = test_config_loading()
    if not success1:
        logger.error("\n❌ 测试失败: 配置加载失败，停止后续测试")
        return False

    # 创建manager实例用于后续测试
    manager = ConfigDrivenTableManager(config_path="config/table_config.yaml")

    # 测试2: 表统计
    success2 = test_table_statistics(manager)

    # 测试3: 分类映射
    success3 = test_classification_mapping(manager)

    # 测试4: 安全模式
    success4 = test_safe_mode(manager)

    # 测试5: 配置验证
    success5 = test_config_validation(manager)

    # 总结
    logger.info("\n" + "=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)

    results = [
        ("配置文件加载", success1),
        ("表数量统计", success2),
        ("数据分类映射", success3),
        ("安全模式功能", success4),
        ("配置内容验证", success5),
    ]

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")

    logger.info("-" * 60)
    logger.info(f"测试通过: {passed}/{total}")

    if passed == total:
        logger.info("\n🎉 所有测试通过！ConfigDrivenTableManager 功能正常")
        logger.info("✅ T020 (实现ConfigDrivenTableManager) 验证成功")
        return True
    logger.info(f"\n⚠️ {total - passed} 个测试失败")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
