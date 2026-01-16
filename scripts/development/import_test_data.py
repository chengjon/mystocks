import pandas as pd
import numpy as np
import subprocess


def generate_test_data(symbol, start_date, end_date):
    """生成测试K线数据"""
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    # 过滤掉周末
    dates = dates[dates.weekday < 5]

    data = []
    base_price = np.random.uniform(10, 50)

    for i, date in enumerate(dates):
        if i == 0:
            open_price = base_price
        else:
            # 基于前一天的收盘价进行小幅波动
            prev_close = data[-1]["close"]
            change_pct = np.random.uniform(-0.05, 0.05)  # -5% 到 5% 的变化
            open_price = prev_close * (1 + change_pct)

        high_price = open_price * (1 + abs(np.random.uniform(0, 0.03)))
        low_price = open_price * (1 - abs(np.random.uniform(0, 0.03)))
        close_price = np.random.uniform(low_price, high_price)
        volume = np.random.randint(1000000, 100000000)
        amount = close_price * volume

        data.append(
            {
                "symbol": symbol,
                "date": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume,
                "amount": round(amount, 2),
            }
        )

    return data


def import_test_data():
    """导入测试数据到数据库"""
    symbols = [
        ("000001.SZ", "平安银行"),
        ("000002.SZ", "万科A"),
        ("600000.SH", "浦发银行"),
        ("600036.SH", "招商银行"),
    ]

    # 插入股票基本信息
    print("插入股票基本信息...")
    for symbol, name in symbols:
        market = symbol.split(".")[-1]
        industry = "银行" if "银行" in name else "房地产"
        area = "深圳" if market == "SZ" else "上海"
        list_date = "2000-01-01"

        insert_sql = f"""
        INSERT INTO symbols_info (symbol, name, industry, area, market, list_date)
        VALUES ('{symbol}', '{name}', '{industry}', '{area}', '{market}', '{list_date}')
        ON CONFLICT (symbol) DO NOTHING;
        """

        cmd = f'echo "{insert_sql}" | docker exec -i mystocks_postgres psql -U postgres -d mystocks'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"插入股票信息失败: {result.stderr}")
        else:
            print(f"已插入股票信息: {symbol} - {name}")

    # 生成并插入K线数据
    for symbol, name in symbols:
        print(f"正在为 {symbol} ({name}) 生成测试数据...")
        data = generate_test_data(symbol, "2024-01-01", "2024-12-31")

        # 准备批量插入的SQL
        values = []
        for row in data:
            values.append(
                f"('{row['symbol']}', '{row['date']}', {row['open']}, {row['high']}, {row['low']}, {row['close']}, {row['volume']}, {row['amount']})"
            )

        if values:
            insert_sql = f"""
            INSERT INTO daily_kline (symbol, date, open, high, low, close, volume, amount)
            VALUES {", ".join(values)};
            """

            cmd = f'echo "{insert_sql}" | docker exec -i mystocks_postgres psql -U postgres -d mystocks'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"插入K线数据失败: {result.stderr}")
            else:
                print(f"已为 {symbol} 插入 {len(data)} 条K线数据")
        else:
            print(f"没有生成 {symbol} 的数据")

    print("测试数据导入完成！")


if __name__ == "__main__":
    import_test_data()
