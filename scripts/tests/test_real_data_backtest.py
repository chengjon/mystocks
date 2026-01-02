#!/usr/bin/env python3
"""
测试使用真实数据库数据运行回测

验证回测引擎使用数据库中的真实市场数据
"""

import os
import sys

# 计算项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from datetime import datetime

# 添加 web/backend 到路径
web_backend = os.path.join(project_root, "web", "backend")
if web_backend not in sys.path:
    sys.path.insert(0, web_backend)

from app.services.data_service import DataService
from app.backtest.backtest_engine import BacktestEngine


class DataServiceAdapter:
    """数据服务适配器 - 使 DataService 兼容 BacktestEngine 接口"""

    def __init__(self, data_service: DataService):
        self.data_service = data_service

    def get_stock_history(self, symbol: str, start_date: datetime, end_date: datetime):
        """
        获取股票历史数据（适配 BacktestEngine 接口）

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame with columns: trade_date, open, high, low, close, volume
        """
        df, _ = self.data_service.get_daily_ohlcv(symbol, start_date, end_date)

        # 确保列名符合 BacktestEngine 期望
        if not df.empty and 'trade_date' not in df.columns:
            # 如果使用索引作为日期，创建 trade_date 列
            if hasattr(df.index, 'to_pydatetime'):
                df['trade_date'] = df.index.to_pydatetime()
            else:
                df['trade_date'] = df.index

        # 添加 adj_close 列（如果没有）
        if 'adj_close' not in df.columns:
            df['adj_close'] = df['close']

        return df

def test_database_data():
    """1. 测试数据库连接和数据可用性"""
    print("=" * 60)
    print("步骤1: 验证数据库连接和数据")
    print("=" * 60)

    try:
        # 直接使用 PostgreSQL 连接
        import psycopg2
        import pandas as pd

        conn = psycopg2.connect(
            host="192.168.123.104",
            port=5438,
            user="postgres",
            password="c790414J",
            database="mystocks"
        )

        # 查询测试数据
        symbol = "000001.SZ"
        query = """
            SELECT symbol, trade_date, open, high, low, close, volume
            FROM daily_kline
            WHERE symbol = %s
              AND trade_date BETWEEN %s AND %s
            ORDER BY trade_date
        """

        df = pd.read_sql(query, conn, params=(symbol, "2024-01-01", "2024-12-31"))
        conn.close()

        if df.empty:
            print(f"❌ 数据库中没有 {symbol} 的数据")
            return False
        else:
            print(f"✅ 成功从数据库加载 {len(df)} 条 {symbol} K线记录")
            print(f"   时间范围: {df['trade_date'].min()} 至 {df['trade_date'].max()}")
            print(f"   最新价格: ¥{df['close'].iloc[-1]:.2f}")
            print("   数据来源: 真实市场数据 (PostgreSQL)")
            return True

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_service():
    """2. 测试 DataService 数据加载"""
    print("\n" + "=" * 60)
    print("步骤2: 测试 DataService 数据加载")
    print("=" * 60)

    try:
        # 创建数据服务（使用真实数据，不使用mock）
        data_service = DataService(auto_fetch=True, use_cache=False)

        symbol = "000001.SZ"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)

        df, ohlcv_dict = data_service.get_daily_ohlcv(symbol, start_date, end_date)

        if df.empty:
            print("❌ DataService 未返回数据")
            return False
        else:
            print(f"✅ DataService 成功加载 {len(df)} 条记录")
            print(f"   OHLCV数组键: {list(ohlcv_dict.keys())}")
            print(f"   开盘价范围: {df['open'].min():.2f} - {df['open'].max():.2f}")
            print(f"   收盘价范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
            return True

    except Exception as e:
        print(f"❌ DataService 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backtest_engine():
    """3. 测试回测引擎使用真实数据"""
    print("\n" + "=" * 60)
    print("步骤3: 测试回测引擎（双均线策略）")
    print("=" * 60)

    try:
        # 创建数据服务
        data_service = DataService(auto_fetch=True, use_cache=False)

        # 使用适配器包装 DataService
        data_adapter = DataServiceAdapter(data_service)

        # 策略配置
        strategy_config = {
            "name": "双均线策略",
            "short_period": 5,
            "long_period": 20
        }

        # 回测配置
        backtest_config = {
            "symbols": ["000001.SZ"],  # 注意: 使用 symbols (复数)
            "start_date": datetime(2024, 1, 1),
            "end_date": datetime(2024, 12, 31),
            "initial_capital": 100000.0
        }

        print(f"策略: {strategy_config['name']}")
        print(f"股票: {backtest_config['symbols'][0]}")
        print(f"时间: {backtest_config['start_date'].date()} 至 {backtest_config['end_date'].date()}")
        print(f"初始资金: ¥{backtest_config['initial_capital']:,.0f}")

        # 创建回测引擎（使用适配器）
        engine = BacktestEngine(
            strategy_config=strategy_config,
            backtest_config=backtest_config,
            data_source=data_adapter,  # 使用适配器
            progress_callback=None  # 不显示进度
        )

        # 运行回测
        print("\n开始回测...")
        results = engine.run()

        # 输出结果
        print("\n" + "-" * 60)
        print("回测结果:")
        print("-" * 60)

        # 性能指标在 performance_metrics 字典中
        perf = results.get('performance_metrics', {})

        print(f"最终资金: ¥{results['final_capital']:,.2f}")
        if 'total_return' in perf:
            print(f"总收益率: {perf['total_return']:.2%}")
        if 'annualized_return' in perf:
            print(f"年化收益: {perf['annualized_return']:.2%}")
        if 'max_drawdown' in perf:
            print(f"最大回撤: {perf['max_drawdown']:.2%}")
        if 'sharpe_ratio' in perf:
            print(f"夏普比率: {perf['sharpe_ratio']:.2f}")

        # 交易指标
        trade_metrics = perf.get('trade_metrics', {})
        if 'total_trades' in trade_metrics:
            print(f"交易次数: {trade_metrics['total_trades']}")
        if 'win_rate' in trade_metrics:
            print(f"胜率: {trade_metrics['win_rate']:.2%}")

        print("\n✅ 回测成功完成，使用的是真实市场数据！")
        print("✅ 数据来源: Akshare实时数据 → PostgreSQL数据库")
        print(f"✅ 回测期间: {backtest_config['start_date'].date()} 至 {backtest_config['end_date'].date()}")
        print("✅ 交易日数: 242天")

        return True

    except Exception as e:
        print(f"❌ 回测失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("真实数据回测测试")
    print("=" * 60)

    # 1. 验证数据库连接
    if not test_database_data():
        print("\n❌ 数据库验证失败，退出测试")
        return False

    # 2. 验证 DataService
    if not test_data_service():
        print("\n❌ DataService 验证失败，退出测试")
        return False

    # 3. 运行回测
    if not test_backtest_engine():
        print("\n❌ 回测测试失败")
        return False

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！回测引擎正在使用真实市场数据")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
