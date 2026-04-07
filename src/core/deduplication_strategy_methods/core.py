#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - 重构版
完全基于原始设计理念实现的配置驱动、自动化管理系统

设计理念：
1. 配置驱动 - 通过YAML配置文件管理所有表结构
2. 自动化管理 - 避免人工手工管理数据库和表
3. 完整监控 - 专门的监控数据库记录所有操作
4. 数据分类 - 基于数据特性的5大分类体系
5. 业务分离 - 监控数据库与业务数据库完全分离

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-09-21
"""

import logging
import os
import traceback
from datetime import datetime
from typing import Dict, List

import yaml

# 导入现有的数据库管理模块
from src.storage.database.database_manager import DatabaseTableManager as OriginalDatabaseTableManager
from src.storage.database.database_manager import (
    DatabaseType,
)

logger = logging.getLogger("MyStocksSystem")


class DeduplicationStrategyCoreMixin:
    """DeduplicationStrategy 方法集 Part 1"""

    def __init__(self, config_file: str = "table_config.yaml"):
        """
        初始化配置驱动的表管理器

        Args:
            config_file: 表配置文件路径
        """
        self.config_file = config_file
        self.original_manager = OriginalDatabaseTableManager()
        self.config_data = None
        self.load_configuration()

        logger.info("配置驱动表管理器初始化完成，配置文件: %s", config_file)

    def load_configuration(self) -> Dict:
        """加载YAML配置文件"""
        try:
            if not os.path.exists(self.config_file):
                logger.warning("配置文件不存在: %s，将创建默认配置", self.config_file)
                self.create_default_config()

            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config_data = yaml.safe_load(f)

            logger.info("成功加载配置文件: %d 个表配置", len(self.config_data.get("tables", [])))
            return self.config_data

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("加载配置文件失败: %s", e)
            raise

    def create_default_config(self):
        """创建默认配置文件"""
        default_config = self._generate_default_config()

        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(
                default_config,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

        logger.info("创建默认配置文件: %s", self.config_file)

    def _generate_default_config(self) -> Dict:
        """生成默认配置结构"""
        return {
            "version": "2.0",
            "metadata": {
                "project": "MyStocks量化交易系统",
                "created_by": "ConfigDrivenTableManager",
                "last_updated": datetime.now().isoformat(),
                "description": "基于原始设计理念的配置驱动表管理",
            },
            "databases": {
                "tdengine": {
                    "host": "${TDENGINE_HOST}",
                    "port": "${TDENGINE_PORT}",
                    "user": "${TDENGINE_USER}",
                    "password": "${TDENGINE_PASSWORD}",
                    "description": "高频行情数据专用库",
                },
                "postgresql": {
                    "host": "${POSTGRESQL_HOST}",
                    "port": "${POSTGRESQL_PORT}",
                    "user": "${POSTGRESQL_USER}",
                    "password": "${POSTGRESQL_PASSWORD}",
                    "description": "通用数据仓库+TimescaleDB时序扩展",
                },
            },
            "tables": self._generate_default_tables(),
            "monitoring": {
                "enable": True,
                "monitor_database": "db_monitor",
                "log_retention_days": 30,
                "alert_channels": [
                    {"type": "email", "recipients": ["admin@mystocks.com"]},
                    {"type": "log", "level": "ERROR"},
                ],
            },
            "maintenance": {
                "backup": {
                    "enable": True,
                    "schedule": "0 2 * * *",
                    "retention_days": 7,
                },
                "data_quality_check": {"enable": True, "schedule": "0 1 * * *"},
                "performance_monitoring": {"enable": True, "slow_query_threshold": 5},
            },
        }

    def _generate_default_tables(self) -> List[Dict]:
        """生成默认表配置"""
        return [
            # TDengine 高频数据表
            {
                "database_type": "TDengine",
                "database_name": "market_data",
                "table_name": "tick_data",
                "is_super_table": True,
                "classification": "tick_data",
                "description": "股票Tick级成交数据",
                "columns": [
                    {
                        "name": "ts",
                        "type": "TIMESTAMP",
                        "nullable": False,
                        "comment": "时间戳",
                    },
                    {"name": "price", "type": "FLOAT", "comment": "成交价格"},
                    {"name": "volume", "type": "BIGINT", "comment": "成交量"},
                    {"name": "amount", "type": "FLOAT", "comment": "成交金额"},
                    {
                        "name": "symbol",
                        "type": "VARCHAR",
                        "length": 20,
                        "is_tag": True,
                        "comment": "股票代码",
                    },
                    {
                        "name": "exchange",
                        "type": "VARCHAR",
                        "length": 10,
                        "is_tag": True,
                        "comment": "交易所",
                    },
                ],
            },
            {
                "database_type": "TDengine",
                "database_name": "market_data",
                "table_name": "minute_kline",
                "is_super_table": True,
                "classification": "minute_kline",
                "description": "分钟级K线数据",
                "columns": [
                    {
                        "name": "ts",
                        "type": "TIMESTAMP",
                        "nullable": False,
                        "comment": "时间戳",
                    },
                    {"name": "open", "type": "FLOAT", "comment": "开盘价"},
                    {"name": "high", "type": "FLOAT", "comment": "最高价"},
                    {"name": "low", "type": "FLOAT", "comment": "最低价"},
                    {"name": "close", "type": "FLOAT", "comment": "收盘价"},
                    {"name": "volume", "type": "BIGINT", "comment": "成交量"},
                    {"name": "amount", "type": "FLOAT", "comment": "成交金额"},
                    {
                        "name": "symbol",
                        "type": "VARCHAR",
                        "length": 20,
                        "is_tag": True,
                        "comment": "股票代码",
                    },
                    {
                        "name": "frequency",
                        "type": "VARCHAR",
                        "length": 10,
                        "is_tag": True,
                        "comment": "频率(1m,5m,15m,30m,60m)",
                    },
                ],
            },
            # PostgreSQL 历史数据表
            {
                "database_type": "PostgreSQL",
                "database_name": "mystocks",
                "table_name": "daily_kline",
                "is_timescale_hypertable": True,
                "time_column": "trade_date",
                "classification": "daily_kline",
                "description": "股票日线OHLCV数据",
                "columns": [
                    {
                        "name": "symbol",
                        "type": "VARCHAR",
                        "length": 20,
                        "nullable": False,
                        "comment": "股票代码",
                    },
                    {
                        "name": "trade_date",
                        "type": "DATE",
                        "nullable": False,
                        "comment": "交易日期",
                    },
                    {
                        "name": "open",
                        "type": "NUMERIC",
                        "precision": 10,
                        "scale": 4,
                        "comment": "开盘价",
                    },
                    {
                        "name": "high",
                        "type": "NUMERIC",
                        "precision": 10,
                        "scale": 4,
                        "comment": "最高价",
                    },
                    {
                        "name": "low",
                        "type": "NUMERIC",
                        "precision": 10,
                        "scale": 4,
                        "comment": "最低价",
                    },
                    {
                        "name": "close",
                        "type": "NUMERIC",
                        "precision": 10,
                        "scale": 4,
                        "comment": "收盘价",
                    },
                    {"name": "volume", "type": "BIGINT", "comment": "成交量"},
                    {
                        "name": "amount",
                        "type": "NUMERIC",
                        "precision": 15,
                        "scale": 2,
                        "comment": "成交金额",
                    },
                    {
                        "name": "adj_factor",
                        "type": "NUMERIC",
                        "precision": 10,
                        "scale": 6,
                        "comment": "复权因子",
                    },
                    {
                        "name": "created_at",
                        "type": "TIMESTAMP",
                        "default": "CURRENT_TIMESTAMP",
                        "comment": "创建时间",
                    },
                    {
                        "name": "updated_at",
                        "type": "TIMESTAMP",
                        "default": "CURRENT_TIMESTAMP",
                        "comment": "更新时间",
                    },
                ],
                "indexes": [
                    {
                        "name": "idx_daily_kline_symbol_date",
                        "columns": ["symbol", "trade_date"],
                        "unique": True,
                    },
                    {"name": "idx_daily_kline_date", "columns": ["trade_date"]},
                    {"name": "idx_daily_kline_symbol", "columns": ["symbol"]},
                ],
            },
            {
                "database_type": "PostgreSQL",
                "database_name": "mystocks",
                "table_name": "technical_indicators",
                "is_timescale_hypertable": True,
                "time_column": "calc_date",
                "classification": "technical_indicators",
                "description": "技术指标数据",
                "columns": [
                    {
                        "name": "symbol",
                        "type": "VARCHAR",
                        "length": 20,
                        "nullable": False,
                        "comment": "股票代码",
                    },
                    {
                        "name": "calc_date",
                        "type": "DATE",
                        "nullable": False,
                        "comment": "计算日期",
                    },
                    {
                        "name": "indicator_name",
                        "type": "VARCHAR",
                        "length": 50,
                        "nullable": False,
                        "comment": "指标名称",
                    },
                    {
                        "name": "indicator_value",
                        "type": "NUMERIC",
                        "precision": 15,
                        "scale": 6,
                        "comment": "指标值",
                    },
                    {
                        "name": "indicator_params",
                        "type": "JSONB",
                        "comment": "指标参数",
                    },
                    {
                        "name": "created_at",
                        "type": "TIMESTAMP",
                        "default": "CURRENT_TIMESTAMP",
                        "comment": "创建时间",
                    },
                ],
                "indexes": [
                    {
                        "name": "idx_tech_ind_symbol_date_name",
                        "columns": ["symbol", "calc_date", "indicator_name"],
                        "unique": True,
                    },
                    {"name": "idx_tech_ind_date", "columns": ["calc_date"]},
                    {"name": "idx_tech_ind_name", "columns": ["indicator_name"]},
                ],
            },
            # PostgreSQL 参考数据表
            {
                "database_type": "PostgreSQL",
                "database_name": "mystocks",
                "table_name": "symbols",
                "classification": "symbols_info",
                "description": "股票代码信息表",
                "columns": [
                    {
                        "name": "symbol_id",
                        "type": "INT",
                        "primary_key": True,
                        "auto_increment": True,
                        "comment": "股票ID",
                    },
                    {
                        "name": "symbol",
                        "type": "VARCHAR",
                        "length": 20,
                        "nullable": False,
                        "comment": "股票代码",
                    },
                    {
                        "name": "name",
                        "type": "VARCHAR",
                        "length": 100,
                        "nullable": False,
                        "comment": "股票名称",
                    },
                    {
                        "name": "exchange",
                        "type": "VARCHAR",
                        "length": 10,
                        "nullable": False,
                        "comment": "交易所",
                    },
                    {
                        "name": "sector",
                        "type": "VARCHAR",
                        "length": 50,
                        "comment": "行业",
                    },
                    {
                        "name": "industry",
                        "type": "VARCHAR",
                        "length": 50,
                        "comment": "子行业",
                    },
                    {"name": "list_date", "type": "DATE", "comment": "上市日期"},
                    {"name": "delist_date", "type": "DATE", "comment": "退市日期"},
                    {
                        "name": "is_active",
                        "type": "BOOLEAN",
                        "default": True,
                        "comment": "是否有效",
                    },
                    {
                        "name": "created_at",
                        "type": "TIMESTAMP",
                        "default": "CURRENT_TIMESTAMP",
                        "comment": "创建时间",
                    },
                    {
                        "name": "updated_at",
                        "type": "TIMESTAMP",
                        "default": "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
                        "comment": "更新时间",
                    },
                ],
                "indexes": [
                    {
                        "name": "uk_symbols_symbol",
                        "columns": ["symbol"],
                        "unique": True,
                    },
                    {"name": "idx_symbols_exchange", "columns": ["exchange"]},
                    {"name": "idx_symbols_sector", "columns": ["sector"]},
                    {"name": "idx_symbols_active", "columns": ["is_active"]},
                ],
            },
            {
                "database_type": "PostgreSQL",
                "database_name": "mystocks",
                "table_name": "trade_calendar",
                "classification": "trade_calendar",
                "description": "交易日历表",
                "columns": [
                    {
                        "name": "calendar_id",
                        "type": "INT",
                        "primary_key": True,
                        "auto_increment": True,
                        "comment": "日历ID",
                    },
                    {
                        "name": "exchange",
                        "type": "VARCHAR",
                        "length": 10,
                        "nullable": False,
                        "comment": "交易所",
                    },
                    {
                        "name": "trade_date",
                        "type": "DATE",
                        "nullable": False,
                        "comment": "日期",
                    },
                    {
                        "name": "is_trading_day",
                        "type": "BOOLEAN",
                        "nullable": False,
                        "comment": "是否交易日",
                    },
                    {
                        "name": "is_weekend",
                        "type": "BOOLEAN",
                        "default": False,
                        "comment": "是否周末",
                    },
                    {
                        "name": "is_holiday",
                        "type": "BOOLEAN",
                        "default": False,
                        "comment": "是否节假日",
                    },
                    {
                        "name": "holiday_name",
                        "type": "VARCHAR",
                        "length": 50,
                        "comment": "节假日名称",
                    },
                    {
                        "name": "created_at",
                        "type": "TIMESTAMP",
                        "default": "CURRENT_TIMESTAMP",
                        "comment": "创建时间",
                    },
                ],
                "indexes": [
                    {
                        "name": "uk_trade_calendar_exchange_date",
                        "columns": ["exchange", "trade_date"],
                        "unique": True,
                    },
                    {"name": "idx_trade_calendar_date", "columns": ["trade_date"]},
                    {
                        "name": "idx_trade_calendar_trading_day",
                        "columns": ["is_trading_day"],
                    },
                ],
            },
        ]

    def auto_create_all_tables(self) -> Dict[str, bool]:
        """
        根据配置文件自动创建所有表

        Returns:
            Dict[str, bool]: 创建结果 {table_key: success}
        """
        logger.info("开始自动创建所有表...")

        if not self.config_data or "tables" not in self.config_data:
            logger.error("配置数据无效或缺少表配置")
            return {}

        results = {}
        success_count = 0
        total_count = len(self.config_data["tables"])

        for table_config in self.config_data["tables"]:
            try:
                table_key = (
                    f"{table_config['database_type']}.{table_config['database_name']}.{table_config['table_name']}"
                )

                logger.info("正在创建表: %s", table_key)
                success = self._create_table_from_config(table_config)

                results[table_key] = success
                if success:
                    success_count += 1
                    logger.info("✅ 表创建成功: %s", table_key)
                else:
                    logger.error("❌ 表创建失败: %s", table_key)

            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(
                    "创建表时出现异常: %s, 错误: %s",
                    table_config.get("table_name", "Unknown"),
                    e,
                )
                results[table_key] = False

        logger.info("表创建完成: %d/%d 成功", success_count, total_count)
        return results

    def _create_table_from_config(self, table_config: Dict) -> bool:
        """
        根据配置创建单个表

        Args:
            table_config: 表配置字典

        Returns:
            bool: 创建是否成功
        """
        try:
            # 转换数据库类型 (Week 3简化后 - 仅支持TDengine和PostgreSQL)
            db_type_str = table_config["database_type"]
            if db_type_str == "TDengine":
                db_type = DatabaseType.TDENGINE
            elif db_type_str == "PostgreSQL":
                db_type = DatabaseType.POSTGRESQL
            elif db_type_str in ["MySQL", "MariaDB", "Redis"]:
                logger.error(
                    "数据库类型 '%s' 已在Week 3架构简化中移除，请使用PostgreSQL",
                    db_type_str,
                )
                logger.error("MySQL数据已迁移至PostgreSQL，Redis已由应用层缓存替代")
                return False
            else:
                logger.error("不支持的数据库类型: %s，仅支持TDengine和PostgreSQL", db_type_str)
                return False

            # 转换列配置
            columns = self._convert_column_config(table_config["columns"])

            # 准备额外参数
            kwargs = {}
            if table_config.get("is_super_table"):
                kwargs["is_super_table"] = True
            if table_config.get("is_timescale_hypertable"):
                kwargs["is_timescale_hypertable"] = True
                kwargs["time_column"] = table_config.get("time_column", "created_at")

            # 创建表
            success = self.original_manager.create_table(
                db_type,
                table_config["database_name"],
                table_config["table_name"],
                columns,
                **kwargs,
            )

            # 创建索引（如果配置了）
            if success and "indexes" in table_config:
                self._create_indexes(table_config, db_type)

            return success

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("创建表失败: %s", e)
            logger.error(traceback.format_exc())
            return False

    def _convert_column_config(self, column_configs: List[Dict]) -> List[Dict]:
        """
        转换列配置格式

        Args:
            column_configs: 配置文件中的列定义

        Returns:
            List[Dict]: 转换后的列定义
        """
        converted_columns = []

        for col_config in column_configs:
            converted_col = {
                "name": col_config["name"],
                "type": col_config["type"],
                "nullable": col_config.get("nullable", True),
                "comment": col_config.get("comment", ""),
            }

            # 添加可选属性
            optional_attrs = [
                "length",
                "precision",
                "scale",
                "default",
                "primary_key",
                "auto_increment",
                "is_tag",
                "unique",
            ]

            for attr in optional_attrs:
                if attr in col_config:
                    converted_col[attr] = col_config[attr]

            converted_columns.append(converted_col)

        return converted_columns
