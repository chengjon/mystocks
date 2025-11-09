#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沪深市场A股实时数据保存系统 - 离线版
完全离线运行，只需要efinance库，数据保存到CSV文件

功能特点：
1. 从efinance获取沪深A股实时数据
2. 保存到CSV文件（带时间戳）
3. 自动创建备份目录
4. 支持强制更新
5. 无需任何数据库依赖

适用场景：
- 快速测试和验证
- 数据收集和备份
- 开发环境测试
- 离线数据分析

作者: MyStocks项目组
日期: 2025-09-21
版本: 离线版 v1.0
"""

import os
import sys
import logging
import argparse
import pandas as pd
import json
from datetime import datetime
from typing import Optional, Dict, Any


class OfflineRealtimeDataSaver:
    """离线版实时数据保存器 - 只使用CSV文件"""

    def __init__(self):
        """初始化离线版数据保存器"""
        self.logger = None
        self.config = {
            "market_symbol": "hs",
            "backup_dir": "./data_backup",
            "add_timestamp": True,
            "enable_validation": True,
            "max_retry_attempts": 3,
            "export_json": True,
            "export_excel": False,
        }

        self._setup_logging()
        self._create_backup_directory()

    def _setup_logging(self):
        """配置日志系统"""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.StreamHandler(sys.stdout)],
        )

        self.logger = logging.getLogger("OfflineRealtimeSaver")
        self.logger.info("离线版实时数据保存器启动")

    def _create_backup_directory(self):
        """创建备份目录"""
        try:
            os.makedirs(self.config["backup_dir"], exist_ok=True)
            self.logger.info(f"✅ 备份目录已创建: {self.config['backup_dir']}")
        except Exception as e:
            self.logger.error(f"❌ 创建备份目录失败: {e}")
            # 使用当前目录作为备份目录
            self.config["backup_dir"] = "."

    def check_dependencies(self) -> bool:
        """检查依赖库"""
        self.logger.info("检查依赖库...")

        missing_libs = []

        # 检查efinance
        try:
            import efinance

            self.logger.info("✅ efinance 已安装")
        except ImportError:
            missing_libs.append("efinance")

        # 检查pandas（通常已安装）
        try:
            import pandas

            self.logger.info("✅ pandas 已安装")
        except ImportError:
            missing_libs.append("pandas")

        if missing_libs:
            self.logger.error(f"❌ 缺少依赖库: {missing_libs}")
            self.logger.info("💡 请运行以下命令安装:")
            for lib in missing_libs:
                self.logger.info(f"   pip install {lib}")
            return False

        self.logger.info("✅ 所有依赖库检查通过")
        return True

    def get_realtime_market_data(
        self, market_symbol: str = None
    ) -> Optional[pd.DataFrame]:
        """获取实时市场数据"""
        symbol = market_symbol or self.config["market_symbol"]
        self.logger.info(f"获取{symbol}市场实时数据...")

        try:
            import efinance as ef

            # 获取实时数据
            self.logger.info("🔄 正在从efinance获取数据...")
            data = ef.stock.get_realtime_quotes()

            if data is None or data.empty:
                self.logger.error("❌ 未获取到数据")
                return None

            # 根据市场代码过滤数据
            if symbol == "sh":
                # 上海市场：6开头的股票
                data = data[data["股票代码"].str.startswith("6")]
            elif symbol == "sz":
                # 深圳市场：0和3开头的股票
                data = data[data["股票代码"].str.startswith(("0", "3"))]
            # 'hs' 沪深市场：使用全部数据

            self.logger.info(f"✅ 成功获取 {symbol} 市场数据，共 {len(data)} 条记录")

            # 添加额外信息
            if self.config["add_timestamp"]:
                data["数据获取时间"] = datetime.now()
                data["市场代码"] = symbol
                data["数据来源"] = "efinance"

            # 数据验证
            if self.config["enable_validation"]:
                self._validate_data(data)

            return data

        except ImportError:
            self.logger.error("❌ efinance库未安装，请运行: pip install efinance")
            return None
        except Exception as e:
            self.logger.error(f"❌ 获取数据失败: {e}")
            return None

    def _validate_data(self, data: pd.DataFrame):
        """验证数据质量"""
        try:
            # 基础检查
            if data.empty:
                self.logger.warning("⚠️ 数据为空")
                return

            # 检查关键列
            key_columns = ["股票代码", "股票名称", "最新价"]
            missing_columns = [col for col in key_columns if col not in data.columns]
            if missing_columns:
                self.logger.warning(f"⚠️ 缺少关键列: {missing_columns}")

            # 统计信息
            self.logger.info(f"📊 数据统计:")
            self.logger.info(f"   总记录数: {len(data)}")
            self.logger.info(f"   列数: {len(data.columns)}")

            # 空值检查
            null_counts = data.isnull().sum()
            if null_counts.sum() > 0:
                self.logger.info(
                    f"   空值统计: {null_counts[null_counts > 0].head().to_dict()}"
                )
            else:
                self.logger.info("   无空值")

            # 价格范围检查
            if "最新价" in data.columns:
                prices = data["最新价"].dropna()
                if len(prices) > 0:
                    self.logger.info(
                        f"   价格范围: {prices.min():.2f} - {prices.max():.2f}"
                    )

            self.logger.info("✅ 数据验证完成")

        except Exception as e:
            self.logger.error(f"❌ 数据验证失败: {e}")

    def save_to_csv(self, data: pd.DataFrame, market_symbol: str = None) -> str:
        """保存数据到CSV文件"""
        try:
            symbol = market_symbol or self.config["market_symbol"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 生成文件名
            filename = f"realtime_market_{symbol}_{timestamp}.csv"
            filepath = os.path.join(self.config["backup_dir"], filename)

            # 保存CSV（使用UTF-8编码，支持中文）
            data.to_csv(filepath, index=False, encoding="utf-8-sig")

            self.logger.info(f"✅ 数据已保存到CSV: {filepath}")
            self.logger.info(f"📊 文件大小: {os.path.getsize(filepath)} 字节")

            return filepath

        except Exception as e:
            self.logger.error(f"❌ CSV保存失败: {e}")
            return None

    def save_to_json(self, data: pd.DataFrame, market_symbol: str = None) -> str:
        """保存数据到JSON文件"""
        if not self.config["export_json"]:
            return None

        try:
            symbol = market_symbol or self.config["market_symbol"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 生成文件名
            filename = f"realtime_market_{symbol}_{timestamp}.json"
            filepath = os.path.join(self.config["backup_dir"], filename)

            # 转换日期时间为字符串
            data_copy = data.copy()
            for col in data_copy.columns:
                if data_copy[col].dtype == "datetime64[ns]":
                    data_copy[col] = data_copy[col].dt.strftime("%Y-%m-%d %H:%M:%S")

            # 保存JSON
            data_dict = data_copy.to_dict(orient="records")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)

            self.logger.info(f"✅ 数据已保存到JSON: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"❌ JSON保存失败: {e}")
            return None

    def save_to_excel(self, data: pd.DataFrame, market_symbol: str = None) -> str:
        """保存数据到Excel文件"""
        if not self.config["export_excel"]:
            return None

        try:
            symbol = market_symbol or self.config["market_symbol"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 生成文件名
            filename = f"realtime_market_{symbol}_{timestamp}.xlsx"
            filepath = os.path.join(self.config["backup_dir"], filename)

            # 保存Excel
            data.to_excel(filepath, index=False, engine="openpyxl")

            self.logger.info(f"✅ 数据已保存到Excel: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"❌ Excel保存失败: {e}")
            if "openpyxl" in str(e):
                self.logger.info("💡 请安装openpyxl: pip install openpyxl")
            return None

    def create_summary_report(self, data: pd.DataFrame, saved_files: list):
        """创建汇总报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(
                self.config["backup_dir"], f"summary_report_{timestamp}.txt"
            )

            with open(report_file, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("沪深市场A股实时数据保存报告\n")
                f.write("=" * 60 + "\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"市场代码: {self.config['market_symbol']}\n")
                f.write(f"数据来源: efinance\n")
                f.write("\n")

                f.write("数据统计:\n")
                f.write(f"  总记录数: {len(data)}\n")
                f.write(f"  数据列数: {len(data.columns)}\n")

                if "最新价" in data.columns:
                    prices = data["最新价"].dropna()
                    if len(prices) > 0:
                        f.write(
                            f"  价格范围: {prices.min():.2f} - {prices.max():.2f}\n"
                        )

                f.write("\n保存的文件:\n")
                for file_path in saved_files:
                    if file_path:
                        f.write(f"  - {file_path}\n")

                f.write("\n数据列名:\n")
                for i, col in enumerate(data.columns, 1):
                    f.write(f"  {i:2d}. {col}\n")

            self.logger.info(f"✅ 汇总报告已生成: {report_file}")

        except Exception as e:
            self.logger.error(f"❌ 生成汇总报告失败: {e}")

    def run(self, market_symbol: str = None, force_update: bool = False) -> bool:
        """运行完整流程"""
        try:
            symbol = market_symbol or self.config["market_symbol"]

            self.logger.info("=" * 60)
            self.logger.info("🚀 离线版沪深市场A股实时数据保存系统")
            self.logger.info("=" * 60)
            self.logger.info(f"📊 目标市场: {symbol}")
            self.logger.info(f"🗂️ 备份目录: {self.config['backup_dir']}")
            self.logger.info(f"🔄 强制更新: {'是' if force_update else '否'}")
            self.logger.info("=" * 60)

            # 1. 检查依赖
            if not self.check_dependencies():
                return False

            # 2. 获取数据（支持重试）
            data = None
            for attempt in range(self.config["max_retry_attempts"]):
                self.logger.info(f"📡 第{attempt + 1}次获取数据...")
                data = self.get_realtime_market_data(symbol)
                if data is not None:
                    break
                self.logger.warning(f"⚠️ 第{attempt + 1}次获取失败")

            if data is None:
                self.logger.error("💥 多次重试后仍无法获取数据")
                return False

            # 3. 保存数据到多种格式
            saved_files = []

            # CSV文件（主要格式）
            csv_file = self.save_to_csv(data, symbol)
            saved_files.append(csv_file)

            # JSON文件（可选）
            json_file = self.save_to_json(data, symbol)
            saved_files.append(json_file)

            # Excel文件（可选）
            excel_file = self.save_to_excel(data, symbol)
            saved_files.append(excel_file)

            # 4. 生成汇总报告
            self.create_summary_report(data, saved_files)

            # 5. 显示结果
            success_count = len([f for f in saved_files if f is not None])

            self.logger.info("=" * 60)
            self.logger.info("🎉 数据保存完成！")
            self.logger.info(f"📊 数据记录数: {len(data)}")
            self.logger.info(f"💾 保存文件数: {success_count}")
            self.logger.info(
                f"📁 保存位置: {os.path.abspath(self.config['backup_dir'])}"
            )

            # 显示文件列表
            for file_path in saved_files:
                if file_path:
                    file_size = os.path.getsize(file_path)
                    self.logger.info(
                        f"   ✅ {os.path.basename(file_path)} ({file_size} 字节)"
                    )

            self.logger.info("=" * 60)

            return True

        except Exception as e:
            self.logger.error(f"💥 程序执行失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="沪深市场A股实时数据保存系统 - 离线版")
    parser.add_argument(
        "--market",
        choices=["hs", "sh", "sz"],
        default="hs",
        help="市场代码 (hs=沪深, sh=上海, sz=深圳)",
    )
    parser.add_argument("--force-update", action="store_true", help="强制更新")
    parser.add_argument("--backup-dir", default="./data_backup", help="备份目录路径")
    parser.add_argument("--export-json", action="store_true", help="导出JSON格式")
    parser.add_argument("--export-excel", action="store_true", help="导出Excel格式")

    args = parser.parse_args()

    print("沪深市场A股实时数据保存系统 - 离线版")
    print("=" * 60)
    print(f"市场代码: {args.market}")
    print(f"备份目录: {args.backup_dir}")
    print(f"导出JSON: {'是' if args.export_json else '否'}")
    print(f"导出Excel: {'是' if args.export_excel else '否'}")
    print("=" * 60)

    # 创建保存器
    saver = OfflineRealtimeDataSaver()
    saver.config["market_symbol"] = args.market
    saver.config["backup_dir"] = args.backup_dir
    saver.config["export_json"] = args.export_json
    saver.config["export_excel"] = args.export_excel

    # 运行
    success = saver.run(args.market, args.force_update)

    exit_code = 0 if success else 1
    print(f"程序执行{'成功' if success else '失败'}，退出码: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
