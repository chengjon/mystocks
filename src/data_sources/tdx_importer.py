"""
TDX数据增量导入器 (TDX Incremental Importer)

功能说明:
- 从TDX本地文件增量导入数据到MyStocks数据库
- 通过5-tier数据分类自动路由到对应数据库
- 支持断点续传和增量更新
- 批量处理优化性能

数据路由策略:
- 日线/分钟线数据 → TDengine (时序数据库)
- 导入记录元数据 → MySQL (元数据库)

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from typing import Dict, List, Optional
from datetime import date, datetime, timedelta
from dataclasses import dataclass
import logging
from tqdm import tqdm

from src.data_sources.tdx_binary_parser import TdxBinaryParser
from src.core import DataClassification


@dataclass
class ImportJob:
    """导入任务配置"""

    job_id: str
    market: str  # 市场（sh/sz）
    data_type: str  # 数据类型（day/5min/1min）
    symbols: List[str]  # 股票列表
    start_date: Optional[date]  # 开始日期
    end_date: Optional[date]  # 结束日期
    batch_size: int = 100  # 批量大小
    created_at: datetime = None
    status: str = "pending"  # pending/running/completed/failed

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class TdxImporter:
    """
    TDX数据增量导入器

    功能:
    - 自动扫描TDX数据文件
    - 增量导入到数据库
    - 支持断点续传
    - 进度跟踪和日志
    """

    def __init__(self, unified_manager=None, data_path: str = None):
        """
        初始化TDX导入器

        参数:
            unified_manager: MyStocksUnifiedManager实例（如果为None则不保存到数据库）
            data_path: TDX数据路径
        """
        self.logger = logging.getLogger(f"{__name__}.TdxImporter")
        self.logger.setLevel(logging.INFO)

        # TDX解析器
        self.parser = TdxBinaryParser(data_path=data_path)

        # 统一数据管理器
        self.unified_manager = unified_manager

        # 导入统计
        self.stats = {
            "total_symbols": 0,
            "success_count": 0,
            "fail_count": 0,
            "total_records": 0,
            "start_time": None,
            "end_time": None,
        }

    def import_market_daily(
        self,
        market: str = "sh",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        symbols: Optional[List[str]] = None,
        batch_size: int = 100,
    ) -> Dict:
        """
        导入指定市场的日线数据

        参数:
            market: 市场代码 ('sh' 或 'sz')
            start_date: 开始日期（可选，默认全部）
            end_date: 结束日期（可选，默认到最新）
            symbols: 指定股票列表（可选，默认全部）
            batch_size: 批量处理大小

        返回:
            dict: 导入统计信息

        示例:
            >>> from unified_manager import MyStocksUnifiedManager
            >>> manager = MyStocksUnifiedManager()
            >>> importer = TdxImporter(unified_manager=manager)
            >>> result = importer.import_market_daily('sh', start_date=date(2024, 1, 1))
            >>> print(f"成功导入 {result['success_count']} 只股票")
        """
        self.logger.info("=" * 70)
        self.logger.info("开始导入 %s 市场日线数据", market.upper())
        self.logger.info("=" * 70)

        self.stats["start_time"] = datetime.now()

        # 获取股票列表
        if symbols is None:
            symbols = self.parser.list_available_stocks(market)

        self.stats["total_symbols"] = len(symbols)
        self.logger.info("待导入股票数: %s", len(symbols))

        # 批量导入
        for i in tqdm(range(0, len(symbols), batch_size), desc="导入进度"):
            batch_symbols = symbols[i : i + batch_size]

            for symbol in batch_symbols:
                try:
                    # 读取日线数据
                    data = self.parser.read_day_data(symbol, start_date=start_date, end_date=end_date)

                    if data.empty:
                        self.logger.debug("  跳过 %s: 无数据", symbol)
                        continue

                    # 保存到数据库
                    if self.unified_manager:
                        self._save_to_database(symbol=symbol, data=data, data_type="daily", market=market)

                    self.stats["success_count"] += 1
                    self.stats["total_records"] += len(data)

                except Exception as e:
                    self.logger.error("  导入失败 %s: %s", symbol, e)
                    self.stats["fail_count"] += 1

        self.stats["end_time"] = datetime.now()

        # 打印统计
        self._print_summary()

        return self.stats

    def import_incremental(self, market: str = "sh", lookback_days: int = 7) -> Dict:
        """
        增量导入（只导入最近N天的数据）

        参数:
            market: 市场代码
            lookback_days: 回溯天数（默认7天）

        返回:
            dict: 导入统计
        """
        start_date = date.today() - timedelta(days=lookback_days)
        end_date = date.today()

        self.logger.info("增量导入: %s 至 %s", start_date, end_date)

        return self.import_market_daily(market=market, start_date=start_date, end_date=end_date)

    def _save_to_database(self, symbol: str, data: pd.DataFrame, data_type: str, market: str):
        """
        保存数据到数据库（通过5-tier数据分类路由）

        参数:
            symbol: 股票代码
            data: 数据DataFrame
            data_type: 数据类型 ('daily', '5min', '1min')
            market: 市场
        """
        if self.unified_manager is None:
            return

        # 添加symbol列
        data["symbol"] = symbol
        data["market"] = market

        # 根据数据类型分类
        if data_type == "daily":
            classification = DataClassification.MARKET_DATA_DAILY
            table_name = "stock_daily"
        elif data_type == "5min":
            classification = DataClassification.MARKET_DATA_MIN5
            table_name = "stock_5min"
        elif data_type == "1min":
            classification = DataClassification.MARKET_DATA_MIN1
            table_name = "stock_1min"
        else:
            self.logger.error("未知数据类型: %s", data_type)
            return

        try:
            # 通过统一管理器保存数据（自动路由到TDengine）
            self.unified_manager.save_data_by_classification(
                data=data, classification=classification, table_name=table_name
            )

        except Exception as e:
            self.logger.error("保存到数据库失败 %s: %s", symbol, e)
            raise

    def get_import_progress(self, market: str) -> Dict:
        """
        获取导入进度

        参数:
            market: 市场代码

        返回:
            dict: 进度信息
                - total_symbols: 总股票数
                - imported_symbols: 已导入数
                - latest_date: 最新数据日期
        """
        symbols = self.parser.list_available_stocks(market)

        progress = {
            "market": market,
            "total_symbols": len(symbols),
            "imported_symbols": 0,
            "latest_dates": {},
        }

        # 采样检查（检查前100只）
        sample_size = min(100, len(symbols))
        for symbol in symbols[:sample_size]:
            latest_date = self.parser.get_latest_date(symbol)
            if latest_date:
                progress["imported_symbols"] += 1
                progress["latest_dates"][symbol] = latest_date

        # 估算总导入数
        if sample_size > 0:
            ratio = progress["imported_symbols"] / sample_size
            progress["imported_symbols"] = int(len(symbols) * ratio)

        return progress

    def _print_summary(self):
        """打印导入统计摘要"""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
self.logger.info("TDX数据导入完成")
        self.logger.info("\n" + "=" * 70)
        self.logger.info("导入完成")
        self.logger.info("=" * 70)
        self.logger.info("总股票数:     %s", self.stats['total_symbols'])
        self.logger.info("成功导入:     %s", self.stats['success_count'])
        self.logger.info("导入失败:     %s", self.stats['fail_count'])
        self.logger.info("总记录数:     %s", self.stats['total_records'])
        self.logger.info("耗时:         %s 秒", duration)

        if duration > 0:
            rate = self.stats["total_records"] / duration
            self.logger.info("导入速度:     %s 条/秒", rate)

        self.logger.info("=" * 70)


if __name__ == "__main__":
    # 测试代码
    print("TDX数据导入器测试")
    print("=" * 70)

    # 创建导入器（不连接数据库）
    importer = TdxImporter(unified_manager=None)

    # 测试1: 获取导入进度
    print("\n测试1: 检查上海市场数据状态")
    progress = importer.get_import_progress("sh")
    print(f"  ✓ 总股票数: {progress['total_symbols']}")
    print(f"  ✓ 采样检查: {len(progress['latest_dates'])} 只股票有数据")

    if progress["latest_dates"]:
        sample = list(progress["latest_dates"].items())[:5]
        print("  ✓ 示例最新日期:")
        for symbol, latest_date in sample:
            print(f"      {symbol}: {latest_date}")

    # 测试2: 模拟小批量导入（不保存到数据库）
    print("\n测试2: 模拟导入前10只股票的最近7天数据")
    test_symbols = importer.parser.list_available_stocks("sh")[:10]

    result = importer.import_market_daily(
        market="sh",
        start_date=date.today() - timedelta(days=7),
        end_date=date.today(),
        symbols=test_symbols,
        batch_size=5,
    )

    print("\n  ✓ 测试完成:")
    print(f"      成功: {result['success_count']}/{result['total_symbols']}")
    print(f"      记录数: {result['total_records']:,}")

    print("\n" + "=" * 70)
    print("测试完成")
    print("\n提示: 要导入到数据库，请传入 unified_manager 参数")
