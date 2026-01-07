/**
 * Stock-Analysis 代码示例
 */

// 日线解析代码
export const DAY_PARSER_CODE = `import struct
import pandas as pd
from datetime import datetime

def parse_tdx_day_file(file_path):
    """
    解析通达信日线数据文件 (.day)

    Returns:
        pd.DataFrame: 包含 OHLCV 数据的 DataFrame
    """
    data = []

    with open(file_path, 'rb') as f:
        while True:
            # 读取32字节
            record = f.read(32)
            if len(record) != 32:
                break

            # 解析数据 (小端序)
            fields = struct.unpack('<IIIIIfII', record)

            date = fields[0]  # YYYYMMDD 格式
            open_price = fields[1] / 100.0
            high_price = fields[2] / 100.0
            low_price = fields[3] / 100.0
            close_price = fields[4] / 100.0
            amount = fields[5]  # 成交额
            volume = fields[6]  # 成交量

            # 转换日期格式
            date_str = str(date)
            date_obj = datetime.strptime(date_str, '%Y%m%d')

            data.append({
                'date': date_obj,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'amount': amount
            })

    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df

# 使用示例
df = parse_tdx_day_file('D:/tdx/vipdoc/sh/lday/sh600000.day')
print(df.head())
print(f"总共 {len(df)} 条记录")`

// 分钟线解析代码
export const MINUTE_PARSER_CODE = `

import struct
import pandas as pd
from datetime import datetime, timedelta

def parse_tdx_minute_file(file_path):
    """
    解析通达信分钟线数据文件 (.lc1)

    Returns:
        pd.DataFrame: 包含 OHLCV 数据的 DataFrame
    """
    data = []

    with open(file_path, 'rb') as f:
        while True:
            record = f.read(32)
            if len(record) != 32:
                break

            fields = struct.unpack('<HHIIIIfII', record)

            date = fields[0]  # 天数(从1900/1/1开始)
            minute = fields[1]  # 分钟(0-1439)
            open_price = fields[2] / 100.0
            high_price = fields[3] / 100.0
            low_price = fields[4] / 100.0
            close_price = fields[5] / 100.0
            amount = fields[6]
            volume = fields[7]

            # 计算实际日期时间
            base_date = datetime(1900, 1, 1)
            actual_date = base_date + timedelta(days=date)
            hour = minute // 60
            min = minute % 60
            dt = actual_date.replace(hour=hour, minute=min)

            data.append({
                'datetime': dt,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'amount': amount
            })

    df = pd.DataFrame(data)
    df.set_index('datetime', inplace=True)
    return df`

// 批量读取代码
export const BATCH_LOAD_CODE = `

import os
from pathlib import Path

def load_all_stocks_data(tdx_path, market='sh'):
    """
    批量加载指定市场的所有股票数据

    Args:
        tdx_path: 通达信数据目录
        market: 市场代码 ('sh' 或 'sz')

    Returns:
        dict: {股票代码: DataFrame}
    """
    data_dir = Path(tdx_path) / 'vipdoc' / market / 'lday'
    stocks_data = {}

    for file_path in data_dir.glob(f'{market}*.day'):
        # 提取股票代码
        code = file_path.stem[2:]  # 去掉 'sh' 或 'sz' 前缀

        try:
            df = parse_tdx_day_file(str(file_path))
            stocks_data[code] = df
            print(f"已加载 {market}{code}: {len(df)} 条记录")
        except Exception as e:
            print(f"加载 {file_path} 失败: {e}")

    return stocks_data

# 使用示例
tdx_path = 'D:/tdx'
sh_stocks = load_all_stocks_data(tdx_path, 'sh')
sz_stocks = load_all_stocks_data(tdx_path, 'sz')

print(f"上海市场: {len(sh_stocks)} 只股票")
print(f"深圳市场: {len(sz_stocks)} 只股票")`

// 策略示例代码
export const STRATEGY_EXAMPLES = {
  ma_bullish: `import talib as ta

def filter_ma_bullish(df):
    """均线多头排列筛选"""
    # 计算均线
    df['ma5'] = ta.SMA(df['close'], 5)
    df['ma10'] = ta.SMA(df['close'], 10)
    df['ma20'] = ta.SMA(df['close'], 20)
    df['ma60'] = ta.SMA(df['close'], 60)

    # 筛选条件
    condition = (
        (df['ma5'] > df['ma10']) &
        (df['ma10'] > df['ma20']) &
        (df['ma20'] > df['ma60'])
    )

    return df[condition]`,

  macd_golden: `def filter_macd_golden_cross(df):
    """MACD 金叉筛选"""
    # 计算 MACD
    macd, signal, hist = ta.MACD(df['close'],
                                   fastperiod=12,
                                   slowperiod=26,
                                   signalperiod=9)

    df['macd'] = macd
    df['signal'] = signal
    df['hist'] = hist

    # 筛选条件: 今日金叉 且 昨日死叉
    condition = (
        (df['macd'] > df['signal']) &  # 今日快线在上
        (df['macd'].shift(1) <= df['signal'].shift(1)) &  # 昨日快线在下
        (df['hist'] > 0)  # 柱状图为正
    )

    return df[condition]`,

  breakout_volume: `def filter_breakout_with_volume(df, lookback=20, vol_ratio=1.5):
    """放量突破筛选"""
    # 计算N日最高价
    df['high_n'] = df['high'].rolling(lookback).max().shift(1)

    # 计算N日平均成交量
    df['vol_ma'] = df['volume'].rolling(lookback).mean()

    # 筛选条件
    condition = (
        (df['close'] > df['high_n']) &  # 突破前期高点
        (df['volume'] > df['vol_ma'] * vol_ratio)  # 成交量放大
    )

    return df[condition]`,

  rsi_oversold: `def filter_rsi_oversold(df, period=14, oversold=30):
    """RSI 超卖反弹筛选"""
    # 计算 RSI
    df['rsi'] = ta.RSI(df['close'], timeperiod=period)

    # 筛选条件: 昨日超卖,今日回升
    condition = (
        (df['rsi'].shift(1) < oversold) &  # 昨日超卖
        (df['rsi'] > oversold) &  # 今日脱离超卖
        (df['rsi'] > df['rsi'].shift(1))  # RSI 上升
    )

    return df[condition]`,

  bottom_volume: `def filter_bottom_volume(df, lookback=60):
    """底部放量筛选"""
    # 计算60日最低价和当前价格相对位置
    df['low_60'] = df['low'].rolling(lookback).min()
    df['price_position'] = (df['close'] - df['low_60']) / (df['high'].rolling(lookback).max() - df['low_60'])

    # 计算成交量比率
    df['vol_ma5'] = df['volume'].rolling(5).mean()
    df['vol_ma20'] = df['volume'].rolling(20).mean()
    df['vol_ratio'] = df['vol_ma5'] / df['vol_ma20']

    # 筛选条件
    condition = (
        (df['price_position'] < 0.3) &  # 价格在底部30%区域
        (df['vol_ratio'] > 1.5)  # 5日均量 > 20日均量的1.5倍
    )

    return df[condition]`
}

// 组合筛选代码
export const COMPREHENSIVE_FILTER_CODE = `
def comprehensive_filter(stock_code):
    """
    综合筛选策略:
    1. 均线多头排列
    2. MACD 金叉
    3. RSI 不超买 (< 70)
    4. 成交量放大
    """
    df = load_stock_data(stock_code)

    # 计算所有指标
    df['ma5'] = ta.SMA(df['close'], 5)
    df['ma10'] = ta.SMA(df['close'], 10)
    df['ma20'] = ta.SMA(df['close'], 20)

    macd, signal, _ = ta.MACD(df['close'])
    df['macd'] = macd
    df['signal'] = signal

    df['rsi'] = ta.RSI(df['close'], 14)
    df['vol_ma'] = df['volume'].rolling(20).mean()

    # 组合筛选条件
    condition = (
        (df['ma5'] > df['ma10']) &
        (df['ma10'] > df['ma20']) &
        (df['macd'] > df['signal']) &
        (df['rsi'] < 70) &
        (df['volume'] > df['vol_ma'] * 1.2)
    )

    # 获取最新一天的筛选结果
    latest = df[condition].iloc[-1] if condition.any() else None

    return latest

# 批量筛选
results = []
for code in all_stock_codes:
    result = comprehensive_filter(code)
    if result is not None:
        results.append({
            'code': code,
            'close': result['close'],
            'rsi': result['rsi'],
            'volume_ratio': result['volume'] / result['vol_ma']
        })

# 输出结果
print(f"共筛选出 {len(results)} 只股票")
for r in results[:10]:  # 显示前10只
    print(f"{r['code']}: 收盘价={r['close']:.2f}, RSI={r['rsi']:.2f}")`

// 回测代码示例
export const BACKTEST_EXAMPLES = {
  simple: `from rqalpha.api import *

def init(context):
    """策略初始化"""
    context.stock = "000001.XSHE"
    context.ma_short = 5
    context.ma_long = 20

def before_trading(context):
    """盘前处理"""
    pass

def handle_bar(context, bar_dict):
    """每个bar的处理逻辑"""
    # 获取历史数据
    prices = history_bars(context.stock, context.ma_long + 1, '1d', 'close')

    # 计算均线
    ma_short = prices[-context.ma_short:].mean()
    ma_long = prices[-context.ma_long:].mean()

    # 当前持仓
    position = context.portfolio.positions[context.stock]

    # 交易逻辑
    if ma_short > ma_long and position.quantity == 0:
        # 金叉买入
        order_target_percent(context.stock, 0.95)
        logger.info(f"买入信号: MA{context.ma_short} > MA{context.ma_long}")
    elif ma_short < ma_long and position.quantity > 0:
        # 死叉卖出
        order_target_percent(context.stock, 0)
        logger.info(f"卖出信号: MA{context.ma_short} < MA{context.ma_long}")`,

  multi_stock: `from rqalpha.api import *

def init(context):
    """初始化股票池"""
    context.stocks = [
        "000001.XSHE",  # 平安银行
        "600000.XSHG",  # 浦发银行
        "600036.XSHG",  # 招商银行
        "601398.XSHG"   # 工商银行
    ]
    context.holding_days = {}

def handle_bar(context, bar_dict):
    """多股票轮动策略"""
    # 计算每只股票的动量
    momentums = {}
    for stock in context.stocks:
        try:
            prices = history_bars(stock, 20, '1d', 'close')
            momentum = (prices[-1] - prices[0]) / prices[0]
            momentums[stock] = momentum
        except:
            continue

    # 按动量排序
    sorted_stocks = sorted(momentums.items(), key=lambda x: x[1], reverse=True)

    # 持有前2名
    target_stocks = [s[0] for s in sorted_stocks[:2]]

    # 调仓
    current_positions = list(context.portfolio.positions.keys())

    # 卖出不在目标池的股票
    for stock in current_positions:
        if stock not in target_stocks:
            order_target_percent(stock, 0)
            logger.info(f"卖出 {stock}")

    # 买入目标股票
    target_weight = 0.45  # 每只股票45%仓位
    for stock in target_stocks:
        order_target_percent(stock, target_weight)
        logger.info(f"买入 {stock}, 目标仓位 {target_weight*100}%")`,

  run_backtest: `# 运行回测的命令
rqalpha run \\
    -f strategy.py \\
    -s 2020-01-01 \\
    -e 2021-12-31 \\
    --stock-starting-cash 100000 \\
    --frequency 1d \\
    --benchmark 000300.XSHG \\
    --output-file results.pkl \\
    --plot

# 或者使用 Python API
from rqalpha import run

config = {
    "base": {
        "start_date": "2020-01-01",
        "end_date": "2021-12-31",
        "frequency": "1d",
        "accounts": {
            "stock": 100000
        }
    },
    "mod": {
        "sys_analyser": {
            "enabled": True,
            "plot": True,
            "output_file": "results.pkl"
        }
    }
}

result = run(config=config, strategy_file="strategy.py")
print(f"总收益率: {result['summary']['total_returns']:.2%}")
print(f"夏普比率: {result['summary']['sharpe']:.2f}")
print(f"最大回撤: {result['summary']['max_drawdown']:.2%}")`
}

// 实时监控代码
export const REALTIME_MONITOR_CODE = `
import time
import schedule
from datetime import datetime

def realtime_monitor():
    """实时监控主函数"""
    print(f"{datetime.now()} - 开始筛选...")

    # 加载所有股票数据
    all_stocks = load_all_stocks()

    # 执行筛选
    matched_stocks = []
    for code, df in all_stocks.items():
        if check_strategy(df):
            matched_stocks.append(code)

    if matched_stocks:
        print(f"发现 {len(matched_stocks)} 只股票符合条件:")
        for code in matched_stocks:
            print(f"  {code}")

        # 发送通知
        send_notification(matched_stocks)

def check_strategy(df):
    """检查策略条件"""
    latest = df.iloc[-1]

    # 示例: MACD金叉 + RSI不超买
    condition = (
        latest['macd'] > latest['signal'] and
        latest['macd_prev'] <= latest['signal_prev'] and
        latest['rsi'] < 70
    )

    return condition

def send_notification(stocks):
    """发送通知"""
    message = f"发现{len(stocks)}只股票符合条件:\\n"
    message += "\\n".join(stocks)

    # 发送邮件
    send_email("股票筛选提醒", message)

    # 发送微信 (Server酱)
    send_wechat(message)

# 设置定时任务
schedule.every(5).minutes.do(realtime_monitor)  # 每5分钟执行一次

# 只在交易时间运行
def run_scheduler():
    while True:
        now = datetime.now()
        # 交易日的 9:30-11:30 和 13:00-15:00
        if now.weekday() < 5:  # 周一到周五
            if (9 <= now.hour < 12) or (13 <= now.hour < 15):
                schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    print("开始实时监控...")
    run_scheduler()`

// 盘后筛选代码
export const AFTER_MARKET_CODE = `
def after_market_screen():
    """盘后自动筛选"""
    print(f"{datetime.now()} - 开始盘后筛选...")

    # 更新所有股票数据
    update_all_stocks()

    # 执行多个策略筛选
    strategies = {
        '均线多头': filter_ma_bullish,
        'MACD金叉': filter_macd_golden_cross,
        '放量突破': filter_breakout_with_volume,
        'RSI超卖': filter_rsi_oversold
    }

    report = []
    for name, strategy in strategies.items():
        matched = []
        for code in all_stock_codes:
            df = load_stock_data(code)
            if strategy(df):
                matched.append(code)

        report.append({
            'strategy': name,
            'count': len(matched),
            'stocks': matched[:10]  # 只保留前10只
        })

    # 生成HTML报告
    generate_html_report(report)

    # 发送邮件
    send_email_report(report)

# 每个交易日下午3点15分执行
schedule.every().day.at("15:15").do(after_market_screen)`
