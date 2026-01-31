#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沪深市场A股实时数据保存系统 - 简化版
专注于实时数据获取和Redis存储，避免复杂的数据库依赖

核心功能：
1. 从efinance获取沪深A股实时数据
2. 保存到Redis热数据存储（5分钟过期）
3. 可选：导出到CSV文件作为备份
4. 支持强制更新（跳过缓存）

作者: MyStocks项目组
日期: 2025-09-21
版本: 简化版 v1.0
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import redis
from dotenv import load_dotenv


class SimpleRealtimeDataSaver:
    """简化版实时数据保存器 - 只使用Redis和CSV"""

    def __init__(self, config_file: str = None):
        """初始化简化版数据保存器"""

        # 设置配置文件路径
        if config_file and os.path.exists(config_file):
            self.config_file = config_file
        elif os.path.exists("db_manager/realtime_market_config.env"):
            self.config_file = "db_manager/realtime_market_config.env"
        elif os.path.exists("realtime_market_config.env"):
            self.config_file = "realtime_market_config.env"
        else:
            self.config_file = None

        self.logger = None
        self.redis_client = None
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
            handlers=[logging.StreamHandler(sys.stdout)],
        )

        self.logger = logging.getLogger("SimpleRealtimeSaver")
        self.logger.info("简化版实时数据保存器初始化")

    def _load_config(self):
        """加载配置参数"""
        # 加载默认环境变量
        load_dotenv()

        # 如果有专用配置文件，则加载
        if self.config_file:
            load_dotenv(self.config_file, override=True)
            self.logger.info("✅ 成功加载配置文件: %s", self.config_file)
        else:
            self.logger.info("⚠️ 使用默认配置")

        # 配置参数
        self.config = {
            # 数据源配置
            "market_symbol": os.getenv("MARKET_SYMBOL", "hs"),
            "data_source_timeout": int(os.getenv("DATA_SOURCE_TIMEOUT", "30")),
            # Redis配置
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", "6379")),
            "redis_password": os.getenv("REDIS_PASSWORD", None),
            "redis_db": int(os.getenv("REDIS_DB", "0")),
            "cache_expire_seconds": int(os.getenv("CACHE_EXPIRE_SECONDS", "300")),
            # 数据处理配置
            "add_timestamp_column": os.getenv("ADD_TIMESTAMP_COLUMN", "true").lower() == "true",
            "enable_data_validation": os.getenv("ENABLE_DATA_VALIDATION", "true").lower() == "true",
            "max_retry_attempts": int(os.getenv("MAX_RETRY_ATTEMPTS", "3")),
            # 备份配置
            "save_to_csv": os.getenv("SAVE_TO_CSV", "true").lower() == "true",
            "csv_backup_dir": os.getenv("CSV_BACKUP_DIR", "./backup"),
            # 日志配置
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
        }

        # 更新日志级别
        log_level = getattr(logging, self.config["log_level"].upper())
        self.logger.setLevel(log_level)

        self.logger.info("✅ 配置参数加载完成")
        self.logger.info("📊 市场代码: %s", self.config["market_symbol"])
        self.logger.info("💾 Redis服务器: {self.config['redis_host']}:{self.config['redis_port']")
        self.logger.info("📁 CSV备份: %s", self.config["save_to_csv"])

    def initialize_redis(self) -> bool:
        """初始化Redis连接"""
        self.logger.info("初始化Redis连接...")

        try:
            # 创建Redis连接（使用连接池）
            self.redis_client = redis.Redis(
                host=self.config["redis_host"],
                port=self.config["redis_port"],
                password=self.config["redis_password"],
                db=self.config["redis_db"],
                decode_responses=True,
                connection_pool=redis.ConnectionPool(
                    host=self.config["redis_host"],
                    port=self.config["redis_port"],
                    password=self.config["redis_password"],
                    db=self.config["redis_db"],
                    max_connections=10,
                ),
            )

            # 测试连接
            self.redis_client.ping()
            self.logger.info("✅ Redis连接成功")
            return True

        except Exception as e:
            self.logger.error("❌ Redis连接失败: %s", e)
            self.logger.info("💡 请检查Redis服务是否启动，或使用CSV备份模式")
            return False

    def close(self):
        """关闭所有连接"""
        if self.redis_client is not None:
            try:
                self.redis_client.close()
                self.logger.info("Redis连接已关闭")
            except Exception as e:
                self.logger.error("关闭Redis连接失败: %s", e)

    def get_realtime_market_data(self) -> Optional[pd.DataFrame]:
        """获取实时市场数据"""
        self.logger.info("获取%s市场实时数据...", self.config["market_symbol"])

        try:
            # 尝试导入efinance
            try:
                import efinance as ef
            except ImportError:
                self.logger.error("❌ efinance库未安装，请运行: pip install efinance")
                return None

            # 获取实时数据
            if self.config["market_symbol"] == "hs":
                # 沪深市场
                data = ef.stock.get_realtime_quotes()
            elif self.config["market_symbol"] == "sh":
                # 上海市场
                data = ef.stock.get_realtime_quotes()
                if data is not None:
                    data = data[data["股票代码"].str.startswith("6")]
            elif self.config["market_symbol"] == "sz":
                # 深圳市场
                data = ef.stock.get_realtime_quotes()
                if data is not None:
                    data = data[data["股票代码"].str.startswith(("0", "3"))]
            else:
                self.logger.error("❌ 不支持的市场代码: %s", self.config["market_symbol"])
                return None

            if isinstance(data, pd.DataFrame) and not data.empty:
                self.logger.info("✅ 成功获取实时数据，共 %s 条记录", len(data))

                # 添加数据获取时间戳
                if self.config["add_timestamp_column"]:
                    data["data_update_time"] = datetime.now()
                    data["market_symbol"] = self.config["market_symbol"]

                # 数据验证
                if self.config["enable_data_validation"]:
                    if self._validate_market_data(data):
                        self.logger.info("✅ 数据验证通过")
                    else:
                        self.logger.warning("⚠️ 数据验证存在问题，但继续处理")

                return data
            else:
                self.logger.error("❌ 未获取到有效的实时市场数据")
                return None

        except Exception as e:
            self.logger.error("❌ 获取实时市场数据失败: %s", e)
            return None

    def _validate_market_data(self, data: pd.DataFrame) -> bool:
        """验证市场数据的基本结构"""
        try:
            if data.empty:
                self.logger.warning("⚠️ 数据为空")
                return False

            # 检查关键列
            expected_columns = ["股票代码", "股票名称"]
            missing_columns = [col for col in expected_columns if col not in data.columns]

            if missing_columns:
                self.logger.warning("⚠️ 缺少关键列: %s", missing_columns)

            # 检查空值
            null_counts = data.isnull().sum()
            if null_counts.any():
                self.logger.info("📊 数据包含空值统计: %s", null_counts[null_counts > 0].head().to_dict())

            return True

        except Exception as e:
            self.logger.error("❌ 数据验证失败: %s", e)
            return False

    def save_to_redis(self, data: pd.DataFrame) -> bool:
        """保存数据到Redis"""
        if not self.redis_client:
            self.logger.warning("⚠️ Redis未连接，跳过Redis保存")
            return False

        try:
            self.logger.info("💾 保存数据到Redis...")

            # 生成Redis键名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            redis_key = f"realtime_positions:{self.config['market_symbol']}:{timestamp}"

            # 将DataFrame转换为JSON
            data_json = data.to_json(orient="records", date_format="iso")

            # 保存到Redis并设置过期时间
            self.redis_client.setex(redis_key, self.config["cache_expire_seconds"], data_json)

            # 设置最新数据键（不过期）
            latest_key = f"realtime_positions:{self.config['market_symbol']}:latest"
            self.redis_client.set(latest_key, redis_key)

            self.logger.info("✅ 数据已保存到Redis: %s", redis_key)
            self.logger.info("⏰ 过期时间: %s 秒", self.config["cache_expire_seconds"])

            return True

        except Exception as e:
            self.logger.error("❌ Redis保存失败: %s", e)
            return False

    def save_to_csv(self, data: pd.DataFrame) -> bool:
        """保存数据到CSV文件"""
        if not self.config["save_to_csv"]:
            return True

        try:
            # 创建备份目录
            backup_dir = self.config["csv_backup_dir"]
            os.makedirs(backup_dir, exist_ok=True)

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"realtime_market_{self.config['market_symbol']}_{timestamp}.csv"
            filepath = os.path.join(backup_dir, filename)

            # 保存CSV
            data.to_csv(filepath, index=False, encoding="utf-8-sig")

            self.logger.info("✅ 数据已备份到CSV: %s", filepath)
            return True

        except Exception as e:
            self.logger.error("❌ CSV保存失败: %s", e)
            return False

    def force_update(self) -> Dict[str, Any]:
        """强制更新（清除缓存并获取最新数据）"""
        self.logger.info("🔄 执行强制更新...")

        try:
            # 清除Redis缓存
            if self.redis_client:
                pattern = f"realtime_positions:{self.config['market_symbol']}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    self.logger.info("🗑️ 已清除 %s 个Redis缓存键", len(keys))

            # 获取最新数据
            fresh_data = self.get_realtime_market_data()

            if fresh_data is None or fresh_data.empty:
                return {"success": False, "error": "获取数据失败"}

            # 标记为强制更新
            fresh_data["force_update_flag"] = True
            fresh_data["update_source"] = "force_update"

            # 保存数据
            save_results = self.save_data(fresh_data)

            result = {
                "success": any(save_results.values()),
                "update_time": datetime.now(),
                "data_count": len(fresh_data),
                "market_symbol": self.config["market_symbol"],
                "save_results": save_results,
            }

            if result["success"]:
                self.logger.info("✅ 强制更新成功: %s 条记录", len(fresh_data))
            else:
                self.logger.error("❌ 强制更新失败")

            return result

        except Exception as e:
            self.logger.error("❌ 强制更新异常: %s", e)
            return {"success": False, "error": str(e)}

    def save_data(self, data: pd.DataFrame) -> Dict[str, bool]:
        """保存数据到所有配置的目标"""
        save_results = {}

        # 保存到Redis
        save_results["redis"] = self.save_to_redis(data)

        # 保存到CSV
        save_results["csv"] = self.save_to_csv(data)

        return save_results

    def run(self, force_update: bool = False) -> bool:
        """执行完整的数据获取和保存流程"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("🚀 简化版沪深市场A股实时数据保存系统启动")
            self.logger.info("=" * 60)

            # 1. 初始化Redis连接（可选）
            self.initialize_redis()

            # 2. 执行强制更新或正常更新
            if force_update:
                result = self.force_update()
                return result["success"]

            # 3. 获取实时市场数据（支持重试）
            market_data = None
            for attempt in range(self.config["max_retry_attempts"]):
                market_data = self.get_realtime_market_data()
                if market_data is not None:
                    break
                self.logger.warning("⚠️ 第 %s 次尝试获取数据失败", attempt + 1)

            if market_data is None:
                self.logger.error("💥 多次重试后仍无法获取数据")
                return False

            # 4. 保存数据
            save_results = self.save_data(market_data)

            # 5. 检查保存结果
            success_count = sum(1 for result in save_results.values() if result)
            total_count = len(save_results)

            if success_count > 0:
                self.logger.info("=" * 60)
                self.logger.info("🎉 实时数据保存完成！")
                self.logger.info("📊 数据记录数: %s", len(market_data))
                self.logger.info("💾 保存成功率: %s/%s", success_count, total_count)

                # 显示具体的保存结果
                for save_type, result in save_results.items():
                    status = "✅ 成功" if result else "❌ 失败"
                    if save_type == "redis":
                        self.logger.info("🔥 Redis存储: %s", status)
                    elif save_type == "csv":
                        self.logger.info("📁 CSV备份: %s", status)

                self.logger.info("=" * 60)
                return True
            else:
                self.logger.error("💥 所有数据保存操作都失败了")
                return False

        except Exception as e:
            self.logger.error("💥 程序执行过程中发生错误: %s", e)
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="沪深市场A股实时数据保存系统 - 简化版")
    parser.add_argument("--config", default=None, help="配置文件路径")
    parser.add_argument("--force-update", action="store_true", help="强制更新，跳过缓存")
    parser.add_argument(
        "--market",
        choices=["hs", "sh", "sz"],
        default="hs",
        help="市场代码 (hs=沪深, sh=上海, sz=深圳)",
    )

    args = parser.parse_args()

    print("沪深市场A股实时数据保存系统 - 简化版")
    print("=" * 60)
    print(f"市场代码: {args.market}")
    print(f"强制更新: {'是' if args.force_update else '否'}")
    if args.config:
        print(f"配置文件: {args.config}")
    print("=" * 60)

    # 设置市场代码环境变量
    os.environ["MARKET_SYMBOL"] = args.market

    # 创建数据保存器并运行
    saver = SimpleRealtimeDataSaver(args.config)
    success = saver.run(force_update=args.force_update)

    exit_code = 0 if success else 1
    print(f"程序执行{'成功' if success else '失败'}，退出码: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
