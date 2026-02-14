<template>

    <div class="page-header">
      <h1 class="page-title">PYTDX</h1>
      <p class="page-subtitle">TONGDAXIN DATA INTERFACE | PYTHON | REALTIME | HISTORICAL</p>
      <div class="decorative-line"></div>
    </div>

    <div class="function-nav tabs-nav">
      <button
        v-for="(tab, _idx) in tabs"
        :key="tab.key"
        class="btn"
        @click="activeTab = tab.key"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </div>

    <div class="card main-card" v-show="activeTab === 'overview'">
      <div class="card-header">
        <h3 class="card-title">📋 PROJECT OVERVIEW</h3>
        <span class="badge badge-success">MIGRATED</span>
      </div>

      <div class="content-section">
        <h3>🎯 PYTDX INTRODUCTION</h3>
        <p>pytdx is a pure Python implementation of the Tongdaoxin network protocol interface library. It provides a complete Python API for obtaining real-time and historical market data by reverse-engineering Tongdaoxin's network protocol, without requiring the Tongdaoxin client installation.</p>

        <h3 style="margin-top: 30px;">✨ CORE FEATURES</h3>
        <div class="features-grid" style="margin-top: 20px;">
          <div class="card feature-card">
            <h4>📊 MARKET DATA API</h4>
            <ul>
              <li>Real-time quotes (Level-1)</li>
              <li>Historical K-line data (Daily/Weekly/Monthly/Minute)</li>
              <li>Intraday data (Tick level)</li>
              <li>Order book data (5-level bid/ask)</li>
              <li>Transaction history data</li>
            </ul>
          </div>
          <div class="card feature-card">
            <h4>🗂️ BASIC DATA API</h4>
            <ul>
              <li>Stock list query (A-shares/Indices/Sectors)</li>
              <li>Financial data query</li>
              <li>Company information query</li>
              <li>Dividend/rights adjustment data</li>
              <li>Sector component stocks</li>
            </ul>
          </div>
          <div class="card feature-card">
            <h4>🔌 EXTENDED MARKET API</h4>
            <ul>
              <li>Level-2 10-level quotes (requires permission)</li>
              <li>Transaction-by-transaction data</li>
              <li>Main force fund flow</li>
              <li>Dragon Tiger list data</li>
              <li>Large order tracking</li>
            </ul>
          </div>
          <div class="card feature-card">
            <h4>🛠️ UTILITY FEATURES</h4>
            <ul>
              <li>Cross-platform support (Windows/Mac/Linux)</li>
              <li>Automatic server selection and load balancing</li>
              <li>Data caching mechanism</li>
              <li>Concurrent request support</li>
              <li>Error retry mechanism</li>
            </ul>
          </div>
        </div>

        <h3 style="margin-top: 30px;">🌟 PROJECT ADVANTAGES</h3>
        <div class="advantage-grid" style="margin-top: 15px;">
          <div class="advantage-item">
            <div class="advantage-icon">🐍</div>
            <div class="advantage-content">
              <div class="advantage-title">PURE PYTHON</div>
              <div class="advantage-desc">No Tongdaoxin client required, cross-platform support</div>
            </div>
          </div>
          <div class="advantage-item">
            <div class="advantage-icon">💰</div>
            <div class="advantage-content">
              <div class="advantage-title">FREE TO USE</div>
              <div class="advantage-desc">Completely free, no purchase required</div>
            </div>
          </div>
          <div class="advantage-item">
            <div class="advantage-icon">⚡</div>
            <div class="advantage-content">
              <div class="advantage-title">REAL-TIME DATA</div>
              <div class="advantage-desc">Direct connection to Tongdaoxin servers</div>
            </div>
          </div>
          <div class="advantage-item">
            <div class="advantage-icon">📈</div>
            <div class="advantage-content">
              <div class="advantage-title">HISTORICAL DATA</div>
              <div class="advantage-desc">Complete historical K-line data support</div>
            </div>
          </div>
          <div class="advantage-item">
            <div class="advantage-icon">🔗</div>
            <div class="advantage-content">
              <div class="advantage-title">EASY INTEGRATION</div>
              <div class="advantage-desc">Clean API design, easy to integrate</div>
            </div>
          </div>
          <div class="advantage-item">
            <div class="advantage-icon">🔧</div>
            <div class="advantage-content">
              <div class="advantage-title">ACTIVE MAINTENANCE</div>
              <div class="advantage-desc">Active GitHub maintenance, good community support</div>
            </div>
          </div>
        </div>

          <div class="alert-title">📚 PROJECT RESOURCES</div>
          <ul style="margin-top: 10px;">
            <li>GitHub: <a href="https://github.com/rainx/pytdx" target="_blank" class="link">https://github.com/rainx/pytdx</a></li>
            <li>Documentation: Complete API documentation and usage examples</li>
            <li>Community: Active Issue discussions and Q&A</li>
            <li>Updates: Continuous updates to support latest Tongdaoxin protocol</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="card main-card" v-show="activeTab === 'install'">
      <div class="card-header">
        <h3 class="card-title">⚙️ INSTALLATION & CONFIG</h3>
        <span class="badge badge-success">INTEGRATED</span>
      </div>

      <div class="content-section">
        <h3>📦 INSTALLATION</h3>
        <p>pytdx can be installed directly via pip:</p>

        <pre v-pre class="code-block"># Install pytdx
pip install pytdx

# Or install from source
git clone https://github.com/rainx/pytdx.git
cd pytdx
python setup.py install</pre>

        <h3 style="margin-top: 30px;">🔧 BASIC CONFIGURATION</h3>
        <p>pytdx provides two main API types:</p>

        <div class="tabs">
          <div class="tabs-header">
            <button
              v-for="(tab, _idx) in installTabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: installTab === tab.key }"
              @click="installTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content" v-show="installTab === 'standard'">
            <h4>📊 TdxHq_API - Standard Market Interface</h4>
            <p>Used to obtain basic market data such as K-lines and real-time prices:</p>

            <pre v-pre class="code-block">from pytdx.hq import TdxHq_API

# Create API object
api = TdxHq_API()

# Connect to server
if api.connect('119.147.212.81', 7709):
    print("Connection successful!")

    # Execute data queries here...

    # Disconnect
    api.disconnect()
else:
    print("Connection failed")</pre>

            <h4 style="margin-top: 20px;">🌐 AVAILABLE SERVERS</h4>
            <table class="table" style="margin-top: 10px;">
              <thead>
                <tr>
                  <th>IP ADDRESS</th>
                  <th>PORT</th>
                  <th>LOCATION</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="server in standardServers" :key="server.ip">
                  <td class="server-ip">{{ server.ip }}</td>
                  <td class="server-port">{{ server.port }}</td>
                  <td>{{ server.location }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="tab-content" v-show="installTab === 'extended'">
            <h4>🔌 TdxExHq_API - Extended Market Interface</h4>
            <p>Provides more detailed market data including Level-2 and financial data:</p>

            <pre v-pre class="code-block">from pytdx.exhq import TdxExHq_API

# Create extended API object
api = TdxExHq_API()

# Connect to server (extended market server)
if api.connect('106.14.95.149', 7727):
    print("Connection successful!")

    # Execute extended data queries...

    api.disconnect()
else:
    print("Connection failed")</pre>

            <h4 style="margin-top: 20px;">🌐 EXTENDED SERVERS</h4>
            <table class="table" style="margin-top: 10px;">
              <thead>
                <tr>
                  <th>IP ADDRESS</th>
                  <th>PORT</th>
                  <th>LOCATION</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="server in extendedServers" :key="server.ip">
                  <td class="server-ip">{{ server.ip }}</td>
                  <td class="server-port">{{ server.port }}</td>
                  <td>{{ server.location }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="tab-content" v-show="installTab === 'auto'">
            <h4>🔄 BestIP - Automatic Best Server Selection</h4>
            <p>pytdx provides automatic selection of the lowest latency server:</p>

            <pre v-pre class="code-block">from pytdx.hq import TdxHq_API
from pytdx.util.best_ip import select_best_ip

# Automatically select best server
best_ip = select_best_ip()
print(f"Best server: {best_ip['ip']}:{best_ip['port']}")

# Connect to best server
api = TdxHq_API()
if api.connect(best_ip['ip'], best_ip['port']):
    print("Connection successful!")
    api.disconnect()</pre>

              <div class="alert-title">💡 RECOMMENDATION</div>
              <p><strong>Using automatic server selection in production environments can improve connection success rate and data retrieval speed.</strong></p>
            </div>
          </div>
        </div>

        <h3 style="margin-top: 30px;">🔐 CONNECTION MANAGEMENT WITH STATEMENT</h3>
        <p>Using with statements for connection management is recommended for automatic handling of connections and disconnections:</p>

        <pre v-pre class="code-block">from pytdx.hq import TdxHq_API

# Use with statement
with TdxHq_API() as api:
    if api.connect('119.147.212.81', 7709):
        # Query data
        data = api.get_security_quotes([(0, '000001')])
        print(data)
    # Automatic disconnection</pre>
      </div>
    </div>

    <div class="card main-card" v-show="activeTab === 'api'">
      <div class="card-header">
        <h3 class="card-title">💻 API USAGE EXAMPLES</h3>
        <span class="badge badge-warning">DOCUMENTATION</span>
      </div>

      <div class="content-section">
        <h3>📊 COMMON API EXAMPLES</h3>

        <div class="accordion">
          <div class="accordion-item" v-for="(item, index) in apiExamples" :key="index">
            <button class="accordion-header" :class="{ active: activeAccordion === index }" @click="toggleAccordion(index)">
              <span class="accordion-number">{{ index + 1 }}</span>
              <span class="accordion-title">{{ item.title }}</span>
              <span class="accordion-icon">{{ activeAccordion === index ? '−' : '+' }}</span>
            </button>
            <div class="accordion-content" v-show="activeAccordion === index">
              <div class="api-content">
                <h4>{{ item.subtitle }}</h4>
                <pre v-pre class="code-block">{{ item.code }}</pre>

                <div v-if="item.tableData">
                  <h4 style="margin-top: 15px;">{{ item.tableTitle }}</h4>
                  <table class="table" style="margin-top: 10px;">
                    <thead>
                      <tr>
                        <th v-for="col in item.tableCols" :key="col">{{ col }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, rowIndex) in item.tableData" :key="rowIndex">
                        <td v-for="col in item.tableCols" :key="col" :class="{ 'code-field': col === 'Field' }">{{ row[col.toLowerCase()] || row[col] }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card main-card" v-show="activeTab === 'export'">
      <div class="card-header">
        <h3 class="card-title">💾 DATA EXPORT</h3>
        <span class="badge badge-warning">DOCUMENTATION</span>
      </div>

      <div class="content-section">
        <h3>📤 DATA EXPORT FEATURES</h3>
        <p>pytdx can easily export obtained data to various formats:</p>

        <div class="tabs">
          <div class="tabs-header">
            <button
              v-for="(tab, _idx) in exportTabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: exportTab === tab.key }"
              @click="exportTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content" v-show="exportTab === 'csv'">
            <pre v-pre class="code-block">from pytdx.hq import TdxHq_API
import pandas as pd

def export_to_csv(market, code, filename, count=1000):
    """Export K-line data to CSV file"""

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        # Get K-line data
        bars = api.get_security_bars(
            category=4,
            market=market,
            code=code,
            start=0,
            count=count
        )

        # Convert to DataFrame
        df = pd.DataFrame(bars)

        # Export to CSV
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Exported {len(df)} records to {filename}")

# Usage example
export_to_csv(0, '000001', '000001_daily.csv', count=500)</pre>
          </div>

          <div class="tab-content" v-show="exportTab === 'database'">
            <pre v-pre class="code-block">from pytdx.hq import TdxHq_API
import pandas as pd
from sqlalchemy import create_engine

def export_to_database(market, code, table_name, count=1000):
    """Export K-line data to PostgreSQL database"""

    # Create database connection
    engine = create_engine(
        'postgresql://user:password@localhost:5432/stocks'
    )

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        # Get K-line data
        bars = api.get_security_bars(
            category=4,
            market=market,
            code=code,
            start=0,
            count=count
        )

        # Convert to DataFrame
        df = pd.DataFrame(bars)
        df['code'] = code
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Write to database
        df.to_sql(
            table_name,
            engine,
            if_exists='append',
            index=False
        )

        print(f"Exported {len(df)} records to database table {table_name}")

# Usage example
export_to_database(0, '000001', 'stock_daily', count=500)</pre>
          </div>

          <div class="tab-content" v-show="exportTab === 'schedule'">
            <pre v-pre class="code-block">import schedule
import time
from pytdx.hq import TdxHq_API
import pandas as pd

def update_stock_data():
    """Scheduled stock data update"""
    print(f"Starting data update - {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Stock list
    stocks = [
        (0, '000001'),
        (1, '600000'),
        (1, '600036')
    ]

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        for market, code in stocks:
            try:
                # Get latest 100 K-lines
                bars = api.get_security_bars(
                    category=4,
                    market=market,
                    code=code,
                    start=0,
                    count=100
                )

                # Save to CSV
                df = pd.DataFrame(bars)
                filename = f"data/{code}_daily.csv"
                df.to_csv(filename, index=False)

                print(f"Updated {code}")

            except Exception as e:
                print(f"Update {code} failed: {e}")

# Update at 3:15 PM every day
schedule.every().day.at("15:15").do(update_stock_data)

# Continuous running
while True:
    schedule.run_pending()
    time.sleep(60)</pre>
          </div>
        </div>
      </div>
    </div>

    <div class="card main-card" v-show="activeTab === 'status'">
      <div class="card-header">
        <h3 class="card-title">✅ INTEGRATION STATUS</h3>
      </div>

      <div class="content-section">
        <h3>📦 INTEGRATED FEATURES</h3>
        <table class="table" style="margin-top: 15px;">
          <thead>
            <tr>
              <th>FEATURE</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>pytdx Library</td>
              <td><span class="badge badge-success">✅ INSTALLED</span></td>
            </tr>
            <tr>
              <td>API Documentation</td>
              <td><span class="badge badge-success">✅ ORGANIZED</span></td>
            </tr>
            <tr>
              <td>Usage Examples</td>
              <td><span class="badge badge-success">✅ COLLECTED</span></td>
            </tr>
            <tr>
              <td>Backend API</td>
              <td><span class="badge badge-warning">⏳ PENDING</span></td>
            </tr>
            <tr>
              <td>Real-time Data Service</td>
              <td><span class="badge badge-info">📅 PLANNED</span></td>
            </tr>
            <tr>
              <td>Data Caching</td>
              <td><span class="badge badge-info">📅 PLANNED</span></td>
            </tr>
          </tbody>
        </table>

        <h3 style="margin-top: 30px;">🎯 FUTURE INTEGRATION PLAN</h3>
        <div class="timeline" style="margin-top: 20px;">
          <div class="timeline-item">
            <div class="timeline-marker">1</div>
            <div class="timeline-content">
              <div class="timeline-title">PHASE 1: BACKEND API</div>
              <div class="timeline-desc">Wrap pytdx functionality as RESTful API, providing standardized data interfaces</div>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-marker">2</div>
            <div class="timeline-content">
              <div class="timeline-title">PHASE 2: REAL-TIME SERVICE</div>
              <div class="timeline-desc">Establish WebSocket push service for real-time market data</div>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-marker">3</div>
            <div class="timeline-content">
              <div class="timeline-title">PHASE 3: CACHE LAYER</div>
              <div class="timeline-desc">Implement Redis cache to improve data access speed</div>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-marker">4</div>
            <div class="timeline-content">
              <div class="timeline-title">PHASE 4: VISUALIZATION</div>
              <div class="timeline-desc">Display real-time quotes and K-line charts in web interface</div>
            </div>
          </div>
        </div>

        <h3 style="margin-top: 30px;">💡 USE CASES</h3>
        <div class="features-grid" style="margin-top: 20px;">
          <div class="card feature-card">
            <h4>🎯 REAL-TIME MONITORING</h4>
            <p>Use pytdx to obtain real-time market data, combined with strategies for monitoring and alerts. Suitable for short-term trading and intraday strategies.</p>
          </div>
          <div class="card feature-card">
            <h4>📊 HISTORICAL BACKTESTING</h4>
            <p>Obtain complete historical K-line data for strategy backtesting and parameter optimization. Supports multi-period data analysis.</p>
          </div>
          <div class="card feature-card">
            <h4>💾 DATA COLLECTION</h4>
            <p>Scheduled collection and update of stock data, establishing local database. Supports full market data collection and incremental updates.</p>
          </div>
          <div class="card feature-card">
            <h4>🔍 QUANTITATIVE ANALYSIS</h4>
            <p>Combine technical indicators and factor analysis to build quantitative stock selection system. Supports multi-factor models and machine learning.</p>
          </div>
        </div>

          <div class="alert-title">⚠️ USAGE NOTES</div>
          <ul style="margin-top: 10px;">
            <li><strong>Rate Limiting</strong>: Avoid too frequent requests, recommended interval at least 1 second</li>
            <li><strong>Data Delay</strong>: Tongdaoxin free data has 3-5 second delay</li>
            <li><strong>Server Stability</strong>: Servers may be unstable, need to implement reconnection mechanism</li>
            <li><strong>Data Accuracy</strong>: Recommended to compare with official data sources</li>
            <li><strong>Compliance</strong>: For personal study and research only, commercial use requires consultation with Tongdaoxin</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('overview')
const installTab = ref('standard')
const exportTab = ref('csv')
const activeAccordion = ref(0)

const tabs = [
  { key: 'overview', label: 'Overview', icon: '📋' },
  { key: 'install', label: 'Install', icon: '⚙️' },
  { key: 'api', label: 'API', icon: '💻' },
  { key: 'export', label: 'Export', icon: '💾' },
  { key: 'status', label: 'Status', icon: '✅' }
]

const installTabs = [
  { key: 'standard', label: 'Standard API' },
  { key: 'extended', label: 'Extended API' },
  { key: 'auto', label: 'Auto Select' }
]

const exportTabs = [
  { key: 'csv', label: 'CSV Export' },
  { key: 'database', label: 'Database' },
  { key: 'schedule', label: 'Scheduled' }
]

const standardServers = [
  { ip: '119.147.212.81', port: '7709', location: 'Shenzhen' },
  { ip: '114.80.63.12', port: '7709', location: 'Shanghai' },
  { ip: '60.12.136.250', port: '7709', location: 'Hangzhou' },
  { ip: '115.238.90.165', port: '7709', location: 'Nanjing' }
]

const extendedServers = [
  { ip: '106.14.95.149', port: '7727', location: 'Shanghai' },
  { ip: '119.147.164.60', port: '7727', location: 'Shenzhen' },
  { ip: '47.103.48.45', port: '7727', location: 'Hangzhou' }
]

const apiExamples = [
  {
    title: 'Get Real-time Quotes',
    subtitle: 'get_security_quotes() - Get real-time quotes for multiple stocks',
    code: `from pytdx.hq import TdxHq_API

api = TdxHq_API()
with api.connect('119.147.212.81', 7709):
    # Query multiple stocks (market code, stock code)
    # Market code: 0-Shenzhen, 1-Shanghai
    quotes = api.get_security_quotes([
        (0, '000001'),  # Ping An Bank
        (1, '600000'),  # SPD Bank
        (1, '000001')   # SSE Index
    ])

    for quote in quotes:
        print(f"Stock: {quote['code']}")
        print(f"  Name: {quote['name']}")
        print(f"  Price: {quote['price']}")
        print(f"  Change: {quote['percent']}%")
        print(f"  Volume: {quote['vol']}")
        print(f"  Amount: {quote['amount']}")`,
    tableTitle: 'Response Fields',
    tableCols: ['Field', 'Description'],
    tableData: [
      { field: 'code', description: 'Stock code' },
      { field: 'name', description: 'Stock name' },
      { field: 'price', description: 'Current price' },
      { field: 'open', description: 'Open price' },
      { field: 'high', description: 'High price' },
      { field: 'low', description: 'Low price' },
      { field: 'percent', description: 'Change %' },
      { field: 'vol', description: 'Volume' }
    ]
  },
  {
    title: 'Get K-line Data',
    subtitle: 'get_security_bars() - Get K-line data',
    code: `from pytdx.hq import TdxHq_API

api = TdxHq_API()
with api.connect('119.147.212.81', 7709):
    # Get daily K-line data
    # Parameters: (K-line type, market code, stock code, start position, count)
    # K-line types: 4-Daily, 5-Weekly, 6-Monthly, 7-5min, 8-15min, 9-30min, 10-60min
    bars = api.get_security_bars(
        category=4,      # Daily K-line
        market=0,        # Shenzhen market
        code='000001',   # Ping An Bank
        start=0,         # Start from newest
        count=100        # Get 100 K-lines
    )

    print(f"Got {len(bars)} K-lines")
    for bar in bars[:5]:
        print(f"{bar['datetime']} - "
              f"O:{bar['open']} "
              f"H:{bar['high']} "
              f"L:{bar['low']} "
              f"C:{bar['close']} "
              f"V:{bar['vol']}")`,
    tableTitle: 'K-line Type Codes',
    tableCols: ['Code', 'Type', 'Description'],
    tableData: [
      { code: '4', type: 'Daily', description: 'Daily K-line data' },
      { code: '5', type: 'Weekly', description: 'Weekly K-line data' },
      { code: '6', type: 'Monthly', description: 'Monthly K-line data' },
      { code: '7', type: '5min', description: '5-minute K-line' },
      { code: '8', type: '15min', description: '15-minute K-line' },
      { code: '9', type: '30min', description: '30-minute K-line' },
      { code: '10', type: '60min', description: '60-minute K-line' }
    ]
  },
  {
    title: 'Get Stock List',
    subtitle: 'get_security_list() - Get market stock list',
    code: `from pytdx.hq import TdxHq_API

api = TdxHq_API()
with api.connect('119.147.212.81', 7709):
    # Get Shenzhen A-share list
    # Market: 0-Shenzhen, 1-Shanghai
    # Type: 0-Stock, 1-Index, 2-Fund
    sz_stocks = api.get_security_list(market=0, start=0)

    print(f"Shenzhen stocks: {len(sz_stocks)}")
    for stock in sz_stocks[:10]:
        print(f"{stock['code']} - {stock['name']}")

    # Get Shanghai A-share list
    sh_stocks = api.get_security_list(market=1, start=0)
    print(f"\\nShanghai stocks: {len(sh_stocks)}")`
  },
  {
    title: 'Batch Get Data',
    subtitle: 'Batch fetch K-line data for multiple stocks',
    code: `from pytdx.hq import TdxHq_API
import pandas as pd

def get_multiple_stocks_kline(codes, count=100):
    result = {}

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        for market, code in codes:
            try:
                bars = api.get_security_bars(
                    category=4,  # Daily K-line
                    market=market,
                    code=code,
                    start=0,
                    count=count
                )

                df = pd.DataFrame(bars)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)

                result[code] = df
                print(f"Got {code}: {len(df)} records")

            except Exception as e:
                print(f"Failed {code}: {e}")

    return result

# Usage
stocks = [
    (0, '000001'),  # Ping An Bank
    (1, '600000'),  # SPD Bank
    (1, '600036')   # China Merchants Bank
]

data = get_multiple_stocks_kline(stocks, count=200)`
  }
]

const toggleAccordion = (index) => {
  activeAccordion.value = activeAccordion.value === index ? -1 : index
}
</script>

<style scoped lang="scss">
@import './styles/TdxpyDemo.scss';
</style>
