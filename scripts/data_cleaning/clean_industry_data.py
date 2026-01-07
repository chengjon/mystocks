#!/usr/bin/env python3
"""
数据清洗和验证脚本

功能:
1. 清洗脏数据 - industry = name 的记录设置为 NULL
2. 验证 adj_factor 数据完整性
3. 验证K线数据结构
4. 生成数据质量报告

用法:
    python scripts/data_cleaning/clean_industry_data.py --help
    python scripts/data_cleaning/clean_industry_data.py --dry-run
    python scripts/data_cleaning/clean_industry_data.py --apply
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清洗器"""

    def __init__(self, dry_run: bool = False):
        """
        初始化数据清洗器

        参数:
            dry_run: True表示仅预览不实际执行清洗
        """
        self.dry_run = dry_run
        self.stats = {
            "total_rows": 0,
            "dirty_industry_rows": 0,
            "null_adj_factor": 0,
            "zero_adj_factor": 0,
            "fixed_rows": 0,
        }

    def load_kline_data(self, file_path: str) -> pd.DataFrame:
        """加载K线数据"""
        logger.info(f"加载K线数据: {file_path}")

        # 根据文件类型选择读取方式
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".parquet"):
            df = pd.read_parquet(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path}")

        logger.info(f"加载完成: {len(df)} 行, {len(df.columns)} 列")
        logger.info(f"列名: {list(df.columns)}")

        self.stats["total_rows"] = len(df)
        return df

    def load_industry_data(self, file_path: str) -> pd.DataFrame:
        """加载行业数据"""
        logger.info(f"加载行业数据: {file_path}")

        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".parquet"):
            df = pd.read_parquet(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path}")

        logger.info(f"加载完成: {len(df)} 行")
        return df

    def identify_dirty_industry_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        识别脏行业数据 - industry == name 的记录

        返回:
            包含脏数据标记的DataFrame
        """
        logger.info("识别脏行业数据...")

        if "industry" not in df.columns or "name" not in df.columns:
            logger.warning("数据中缺少 'industry' 或 'name' 列")
            return df

        # 标记 industry == name 的记录
        dirty_mask = df["industry"] == df["name"]
        dirty_count = dirty_mask.sum()

        self.stats["dirty_industry_rows"] = dirty_count

        if dirty_count > 0:
            logger.warning(f"发现 {dirty_count} 条脏行业数据 ({dirty_count / len(df) * 100:.2f}%)")
            logger.info("脏数据示例:")
            dirty_examples = df[dirty_mask][["symbol", "name", "industry"]].head(10)
            for _, row in dirty_examples.iterrows():
                logger.info(f"  {row['symbol']}: name='{row['name']}', industry='{row['industry']}'")
        else:
            logger.info("未发现脏行业数据")

        return df

    def clean_industry_data(self, df: pd.DataFrame, industry_col: str = "industry") -> pd.DataFrame:
        """
        清洗脏行业数据 - 将 industry == name 设置为 NULL

        参数:
            df: 输入数据
            industry_col: 行业列名

        返回:
            清洗后的DataFrame
        """
        logger.info(f"清洗行业数据: {industry_col} 列")

        if industry_col not in df.columns:
            logger.error(f"列 '{industry_col}' 不存在")
            return df

        df = df.copy()

        # 找出需要清洗的行
        cleanable_mask = df[industry_col] == df["name"]

        if cleanable_mask.any():
            cleaned_count = cleanable_mask.sum()
            self.stats["fixed_rows"] += cleaned_count

            if self.dry_run:
                logger.info(f"[DRY-RUN] 会清洗 {cleaned_count} 条记录")
            else:
                # 将脏数据的 industry 设置为 NULL/空字符串
                df.loc[cleanable_mask, industry_col] = np.nan
                logger.info(f"已清洗 {cleaned_count} 条记录")
        else:
            logger.info("无需清洗")

        return df

    def verify_adj_factor(self, df: pd.DataFrame) -> Dict:
        """
        验证 adj_factor 数据完整性

        参数:
            df: K线数据

        返回:
            验证结果字典
        """
        logger.info("验证 adj_factor 数据...")

        if "adj_factor" not in df.columns:
            logger.warning("数据中缺少 'adj_factor' 列")
            return {
                "has_column": False,
                "total_rows": len(df),
                "null_count": 0,
                "zero_count": 0,
                "valid_count": 0,
                "valid_percent": 0,
            }

        total = len(df)
        null_count = df["adj_factor"].isna().sum()
        zero_count = (df["adj_factor"] == 0).sum()
        # 有效数据: 非空且非零
        valid_count = ((df["adj_factor"].notna()) & (df["adj_factor"] != 0)).sum()

        self.stats["null_adj_factor"] = null_count
        self.stats["zero_adj_factor"] = zero_count

        result = {
            "has_column": True,
            "total_rows": total,
            "null_count": null_count,
            "zero_count": zero_count,
            "valid_count": valid_count,
            "valid_percent": valid_count / total * 100 if total > 0 else 0,
        }

        logger.info(f"adj_factor 验证结果:")
        logger.info(f"  总行数: {total}")
        logger.info(f"  空值: {null_count} ({null_count / total * 100:.2f}%)")
        logger.info(f"  零值: {zero_count} ({zero_count / total * 100:.2f}%)")
        logger.info(f"  有效: {valid_count} ({result['valid_percent']:.2f}%)")

        if null_count > 0 or zero_count > 0:
            logger.warning("adj_factor 存在不完整数据，建议填充默认值 1.0")

        return result

    def verify_kline_structure(self, df: pd.DataFrame) -> Dict:
        """
        验证K线数据结构

        参数:
            df: K线数据

        返回:
            验证结果字典
        """
        logger.info("验证K线数据结构...")

        required_columns = ["symbol", "trade_date", "open", "high", "low", "close", "volume"]
        optional_columns = ["amount", "adj_factor"]

        result = {
            "has_all_required": True,
            "missing_columns": [],
            "column_types": {},
            "null_counts": {},
            "completeness": {},
        }

        # 检查必需列
        for col in required_columns:
            if col not in df.columns:
                result["missing_columns"].append(col)
                result["has_all_required"] = False
            else:
                # 检查数据类型
                result["column_types"][col] = str(df[col].dtype)
                # 检查空值
                null_count = df[col].isna().sum()
                result["null_counts"][col] = null_count
                result["completeness"][col] = (len(df) - null_count) / len(df) * 100 if len(df) > 0 else 0

        if result["missing_columns"]:
            logger.error(f"缺少必需列: {result['missing_columns']}")
        else:
            logger.info("所有必需列存在")
            for col in required_columns:
                null_pct = result["null_counts"].get(col, 0) / len(df) * 100
                logger.info(f"  {col}: {result['column_types'][col]}, 空值率: {null_pct:.2f}%")

        # 检查可选列
        for col in optional_columns:
            if col in df.columns:
                logger.info(f"  可选列 {col}: {df[col].dtype}")

        return result

    def fix_adj_factor(self, df: pd.DataFrame, default_value: float = 1.0) -> pd.DataFrame:
        """
        修复 adj_factor - 将空值和零值填充为默认值

        参数:
            df: 输入数据
            default_value: 默认值

        返回:
            修复后的DataFrame
        """
        logger.info(f"修复 adj_factor (默认值: {default_value})")

        if "adj_factor" not in df.columns:
            logger.warning("数据中缺少 'adj_factor' 列")
            return df

        df = df.copy()

        # 需要修复的行
        fixable_mask = df["adj_factor"].isna() | (df["adj_factor"] == 0)
        fixable_count = fixable_mask.sum()

        if fixable_count > 0:
            self.stats["fixed_rows"] += fixable_count

            if self.dry_run:
                logger.info(f"[DRY-RUN] 会修复 {fixable_count} 条记录的 adj_factor")
            else:
                df.loc[fixable_mask, "adj_factor"] = default_value
                logger.info(f"已修复 {fixable_count} 条记录的 adj_factor")
        else:
            logger.info("无需修复 adj_factor")

        return df

    def generate_report(self) -> str:
        """生成数据清洗报告"""
        report = []
        report.append("=" * 60)
        report.append("数据清洗报告")
        report.append(f"执行时间: {datetime.now().isoformat()}")
        report.append(f"模式: {'预览' if self.dry_run else '执行'}")
        report.append("=" * 60)
        report.append("")
        report.append("统计信息:")
        report.append(f"  总行数: {self.stats['total_rows']}")
        report.append(f"  脏行业数据行数: {self.stats['dirty_industry_rows']}")
        report.append(f"  adj_factor空值行数: {self.stats['null_adj_factor']}")
        report.append(f"  adj_factor零值行数: {self.stats['zero_adj_factor']}")
        report.append(f"  修复行数: {self.stats['fixed_rows']}")
        report.append("")
        report.append("建议:")

        if self.stats["dirty_industry_rows"] > 0:
            report.append(f"  - 发现 {self.stats['dirty_industry_rows']} 条脏行业数据")
            report.append(f"    建议: 将 industry = name 的记录设置为 NULL")

        if self.stats["null_adj_factor"] > 0 or self.stats["zero_adj_factor"] > 0:
            total_bad = self.stats["null_adj_factor"] + self.stats["zero_adj_factor"]
            report.append(f"  - 发现 {total_bad} 条不完整的 adj_factor 数据")
            report.append(f"    建议: 填充默认值 1.0")

        if self.stats["fixed_rows"] == 0:
            report.append("  - 数据质量良好，无需清洗")

        report.append("=" * 60)

        return "\n".join(report)

    def save_data(self, df: pd.DataFrame, output_path: str):
        """保存清洗后的数据"""
        logger.info(f"保存数据: {output_path}")

        if self.dry_run:
            logger.info("[DRY-RUN] 不会实际保存文件")
            return

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if output_path.endswith(".csv"):
            df.to_csv(output_path, index=False)
        elif output_path.endswith(".parquet"):
            df.to_parquet(output_path, index=False)
        elif output_path.endswith(".xlsx"):
            df.to_excel(output_path, index=False)
        else:
            raise ValueError(f"不支持的文件格式: {output_path}")

        logger.info(f"数据已保存: {len(df)} 行")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="数据清洗和验证脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览清洗操作
  python clean_industry_data.py --dry-run --kline data/kline.csv --industry data/industry.csv

  # 执行清洗
  python clean_industry_data.py --apply --kline data/kline.csv --output data/kline_cleaned.csv

  # 仅验证数据
  python clean_industry_data.py --verify-only --kline data/kline.csv
        """,
    )

    parser.add_argument("--kline", type=str, help="K线数据文件路径")
    parser.add_argument("--industry", type=str, help="行业数据文件路径 (可选)")
    parser.add_argument("--output", type=str, help="输出文件路径")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际执行清洗")
    parser.add_argument("--verify-only", action="store_true", help="仅验证数据，不清洗")
    parser.add_argument("--fix-adj-factor", action="store_true", help="修复 adj_factor 数据")
    parser.add_argument("--adj-default", type=float, default=1.0, help="adj_factor 默认值")
    parser.add_argument(
        "--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别"
    )

    args = parser.parse_args()

    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # 初始化清洗器
    cleaner = DataCleaner(dry_run=args.dry_run)

    # 验证模式
    if args.verify_only and args.kline:
        df = cleaner.load_kline_data(args.kline)

        print("\n" + "=" * 60)
        print("K线数据结构验证")
        print("=" * 60)
        cleaner.verify_kline_structure(df)

        print("\n" + "=" * 60)
        print("adj_factor 数据验证")
        print("=" * 60)
        adj_result = cleaner.verify_adj_factor(df)

        print("\n" + "=" * 60)
        print("行业数据清洗验证")
        print("=" * 60)
        cleaner.identify_dirty_industry_data(df)

        print("\n" + cleaner.generate_report())
        return

    # 加载数据
    if args.kline:
        df = cleaner.load_kline_data(args.kline)

        # 验证数据
        print("\n验证数据...")
        cleaner.verify_kline_structure(df)
        cleaner.verify_adj_factor(df)
        dirty_df = cleaner.identify_dirty_industry_data(df)

        # 清洗行业数据
        if not args.verify_only:
            cleaned_df = cleaner.clean_industry_data(dirty_df)

            # 修复 adj_factor
            if args.fix_adj_factor:
                cleaned_df = cleaner.fix_adj_factor(cleaned_df, args.adj_default)

            # 保存数据
            if args.output:
                cleaner.save_data(cleaned_df, args.output)

        # 输出报告
        print("\n" + cleaner.generate_report())

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
