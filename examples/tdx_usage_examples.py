"""
TDX数据源适配器使用示例

展示TDX适配器的常见使用场景和最佳实践

作者: MyStocks Team
日期: 2025-10-15
"""

import logging
from datetime import datetime, timedelta
from src.adapters.tdx_adapter import TdxDataSource
from src.adapters.data_source_manager import get_default_manager

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def example_1_basic_quote():
    """示例1: 获取实时行情"""
    print("\n" + "=" * 70)
    print("示例1: 获取实时行情")
    print("=" * 70)

    tdx = TdxDataSource()

    # 获取单只股票行情
    quote = tdx.get_real_time_data("600519")

    if isinstance(quote, dict):
        print(f"\n股票: {quote['name']} ({quote['code']})")
        print(f"最新价: ¥{quote['price']:.2f}")
        print(
            f"涨跌: {quote['price'] - quote['pre_close']:+.2f} "
            f"({(quote['price']/quote['pre_close']-1)*100:+.2f}%)"
        )
        print(f"今开: ¥{quote['open']:.2f}")
        print(f"最高: ¥{quote['high']:.2f}")
        print(f"最低: ¥{quote['low']:.2f}")
        print(f"成交量: {quote['volume']:,}手")
        print(f"成交额: ¥{quote['amount']/1e8:.2f}亿")
        print(f"时间: {quote['timestamp']}")
    else:
        print(f"获取失败: {quote}")


def example_2_multiple_quotes():
    """示例2: 批量获取多只股票行情"""
    print("\n" + "=" * 70)
    print("示例2: 批量获取行情")
    print("=" * 70)

    tdx = TdxDataSource()

    symbols = [
        ("600519", "贵州茅台"),
        ("600036", "招商银行"),
        ("000001", "平安银行"),
        ("300750", "宁德时代"),
    ]

    print(
        f"\n{'股票代码':10s} {'股票名称':10s} {'最新价':>10s} {'涨跌幅':>10s} {'成交额':>12s}"
    )
    print("-" * 70)

    for symbol, name in symbols:
        quote = tdx.get_real_time_data(symbol)

        if isinstance(quote, dict):
            change_pct = (quote["price"] / quote["pre_close"] - 1) * 100
            amount_yi = quote["amount"] / 1e8

            print(
                f"{symbol:10s} {quote['name']:10s} "
                f"{quote['price']:10.2f} "
                f"{change_pct:+9.2f}% "
                f"{amount_yi:11.2f}亿"
            )


def example_3_daily_kline():
    """示例3: 获取日线数据并分析"""
    print("\n" + "=" * 70)
    print("示例3: 日线数据分析")
    print("=" * 70)

    tdx = TdxDataSource()

    # 获取最近30天日线
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    df = tdx.get_stock_daily("600519", start_date, end_date)

    if not df.empty:
        print(f"\n获取贵州茅台日线数据: {len(df)}条")
        print(f"日期范围: {df['date'].min()} ~ {df['date'].max()}")

        # 计算简单统计指标
        print(f"\n价格统计:")
        print(f"  最高价: ¥{df['high'].max():.2f}")
        print(f"  最低价: ¥{df['low'].min():.2f}")
        print(f"  平均价: ¥{df['close'].mean():.2f}")
        print(f"  涨跌幅: {(df['close'].iloc[-1]/df['close'].iloc[0]-1)*100:+.2f}%")

        print(f"\n成交量统计:")
        print(f"  最大成交量: {df['volume'].max():,.0f}手")
        print(f"  平均成交量: {df['volume'].mean():,.0f}手")
        print(f"  总成交额: ¥{df['amount'].sum()/1e8:.2f}亿")


def example_4_intraday_kline():
    """示例4: 盘中分钟线监控"""
    print("\n" + "=" * 70)
    print("示例4: 盘中分钟线监控")
    print("=" * 70)

    tdx = TdxDataSource()

    # 获取今天的5分钟K线
    today = datetime.now().strftime("%Y-%m-%d")

    df = tdx.get_stock_kline("600519", today, today, period="5m")

    if not df.empty:
        print(f"\n获取5分钟K线: {len(df)}条")

        # 显示最近10根K线
        print(f"\n最近10根K线:")
        print(
            df[["date", "open", "high", "low", "close", "volume"]]
            .tail(10)
            .to_string(index=False)
        )

        # 计算当日涨跌
        if len(df) > 0:
            first_price = df["open"].iloc[0]
            last_price = df["close"].iloc[-1]
            change = (last_price / first_price - 1) * 100
            print(
                f"\n当日涨跌: {change:+.2f}% (开盘{first_price:.2f} → 现价{last_price:.2f})"
            )


def example_5_multiperiod_comparison():
    """示例5: 多周期K线对比"""
    print("\n" + "=" * 70)
    print("示例5: 多周期K线对比")
    print("=" * 70)

    tdx = TdxDataSource()

    # 获取最近2天的不同周期K线
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    periods = [
        ("5m", "5分钟"),
        ("15m", "15分钟"),
        ("30m", "30分钟"),
        ("1h", "1小时"),
        ("1d", "日线"),
    ]

    print(f"\n{'周期':10s} {'数据条数':>10s} {'时间跨度':>12s} {'涨跌幅':>10s}")
    print("-" * 70)

    for period, name in periods:
        df = tdx.get_stock_kline("600519", start_date, end_date, period=period)

        if not df.empty:
            time_span = f"{len(df)}条"
            change = (df["close"].iloc[-1] / df["open"].iloc[0] - 1) * 100

            print(
                f"{name:10s} {time_span:>10s} "
                f"{df['date'].min()[:10]:>12s} "
                f"{change:+9.2f}%"
            )


def example_6_index_data():
    """示例6: 指数数据获取"""
    print("\n" + "=" * 70)
    print("示例6: 指数数据获取")
    print("=" * 70)

    tdx = TdxDataSource()

    # 主要指数列表
    indices = [
        ("000001", "上证指数"),
        ("399001", "深证成指"),
        ("399006", "创业板指"),
    ]

    # 获取指数日线数据
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    print(f"\n{'指数代码':10s} {'指数名称':10s} {'最新点位':>10s} {'涨跌幅':>10s}")
    print("-" * 70)

    for symbol, name in indices:
        df = tdx.get_index_daily(symbol, start_date, end_date)

        if not df.empty:
            latest = df["close"].iloc[-1]
            first = df["open"].iloc[0]
            change = (latest / first - 1) * 100

            print(f"{symbol:10s} {name:10s} {latest:10.2f} {change:+9.2f}%")


def example_7_data_source_manager():
    """示例7: 使用数据源管理器"""
    print("\n" + "=" * 70)
    print("示例7: 数据源管理器(推荐)")
    print("=" * 70)

    # 获取默认管理器(自动注册TDX和AKShare)
    manager = get_default_manager()

    print(f"\n已注册的数据源: {manager.list_sources()}")

    # 方式1: 明确指定数据源
    print("\n方式1: 明确指定使用TDX")
    quote = manager.get_real_time_data("600519", source="tdx")
    if isinstance(quote, dict):
        print(f"  {quote['name']}: ¥{quote['price']:.2f}")

    # 方式2: 自动选择(按优先级)
    print("\n方式2: 自动选择数据源")
    quote = manager.get_real_time_data("600519")  # 优先TDX
    if isinstance(quote, dict):
        print(f"  {quote['name']}: ¥{quote['price']:.2f}")

    # 方式3: 历史数据自动故障转移
    print("\n方式3: 历史数据(自动故障转移)")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    df = manager.get_stock_daily("600519", start_date, end_date)
    if not df.empty:
        print(f"  获取{len(df)}条日线数据")


def example_8_error_handling():
    """示例8: 错误处理最佳实践"""
    print("\n" + "=" * 70)
    print("示例8: 错误处理")
    print("=" * 70)

    tdx = TdxDataSource()

    # 1. 处理无效股票代码
    print("\n1. 无效股票代码:")
    quote = tdx.get_real_time_data("AAPL")  # 美股代码,无效
    if isinstance(quote, str):
        print(f"  错误: {quote}")

    # 2. 处理不存在的股票
    print("\n2. 不存在的股票代码:")
    quote = tdx.get_real_time_data("999999")
    if isinstance(quote, str):
        print(f"  错误: {quote}")

    # 3. 处理空数据
    print("\n3. 空数据处理:")
    df = tdx.get_stock_daily("999999", "2024-01-01", "2024-12-31")
    if df.empty:
        print(f"  返回空DataFrame,数据量: {len(df)}")

    # 4. 推荐的错误处理模式
    print("\n4. 推荐的错误处理模式:")
    try:
        quote = tdx.get_real_time_data("600519")

        if isinstance(quote, dict):
            # 正常处理数据
            print(f"  ✓ 成功: {quote['name']} ¥{quote['price']:.2f}")
        else:
            # 处理错误消息
            print(f"  ✗ 失败: {quote}")

    except Exception as e:
        # 处理异常
        print(f"  ✗ 异常: {e}")


def main():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print("TDX数据源适配器 - 使用示例集合")
    print("=" * 70)

    examples = [
        ("基础实时行情", example_1_basic_quote),
        ("批量行情查询", example_2_multiple_quotes),
        ("日线数据分析", example_3_daily_kline),
        ("盘中分钟线", example_4_intraday_kline),
        ("多周期对比", example_5_multiperiod_comparison),
        ("指数数据", example_6_index_data),
        ("数据源管理器", example_7_data_source_manager),
        ("错误处理", example_8_error_handling),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name}示例执行失败: {e}")

    print("\n" + "=" * 70)
    print("所有示例执行完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
