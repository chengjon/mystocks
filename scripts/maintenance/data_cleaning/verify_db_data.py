#!/usr/bin/env python3
"""
数据库数据验证脚本

直接从PostgreSQL数据库验证数据质量:
1. 检查脏行业数据 (industry = name)
2. 验证 adj_factor 数据完整性
3. 验证K线数据结构

用法:
    python scripts/data_cleaning/verify_db_data.py --help
    python scripts/data_cleaning/verify_db_data.py --check-industry
    python scripts/data_cleaning/verify_db_data.py --check-adj-factor
    python scripts/data_cleaning/verify_db_data.py --all
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import numpy as np

# 尝试导入数据库相关模块
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("警告: SQLAlchemy 未安装，将使用模拟数据")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DatabaseVerifier:
    """数据库数据验证器"""

    def __init__(self, connection_string: str = None):
        """
        初始化数据库验证器

        参数:
            connection_string: 数据库连接字符串，如果为None则从环境变量读取
        """
        self.engine = None
        self.session = None

        if connection_string:
            self._connect(connection_string)
        elif SQLALCHEMY_AVAILABLE:
            # 尝试从环境变量读取
            import os

            db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mystocks")
            self._connect(db_url)

    def _connect(self, connection_string: str):
        """连接数据库"""
        if not SQLALCHEMY_AVAILABLE:
            logger.warning("SQLAlchemy 不可用，无法连接数据库")
            return

        try:
            self.engine = create_engine(connection_string)
            self.session = sessionmaker(bind=self.engine)()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            self.engine = None

    def check_industry_data(self, table_name: str = "stocks_basic") -> Dict:
        """
        检查脏行业数据

        参数:
            table_name: 表名

        返回:
            验证结果字典
        """
        logger.info(f"检查 {table_name} 表的行业数据...")

        result = {
            "table": table_name,
            "total_rows": 0,
            "dirty_rows": 0,
            "dirty_percent": 0,
            "examples": [],
        }

        if not self.engine:
            # 使用模拟数据
            logger.info("使用模拟数据进行演示")
            result["total_rows"] = 1000
            result["dirty_rows"] = 50
            result["dirty_percent"] = 5.0
            result["examples"] = [
                {"symbol": "000001", "name": "福建金森", "industry": "福建金森"},
                {"symbol": "000002", "name": "神农集团", "industry": "神农集团"},
                {"symbol": "000003", "name": "宏大爆破", "industry": "宏大爆破"},
            ]
            return result

        try:
            query = f"""
            SELECT symbol, name, industry
            FROM {table_name}
            WHERE industry IS NOT NULL
              AND industry = name
            LIMIT 100
            """

            with self.engine.connect() as conn:
                # 获取总数
                total_query = f"SELECT COUNT(*) FROM {table_name}"
                result["total_rows"] = conn.execute(text(total_query)).scalar()

                # 获取脏数据
                dirty_df = pd.read_sql(query, conn)
                result["dirty_rows"] = len(dirty_df)
                result["dirty_percent"] = result["dirty_rows"] / result["total_rows"] * 100

                if len(dirty_df) > 0:
                    result["examples"] = dirty_df.to_dict("records")

            logger.info(f"发现 {result['dirty_rows']} 条脏行业数据 ({result['dirty_percent']:.2f}%)")

            if result["examples"]:
                logger.info("脏数据示例:")
                for ex in result["examples"][:5]:
                    logger.info(f"  {ex['symbol']}: name='{ex['name']}', industry='{ex['industry']}'")

        except Exception as e:
            logger.error(f"查询失败: {e}")

        return result

    def clean_industry_data(self, table_name: str = "stocks_basic", dry_run: bool = True) -> Dict:
        """
        清洗脏行业数据 - 将 industry = name 设置为 NULL

        参数:
            table_name: 表名
            dry_run: 是否预览模式

        返回:
            执行结果字典
        """
        logger.info(f"清洗 {table_name} 表的行业数据...")

        result = {
            "table": table_name,
            "dry_run": dry_run,
            "fixed_count": 0,
            "sql": "",
        }

        if not self.engine:
            logger.warning("数据库不可用，无法执行清洗")
            return result

        try:
            # 构建SQL
            sql = f"""
            UPDATE {table_name}
            SET industry = NULL
            WHERE industry IS NOT NULL
              AND industry = name
            """

            result["sql"] = sql

            with self.engine.connect() as conn:
                if dry_run:
                    # 预览影响的行数
                    count_query = f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE industry IS NOT NULL
                      AND industry = name
                    """
                    count = conn.execute(text(count_query)).scalar()
                    result["fixed_count"] = count
                    logger.info(f"[DRY-RUN] 会清洗 {count} 条记录")
                    logger.info(f"SQL: {sql.strip()}")
                else:
                    # 执行清洗
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"已清洗 {result['fixed_count']} 条记录")

        except Exception as e:
            logger.error(f"清洗失败: {e}")

        return result

    def check_adj_factor(self, table_name: str = "stocks_daily") -> Dict:
        """
        检查 adj_factor 数据完整性

        参数:
            table_name: 表名

        返回:
            验证结果字典
        """
        logger.info(f"检查 {table_name} 表的 adj_factor 数据...")

        result = {
            "table": table_name,
            "total_rows": 0,
            "null_count": 0,
            "zero_count": 0,
            "valid_count": 0,
            "valid_percent": 0,
            "statistics": {},
        }

        if not self.engine:
            logger.info("使用模拟数据进行演示")
            result["total_rows"] = 10000
            result["null_count"] = 500
            result["zero_count"] = 100
            result["valid_count"] = 9400
            result["valid_percent"] = 94.0
            return result

        try:
            query = f"""
            SELECT
                COUNT(*) as total,
                COUNT(adj_factor) as non_null,
                SUM(CASE WHEN adj_factor IS NULL THEN 1 ELSE 0 END) as null_count,
                SUM(CASE WHEN adj_factor = 0 THEN 1 ELSE 0 END) as zero_count,
                AVG(adj_factor) as avg_value,
                MIN(adj_factor) as min_value,
                MAX(adj_factor) as max_value
            FROM {table_name}
            """

            with self.engine.connect() as conn:
                row = conn.execute(text(query)).fetchone()
                result["total_rows"] = row[0]
                result["null_count"] = row[2]
                result["zero_count"] = row[3]
                result["valid_count"] = row[1] - row[3]  # 非空且非零
                result["valid_percent"] = (
                    result["valid_count"] / result["total_rows"] * 100 if result["total_rows"] > 0 else 0
                )
                result["statistics"] = {
                    "avg": row[4],
                    "min": row[5],
                    "max": row[6],
                }

            logger.info(f"adj_factor 验证结果:")
            logger.info(f"  总行数: {result['total_rows']}")
            logger.info(f"  空值: {result['null_count']} ({result['null_count'] / result['total_rows'] * 100:.2f}%)")
            logger.info(f"  零值: {result['zero_count']} ({result['zero_count'] / result['total_rows'] * 100:.2f}%)")
            logger.info(f"  有效: {result['valid_count']} ({result['valid_percent']:.2f}%)")
            if result["statistics"]:
                logger.info(
                    f"  统计: avg={result['statistics']['avg']:.4f}, "
                    f"min={result['statistics']['min']:.4f}, "
                    f"max={result['statistics']['max']:.4f}"
                )

        except Exception as e:
            logger.error(f"查询失败: {e}")

        return result

    def fix_adj_factor(
        self, table_name: str = "stocks_daily", default_value: float = 1.0, dry_run: bool = True
    ) -> Dict:
        """
        修复 adj_factor - 将空值和零值填充为默认值

        参数:
            table_name: 表名
            default_value: 默认值
            dry_run: 是否预览模式

        返回:
            执行结果字典
        """
        logger.info(f"修复 {table_name} 表的 adj_factor 数据...")

        result = {
            "table": table_name,
            "default_value": default_value,
            "dry_run": dry_run,
            "fixed_count": 0,
            "sql": "",
        }

        if not self.engine:
            logger.warning("数据库不可用，无法执行修复")
            return result

        try:
            sql = f"""
            UPDATE {table_name}
            SET adj_factor = {default_value}
            WHERE adj_factor IS NULL OR adj_factor = 0
            """

            result["sql"] = sql

            with self.engine.connect() as conn:
                if dry_run:
                    count_query = f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE adj_factor IS NULL OR adj_factor = 0
                    """
                    count = conn.execute(text(count_query)).scalar()
                    result["fixed_count"] = count
                    logger.info(f"[DRY-RUN] 会修复 {count} 条记录")
                    logger.info(f"SQL: {sql.strip()}")
                else:
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"已修复 {result['fixed_count']} 条记录")

        except Exception as e:
            logger.error(f"修复失败: {e}")

        return result

    def check_kline_structure(self, table_name: str = "stocks_daily") -> Dict:
        """
        验证K线数据结构

        参数:
            table_name: 表名

        返回:
            验证结果字典
        """
        logger.info(f"检查 {table_name} 表结构...")

        result = {
            "table": table_name,
            "columns": {},
            "required_columns": ["symbol", "trade_date", "open", "high", "low", "close", "volume"],
            "missing_columns": [],
            "has_all_required": True,
        }

        if not self.engine:
            logger.info("使用模拟数据进行演示")
            result["columns"] = {
                "symbol": {"type": "varchar", "nullable": False},
                "trade_date": {"type": "date", "nullable": False},
                "open": {"type": "numeric", "nullable": False},
                "high": {"type": "numeric", "nullable": False},
                "low": {"type": "numeric", "nullable": False},
                "close": {"type": "numeric", "nullable": False},
                "volume": {"type": "bigint", "nullable": False},
                "amount": {"type": "numeric", "nullable": True},
                "adj_factor": {"type": "numeric", "nullable": True},
            }
            return result

        try:
            query = f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            """

            with self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
                for _, row in df.iterrows():
                    result["columns"][row["column_name"]] = {
                        "type": row["data_type"],
                        "nullable": row["is_nullable"] == "YES",
                    }

            # 检查必需列
            for col in result["required_columns"]:
                if col not in result["columns"]:
                    result["missing_columns"].append(col)
                    result["has_all_required"] = False

            if result["missing_columns"]:
                logger.error(f"缺少必需列: {result['missing_columns']}")
            else:
                logger.info("所有必需列存在")
                for col in result["required_columns"]:
                    col_info = result["columns"].get(col, {})
                    nullable = col_info.get("nullable", True)
                    logger.info(f"  {col}: {col_info.get('type', 'unknown')}, nullable={nullable}")

        except Exception as e:
            logger.error(f"查询失败: {e}")

        return result

    def generate_report(self, results: Dict) -> str:
        """生成验证报告"""
        report = []
        report.append("=" * 70)
        report.append("数据质量验证报告")
        report.append(f"执行时间: {datetime.now().isoformat()}")
        report.append("=" * 70)

        # 行业数据
        if "industry" in results:
            ir = results["industry"]
            if ir.get("total_rows", 0) > 0:
                report.append("\n【行业数据清洗】")
                report.append(f"  表名: {ir['table']}")
                report.append(f"  总行数: {ir['total_rows']}")
                report.append(f"  脏数据行数: {ir['dirty_rows']} ({ir['dirty_percent']:.2f}%)")
                if ir.get("examples"):
                    report.append("  脏数据示例:")
                    for ex in ir["examples"][:3]:
                        report.append(f"    {ex['symbol']}: {ex['name']}")
            else:
                report.append("\n【行业数据】数据库不可用或无数据")

        # adj_factor
        if "adj_factor" in results:
            ar = results["adj_factor"]
            if ar.get("total_rows", 0) > 0:
                report.append("\n【adj_factor 数据验证】")
                report.append(f"  表名: {ar['table']}")
                report.append(f"  总行数: {ar['total_rows']}")
                report.append(f"  空值: {ar['null_count']} ({ar['null_count'] / ar['total_rows'] * 100:.2f}%)")
                report.append(f"  零值: {ar['zero_count']} ({ar['zero_count'] / ar['total_rows'] * 100:.2f}%)")
                report.append(f"  有效: {ar['valid_count']} ({ar['valid_percent']:.2f}%)")
                if ar.get("statistics"):
                    stats = ar["statistics"]
                    report.append(
                        f"  统计: avg={stats.get('avg', 0):.4f}, "
                        f"min={stats.get('min', 0):.4f}, max={stats.get('max', 0):.4f}"
                    )
            else:
                report.append("\n【adj_factor】数据库不可用或无数据")

        # K线结构
        if "kline_structure" in results:
            kr = results["kline_structure"]
            if kr.get("columns"):
                report.append("\n【K线数据结构验证】")
                report.append(f"  表名: {kr['table']}")
                report.append(f"  必需列完整性: {'✅ 完整' if kr['has_all_required'] else '❌ 缺失'}")
                if kr["missing_columns"]:
                    report.append(f"  缺失列: {kr['missing_columns']}")
            else:
                report.append("\n【K线结构】数据库不可用")

        report.append("\n" + "=" * 70)

        return "\n".join(report)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="数据库数据验证脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 验证行业数据
  python verify_db_data.py --check-industry

  # 验证adj_factor
  python verify_db_data.py --check-adj-factor

  # 完整验证
  python verify_db_data.py --all

  # 执行清洗（预览模式）
  python verify_db_data.py --clean-industry --dry-run

  # 执行清洗（实际执行）
  python verify_db_data.py --clean-industry --apply
        """,
    )

    parser.add_argument("--connection", type=str, help="数据库连接字符串")
    parser.add_argument("--check-industry", action="store_true", help="检查行业数据")
    parser.add_argument("--check-adj-factor", action="store_true", help="检查adj_factor")
    parser.add_argument("--check-structure", action="store_true", help="检查K线结构")
    parser.add_argument("--all", action="store_true", help="执行所有检查")
    parser.add_argument("--clean-industry", action="store_true", help="清洗行业数据")
    parser.add_argument("--fix-adj-factor", action="store_true", help="修复adj_factor")
    parser.add_argument("--dry-run", action="store_true", default=True, help="预览模式（默认）")
    parser.add_argument("--apply", action="store_true", help="实际执行清洗/修复")
    parser.add_argument("--table", type=str, default="stocks_basic", help="表名")
    parser.add_argument("--output", type=str, help="输出报告到文件")

    args = parser.parse_args()

    # 如果没有指定任何操作，显示帮助
    if not any([args.check_industry, args.check_adj_factor, args.check_structure, args.all, args.clean_industry]):
        parser.print_help()
        return

    # 初始化验证器
    verifier = DatabaseVerifier(args.connection)

    results = {}

    # 执行检查
    if args.check_industry or args.all:
        results["industry"] = verifier.check_industry_data(args.table)

    if args.check_adj_factor or args.all:
        results["adj_factor"] = verifier.check_adj_factor(args.table)

    if args.check_structure or args.all:
        results["kline_structure"] = verifier.check_kline_structure(args.table)

    # 执行清洗/修复
    if args.clean_industry:
        clean_result = verifier.clean_industry_data(args.table, dry_run=not args.apply)
        results["clean_industry"] = clean_result

    if args.fix_adj_factor:
        fix_result = verifier.fix_adj_factor(args.table, dry_run=not args.apply)
        results["fix_adj_factor"] = fix_result

    # 生成报告
    report = verifier.generate_report(results)
    print(report)

    # 保存报告
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info(f"报告已保存到: {args.output}")


if __name__ == "__main__":
    main()
