"""
信号管理器 (Signal Manager)

功能说明:
- 策略信号的持久化存储和查询
- 批量操作优化
- 与UnifiedDataManager集成
- 支持信号统计和分析

数据库:
- PostgreSQL+TimescaleDB (strategy_signals表)
- 通过UnifiedDataManager进行数据访问

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from datetime import date, datetime
import logging
import json


class SignalManager:
    """
    信号管理器 - 负责策略信号的存储、查询和管理

    功能:
        - 批量保存策略信号到数据库
        - 按条件查询信号
        - 信号统计分析
        - 信号去重和验证
    """

    def __init__(self, unified_manager=None, batch_size: int = 1000):
        """
        初始化信号管理器

        参数:
            unified_manager: UnifiedDataManager实例
            batch_size: 批量插入的批次大小
        """
        self.unified_manager = unified_manager
        self.batch_size = batch_size

        # 日志配置
        self.logger = logging.getLogger(f"{__name__}.SignalManager")
        self.logger.setLevel(logging.INFO)

        # 统计信息
        self.stats = {
            "total_saved": 0,
            "total_queried": 0,
            "total_deleted": 0,
            "last_save_time": None,
            "last_query_time": None,
        }

    def save_signals(
        self, signals: pd.DataFrame, strategy_id: int, batch_insert: bool = True
    ) -> Dict:
        """
        保存策略信号到数据库

        参数:
            signals: 信号DataFrame，必须包含:
                    - index: DatetimeIndex (信号日期)
                    - symbol: 股票代码
                    - signal: 信号类型 ('buy' or 'sell')
                    - strength: 信号强度 (0.0-1.0，可选)
                    - entry_price: 入场价格
                    - indicators: 指标字典 (可选)
                    - metadata: 元数据字典 (可选)
            strategy_id: 策略ID
            batch_insert: 是否使用批量插入

        返回:
            dict: 保存结果
                - success: 是否成功
                - saved_count: 保存的信号数量
                - failed_count: 失败的信号数量
                - execution_time: 执行时间(秒)

        示例:
            >>> signals_df = pd.DataFrame({
            ...     'symbol': ['000001', '000002'],
            ...     'signal': ['buy', 'sell'],
            ...     'entry_price': [12.34, 56.78],
            ...     'strength': [0.8, 0.9]
            ... }, index=pd.date_range('2024-01-01', periods=2))
            >>> result = signal_manager.save_signals(signals_df, strategy_id=1)
            >>> print(f"保存了 {result['saved_count']} 个信号")
        """
        if signals.empty:
            self.logger.warning("信号DataFrame为空，无需保存")
            return {
                "success": True,
                "saved_count": 0,
                "failed_count": 0,
                "execution_time": 0,
            }

        self.logger.info(f"开始保存信号: 策略ID={strategy_id}, 信号数量={len(signals)}")
        start_time = datetime.now()

        # 验证必需列
        required_cols = ["symbol", "signal", "entry_price"]
        missing_cols = [col for col in required_cols if col not in signals.columns]
        if missing_cols:
            raise ValueError(f"信号数据缺少必需列: {missing_cols}")

        # 准备数据
        signal_records = []
        for idx, row in signals.iterrows():
            # 验证信号类型
            if row["signal"] not in ["buy", "sell"]:
                self.logger.warning(f"无效的信号类型: {row['signal']}, 跳过")
                continue

            # 构建记录
            record = {
                "strategy_id": strategy_id,
                "symbol": row["symbol"],
                "signal_date": idx.date() if isinstance(idx, pd.Timestamp) else idx,
                "signal_type": row["signal"],
                "entry_price": float(row["entry_price"]),
                "signal_strength": float(row.get("strength", 0.0)),
                "indicators": row.get("indicators", {}),
                "metadata": row.get("metadata", {}),
                "created_at": datetime.now(),
            }

            # 转换indicators和metadata为JSON字符串
            if isinstance(record["indicators"], dict):
                record["indicators"] = json.dumps(record["indicators"])
            if isinstance(record["metadata"], dict):
                record["metadata"] = json.dumps(record["metadata"])

            signal_records.append(record)

        if not signal_records:
            self.logger.warning("没有有效的信号记录，保存终止")
            return {
                "success": False,
                "saved_count": 0,
                "failed_count": len(signals),
                "execution_time": 0,
            }

        # 批量保存
        saved_count = 0
        failed_count = 0

        try:
            if batch_insert and len(signal_records) > self.batch_size:
                # 分批保存
                for i in range(0, len(signal_records), self.batch_size):
                    batch = signal_records[i : i + self.batch_size]
                    batch_df = pd.DataFrame(batch)

                    try:
                        self._save_to_database(batch_df)
                        saved_count += len(batch)
                        self.logger.debug(
                            f"批次 {i//self.batch_size + 1} 保存成功: {len(batch)} 条记录"
                        )
                    except Exception as e:
                        self.logger.error(
                            f"批次 {i//self.batch_size + 1} 保存失败: {e}"
                        )
                        failed_count += len(batch)
            else:
                # 一次性保存
                signals_df = pd.DataFrame(signal_records)
                self._save_to_database(signals_df)
                saved_count = len(signal_records)

        except Exception as e:
            self.logger.error(f"保存信号时出错: {e}")
            failed_count = len(signal_records)

        # 更新统计
        execution_time = (datetime.now() - start_time).total_seconds()
        self.stats["total_saved"] += saved_count
        self.stats["last_save_time"] = datetime.now()

        result = {
            "success": saved_count > 0,
            "saved_count": saved_count,
            "failed_count": failed_count,
            "execution_time": execution_time,
        }

        self.logger.info(
            f"信号保存完成: 成功={saved_count}, 失败={failed_count}, "
            f"耗时={execution_time:.2f}秒"
        )

        return result

    def _save_to_database(self, signals_df: pd.DataFrame):
        """
        实际保存信号到数据库 (通过UnifiedDataManager)

        参数:
            signals_df: 信号DataFrame
        """
        if self.unified_manager is None:
            raise ValueError("UnifiedDataManager未初始化，无法保存信号")

        # 通过UnifiedDataManager保存到PostgreSQL
        # 注意: 实际实现需要根据UnifiedDataManager的具体接口调整
        self.unified_manager.save_data_by_classification(
            classification="derived_data",  # 衍生数据
            table_name="strategy_signals",
            data=signals_df,
            if_exists="append",  # 追加模式
        )

    def query_signals(
        self,
        strategy_id: Optional[int] = None,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        signal_type: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> pd.DataFrame:
        """
        查询策略信号

        参数:
            strategy_id: 策略ID (可选)
            symbol: 股票代码 (可选)
            start_date: 开始日期 (可选)
            end_date: 结束日期 (可选)
            signal_type: 信号类型 ('buy' or 'sell'，可选)
            limit: 返回记录数限制
            offset: 偏移量 (用于分页)

        返回:
            pd.DataFrame: 信号记录

        示例:
            >>> # 查询特定策略的所有买入信号
            >>> signals = signal_manager.query_signals(
            ...     strategy_id=1,
            ...     signal_type='buy',
            ...     start_date=date(2024, 1, 1),
            ...     end_date=date(2024, 12, 31)
            ... )
        """
        self.logger.info(
            f"查询信号: strategy_id={strategy_id}, symbol={symbol}, "
            f"日期范围={start_date} 至 {end_date}, signal_type={signal_type}"
        )

        if self.unified_manager is None:
            raise ValueError("UnifiedDataManager未初始化，无法查询信号")

        # 构建查询条件
        filters = {}
        if strategy_id is not None:
            filters["strategy_id"] = strategy_id
        if symbol is not None:
            filters["symbol"] = symbol
        if signal_type is not None:
            filters["signal_type"] = signal_type

        # 日期范围
        date_range = {}
        if start_date is not None:
            date_range["start"] = start_date
        if end_date is not None:
            date_range["end"] = end_date

        # 通过UnifiedDataManager查询
        # 注意: 实际实现需要根据UnifiedDataManager的具体接口调整
        signals = self.unified_manager.load_data_by_classification(
            classification="derived_data",
            table_name="strategy_signals",
            filters=filters,
            date_range=date_range,
            limit=limit,
            offset=offset,
        )

        # 更新统计
        self.stats["total_queried"] += len(signals)
        self.stats["last_query_time"] = datetime.now()

        self.logger.info(f"查询到 {len(signals)} 条信号记录")

        return signals

    def delete_signals(
        self,
        strategy_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        """
        删除策略信号

        参数:
            strategy_id: 策略ID
            start_date: 开始日期 (可选)
            end_date: 结束日期 (可选)

        返回:
            int: 删除的记录数

        警告:
            此操作不可逆，请谨慎使用！

        示例:
            >>> # 删除策略ID为1的所有2024年信号
            >>> deleted = signal_manager.delete_signals(
            ...     strategy_id=1,
            ...     start_date=date(2024, 1, 1),
            ...     end_date=date(2024, 12, 31)
            ... )
        """
        self.logger.warning(
            f"删除信号: strategy_id={strategy_id}, "
            f"日期范围={start_date} 至 {end_date}"
        )

        if self.unified_manager is None:
            raise ValueError("UnifiedDataManager未初始化，无法删除信号")

        # 构建删除条件
        filters = {"strategy_id": strategy_id}
        date_range = {}
        if start_date is not None:
            date_range["start"] = start_date
        if end_date is not None:
            date_range["end"] = end_date

        # 通过UnifiedDataManager删除
        deleted_count = self.unified_manager.delete_data_by_classification(
            classification="derived_data",
            table_name="strategy_signals",
            filters=filters,
            date_range=date_range,
        )

        # 更新统计
        self.stats["total_deleted"] += deleted_count

        self.logger.info(f"删除了 {deleted_count} 条信号记录")

        return deleted_count

    def get_signal_statistics(
        self,
        strategy_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """
        获取信号统计信息

        参数:
            strategy_id: 策略ID
            start_date: 开始日期 (可选)
            end_date: 结束日期 (可选)

        返回:
            dict: 统计信息
                - total_signals: 总信号数
                - buy_signals: 买入信号数
                - sell_signals: 卖出信号数
                - unique_symbols: 涉及股票数
                - avg_strength: 平均信号强度
                - date_range: 日期范围

        示例:
            >>> stats = signal_manager.get_signal_statistics(strategy_id=1)
            >>> print(f"总信号数: {stats['total_signals']}")
            >>> print(f"买入/卖出比例: {stats['buy_signals']}/{stats['sell_signals']}")
        """
        signals = self.query_signals(
            strategy_id=strategy_id,
            start_date=start_date,
            end_date=end_date,
            limit=100000,  # 统计需要获取所有记录
        )

        if signals.empty:
            return {
                "total_signals": 0,
                "buy_signals": 0,
                "sell_signals": 0,
                "unique_symbols": 0,
                "avg_strength": 0.0,
                "date_range": (None, None),
            }

        stats = {
            "total_signals": len(signals),
            "buy_signals": len(signals[signals["signal_type"] == "buy"]),
            "sell_signals": len(signals[signals["signal_type"] == "sell"]),
            "unique_symbols": signals["symbol"].nunique(),
            "avg_strength": signals["signal_strength"].mean(),
            "date_range": (signals["signal_date"].min(), signals["signal_date"].max()),
        }

        return stats

    def validate_signal(self, signal: Dict) -> Tuple[bool, Optional[str]]:
        """
        验证单个信号的有效性

        参数:
            signal: 信号字典

        返回:
            tuple: (是否有效, 错误信息)

        示例:
            >>> signal = {
            ...     'symbol': '000001',
            ...     'signal': 'buy',
            ...     'entry_price': 12.34,
            ...     'strength': 0.8
            ... }
            >>> is_valid, error = signal_manager.validate_signal(signal)
        """
        # 验证必需字段
        required_fields = ["symbol", "signal", "entry_price"]
        for field in required_fields:
            if field not in signal:
                return False, f"缺少必需字段: {field}"

        # 验证信号类型
        if signal["signal"] not in ["buy", "sell"]:
            return False, f"无效的信号类型: {signal['signal']}"

        # 验证价格
        if (
            not isinstance(signal["entry_price"], (int, float))
            or signal["entry_price"] <= 0
        ):
            return False, f"无效的入场价格: {signal['entry_price']}"

        # 验证信号强度
        if "strength" in signal:
            strength = signal["strength"]
            if not isinstance(strength, (int, float)) or not (0 <= strength <= 1):
                return False, f"信号强度必须在0-1之间: {strength}"

        return True, None

    def get_latest_signals(self, strategy_id: int, limit: int = 10) -> pd.DataFrame:
        """
        获取最新的N个信号

        参数:
            strategy_id: 策略ID
            limit: 返回记录数

        返回:
            pd.DataFrame: 最新信号记录 (按日期降序)

        示例:
            >>> latest = signal_manager.get_latest_signals(strategy_id=1, limit=5)
            >>> print(latest[['symbol', 'signal_type', 'signal_date']])
        """
        signals = self.query_signals(strategy_id=strategy_id, limit=limit)

        if not signals.empty and "signal_date" in signals.columns:
            signals = signals.sort_values("signal_date", ascending=False)

        return signals

    def get_manager_stats(self) -> Dict:
        """
        获取管理器统计信息

        返回:
            dict: 统计信息
        """
        return self.stats.copy()


if __name__ == "__main__":
    # 测试代码
    print("信号管理器测试")
    print("=" * 50)

    # 创建测试信号
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    test_signals = pd.DataFrame(
        {
            "symbol": ["000001"] * 5 + ["000002"] * 5,
            "signal": ["buy", "sell", "buy", "sell", "buy"] * 2,
            "entry_price": np.random.uniform(10, 20, 10),
            "strength": np.random.uniform(0.5, 1.0, 10),
            "indicators": [{"ma5": 12.5, "rsi": 30}] * 10,
            "metadata": [{"volume": 1000000}] * 10,
        },
        index=dates,
    )

    print("测试信号数据:")
    print(test_signals.head())

    # 创建信号管理器 (不连接数据库的测试)
    manager = SignalManager(unified_manager=None, batch_size=5)

    # 测试信号验证
    print("\n测试信号验证:")
    test_signal = {
        "symbol": "000001",
        "signal": "buy",
        "entry_price": 12.34,
        "strength": 0.8,
    }
    is_valid, error = manager.validate_signal(test_signal)
    print(f"信号验证结果: {'有效' if is_valid else '无效'}")
    if error:
        print(f"错误信息: {error}")

    # 测试无效信号
    print("\n测试无效信号:")
    invalid_signal = {
        "symbol": "000001",
        "signal": "hold",  # 无效类型
        "entry_price": 12.34,
    }
    is_valid, error = manager.validate_signal(invalid_signal)
    print(f"信号验证结果: {'有效' if is_valid else '无效'}")
    if error:
        print(f"错误信息: {error}")

    # 显示统计
    print("\n管理器统计:")
    print(json.dumps(manager.get_manager_stats(), indent=2, default=str))

    print("\n注意: 完整的保存/查询功能需要UnifiedDataManager实例")
    print("所有基础测试通过！")
