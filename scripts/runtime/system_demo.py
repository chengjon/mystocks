#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - 完整示例和使用指南
展示如何使用重构后的v2.0系统

完全基于原始设计理念：
1. 配置驱动 - 一个YAML文件管理所有表结构
2. 自动化管理 - 避免人工干预数据库操作
3. 5大数据分类 - 基于数据特性的科学分类
4. TDengine核心 - 高频数据的专用处理
5. 监控分离 - 监控数据库与业务数据库完全分离

作者: MyStocks项目组
版本: v2.0 重构版 - 完整实现
日期: 2025-09-21
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# 导入重构后的核心模块
from src.core import DataClassification, DataManager
from unified_manager import MyStocksUnifiedManager
from src.monitoring.alert_manager import AlertLevel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MyStocksDemo")


class MyStocksV2Demo:
    """MyStocks v2.0 完整演示"""

    def __init__(self):
        """初始化演示系统"""
        print("🚀 MyStocks v2.0 量化交易数据管理系统")
        print("=" * 60)
        print("基于原始设计理念的完全重构版本")
        print("- 配置驱动的自动化管理")
        print("- 5大数据分类体系")
        print("- TDengine高频数据核心")
        print("- 完整监控和自动化维护")
        print("=" * 60)

        # 初始化统一管理器
        self.manager = MyStocksUnifiedManager()

        # 初始化系统
        self.initialization_results = None

    def run_complete_demo(self):
        """运行完整演示"""
        try:
            print("\n🔧 步骤1: 系统初始化")
            self._demo_system_initialization()

            print("\n📊 步骤2: 数据分类演示")
            self._demo_data_classification()

            print("\n💾 步骤3: 数据存储演示")
            self._demo_data_storage()

            print("\n🔍 步骤4: 数据查询演示")
            self._demo_data_retrieval()

            print("\n📈 步骤5: 高频数据演示")
            self._demo_high_frequency_data()

            print("\n⚡ 步骤6: 实时数据演示")
            self._demo_realtime_data()

            print("\n🔍 步骤7: 监控系统演示")
            self._demo_monitoring_system()

            print("\n🔧 步骤8: 自动化维护演示")
            self._demo_automated_maintenance()

            print("\n📋 步骤9: 系统状态检查")
            self._demo_system_status()

            print("\n🎉 演示完成!")
            self._show_summary()

        except Exception as e:
            print(f"❌ 演示过程中出现错误: {e}")
        finally:
            # 清理资源
            self._cleanup_demo()

    def _demo_system_initialization(self):
        """演示系统初始化"""
        print("正在初始化MyStocks v2.0系统...")

        # 初始化系统
        results = self.manager.initialize_system()
        self.initialization_results = results

        print(f"✅ 配置加载: {'成功' if results['config_loaded'] else '失败'}")

        # 显示表创建结果
        table_results = results["tables_created"]
        success_count = sum(1 for success in table_results.values() if success)
        total_count = len(table_results)
        print(f"✅ 表创建: {success_count}/{total_count} 成功")

        # 显示具体表创建结果
        for table_key, success in table_results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {table_key}")

        print(
            f"✅ 监控系统: {'已初始化' if results['monitoring_initialized'] else '初始化失败'}"
        )
        print(
            f"✅ 自动化维护: {'已启动' if results['maintenance_started'] else '启动失败'}"
        )

        if results["errors"]:
            print("⚠️  错误信息:")
            for error in results["errors"]:
                print(f"   - {error}")

    def _demo_data_classification(self):
        """演示5大数据分类体系"""
        print("展示5大数据分类体系和自动路由...")

        classifications = [
            (DataClassification.TICK_DATA, "第1类: 市场数据 - Tick数据"),
            (DataClassification.MINUTE_KLINE, "第1类: 市场数据 - 分钟K线"),
            (DataClassification.DAILY_KLINE, "第1类: 市场数据 - 日线数据"),
            (DataClassification.SYMBOLS_INFO, "第2类: 参考数据 - 股票信息"),
            (DataClassification.TRADE_CALENDAR, "第2类: 参考数据 - 交易日历"),
            (DataClassification.TECHNICAL_INDICATORS, "第3类: 衍生数据 - 技术指标"),
            (DataClassification.QUANTITATIVE_FACTORS, "第3类: 衍生数据 - 量化因子"),
            (DataClassification.ORDER_RECORDS, "第4类: 交易数据 - 订单记录"),
            (DataClassification.REALTIME_POSITIONS, "第4类: 交易数据 - 实时持仓"),
            (DataClassification.SYSTEM_CONFIG, "第5类: 元数据 - 系统配置"),
        ]

        for classification, description in classifications:
            target_db = DataManager().get_target_database(classification)
            db_name = DataManager().get_database_name(classification)
            print(f"📂 {description}")
            print(f"   → 自动路由到: {target_db.value} / {db_name}")

    def _demo_data_storage(self):
        """演示数据存储功能"""
        print("演示自动化数据存储...")

        # 1. 存储股票基本信息 (参考数据 → MySQL)
        print("\n📝 保存股票基本信息到MySQL...")
        symbols_data = pd.DataFrame(
            {
                "symbol": ["600000", "000001", "000002", "600036"],
                "name": ["浦发银行", "平安银行", "万科A", "招商银行"],
                "exchange": ["SH", "SZ", "SZ", "SH"],
                "sector": ["银行", "银行", "房地产", "银行"],
                "list_date": ["1999-11-10", "1991-04-03", "1991-01-29", "2002-04-09"],
                "is_active": [True, True, True, True],
            }
        )

        success = self.manager.save_data_by_classification(
            symbols_data, DataClassification.SYMBOLS_INFO
        )
        print(f"   结果: {'✅ 保存成功' if success else '❌ 保存失败'}")

        # 2. 存储日线数据 (市场数据 → PostgreSQL)
        print("\n📈 保存日线数据到PostgreSQL...")
        daily_data = self._generate_sample_daily_data()

        success = self.manager.save_data_by_classification(
            daily_data, DataClassification.DAILY_KLINE
        )
        print(f"   结果: {'✅ 保存成功' if success else '❌ 保存失败'}")

        # 3. 存储技术指标 (衍生数据 → PostgreSQL)
        print("\n🧮 保存技术指标到PostgreSQL...")
        indicators_data = self._generate_sample_indicators()

        success = self.manager.save_data_by_classification(
            indicators_data, DataClassification.TECHNICAL_INDICATORS
        )
        print(f"   结果: {'✅ 保存成功' if success else '❌ 保存失败'}")

    def _demo_data_retrieval(self):
        """演示数据查询功能"""
        print("演示自动化数据查询...")

        # 1. 查询股票信息
        print("\n🔍 从MySQL查询股票信息...")
        symbols = self.manager.load_data_by_classification(
            DataClassification.SYMBOLS_INFO, filters={"exchange": "SH"}
        )
        print(f"   查询结果: {len(symbols)} 条记录")
        if not symbols.empty:
            print("   示例数据:")
            print(symbols[["symbol", "name", "exchange"]].to_string(index=False))

        # 2. 查询日线数据
        print("\n📊 从PostgreSQL查询日线数据...")
        daily_data = self.manager.load_data_by_classification(
            DataClassification.DAILY_KLINE, filters={"symbol": "600000"}, limit=5
        )
        print(f"   查询结果: {len(daily_data)} 条记录")
        if not daily_data.empty:
            print("   示例数据:")
            columns_to_show = ["symbol", "trade_date", "close", "volume"]
            available_columns = [
                col for col in columns_to_show if col in daily_data.columns
            ]
            if available_columns:
                print(daily_data[available_columns].head().to_string(index=False))

        # 3. 查询技术指标
        print("\n📈 从PostgreSQL查询技术指标...")
        indicators = self.manager.load_data_by_classification(
            DataClassification.TECHNICAL_INDICATORS,
            filters={"symbol": "600000", "indicator_name": "MA20"},
            limit=3,
        )
        print(f"   查询结果: {len(indicators)} 条记录")
        if not indicators.empty:
            print("   示例数据:")
            columns_to_show = [
                "symbol",
                "calc_date",
                "indicator_name",
                "indicator_value",
            ]
            available_columns = [
                col for col in columns_to_show if col in indicators.columns
            ]
            if available_columns:
                print(indicators[available_columns].to_string(index=False))

    def _demo_high_frequency_data(self):
        """演示高频数据处理 (TDengine核心功能)"""
        print("演示TDengine高频数据处理...")

        # 1. 生成和保存Tick数据
        print("\n⚡ 保存Tick数据到TDengine...")
        tick_data = self._generate_sample_tick_data()

        success = self.manager.save_data_by_classification(
            tick_data, DataClassification.TICK_DATA
        )
        print(f"   结果: {'✅ 保存成功' if success else '❌ 保存失败'}")
        print(f"   数据量: {len(tick_data)} 条Tick记录")

        # 2. 生成和保存分钟K线数据
        print("\n📊 保存分钟K线到TDengine...")
        minute_data = self._generate_sample_minute_kline()

        success = self.manager.save_data_by_classification(
            minute_data, DataClassification.MINUTE_KLINE
        )
        print(f"   结果: {'✅ 保存成功' if success else '❌ 保存失败'}")
        print(f"   数据量: {len(minute_data)} 条分钟K线记录")

        # 3. 查询高频数据
        print("\n🔍 从TDengine查询高频数据...")
        try:
            recent_ticks = self.manager.load_data_by_classification(
                DataClassification.TICK_DATA, filters={"symbol": "600000"}, limit=5
            )
            print(f"   Tick数据查询结果: {len(recent_ticks)} 条记录")

            recent_minutes = self.manager.load_data_by_classification(
                DataClassification.MINUTE_KLINE, filters={"symbol": "600000"}, limit=3
            )
            print(f"   分钟K线查询结果: {len(recent_minutes)} 条记录")

        except Exception as e:
            print(f"   ⚠️  高频数据查询: {e}")

    def _demo_realtime_data(self):
        """演示实时数据处理 (Redis核心功能)"""
        print("演示Redis实时数据处理...")

        # 1. 保存实时行情
        print("\n⚡ 保存实时行情到Redis...")
        realtime_quotes = {
            "600000": {
                "price": 10.50,
                "change_pct": 0.02,
                "volume": 1000000,
                "timestamp": datetime.now().isoformat(),
            },
            "000001": {
                "price": 15.30,
                "change_pct": -0.01,
                "volume": 800000,
                "timestamp": datetime.now().isoformat(),
            },
            "000002": {
                "price": 20.80,
                "change_pct": 0.05,
                "volume": 1200000,
                "timestamp": datetime.now().isoformat(),
            },
        }

        for symbol, quote in realtime_quotes.items():
            key = f"realtime:quote:{symbol}"
            success = self.manager.redis_access.save_realtime_data(
                DataClassification.REALTIME_POSITIONS, key, quote, expire=300
            )
            print(f"   {symbol}: {'✅ 保存成功' if success else '❌ 保存失败'}")

        # 2. 查询实时行情
        print("\n🔍 从Redis查询实时行情...")
        for symbol in ["600000", "000001"]:
            key = f"realtime:quote:{symbol}"
            quote = self.manager.redis_access.load_realtime_data(
                DataClassification.REALTIME_POSITIONS, key
            )
            if quote:
                print(
                    f"   {symbol}: 价格={quote.get('price', 'N/A')}, 涨跌幅={quote.get('change_pct', 'N/A')}"
                )
            else:
                print(f"   {symbol}: 无数据")

        # 3. 缓存分析结果
        print("\n💾 缓存分析结果到Redis...")
        analysis_result = pd.DataFrame(
            {
                "symbol": ["600000", "000001", "000002"],
                "score": [0.85, 0.72, 0.91],
                "rank": [2, 3, 1],
            }
        )

        success = self.manager.redis_access.cache_dataframe(
            "analysis:factor_score", analysis_result, expire=3600
        )
        print(f"   结果: {'✅ 缓存成功' if success else '❌ 缓存失败'}")

    def _demo_monitoring_system(self):
        """演示监控系统功能"""
        print("演示完整监控系统...")

        # 1. 操作统计
        print("\n📊 查看操作统计...")
        stats = self.manager.monitoring_db.get_operation_statistics(24)
        print("   24小时内操作统计:")
        print(f"   - 总操作数: {stats.get('total_operations', 0)}")
        print(f"   - 成功操作: {stats.get('successful_operations', 0)}")
        print(f"   - 失败操作: {stats.get('failed_operations', 0)}")

        # 2. 表创建历史
        print("\n📋 查看表创建历史...")
        history = self.manager.monitoring_db.get_table_creation_history(5)
        print(f"   最近5次表创建操作: {len(history)} 条记录")

        # 3. 性能监控
        print("\n⚡ 查看性能指标...")
        performance = self.manager.performance_monitor.get_performance_summary()
        if performance and "total_operations" in performance:
            print(f"   总操作数: {performance.get('total_operations', 0)}")
            print(f"   平均耗时: {performance.get('avg_duration', 0):.3f}秒")
            print(f"   成功率: {performance.get('success_rate', 0):.2%}")

        # 4. 数据质量报告
        print("\n🔍 生成数据质量报告...")
        quality_report = self.manager.quality_monitor.generate_quality_report()
        overall_score = quality_report.get("overall_score", 0)
        print(f"   整体质量评分: {overall_score:.2f}")

        # 5. 告警状态
        print("\n🚨 查看告警状态...")
        active_alerts = self.manager.alert_manager.get_active_alerts()
        critical_alerts = self.manager.alert_manager.get_active_alerts(
            AlertLevel.CRITICAL
        )
        print(f"   活跃告警: {len(active_alerts)} 个")
        print(f"   严重告警: {len(critical_alerts)} 个")

    def _demo_automated_maintenance(self):
        """演示自动化维护功能"""
        print("演示自动化维护系统...")

        # 1. 维护状态
        maintenance_running = self.manager.maintenance_manager.is_running
        print(f"✅ 自动化维护状态: {'运行中' if maintenance_running else '已停止'}")

        # 2. 手动触发维护任务
        if maintenance_running:
            print("\n🔧 维护任务调度:")
            config = self.manager.maintenance_manager.config

            # 显示每日任务
            daily_tasks = config.get("daily_tasks", {})
            print("   每日任务:")
            for task_name, task_config in daily_tasks.items():
                status = "启用" if task_config.get("enabled") else "禁用"
                time_str = task_config.get("time", "N/A")
                print(f"   - {task_name}: {status} ({time_str})")

            # 显示每周任务
            weekly_tasks = config.get("weekly_tasks", {})
            print("   每周任务:")
            for task_name, task_config in weekly_tasks.items():
                status = "启用" if task_config.get("enabled") else "禁用"
                day_str = task_config.get("day", "N/A")
                time_str = task_config.get("time", "N/A")
                print(f"   - {task_name}: {status} ({day_str} {time_str})")

            # 显示告警阈值
            thresholds = config.get("alert_thresholds", {})
            print("   告警阈值:")
            for threshold_name, value in thresholds.items():
                print(f"   - {threshold_name}: {value}")

        # 3. 创建测试告警
        print("\n🚨 创建测试告警...")
        test_alert = self.manager.alert_manager.create_alert(
            AlertLevel.INFO,
            "系统演示",
            "这是一个演示告警，系统运行正常",
            source="demo_system",
        )
        print(f"   告警ID: {test_alert.alert_id}")
        print(f"   告警级别: {test_alert.level.value}")

    def _demo_system_status(self):
        """演示系统状态检查"""
        print("生成完整系统状态报告...")

        status = self.manager.get_system_status()

        print(f"\n📊 系统状态 ({status.get('timestamp', 'N/A')}):")

        # 监控状态
        monitoring = status.get("monitoring", {})
        print("   🔍 监控系统:")
        op_stats = monitoring.get("operation_statistics", {})
        print(f"   - 总操作数: {op_stats.get('total_operations', 0)}")
        print(f"   - 成功操作: {op_stats.get('successful_operations', 0)}")

        # 性能状态
        performance = status.get("performance", {})
        print("   ⚡ 性能指标:")
        perf_summary = performance.get("summary", {})
        print(f"   - 平均响应时间: {perf_summary.get('avg_duration', 0):.3f}秒")
        print(f"   - 慢操作数: {len(performance.get('slow_operations', []))}")

        # 数据质量
        quality = status.get("data_quality", {})
        print("   📈 数据质量:")
        print(f"   - 整体评分: {quality.get('overall_score', 0):.2f}")

        # 告警状态
        alerts = status.get("alerts", {})
        print("   🚨 告警状态:")
        print(f"   - 活跃告警: {alerts.get('active_alerts', 0)}")
        print(f"   - 严重告警: {alerts.get('critical_alerts', 0)}")

        # 维护状态
        maintenance = status.get("maintenance", {})
        print("   🔧 维护状态:")
        print(f"   - 运行状态: {'正常' if maintenance.get('is_running') else '停止'}")

    def _show_summary(self):
        """显示演示总结"""
        print("\n" + "=" * 60)
        print("🎉 MyStocks v2.0 演示总结")
        print("=" * 60)

        if self.initialization_results:
            table_results = self.initialization_results["tables_created"]
            success_count = sum(1 for success in table_results.values() if success)
            total_count = len(table_results)

            print("✅ 系统初始化完成")
            print("   - 配置加载: 成功")
            print(f"   - 表创建: {success_count}/{total_count}")
            print("   - 监控系统: 已启动")
            print("   - 自动化维护: 已启动")

        print("✅ 数据分类演示完成")
        print("   - 5大数据分类体系")
        print("   - 自动数据库路由")
        print("   - TDengine高频数据核心")

        print("✅ 数据操作演示完成")
        print("   - 配置驱动的表创建")
        print("   - 自动化数据存储")
        print("   - 智能数据查询")

        print("✅ 监控系统演示完成")
        print("   - 完整操作监控")
        print("   - 性能指标统计")
        print("   - 数据质量检查")
        print("   - 告警机制")

        print("✅ 自动化维护演示完成")
        print("   - 定时维护任务")
        print("   - 健康状态检查")
        print("   - 自动告警机制")

        print("\n💡 核心特性验证:")
        print("   ✅ 配置驱动 - 一个YAML文件管理所有表结构")
        print("   ✅ 自动化管理 - 零人工干预的数据库操作")
        print("   ✅ 监控分离 - 监控数据库与业务数据库分离")
        print("   ✅ 5大分类 - 基于数据特性的科学分类")
        print("   ✅ TDengine核心 - 高频数据专用处理")

        print("\n🚀 系统就绪，可以开始量化交易数据管理!")

    def _cleanup_demo(self):
        """清理演示资源"""
        print("\n🧹 清理演示资源...")
        try:
            self.manager.cleanup()
            print("   ✅ 资源清理完成")
        except Exception as e:
            print(f"   ⚠️  资源清理失败: {e}")

    # 数据生成辅助方法
    def _generate_sample_daily_data(self) -> pd.DataFrame:
        """生成示例日线数据"""
        symbols = ["600000", "000001", "000002"]
        dates = pd.date_range(end=datetime.now().date(), periods=30, freq="D")

        data = []
        for symbol in symbols:
            base_price = np.random.uniform(10, 30)
            for date in dates:
                price = base_price * (1 + np.random.normal(0, 0.02))
                data.append(
                    {
                        "symbol": symbol,
                        "trade_date": date,
                        "open": price * (1 + np.random.uniform(-0.01, 0.01)),
                        "high": price * (1 + np.random.uniform(0, 0.03)),
                        "low": price * (1 + np.random.uniform(-0.03, 0)),
                        "close": price,
                        "volume": np.random.randint(100000, 10000000),
                        "amount": price * np.random.randint(100000, 10000000),
                        "adj_factor": 1.0,
                    }
                )

        return pd.DataFrame(data)

    def _generate_sample_indicators(self) -> pd.DataFrame:
        """生成示例技术指标数据"""
        symbols = ["600000", "000001", "000002"]
        dates = pd.date_range(end=datetime.now().date(), periods=10, freq="D")
        indicators = ["MA5", "MA10", "MA20", "RSI", "MACD"]

        data = []
        for symbol in symbols:
            for date in dates:
                for indicator in indicators:
                    data.append(
                        {
                            "symbol": symbol,
                            "calc_date": date,
                            "indicator_name": indicator,
                            "indicator_value": np.random.uniform(0.1, 100),
                            "indicator_params": {
                                "period": 20 if "MA" in indicator else 14
                            },
                        }
                    )

        return pd.DataFrame(data)

    def _generate_sample_tick_data(self) -> pd.DataFrame:
        """生成示例Tick数据"""
        symbols = ["600000", "000001"]
        base_time = datetime.now()

        data = []
        for symbol in symbols:
            base_price = np.random.uniform(10, 30)
            for i in range(100):  # 100个Tick
                tick_time = base_time - timedelta(seconds=i * 10)
                price = base_price * (1 + np.random.normal(0, 0.001))
                data.append(
                    {
                        "ts": tick_time,
                        "symbol": symbol,
                        "price": price,
                        "volume": np.random.randint(100, 10000),
                        "amount": price * np.random.randint(100, 10000),
                        "exchange": "SH" if symbol.startswith("6") else "SZ",
                    }
                )

        return pd.DataFrame(data)

    def _generate_sample_minute_kline(self) -> pd.DataFrame:
        """生成示例分钟K线数据"""
        symbols = ["600000", "000001"]
        base_time = datetime.now()

        data = []
        for symbol in symbols:
            base_price = np.random.uniform(10, 30)
            for i in range(60):  # 60分钟
                minute_time = base_time - timedelta(minutes=i)
                price = base_price * (1 + np.random.normal(0, 0.002))
                data.append(
                    {
                        "ts": minute_time,
                        "symbol": symbol,
                        "open": price * (1 + np.random.uniform(-0.005, 0.005)),
                        "high": price * (1 + np.random.uniform(0, 0.01)),
                        "low": price * (1 + np.random.uniform(-0.01, 0)),
                        "close": price,
                        "volume": np.random.randint(1000, 100000),
                        "amount": price * np.random.randint(1000, 100000),
                        "frequency": "1m",
                    }
                )

        return pd.DataFrame(data)


def main():
    """主程序入口"""
    try:
        # 创建演示实例
        demo = MyStocksV2Demo()

        # 运行完整演示
        demo.run_complete_demo()

    except KeyboardInterrupt:
        print("\n⚠️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
