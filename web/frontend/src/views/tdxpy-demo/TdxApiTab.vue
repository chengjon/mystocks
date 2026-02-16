<template>
    <el-card v-show="activeTab === 'api'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>💻 API 使用示例</span>
          <el-tag type="warning">文档</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>📊 常用 API 示例</h3>

        <el-collapse accordion style="margin-top: 20px;">
          <el-collapse-item title="1️⃣ 获取实时行情" name="1">
            <div class="api-content">
              <h4>get_security_quotes() - 获取多只股票的实时行情</h4>

              <pre v-pre class="code-block">from pytdx.hq import TdxHq_API

api = TdxHq_API()
with api.connect('119.147.212.81', 7709):
    # 查询多只股票 (市场代码, 股票代码)
    # 市场代码: 0-深圳, 1-上海
    quotes = api.get_security_quotes([
        (0, '000001'),  # 平安银行
        (1, '600000'),  # 浦发银行
        (1, '000001')   # 上证指数
    ])

    for quote in quotes:
        print(f"股票: {quote['code']}")
        print(f"  名称: {quote['name']}")
        print(f"  当前价: {quote['price']}")
        print(f"  涨跌幅: {quote['percent']}%")
        print(f"  成交量: {quote['vol']}")
        print(f"  成交额: {quote['amount']}")</pre>

              <h4 style="margin-top: 15px;">返回字段说明</h4>
              <el-table :data="quoteFields" stripe size="small" style="margin-top: 10px;">
                <el-table-column prop="field" label="字段" width="120" />
                <el-table-column prop="description" label="说明" />
              </el-table>
            </div>
          </el-collapse-item>

          <el-collapse-item title="2️⃣ 获取K线数据" name="2">
            <div class="api-content">
              <h4>get_security_bars() - 获取K线数据</h4>

              <pre v-pre class="code-block">from pytdx.hq import TdxHq_API

api = TdxHq_API()
with api.connect('119.147.212.81', 7709):
    # 获取日K线数据
    # 参数: (K线类型, 市场代码, 股票代码, 起始位置, 数量)
    # K线类型: 4-日线, 5-周线, 6-月线, 7-5分钟, 8-15分钟, 9-30分钟, 10-60分钟
    bars = api.get_security_bars(
        category=4,      # 日K线
        market=0,        # 深圳市场
        code='000001',   # 平安银行
        start=0,         # 从最新数据开始
        count=100        # 获取100根K线
    )

    print(f"获取到 {len(bars)} 根K线")
    for bar in bars[:5]:  # 显示最新5根
        print(f"{bar['datetime']} - "
              f"开:{bar['open']} "
              f"高:{bar['high']} "
              f"低:{bar['low']} "
              f"收:{bar['close']} "
              f"量:{bar['vol']}")</pre>

              <h4 style="margin-top: 15px;">K线类型代码</h4>
              <el-table :data="klineTypes" stripe size="small" style="margin-top: 10px;">
                <el-table-column prop="code" label="代码" width="80" />
                <el-table-column prop="type" label="类型" width="120" />
                <el-table-column prop="description" label="说明" />
              </el-table>
            </div>
          </el-collapse-item>

          <el-collapse-item title="3️⃣ 获取分时数据" name="3">
            <div class="api-content">
              <h4>get_分时 data() - 获取分时图数据</h4>

              <pre v-pre class="code-block">from pytdx.hq import TdxHq_API

api = TdxHq_API()
with api.connect('119.147.212.81', 7709):
    # 获取分时数据 (Tick级别)
    tick_data = api.get_history_transaction_data(
        market=0,
        code='000001',
        start=0,
        count=2000  # 最多2000条
    )

    print(f"获取到 {len(tick_data)} 条Tick数据")
    for tick in tick_data[:10]:  # 显示前10条
        print(f"{tick['time']} - "
              f"价格:{tick['price']} "
              f"量:{tick['vol']} "
              f"方向:{'买' if tick['buyorsell'] == 0 else '卖'}")</pre>
            </div>
          </el-collapse-item>

          <el-collapse-item title="4️⃣ 获取股票列表" name="4">
            <div class="api-content">
              <h4>get_security_list() - 获取市场股票列表</h4>

              <pre v-pre class="code-block">from pytdx.hq import TdxHq_API

api = TdxHq_API()
with api.connect('119.147.212.81', 7709):
    # 获取深圳A股列表
    # 市场: 0-深圳, 1-上海
    # 类型: 0-股票, 1-指数, 2-基金
    sz_stocks = api.get_security_list(market=0, start=0)

    print(f"深圳市场股票数量: {len(sz_stocks)}")
    for stock in sz_stocks[:10]:  # 显示前10只
        print(f"{stock['code']} - {stock['name']}")

    # 获取上海A股列表
    sh_stocks = api.get_security_list(market=1, start=0)
    print(f"\n上海市场股票数量: {len(sh_stocks)}")

    # 获取指数列表
    indices = api.get_security_list(market=1, start=0)
    print(f"\n指数数量: {len([s for s in indices if s['code'].startswith('000')])}")</pre>
            </div>
          </el-collapse-item>

          <el-collapse-item title="5️⃣ 获取财务数据" name="5">
            <div class="api-content">
              <h4>get_finance_info() - 获取财务数据</h4>

              <pre v-pre class="code-block">from pytdx.exhq import TdxExHq_API

api = TdxExHq_API()
with api.connect('106.14.95.149', 7727):
    # 获取财务数据 (需要扩展行情 API)
    finance_data = api.get_finance_info(market=0, code='000001')

    print(f"股票代码: {finance_data['code']}")
    print(f"每股收益: {finance_data['liutongguben']}")
    print(f"每股净资产: {finance_data['mgsy']}")
    print(f"净资产收益率: {finance_data['mgjzc']}")
    print(f"市盈率: {finance_data['pe']}")
    print(f"市净率: {finance_data['pb']}")</pre>
            </div>
          </el-collapse-item>

          <el-collapse-item title="6️⃣ 批量获取数据" name="6">
            <div class="api-content">
              <h4>批量获取多只股票的K线数据</h4>

              <pre v-pre class="code-block">from pytdx.hq import TdxHq_API
import pandas as pd

def get_multiple_stocks_kline(codes, count=100):
    """
    批量获取多只股票的K线数据

    Args:
        codes: 股票代码列表 [(market, code), ...]
        count: 每只股票获取的K线数量

    Returns:
        dict: {code: DataFrame}
    """
    result = {}

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        for market, code in codes:
            try:
                bars = api.get_security_bars(
                    category=4,  # 日K线
                    market=market,
                    code=code,
                    start=0,
                    count=count
                )

                # 转换为 DataFrame
                df = pd.DataFrame(bars)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)

                result[code] = df
                print(f"已获取 {code}: {len(df)} 条数据")

            except Exception as e:
                print(f"获取 {code} 失败: {e}")

    return result

# 使用示例
stocks = [
    (0, '000001'),  # 平安银行
    (1, '600000'),  # 浦发银行
    (1, '600036')   # 招商银行
]

data = get_multiple_stocks_kline(stocks, count=200)

# 查看数据
for code, df in data.items():
    print(f"\n{code} 最新数据:")
    print(df.tail())</pre>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>

    <!-- 4. 数据导出 -->
</template>

<script setup lang="ts">
interface Props {
  activeTab: string
  quoteFields: Array<{ field: string; description: string }>
  klineTypes: Array<{ code: number; type: string; description: string }>
}

defineProps<Props>()
</script>
