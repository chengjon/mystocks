#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沪深市场A股实时数据保存系统 - efinance版本
严格按照MyStocks系统的统一接口规范和数据分类策略实现

核心设计理念：
1. 使用efinance的ef.stock.get_realtime_quotes()获取沪深A股实时数据
2. 使用统一管理器 (MyStocksUnifiedManager) - 隐藏底层数据库差异
3. 正确的数据分类 - 实时行情数据保存为REALTIME_POSITIONS (Redis) + DAILY_KLINE (PostgreSQL)
4. 自动路由保存 - 系统自动选择最优数据库存储
5. 完整监控集成 - 所有操作自动记录到监控数据库

数据分类策略：
- ef.stock.get_realtime_quotes() 获取的实时行情快照：
  * REALTIME_POSITIONS → Redis (热数据，快速访问)
  * DAILY_KLINE → PostgreSQL+TimescaleDB (持久化存储，分析查询)
- 双重保存确保数据的实时性和持久性

作者: MyStocks项目组
日期: 2025-09-23
修正: 使用efinance接口并保存到PostgreSQL
"""

import os
import sys
import logging
import argparse
import pandas as pd
from datetime import datetime
from typing import Optional, Dict
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入MyStocks统一接口
from unified_manager import MyStocksUnifiedManager
from src.core import DataClassification
from src.adapters.customer_adapter import CustomerDataSource


class RealtimeMarketDataSaver:
    """沪深市场A股实时数据保存器 - 按照MyStocks统一接口规范实现"""

    def __init__(self, config_file: str = "realtime_market_config.env"):
        """初始化数据保存器"""
        self.config_file = config_file
        self.logger = None
        self.unified_manager = None
        self.customer_ds = None
        self.config = {}

        # 初始化
        self._setup_logging()
        self._load_config()

    def _setup_logging(self):
        """配置日志系统"""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler("realtime_market_saver.log", encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )

        self.logger = logging.getLogger("RealtimeMarketSaver")
        self.logger.info("日志系统初始化完成")

    def _load_config(self):
        """加载配置参数"""
        self.logger.info(f"加载配置文件: {self.config_file}")

        # 首先加载默认的.env文件
        load_dotenv()

        # 然后加载专用配置文件
        if os.path.exists(self.config_file):
            load_dotenv(self.config_file, override=True)
            self.logger.info(f"✅ 成功加载配置文件: {self.config_file}")
        else:
            self.logger.warning(f"⚠️ 配置文件不存在: {self.config_file}，使用默认配置")

        # 读取配置参数
        self.config = {
            # 数据源配置
            "market_symbol": os.getenv("MARKET_SYMBOL", "hs"),  # 'hs'=沪深, 'sh'=上海, 'sz'=深圳
            "data_source_timeout": int(os.getenv("DATA_SOURCE_TIMEOUT", "30")),
            # 数据分类配置 - 双重保存策略
            "save_as_realtime": os.getenv("SAVE_AS_REALTIME", "true").lower() == "true",  # Redis热数据
            "save_as_daily": os.getenv("SAVE_AS_DAILY", "true").lower() == "true",  # PostgreSQL持久化
            "save_as_tick": os.getenv("SAVE_AS_TICK", "false").lower() == "true",  # TDengine时序(可选)
            "cache_expire_seconds": int(os.getenv("CACHE_EXPIRE_SECONDS", "300")),  # Redis缓存过期时间
            # 数据处理配置
            "add_timestamp_column": os.getenv("ADD_TIMESTAMP_COLUMN", "true").lower() == "true",
            "enable_data_validation": os.getenv("ENABLE_DATA_VALIDATION", "true").lower() == "true",
            "max_retry_attempts": int(os.getenv("MAX_RETRY_ATTEMPTS", "3")),
            # 日志配置
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_file": os.getenv("LOG_FILE", "realtime_market_saver.log"),
        }

        # 更新日志级别
        log_level = getattr(logging, self.config["log_level"].upper())
        self.logger.setLevel(log_level)

        self.logger.info("✅ 配置参数加载完成")
        self.logger.info(f"📊 市场代码: {self.config['market_symbol']}")
        self.logger.info(f"🔥 保存为实时数据(Redis): {self.config['save_as_realtime']}")
        self.logger.info(f"💾 保存为日线数据(PostgreSQL): {self.config['save_as_daily']}")
        self.logger.info(f"⏱️ 保存为Tick数据(TDengine): {self.config['save_as_tick']}")

    def initialize_unified_manager(self) -> bool:
        """初始化MyStocks统一管理器"""
        self.logger.info("初始化MyStocks统一管理器...")

        try:
            # 创建统一管理器
            self.unified_manager = MyStocksUnifiedManager()

            # 初始化系统
            init_result = self.unified_manager.initialize_system()

            if init_result["config_loaded"]:
                self.logger.info("✅ MyStocks统一管理器初始化成功")

                # 显示系统状态
                status = self.unified_manager.get_system_status()
                monitoring = status.get("monitoring", {})
                op_stats = monitoring.get("operation_statistics", {})

                self.logger.info(f"📊 系统状态 - 总操作数: {op_stats.get('total_operations', 0)}")
                self.logger.info(f"🗄️ 监控系统: {'正常' if monitoring else '未初始化'}")

                return True
            else:
                self.logger.error("❌ MyStocks统一管理器初始化失败")
                self.logger.error(f"错误信息: {init_result.get('errors', [])}")
                return False

        except Exception as e:
            self.logger.error(f"❌ 统一管理器初始化异常: {e}")
            return False

    def initialize_data_source(self) -> bool:
        """初始化数据源适配器"""
        self.logger.info("初始化Customer数据源适配器...")

        try:
            self.customer_ds = CustomerDataSource()

            if not self.customer_ds.efinance_available:
                self.logger.error("❌ efinance库不可用，无法获取实时数据")
                return False

            self.logger.info("✅ Customer数据源适配器初始化成功")
            return True

        except Exception as e:
            self.logger.error(f"❌ 数据源适配器初始化失败: {e}")
            return False

    def get_realtime_market_data(self) -> Optional[pd.DataFrame]:
        """使用efinance获取沪深市场A股实时数据"""
        self.logger.info(f"使用efinance获取{self.config['market_symbol']}市场实时数据...")

        try:
            if not self.customer_ds.efinance_available:
                self.logger.error("❌ efinance库不可用，无法获取实时数据")
                return None

            # 直接使用efinance获取沪深市场A股最新状况
            self.logger.info("📡 正在调用 ef.stock.get_realtime_quotes() 获取沪深A股实时行情...")
            data = self.customer_ds.ef.stock.get_realtime_quotes()

            if isinstance(data, pd.DataFrame) and not data.empty:
                self.logger.info(f"✅ 成功获取实时数据，共 {len(data)} 条记录")
                self.logger.info(f"📊 数据列: {list(data.columns)}")

                # 数据验证
                if self.config["enable_data_validation"]:
                    if self._validate_market_data(data):
                        self.logger.info("✅ 数据验证通过")
                    else:
                        self.logger.warning("⚠️ 数据验证存在问题，但继续处理")

                # 添加数据获取时间戳
                if self.config["add_timestamp_column"]:
                    data["data_update_time"] = datetime.now()
                    data["trade_date"] = datetime.now().date()  # 添加交易日期用于PostgreSQL存储
                    self.logger.info("✅ 已添加数据更新时间戳和交易日期列")

                return data
            else:
                self.logger.error("❌ efinance未返回有效的实时市场数据")
                return None

        except Exception as e:
            self.logger.error(f"❌ 使用efinance获取实时市场数据失败: {e}")
            import traceback

            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
            return None

    def _validate_market_data(self, data: pd.DataFrame) -> bool:
        """验证市场数据的基本结构"""
        try:
            # 检查数据基本要求
            if data.empty:
                self.logger.warning("⚠️ 数据为空")
                return False

            # 检查是否包含关键列（这些列名可能因数据源而异）
            expected_columns = ["股票代码", "code", "symbol", "ts_code"]
            has_symbol_column = any(col in data.columns for col in expected_columns)

            if not has_symbol_column:
                self.logger.warning(f"⚠️ 数据缺少股票代码列，可用列: {list(data.columns)}")
                # 不算验证失败，可能列名不同

            # 检查数据类型合理性
            null_counts = data.isnull().sum()
            if null_counts.any():
                self.logger.info(f"📊 数据包含空值: {null_counts[null_counts > 0].head().to_dict()}")

            return True

        except Exception as e:
            self.logger.error(f"❌ 数据验证失败: {e}")
            return False

    def save_data_using_unified_interface(self, data: pd.DataFrame) -> Dict[str, bool]:
        """使用MyStocks统一接口保存数据"""
        self.logger.info("使用MyStocks统一接口保存数据...")

        save_results = {}

        try:
            # 方案1: 保存为实时数据（Redis热数据）
            if self.config["save_as_realtime"]:
                self.logger.info("📊 保存为实时行情数据 → Redis")

                try:
                    # 使用统一管理器的自动路由保存
                    success = self.unified_manager.save_data_by_classification(
                        data, DataClassification.REALTIME_POSITIONS
                    )

                    if success:
                        self.logger.info("✅ 实时数据保存成功 → Redis (热数据)")
                    else:
                        self.logger.error("❌ 实时数据保存失败")

                    save_results["realtime"] = success

                except Exception as e:
                    self.logger.error(f"❌ 实时数据保存异常: {e}")
                    save_results["realtime"] = False

            # 方案2: 保存为日线数据（PostgreSQL持久化存储）
            if self.config["save_as_daily"]:
                self.logger.info("💾 保存为日线数据 → PostgreSQL+TimescaleDB")

                try:
                    # 准备日线数据格式（用于PostgreSQL存储）
                    daily_data = self._prepare_daily_data(data)

                    if daily_data is not None and not daily_data.empty:
                        # 使用统一管理器的自动路由保存到PostgreSQL
                        success = self.unified_manager.save_data_by_classification(
                            daily_data, DataClassification.DAILY_KLINE
                        )

                        if success:
                            self.logger.info("✅ 日线数据保存成功 → PostgreSQL+TimescaleDB (持久化存储)")
                        else:
                            self.logger.error("❌ 日线数据保存失败")

                        save_results["daily"] = success
                    else:
                        self.logger.warning("⚠️ 日线数据格式化失败，跳过保存")
                        save_results["daily"] = False

                except Exception as e:
                    self.logger.error(f"❌ 日线数据保存异常: {e}")
                    save_results["daily"] = False

            # 方案3: 保存为Tick数据（TDengine时序存储，可选）
            if self.config["save_as_tick"]:
                self.logger.info("⏱️ 保存为Tick数据 → TDengine")

                try:
                    # 准备Tick数据格式
                    tick_data = self._prepare_tick_data(data)

                    if tick_data is not None and not tick_data.empty:
                        # 使用统一管理器的自动路由保存
                        success = self.unified_manager.save_data_by_classification(
                            tick_data, DataClassification.TICK_DATA
                        )

                        if success:
                            self.logger.info("✅ Tick数据保存成功 → TDengine (时序存储)")
                        else:
                            self.logger.error("❌ Tick数据保存失败")

                        save_results["tick"] = success
                    else:
                        self.logger.warning("⚠️ Tick数据格式化失败，跳过保存")
                        save_results["tick"] = False

                except Exception as e:
                    self.logger.error(f"❌ Tick数据保存异常: {e}")
                    save_results["tick"] = False

            return save_results

        except Exception as e:
            self.logger.error(f"❌ 统一接口保存数据失败: {e}")
            return {"error": False}

    def _prepare_daily_data(self, market_data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """将实时市场数据转换为日线数据格式（用于PostgreSQL存储）"""
        try:
            # 将实时数据转换为日线格式，用于PostgreSQL+TimescaleDB存储
            daily_data = market_data.copy()

            # efinance的get_realtime_quotes()返回的常见列名映射
            column_mapping = {
                "股票代码": "symbol",
                "股票名称": "name",
                "最新价": "close",
                "涨跌幅": "pct_chg",
                "涨跌额": "change",
                "成交量": "volume",
                "成交额": "amount",
                "振幅": "amplitude",
                "最高": "high",
                "最低": "low",
                "今开": "open",
                "昨收": "pre_close",
            }

            # 执行列名映射
            for old_col, new_col in column_mapping.items():
                if old_col in daily_data.columns and new_col not in daily_data.columns:
                    daily_data[new_col] = daily_data[old_col]

            # 确保必要的列存在（符合DAILY_KLINE的表结构）

            # 如果没有trade_date，使用当前日期
            if "trade_date" not in daily_data.columns:
                daily_data["trade_date"] = datetime.now().date()

            # 确保symbol列存在
            if "symbol" not in daily_data.columns:
                if "股票代码" in daily_data.columns:
                    daily_data["symbol"] = daily_data["股票代码"]
                else:
                    self.logger.warning("⚠️ 无法找到股票代码列")
                    return None

            # 设置OHLC数据（如果实时数据中没有完整的OHLC，使用最新价作为close）
            if "close" not in daily_data.columns and "最新价" in daily_data.columns:
                daily_data["close"] = daily_data["最新价"]

            # 数据清洗：处理数值字段中的无效值
            numeric_columns = ["open", "high", "low", "close", "volume", "amount"]
            for col in numeric_columns:
                if col in daily_data.columns:
                    # 将字符串 '-' 和空值转换为 None
                    daily_data[col] = daily_data[col].replace(["-", "---", "", " "], None)
                    # 尝试转换为数值类型
                    daily_data[col] = pd.to_numeric(daily_data[col], errors="coerce")

            # 如果没有OHLC的其他值，使用最新价填充
            for col in ["open", "high", "low"]:
                if col not in daily_data.columns and "close" in daily_data.columns:
                    daily_data[col] = daily_data["close"]

            # 添加时间戳
            daily_data["created_at"] = datetime.now()
            daily_data["updated_at"] = datetime.now()

            # 只保留PostgreSQL表结构需要的列
            postgres_columns = [
                "symbol",
                "trade_date",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "amount",
                "created_at",
                "updated_at",
            ]

            # 过滤存在的列
            available_columns = [col for col in postgres_columns if col in daily_data.columns]
            daily_data = daily_data[available_columns]

            self.logger.info(f"📊 日线数据格式化完成，共 {len(daily_data)} 条记录")
            self.logger.info(f"📋 包含列: {list(daily_data.columns)}")

            return daily_data

        except Exception as e:
            self.logger.error(f"❌ 日线数据格式化失败: {e}")
            import traceback

            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
            return None

    def _prepare_tick_data(self, market_data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """将市场数据转换为Tick数据格式（用于TDengine存储）"""
        try:
            # 这里需要根据实际的market_data结构来映射到标准的Tick格式
            # 标准Tick格式通常包含: ts(时间戳), symbol(代码), price(价格), volume(成交量), amount(成交额)

            tick_data = market_data.copy()

            # 添加时间戳列（如果没有的话）
            if "ts" not in tick_data.columns:
                tick_data["ts"] = datetime.now()

            # 尝试映射常见的列名
            column_mapping = {
                "股票代码": "symbol",
                "code": "symbol",
                "现价": "price",
                "最新价": "price",
                "price": "price",
                "成交量": "volume",
                "volume": "volume",
                "成交额": "amount",
                "amount": "amount",
            }

            # 执行列名映射
            for old_col, new_col in column_mapping.items():
                if old_col in tick_data.columns and new_col not in tick_data.columns:
                    tick_data[new_col] = tick_data[old_col]

            # 确保必要的列存在
            required_columns = ["ts", "symbol", "price"]
            missing_columns = [col for col in required_columns if col not in tick_data.columns]

            if missing_columns:
                self.logger.warning(f"⚠️ Tick数据缺少必要列: {missing_columns}")
                # 尝试填充默认值
                for col in missing_columns:
                    if col == "symbol":
                        tick_data["symbol"] = "UNKNOWN"
                    elif col == "price":
                        tick_data["price"] = 0.0

            self.logger.info(f"📊 Tick数据格式化完成，共 {len(tick_data)} 条记录")
            return tick_data

        except Exception as e:
            self.logger.error(f"❌ Tick数据格式化失败: {e}")
            return None

    def run(self) -> bool:
        """执行完整的数据获取和保存流程"""
        try:
            self.logger.info("=" * 70)
            self.logger.info("🚀 沪深市场A股实时数据保存系统启动")
            self.logger.info("📋 使用MyStocks统一接口规范")
            self.logger.info("=" * 70)

            # 1. 初始化MyStocks统一管理器
            if not self.initialize_unified_manager():
                return False

            # 2. 初始化数据源适配器
            if not self.initialize_data_source():
                return False

            # 3. 获取实时市场数据（支持重试）
            market_data = None
            for attempt in range(self.config["max_retry_attempts"]):
                market_data = self.get_realtime_market_data()
                if market_data is not None:
                    break
                self.logger.warning(f"⚠️ 第 {attempt + 1} 次尝试获取数据失败")

            if market_data is None:
                self.logger.error("💥 多次重试后仍无法获取数据")
                return False

            # 4. 使用统一接口保存数据
            save_results = self.save_data_using_unified_interface(market_data)

            # 5. 检查保存结果
            success_count = sum(1 for result in save_results.values() if result)
            total_count = len(save_results)

            if success_count > 0:
                self.logger.info("=" * 70)
                self.logger.info("🎉 沪深市场A股实时数据保存完成！")
                self.logger.info(f"📊 数据记录数: {len(market_data)}")
                self.logger.info(f"💾 保存成功率: {success_count}/{total_count}")

                # 显示具体的保存结果
                for save_type, result in save_results.items():
                    status = "✅ 成功" if result else "❌ 失败"
                    if save_type == "realtime":
                        self.logger.info(f"🔥 实时数据 → Redis: {status}")
                    elif save_type == "daily":
                        self.logger.info(f"💾 日线数据 → PostgreSQL+TimescaleDB: {status}")
                    elif save_type == "tick":
                        self.logger.info(f"⏱️ Tick数据 → TDengine: {status}")

                # 获取并显示系统状态
                try:
                    status = self.unified_manager.get_system_status()
                    monitoring = status.get("monitoring", {})
                    op_stats = monitoring.get("operation_statistics", {})
                    self.logger.info(f"📈 系统总操作数: {op_stats.get('total_operations', 0)}")
                except Exception:
                    pass

                self.logger.info("=" * 70)
                return success_count == total_count  # 全部成功才返回True
            else:
                self.logger.error("💥 所有数据保存操作都失败了")
                return False

        except Exception as e:
            self.logger.error(f"💥 程序执行过程中发生错误: {e}")
            return False
        finally:
            # 清理资源
            if self.unified_manager:
                self.unified_manager.cleanup()
                self.logger.info("🧹 系统资源已清理")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="沪深市场A股实时数据保存系统 - MyStocks统一接口版")
    parser.add_argument(
        "--config",
        default="realtime_market_config.env",
        help="配置文件路径 (默认: realtime_market_config.env)",
    )
    parser.add_argument("--force-update", action="store_true", help="强制更新，跳过Redis缓存")
    parser.add_argument("--enable-fixation", action="store_true", help="启用Redis数据自动固化")

    args = parser.parse_args()

    print("沪深市场A股实时数据保存系统 - MyStocks统一接口版")
    print("=" * 70)
    print(f"配置文件: {args.config}")
    print("使用MyStocks统一管理器进行自动路由保存")
    print("数据分类: REALTIME_POSITIONS → Redis, DAILY_KLINE → PostgreSQL, TICK_DATA → TDengine(可选)")
    print("数据源: efinance.stock.get_realtime_quotes() - 沪深A股实时行情")
    if args.force_update:
        print("🔄 强制更新模式: 跳过Redis缓存")
    if args.enable_fixation:
        print("💾 自动固化模式: 启用Redis数据固化")
    print("=" * 70)

    # 创建数据保存器
    saver = RealtimeMarketDataSaver(args.config)

    # 如果启用强制更新或固化，导入相关模块
    if args.force_update or args.enable_fixation:
        try:
            from redis_data_fixation import RedisDataFixationManager

            fixation_manager = RedisDataFixationManager(saver.unified_manager)

            if args.force_update:
                print("🔄 执行强制更新...")
                update_result = fixation_manager.force_update_realtime_data(
                    market_symbol=saver.config["market_symbol"], bypass_cache=True
                )
                print(f"强制更新结果: {update_result}")

                if update_result.get("success"):
                    print("✅ 强制更新成功，程序结束")
                    sys.exit(0)
                else:
                    print("❌ 强制更新失败，继续正常流程")

        except ImportError as e:
            print(f"⚠️ 固化模块导入失败: {e}")
            print("继续正常流程...")

    # 正常运行
    success = saver.run()

    exit_code = 0 if success else 1
    print(f"程序执行{'成功' if success else '失败'}，退出码: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
