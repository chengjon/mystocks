#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将通过customer接口获取的股票实时行情数据保存到本地数据库中
完整的数据库保存工作流程，遵循db_manager的工作原理
"""

import sys
import os
import pandas as pd
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dotenv import load_dotenv

# 将项目根目录添加到模块搜索路径中
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from adapters.customer_adapter import CustomerDataSource
from db_manager.database_manager import DatabaseTableManager, DatabaseType
from db_manager.df2sql import create_sql_cmd

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("realtime_data_save.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("RealtimeDataSaver")

# 配置参数
MARKET_SYMBOL = "hs"  # 'hs'表示沪深市场
DATABASE_TYPE = DatabaseType.MYSQL  # 数据库类型
DATABASE_NAME = "test_db"  # 数据库名称
TABLE_NAME = "stock_realtime_data"  # 表名
UPDATE_MODE = "replace"  # 数据更新模式: 'replace', 'append', 'ignore'
BATCH_SIZE = 1000  # 批量插入大小
MAX_RETRIES = 3  # 最大重试次数


class RealtimeDataSaver:
    """实时数据保存器 - 完整的数据库保存工作流程"""

    def __init__(
        self,
        database_type=DATABASE_TYPE,
        database_name=DATABASE_NAME,
        table_name=TABLE_NAME,
        update_mode=UPDATE_MODE,
    ):
        """初始化数据保存器"""
        self.database_type = database_type
        self.database_name = database_name
        self.table_name = table_name
        self.update_mode = update_mode

        # 初始化组件
        self.customer_source = CustomerDataSource()
        self.db_manager = DatabaseTableManager()

        logger.info(
            f"初始化实时数据保存器: {database_type.value}/{database_name}/{table_name}"
        )

    def _validate_dataframe(self, df: pd.DataFrame) -> bool:
        """验证DataFrame数据的有效性"""
        if df is None or df.empty:
            logger.warning("DataFrame为空或None")
            return False

        # 检查必要的列是否存在
        required_columns = ["股票代码", "股票名称"]  # 根据实际数据调整
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logger.warning(f"缺少必要的列: {missing_columns}")
            # 不阻止保存，只是警告

        logger.info(f"数据验证通过: {len(df)}行, {len(df.columns)}列")
        return True

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备和清理DataFrame数据"""
        # 创建副本避免修改原数据
        prepared_df = df.copy()

        # 添加时间戳
        prepared_df["data_timestamp"] = datetime.now()
        prepared_df["created_at"] = datetime.now()

        # 处理空值
        prepared_df = prepared_df.fillna("")

        # 处理列名，确保符合数据库命名规范
        prepared_df.columns = [
            col.replace(" ", "_").replace("-", "_") for col in prepared_df.columns
        ]

        logger.info(f"数据准备完成: {len(prepared_df)}行")
        return prepared_df

    def _generate_table_columns(self, df: pd.DataFrame) -> List[Dict]:
        """根据DataFrame生成表列定义"""
        columns = []

        # 添加自增主键
        columns.append(
            {
                "name": "id",
                "type": "INT",
                "nullable": False,
                "primary_key": True,
                "comment": "自增主键",
            }
        )

        for col_name, dtype in df.dtypes.items():
            col_info = {"name": col_name, "nullable": True}

            # 根据pandas数据类型映射到SQL数据类型
            if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(
                dtype
            ):
                max_length = df[col_name].astype(str).apply(len).max()
                varchar_length = min(int(max_length * 1.2) + 50, 500)  # 增加缓冲
                col_info["type"] = "VARCHAR"
                col_info["length"] = varchar_length
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                col_info["type"] = "TIMESTAMP"
                col_info["nullable"] = False if "timestamp" in col_name else True
            elif pd.api.types.is_float_dtype(dtype):
                col_info["type"] = "DECIMAL"
                col_info["precision"] = 18
                col_info["scale"] = 6
            elif pd.api.types.is_integer_dtype(dtype):
                max_value = df[col_name].max() if not pd.isna(df[col_name].max()) else 0
                min_value = df[col_name].min() if not pd.isna(df[col_name].min()) else 0
                if max_value > 2147483647 or min_value < -2147483648:
                    col_info["type"] = "BIGINT"
                else:
                    col_info["type"] = "INT"
            elif pd.api.types.is_bool_dtype(dtype):
                col_info["type"] = "TINYINT"
            else:
                col_info["type"] = "TEXT"

            col_info["comment"] = f"股票数据字段: {col_name}"
            columns.append(col_info)

        logger.info(f"生成表结构定义: {len(columns)}个字段")
        return columns

    def _create_table_if_not_exists(self, df: pd.DataFrame) -> bool:
        """如果表不存在则创建表"""
        try:
            # 检查表是否存在
            if self._table_exists():
                logger.info(f"表 {self.table_name} 已存在")
                return True

            # 生成列定义
            columns = self._generate_table_columns(df)

            # 创建表
            logger.info(f"正在创建表 {self.table_name}...")
            success = self.db_manager.create_table(
                self.database_type, self.database_name, self.table_name, columns
            )

            if success:
                logger.info(f"表 {self.table_name} 创建成功")
            else:
                logger.error(f"表 {self.table_name} 创建失败")

            return success

        except Exception as e:
            logger.error(f"创建表时出现错误: {e}")
            return False

    def _table_exists(self) -> bool:
        """检查表是否存在"""
        try:
            conn = self.db_manager.get_connection(
                self.database_type, self.database_name
            )
            cursor = conn.cursor()

            if self.database_type == DatabaseType.MYSQL:
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s AND table_name = %s",
                    (self.database_name, self.table_name),
                )
            elif self.database_type == DatabaseType.POSTGRESQL:
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = %s",
                    (self.table_name,),
                )
            else:
                # 对于其他数据库类型，尝试查询表
                cursor.execute(f"SELECT 1 FROM {self.table_name} LIMIT 1")

            result = cursor.fetchone()
            return result[0] > 0 if result else False

        except Exception:
            return False

    def _insert_data_batch(self, df: pd.DataFrame) -> bool:
        """批量插入数据"""
        try:
            conn = self.db_manager.get_connection(
                self.database_type, self.database_name
            )
            cursor = conn.cursor()

            # 构建插入语句
            columns = [col for col in df.columns]  # 排除id列
            placeholders = ", ".join(["%s"] * len(columns))

            if self.update_mode == "replace":
                insert_sql = f"REPLACE INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            elif self.update_mode == "ignore":
                insert_sql = f"INSERT IGNORE INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            else:  # append
                insert_sql = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            # 批量插入
            records = df.values.tolist()

            for i in range(0, len(records), BATCH_SIZE):
                batch = records[i : i + BATCH_SIZE]
                cursor.executemany(insert_sql, batch)
                logger.info(f"已插入批次: {i + len(batch)}/{len(records)}")

            conn.commit()
            logger.info(f"成功插入 {len(records)} 条记录")
            return True

        except Exception as e:
            logger.error(f"插入数据时出现错误: {e}")
            conn.rollback()
            return False

    def save_realtime_data(self, market_symbol: str = MARKET_SYMBOL) -> bool:
        """完整的实时数据保存流程"""
        logger.info(f"开始保存 {market_symbol} 市场实时数据")

        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                # 1. 获取实时数据
                logger.info(f"正在获取{market_symbol}市场A股最新状况...")
                realtime_data = self.customer_source.get_real_time_data(market_symbol)

                # 2. 验证数据
                if not isinstance(
                    realtime_data, pd.DataFrame
                ) or not self._validate_dataframe(realtime_data):
                    logger.error("获取的数据无效")
                    return False

                logger.info(f"成功获取到{len(realtime_data)}行实时数据")

                # 3. 准备数据
                prepared_data = self._prepare_dataframe(realtime_data)

                # 4. 创建表（如果不存在）
                if not self._create_table_if_not_exists(prepared_data):
                    logger.error("无法创建或访问数据表")
                    return False

                # 5. 插入数据
                if self._insert_data_batch(prepared_data):
                    logger.info("实时数据保存完成")
                    return True
                else:
                    raise Exception("数据插入失败")

            except Exception as e:
                retry_count += 1
                logger.error(f"保存失败 (重试 {retry_count}/{MAX_RETRIES}): {e}")
                if retry_count < MAX_RETRIES:
                    time.sleep(2**retry_count)  # 指数退避

        logger.error("达到最大重试次数，保存失败")
        return False

    def cleanup(self):
        """清理资源"""
        try:
            self.db_manager.close_all_connections()
            logger.info("资源清理完成")
        except Exception as e:
            logger.error(f"资源清理失败: {e}")


def save_realtime_data_to_db(
    market_symbol=MARKET_SYMBOL,
    database_type=DATABASE_TYPE,
    database_name=DATABASE_NAME,
    table_name=TABLE_NAME,
    update_mode=UPDATE_MODE,
):
    """将股票实时行情数据保存到数据库 - 向后兼容的函数接口"""
    saver = RealtimeDataSaver(
        database_type=database_type,
        database_name=database_name,
        table_name=table_name,
        update_mode=update_mode,
    )

    try:
        return saver.save_realtime_data(market_symbol)
    finally:
        saver.cleanup()


def save_realtime_data_continuous(
    market_symbol=MARKET_SYMBOL,
    interval_minutes=5,
    database_type=DATABASE_TYPE,
    database_name=DATABASE_NAME,
    table_name=TABLE_NAME,
):
    """连续保存实时数据 - 定时任务模式"""
    saver = RealtimeDataSaver(database_type, database_name, table_name)

    logger.info(f"开始连续数据保存任务，间隔: {interval_minutes}分钟")

    try:
        while True:
            logger.info("执行数据保存任务...")
            success = saver.save_realtime_data(market_symbol)

            if success:
                logger.info(f"数据保存成功，等待{interval_minutes}分钟...")
            else:
                logger.error(f"数据保存失败，等待{interval_minutes}分钟后重试...")

            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        logger.info("接收到停止信号，正在退出...")
    except Exception as e:
        logger.error(f"连续保存任务出错: {e}")
    finally:
        saver.cleanup()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="保存股票实时行情数据到数据库")
    parser.add_argument("--market", default=MARKET_SYMBOL, help="市场代码 (默认: hs)")
    parser.add_argument(
        "--db_type", default=DATABASE_TYPE.value, help="数据库类型 (默认: MYSQL)"
    )
    parser.add_argument(
        "--db_name", default=DATABASE_NAME, help="数据库名称 (默认: test_db)"
    )
    parser.add_argument(
        "--table", default=TABLE_NAME, help="表名 (默认: stock_realtime_data)"
    )
    parser.add_argument(
        "--mode",
        default=UPDATE_MODE,
        choices=["replace", "append", "ignore"],
        help="数据更新模式",
    )
    parser.add_argument(
        "--continuous", action="store_true", help="连续模式（定时任务）"
    )
    parser.add_argument(
        "--interval", type=int, default=5, help="连续模式的间隔时间（分钟）"
    )

    args = parser.parse_args()

    # 将数据库类型字符串转换为枚举
    db_type_map = {
        "TDengine": DatabaseType.TDENGINE,
        "PostgreSQL": DatabaseType.POSTGRESQL,
        "Redis": DatabaseType.REDIS,
        "MySQL": DatabaseType.MYSQL,
        "MariaDB": DatabaseType.MARIADB,
    }

    db_type = db_type_map.get(args.db_type, DATABASE_TYPE)

    if args.continuous:
        # 连续模式
        save_realtime_data_continuous(
            market_symbol=args.market,
            interval_minutes=args.interval,
            database_type=db_type,
            database_name=args.db_name,
            table_name=args.table,
        )
    else:
        # 单次执行模式
        success = save_realtime_data_to_db(
            market_symbol=args.market,
            database_type=db_type,
            database_name=args.db_name,
            table_name=args.table,
            update_mode=args.mode,
        )

        if success:
            logger.info("数据保存成功完成")
        else:
            logger.error("数据保存失败")
            sys.exit(1)
