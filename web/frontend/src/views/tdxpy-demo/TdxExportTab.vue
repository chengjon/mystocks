<template>
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
          <el-tab-pane name="export-csv" label="导出到 CSV">
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

          <el-tab-pane name="export-db" label="导出到数据库">
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

          <el-tab-pane name="scheduled-update" label="定时更新">
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
</template>

<script setup lang="ts">
defineProps<{ activeTab: string }>()
</script>
