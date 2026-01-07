<template>
  <div class="tdxpy-demo">

    <div class="page-header">
      <h1 class="page-title">TDPXY DEMO</h1>
      <p class="page-subtitle">PYTONGDAXIN | REAL-TIME DATA | HISTORICAL DATA</p>
    </div>

    <div class="function-nav">
      <el-button
        v-for="tab in tabs"
        :key="tab.key"
        type="activeTab === tab.key ? 'solid' : 'outline'"
        @click="activeTab = tab.key"
      >
        {{ tab.icon }} {{ tab.label }}
      </el-button>
    </div>

    <el-card v-show="activeTab === 'overview'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>PROJECT OVERVIEW</span>
          <el-tag type="success">MIGRATED</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>INTRODUCTION</h3>
        <p>pytdx is a pure Python implementation of Tongdaxin network protocol interface library. It provides a complete Python API for obtaining real-time and historical market data by reverse engineering Tongdaxin's network protocol, without requiring Tongdaxin client installation.</p>

        <h3 style="margin-top: 30px;">CORE FEATURES</h3>
        <div class="features-grid">
          <el-card :hoverable="true">
            <h4>MARKET DATA API</h4>
            <ul>
              <li>Real-time Quotes (Level-1)</li>
              <li>Historical K-line Data (Daily/Weekly/Monthly/Minute)</li>
              <li>Intraday Data (Tick Level)</li>
              <li>Order Book Data (5-level Bid/Ask)</li>
              <li>Transaction History</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>BASIC DATA API</h4>
            <ul>
              <li>Stock List Query (A-Shares/Indices/Sectors)</li>
              <li>Financial Data Query</li>
              <li>Company Information</li>
              <li>Ex-dividend Data</li>
              <li>Sector Components</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>EXTENDED API</h4>
            <ul>
              <li>Level-2 10-level Quotes (requires permission)</li>
              <li>Tick-by-tick Order Data</li>
              <li>Main Force Capital Flow</li>
              <li>Dragon Tiger List Data</li>
              <li>Large Order Tracking</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>TOOLS</h4>
            <ul>
              <li>Cross-platform (Windows/Mac/Linux)</li>
              <li>Auto Server Selection & Load Balancing</li>
              <li>Data Caching Mechanism</li>
              <li>Concurrent Request Support</li>
              <li>Error Retry Mechanism</li>
            </ul>
          </el-card>
        </div>

        <h3 style="margin-top: 30px;">PROJECT ADVANTAGES</h3>
        <el-descriptions :column="2" border style="margin-top: 15px;" class="descriptions">
          <el-descriptions-item label="PURE PYTHON">
            No Tongdaxin client required, cross-platform support
          </el-descriptions-item>
          <el-descriptions-item label="FREE">
            Completely free, no data interface purchase required
          </el-descriptions-item>
          <el-descriptions-item label="REAL-TIME DATA">
            Direct connection to Tongdaxin servers
          </el-descriptions-item>
          <el-descriptions-item label="HISTORICAL DATA">
            Complete historical K-line data support</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px;">LIBRARY REPOSITORY</h3>
        <el-alert
          type="info"
          :closable="false"
          style="margin-top: 20px;"
        >
          <template #title>
            <div style="font-weight: bold;">📚 项目资源</div>
          </template>
          <ul style="margin-top: 10px;">
            <li>GitHub: <el-link href="https://github.com/rainx/pytdx" target="_blank" type="primary">https://github.com/rainx/pytdx</el-link></li>
            <li>PyPI: <el-link href="https://pypi.org/project/pytdx/" target="_blank" type="primary">https://pypi.org/project/pytdx/</el-link></li>
            <li>Documentation: <el-link href="https://pytdx.readthedocs.io/" target="_blank" type="primary">https://pytdx.readthedocs.io/</el-link></li>
            <li>文档: 完整的 API 文档和使用示例</li>
            <li>社区: 活跃的 Issue 讨论和问题解答</li>
            <li>更新: 持续更新以支持最新的通达信协议</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- 2. 安装和配置 -->
    <el-card v-show="activeTab === 'install'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>⚙️ 安装和配置</span>
          <el-tag type="success">已集成</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>📦 安装方式</h3>
        <p>pytdx 可以通过 pip 直接安装:</p>

        <pre v-pre class="code-block"># 安装 pytdx
pip install pytdx

# 或者从源码安装
git clone https://github.com/rainx/pytdx.git
cd pytdx
python setup.py install</pre>

        <h3 style="margin-top: 30px;">🔧 基础配置</h3>
        <p>pytdx 提供了两种主要的 API 类型:</p>

        <el-tabs type="border-card" style="margin-top: 20px;">
          <el-tab-pane label="标准行情 API">
            <div class="tab-content">
              <h4>📊 TdxHq_API - 标准行情接口</h4>
              <p>用于获取基础行情数据,如K线、实时价格等:</p>

              <pre v-pre class="code-block">from pytdx.hq import TdxHq_API

# 创建 API 对象
api = TdxHq_API()

# 连接服务器
if api.connect('119.147.212.81', 7709):
    print("连接成功!")

    # 在这里执行数据查询...

    # 断开连接
    api.disconnect()
else:
    print("连接失败")</pre>

              <h4 style="margin-top: 20px;">🌐 可用服务器列表</h4>
              <el-table :data="standardServers" stripe size="small" style="margin-top: 10px;">
                <el-table-column prop="ip" label="IP地址" width="150" />
                <el-table-column prop="port" label="端口" width="80" />
                <el-table-column prop="location" label="位置" />
              </el-table>
            </div>
          </el-tab-pane>

          <el-tab-pane label="扩展行情 API">
            <div class="tab-content">
              <h4>🔌 TdxExHq_API - 扩展行情接口</h4>
              <p>提供更详细的行情数据,包括 Level-2、财务数据等:</p>

              <pre v-pre class="code-block">from pytdx.exhq import TdxExHq_API

# 创建扩展 API 对象
api = TdxExHq_API()

# 连接服务器 (扩展行情服务器)
if api.connect('106.14.95.149', 7727):
    print("连接成功!")

    # 执行扩展数据查询...

    api.disconnect()
else:
    print("连接失败")</pre>

              <h4 style="margin-top: 20px;">🌐 扩展服务器列表</h4>
              <el-table :data="extendedServers" stripe size="small" style="margin-top: 10px;">
                <el-table-column prop="ip" label="IP地址" width="150" />
                <el-table-column prop="port" label="端口" width="80" />
                <el-table-column prop="location" label="位置" />
              </el-table>
            </div>
          </el-tab-pane>

          <el-tab-pane label="自动服务器选择">
            <div class="tab-content">
              <h4>🔄 BestIP - 自动选择最佳服务器</h4>
              <p>pytdx 提供自动选择延迟最低的服务器功能:</p>

              <pre v-pre class="code-block">from pytdx.hq import TdxHq_API
from pytdx.util.best_ip import select_best_ip

# 自动选择最佳服务器
best_ip = select_best_ip()
print(f"最佳服务器: {best_ip['ip']}:{best_ip['port']}")

# 连接到最佳服务器
api = TdxHq_API()
if api.connect(best_ip['ip'], best_ip['port']):
    print("连接成功!")
    api.disconnect()</pre>

              <el-alert type="info" :closable="false" style="margin-top: 15px;">
                <p><strong>💡 建议:</strong> 在生产环境中使用自动服务器选择功能,可以提高连接成功率和数据获取速度。</p>
              </el-alert>
            </div>
          </el-tab-pane>
        </el-tabs>

        <h3 style="margin-top: 30px;">🔐 with 语句管理连接</h3>
        <p>推荐使用 with 语句管理连接,自动处理连接和断开:</p>

        <pre v-pre class="code-block">from pytdx.hq import TdxHq_API

# 使用 with 语句
with TdxHq_API() as api:
    if api.connect('119.147.212.81', 7709):
        # 查询数据
        data = api.get_security_quotes([(0, '000001')])
        print(data)
    # 自动断开连接</pre>
      </div>
    </el-card>

    <!-- 3. API 使用示例 -->
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
    <el-card v-show="activeTab === 'export'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>💾 数据导出</span>
          <el-tag type="warning">文档</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>📤 数据导出功能</h3>
        <p>pytdx 可以方便地将获取的数据导出为多种格式:</p>

        <el-tabs type="border-card" style="margin-top: 20px;">
          <el-tab-pane label="导出到 CSV">
            <pre v-pre class="code-block">from pytdx.hq import TdxHq_API
import pandas as pd

def export_to_csv(market, code, filename, count=1000):
    """导出K线数据到CSV文件"""

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        # 获取K线数据
        bars = api.get_security_bars(
            category=4,
            market=market,
            code=code,
            start=0,
            count=count
        )

        # 转换为 DataFrame
        df = pd.DataFrame(bars)

        # 导出到 CSV
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"已导出 {len(df)} 条数据到 {filename}")

# 使用示例
export_to_csv(0, '000001', '000001_daily.csv', count=500)</pre>
          </el-tab-pane>

          <el-tab-pane label="导出到数据库">
            <pre v-pre class="code-block">from pytdx.hq import TdxHq_API
import pandas as pd
from sqlalchemy import create_engine

def export_to_database(market, code, table_name, count=1000):
    """导出K线数据到PostgreSQL数据库"""

    # 创建数据库连接
    engine = create_engine(
        'postgresql://user:password@localhost:5432/stocks'
    )

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        # 获取K线数据
        bars = api.get_security_bars(
            category=4,
            market=market,
            code=code,
            start=0,
            count=count
        )

        # 转换为 DataFrame
        df = pd.DataFrame(bars)
        df['code'] = code
        df['datetime'] = pd.to_datetime(df['datetime'])

        # 写入数据库
        df.to_sql(
            table_name,
            engine,
            if_exists='append',
            index=False
        )

        print(f"已导出 {len(df)} 条数据到数据库表 {table_name}")

# 使用示例
export_to_database(0, '000001', 'stock_daily', count=500)</pre>
          </el-tab-pane>

          <el-tab-pane label="定时更新">
            <pre v-pre class="code-block">import schedule
import time
from pytdx.hq import TdxHq_API
import pandas as pd

def update_stock_data():
    """定时更新股票数据"""
    print(f"开始更新数据 - {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 股票列表
    stocks = [
        (0, '000001'),
        (1, '600000'),
        (1, '600036')
    ]

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        for market, code in stocks:
            try:
                # 获取最新100根K线
                bars = api.get_security_bars(
                    category=4,
                    market=market,
                    code=code,
                    start=0,
                    count=100
                )

                # 保存到CSV
                df = pd.DataFrame(bars)
                filename = f"data/{code}_daily.csv"
                df.to_csv(filename, index=False)

                print(f"已更新 {code}")

            except Exception as e:
                print(f"更新 {code} 失败: {e}")

# 每天下午3点15分更新
schedule.every().day.at("15:15").do(update_stock_data)

# 持续运行
while True:
    schedule.run_pending()
    time.sleep(60)</pre>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>

    <!-- 5. 集成状态 -->
    <el-card v-show="activeTab === 'status'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>✅ 集成状态</span>
        </div>
      </template>

      <div class="content-section">
        <h3>📦 已集成功能</h3>
        <el-descriptions :column="1" border style="margin-top: 15px;">
          <el-descriptions-item label="pytdx 库">
            <el-tag type="success">✅ 已安装</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="API 文档">
            <el-tag type="success">✅ 已整理</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="使用示例">
            <el-tag type="success">✅ 已收集</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="后端接口">
            <el-tag type="info">⏳ 待开发</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="实时数据服务">
            <el-tag type="info">⏳ 计划中</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="数据缓存">
            <el-tag type="info">⏳ 计划中</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px;">🎯 后续集成计划</h3>
        <el-timeline style="margin-top: 20px;">
          <el-timeline-item timestamp="Phase 1" placement="top">
            <el-card>
              <h4>后端 API 开发</h4>
              <p>封装 pytdx 功能为 RESTful API,提供标准化数据接口</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 2" placement="top">
            <el-card>
              <h4>实时数据服务</h4>
              <p>建立 WebSocket 推送服务,实现实时行情推送</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 3" placement="top">
            <el-card>
              <h4>数据缓存层</h4>
              <p>实现 Redis 缓存,提高数据访问速度</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 4" placement="top">
            <el-card>
              <h4>数据可视化</h4>
              <p>在 Web 界面中展示实时行情和K线图表</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <h3 style="margin-top: 30px;">💡 应用场景</h3>
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>🎯 实时行情监控</h4>
              <p>使用 pytdx 获取实时行情数据,结合策略进行监控和告警。适用于短线交易和日内策略。</p>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>📊 历史数据回测</h4>
              <p>获取完整的历史K线数据,用于策略回测和参数优化。支持多周期数据分析。</p>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>💾 数据采集系统</h4>
              <p>定时采集和更新股票数据,建立本地数据库。支持全市场数据采集和增量更新。</p>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>🔍 量化分析</h4>
              <p>结合技术指标和因子分析,构建量化选股系统。支持多因子模型和机器学习。</p>
            </el-card>
          </el-col>
        </el-row>

        <el-alert
          type="warning"
          title="⚠️ 使用注意事项"
          :closable="false"
          style="margin-top: 20px;"
        >
          <ul style="margin-top: 10px;">
            <li><strong>频率限制</strong>: 避免过于频繁请求,建议间隔至少1秒</li>
            <li><strong>数据延迟</strong>: 通达信免费数据有3-5秒延迟</li>
            <li><strong>服务器稳定性</strong>: 服务器可能不稳定,需要实现重连机制</li>
            <li><strong>数据准确性</strong>: 建议与官方数据源进行对比验证</li>
            <li><strong>合规使用</strong>: 仅供个人学习研究使用,商业用途需咨询通达信</li>
          </ul>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('overview')

const tabs = [
  { key: 'overview', label: '项目概览', icon: '📋' },
  { key: 'install', label: '安装配置', icon: '⚙️' },
  { key: 'api', label: 'API 示例', icon: '💻' },
  { key: 'export', label: '数据导出', icon: '💾' },
  { key: 'status', label: '集成状态', icon: '✅' }
]

const standardServers = [
  { ip: '119.147.212.81', port: '7709', location: '深圳电信' },
  { ip: '114.80.63.12', port: '7709', location: '上海电信' },
  { ip: '60.12.136.250', port: '7709', location: '杭州电信' },
  { ip: '115.238.90.165', port: '7709', location: '南京电信' }
]

const extendedServers = [
  { ip: '106.14.95.149', port: '7727', location: '上海' },
  { ip: '119.147.164.60', port: '7727', location: '深圳' },
  { ip: '47.103.48.45', port: '7727', location: '杭州' }
]

const quoteFields = [
  { field: 'code', description: '股票代码' },
  { field: 'name', description: '股票名称' },
  { field: 'price', description: '当前价格' },
  { field: 'open', description: '开盘价' },
  { field: 'high', description: '最高价' },
  { field: 'low', description: '最低价' },
  { field: 'pre_close', description: '昨收价' },
  { field: 'percent', description: '涨跌幅 (%)' },
  { field: 'vol', description: '成交量' },
  { field: 'amount', description: '成交额' },
  { field: 'bid1-bid5', description: '五档委买价' },
  { field: 'ask1-ask5', description: '五档委卖价' }
]

const klineTypes = [
  { code: '4', type: '日线', description: '每日K线数据' },
  { code: '5', type: '周线', description: '每周K线数据' },
  { code: '6', type: '月线', description: '每月K线数据' },
  { code: '7', type: '5分钟', description: '5分钟K线数据' },
  { code: '8', type: '15分钟', description: '15分钟K线数据' },
  { code: '9', type: '30分钟', description: '30分钟K线数据' },
  { code: '10', type: '60分钟', description: '60分钟K线数据' },
  { code: '11', type: '1分钟', description: '1分钟K线数据' }
]
</script>

<style scoped>

.tdxpy-demo {
  padding: var(--spacing-6);
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
  background: var(--bg-primary);
}

.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(
      45deg,
      var(--accent-gold) 0px,
      var(--accent-gold) 1px,
      transparent 1px,
      transparent 10px
    ),
    repeating-linear-gradient(
      -45deg,
      var(--accent-gold) 0px,
      var(--accent-gold) 1px,
      transparent 1px,
      transparent 10px
    );
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-8);
  position: relative;
  z-index: 1;

  .page-title {
    font-family: var(--font-display);
    font-size: var(--font-size-h2);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-widest);
    color: var(--accent-gold);
    margin: 0 0 var(--spacing-2) 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    color: var(--fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin: 0;
  }
}

.demo-grid {
  display: flex;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-6);
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.demo-card {
  margin-bottom: var(--spacing-6);
  position: relative;
  z-index: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: var(--font-display);
  font-size: var(--font-size-h4);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--accent-gold);
}

.content-section {
  padding: var(--spacing-4) 0;
  line-height: 1.8;
}

.content-section h3 {
  font-family: var(--font-display);
  font-size: var(--font-size-h4);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--accent-gold);
  margin-bottom: var(--spacing-4);
}

.content-section h4 {
  font-family: var(--font-display);
  font-size: var(--font-size-body);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--fg-primary);
  margin-bottom: var(--spacing-3);
}

.content-section p {
  margin: var(--spacing-3) 0;
  color: var(--fg-primary);
}

.content-section ul {
  padding-left: var(--spacing-6);
  margin: var(--spacing-3) 0;
}

.content-section ul li {
  margin: var(--spacing-2) 0;
  color: var(--fg-primary);
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-4);
  margin-top: var(--spacing-4);
}

.model-list ul {
  padding-left: var(--spacing-5);
  margin: var(--spacing-3) 0;
  list-style: disc;
}

.profiling-section :deep(.el-descriptions__label) {
  background: rgba(212, 175, 55, 0.1) !important;
  color: var(--fg-muted) !important;
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
}

.profiling-section :deep(.el-descriptions__content) {
  background: transparent !important;
  color: var(--fg-primary) !important;
  font-family: var(--font-body);
}

.content-section p {
  color: #606266;
}

.content-section ul {
  padding-left: 25px;
  margin: 10px 0;
}

.content-section ul li {
  margin: 5px 0;
}

.code-block {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre;
  color: #303133;
}

.tab-content,
.api-content {
  padding: 15px;
}

:deep(.el-card__body) {
  padding: 15px;
}

:deep(.el-collapse-item__content) {
  padding: 0;
}

:deep(.el-timeline-item__timestamp) {
  font-weight: bold;
  color: #409eff;
}
</style>
