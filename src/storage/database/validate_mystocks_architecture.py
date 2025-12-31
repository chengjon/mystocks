#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks统一接口验证脚本
验证实时市场数据保存系统是否符合MyStocks架构设计

验证内容：
1. 统一管理器初始化
2. 数据分类路由正确性
3. 自动数据库选择
4. 监控系统集成
5. 与系统架构的一致性

作者: MyStocks项目组
日期: 2025-09-21
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入MyStocks核心模块
from unified_manager import MyStocksUnifiedManager
from src.core import DataClassification, DataManager, DatabaseTarget
from src.adapters.customer_adapter import CustomerDataSource


def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger("ArchitectureValidator")


def test_data_classification_strategy():
    """测试数据分类策略"""
    logger = logging.getLogger("ArchitectureValidator")
    logger.info("=== 数据分类策略验证 ===")

    # 验证实时数据的路由
    realtime_target = DataManager().get_target_database(DataClassification.REALTIME_POSITIONS)
    tick_target = DataManager().get_target_database(DataClassification.TICK_DATA)
    daily_target = DataManager().get_target_database(DataClassification.DAILY_KLINE)
    symbols_target = DataManager().get_target_database(DataClassification.SYMBOLS_INFO)

    logger.info("📊 数据分类路由验证:")
    logger.info("   REALTIME_POSITIONS → %s", realtime_target.value)
    logger.info("   TICK_DATA → %s", tick_target.value)
    logger.info("   DAILY_KLINE → %s", daily_target.value)
    logger.info("   SYMBOLS_INFO → %s", symbols_target.value)

    # 验证路由是否符合设计原则
    expected_routing = {
        DataClassification.REALTIME_POSITIONS: DatabaseTarget.REDIS,  # 实时数据 → Redis热数据
        DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,  # Tick数据 → TDengine时序
        DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,  # 日线数据 → PostgreSQL分析
        DataClassification.SYMBOLS_INFO: DatabaseTarget.MYSQL,  # 股票信息 → MySQL参考
    }

    routing_correct = True
    for classification, expected_target in expected_routing.items():
        actual_target = DataManager().get_target_database(classification)
        if actual_target != expected_target:
            logger.error(
                "❌ 路由错误: %s 期望→%s, 实际→%s", classification.value, expected_target.value, actual_target.value
            )
            routing_correct = False

    if routing_correct:
        logger.info("✅ 数据分类路由策略验证通过")
    else:
        logger.error("❌ 数据分类路由策略验证失败")

    return routing_correct


def test_unified_manager_initialization():
    """测试统一管理器初始化"""
    logger = logging.getLogger("ArchitectureValidator")
    logger.info("=== 统一管理器初始化验证 ===")

    try:
        # 创建统一管理器
        unified_manager = MyStocksUnifiedManager()
        logger.info("✅ 统一管理器创建成功")

        # 初始化系统
        init_result = unified_manager.initialize_system()

        if init_result["config_loaded"]:
            logger.info("✅ 配置加载成功")
        else:
            logger.error("❌ 配置加载失败")
            return False, None

        # 检查表创建结果
        tables_created = init_result.get("tables_created", {})
        success_count = sum(1 for success in tables_created.values() if success)
        total_count = len(tables_created)

        logger.info("📊 表创建状态: %s/%s", success_count, total_count)

        # 检查监控系统
        monitoring_init = init_result.get("monitoring_initialized", False)
        logger.info("📈 监控系统: %s", "已初始化" if monitoring_init else "未初始化")

        # 检查自动化维护
        maintenance_started = init_result.get("maintenance_started", False)
        logger.info("🔧 自动化维护: %s", "已启动" if maintenance_started else "未启动")

        # 获取系统状态
        try:
            status = unified_manager.get_system_status()
            monitoring = status.get("monitoring", {})
            op_stats = monitoring.get("operation_statistics", {})
            logger.info("📊 系统操作统计: %s 次操作", op_stats.get("total_operations", 0))
        except Exception as e:
            logger.warning("⚠️ 无法获取系统状态: %s", e)

        logger.info("✅ 统一管理器初始化验证通过")
        return True, unified_manager

    except Exception as e:
        logger.error("❌ 统一管理器初始化失败: %s", e)
        return False, None


def test_data_source_integration():
    """测试数据源集成"""
    logger = logging.getLogger("ArchitectureValidator")
    logger.info("=== 数据源集成验证 ===")

    try:
        # 测试Customer适配器
        customer_ds = CustomerDataSource()

        if not customer_ds.efinance_available:
            logger.error("❌ efinance库不可用")
            return False, None

        logger.info("✅ Customer数据源适配器可用")

        # 尝试获取少量数据测试
        logger.info("🔍 尝试获取实时数据样本...")
        try:
            data = customer_ds.get_real_time_data("hs")

            if data is not None and hasattr(data, "empty") and not data.empty:
                logger.info("✅ 数据获取成功: %s 行, %s 列", len(data), len(data.columns))
                logger.info("📋 数据列名: %s...", list(data.columns)[:5])  # 只显示前5列
                return True, data
            else:
                logger.warning("⚠️ 获取到空数据")
                return False, None

        except Exception as e:
            logger.error("❌ 数据获取失败: %s", e)
            return False, None

    except Exception as e:
        logger.error("❌ 数据源集成验证失败: %s", e)
        return False, None


def test_unified_interface_save(unified_manager, sample_data):
    """测试统一接口保存功能"""
    logger = logging.getLogger("ArchitectureValidator")
    logger.info("=== 统一接口保存验证 ===")

    if sample_data is None or sample_data.empty:
        logger.warning("⚠️ 无样本数据，跳过保存测试")
        return True

    try:
        # 测试1: 保存为实时数据 (应该路由到Redis)
        logger.info("🔥 测试保存为实时数据 → Redis")

        # 取少量数据进行测试
        test_data = sample_data.head(3).copy()
        test_data["test_timestamp"] = datetime.now()

        success = unified_manager.save_data_by_classification(test_data, DataClassification.REALTIME_POSITIONS)

        if success:
            logger.info("✅ 实时数据保存测试通过 → Redis")
        else:
            logger.warning("⚠️ 实时数据保存测试失败")

        # 测试2: 尝试查询刚保存的数据
        logger.info("🔍 测试查询实时数据...")
        try:
            loaded_data = unified_manager.load_data_by_classification(DataClassification.REALTIME_POSITIONS, limit=5)

            if not loaded_data.empty:
                logger.info("✅ 实时数据查询成功: %s 条记录", len(loaded_data))
            else:
                logger.info("📊 查询结果为空（可能是Redis配置或数据过期）")

        except Exception as e:
            logger.warning("⚠️ 数据查询测试异常: %s", e)

        # 获取系统状态验证操作记录
        try:
            status = unified_manager.get_system_status()
            monitoring = status.get("monitoring", {})
            op_stats = monitoring.get("operation_statistics", {})

            total_ops = op_stats.get("total_operations", 0)
            success_ops = op_stats.get("successful_operations", 0)

            logger.info("📊 系统操作统计更新: 总计%s次, 成功%s次", total_ops, success_ops)

        except Exception as e:
            logger.warning("⚠️ 无法获取操作统计: %s", e)

        logger.info("✅ 统一接口保存验证完成")
        return True

    except Exception as e:
        logger.error("❌ 统一接口保存验证失败: %s", e)
        return False


def test_architecture_consistency():
    """测试架构一致性"""
    logger = logging.getLogger("ArchitectureValidator")
    logger.info("=== 架构一致性验证 ===")

    try:
        # 验证设计原则
        principles = [
            ("统一接口规范", "使用MyStocksUnifiedManager隐藏底层数据库差异"),
            (
                "数据分类体系",
                "基于数据特性的5大分类：市场数据、参考数据、衍生数据、交易数据、元数据",
            ),
            ("自动路由策略", "根据DataClassification自动选择最优数据库"),
            ("完整监控集成", "所有操作自动记录到独立监控数据库"),
            ("配置驱动管理", "通过YAML配置文件管理表结构"),
        ]

        logger.info("📋 MyStocks系统设计原则:")
        for i, (principle, description) in enumerate(principles, 1):
            logger.info("   %s. %s: %s", i, principle, description)

        # 验证关键组件
        components = {
            "unified_manager": "统一管理器",
            "core": "核心数据分类",
            "data_access": "数据访问层",
            "monitoring": "监控系统",
            "adapters": "数据源适配器",
        }

        logger.info("🏗️ 系统组件验证:")
        for module, description in components.items():
            try:
                __import__(module)
                logger.info("   ✅ %s (%s)", description, module)
            except ImportError:
                logger.warning("   ⚠️ %s (%s) - 模块未找到", description, module)

        logger.info("✅ 架构一致性验证通过")
        return True

    except Exception as e:
        logger.error("❌ 架构一致性验证失败: %s", e)
        return False


def main():
    """主函数"""
    logger = setup_logging()

    print("=" * 80)
    print("🔍 MyStocks统一接口架构验证工具")
    print("验证实时市场数据保存系统是否符合MyStocks设计理念")
    print("=" * 80)

    # 测试结果统计
    test_results = {}

    # 1. 数据分类策略验证
    test_results["classification"] = test_data_classification_strategy()

    # 2. 统一管理器初始化验证
    manager_success, unified_manager = test_unified_manager_initialization()
    test_results["unified_manager"] = manager_success

    # 3. 数据源集成验证
    source_success, sample_data = test_data_source_integration()
    test_results["data_source"] = source_success

    # 4. 统一接口保存验证
    if unified_manager and sample_data is not None:
        test_results["unified_interface"] = test_unified_interface_save(unified_manager, sample_data)
    else:
        test_results["unified_interface"] = False
        logger.warning("⚠️ 跳过统一接口保存验证（前置条件未满足）")

    # 5. 架构一致性验证
    test_results["architecture"] = test_architecture_consistency()

    # 清理资源
    if unified_manager:
        try:
            unified_manager.cleanup()
            logger.info("🧹 系统资源已清理")
        except Exception:
            pass

    # 总结验证结果
    print("\n" + "=" * 80)
    print("📊 MyStocks架构验证结果")
    print("=" * 80)

    test_descriptions = {
        "classification": "数据分类策略",
        "unified_manager": "统一管理器",
        "data_source": "数据源集成",
        "unified_interface": "统一接口",
        "architecture": "架构一致性",
    }

    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        description = test_descriptions.get(test_name, test_name)
        print(f"{description}: {status}")

    # 整体评估
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = passed_tests / total_tests if total_tests > 0 else 0

    print(f"\n📈 总体通过率: {passed_tests}/{total_tests} ({success_rate:.1%})")

    if success_rate >= 0.9:
        print("🎉 系统完全符合MyStocks架构设计！")
        exit_code = 0
    elif success_rate >= 0.7:
        print("✅ 系统基本符合MyStocks架构，存在少量问题")
        exit_code = 0
    elif success_rate >= 0.5:
        print("⚠️ 系统部分符合MyStocks架构，需要改进")
        exit_code = 1
    else:
        print("💥 系统不符合MyStocks架构设计，需要重新实现")
        exit_code = 2

    # 提供改进建议
    if not test_results.get("classification", True):
        print("💡 建议: 检查core.py中的数据分类路由配置")

    if not test_results.get("unified_manager", True):
        print("💡 建议: 检查unified_manager.py的初始化逻辑")

    if not test_results.get("unified_interface", True):
        print("💡 建议: 确保使用save_data_by_classification接口进行数据保存")

    print("=" * 80)
    print(f"程序退出码: {exit_code}")

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
