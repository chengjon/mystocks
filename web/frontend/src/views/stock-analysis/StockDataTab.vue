<template>
    <ArtDecoCard v-show="activeTab === 'data'" class="monolithic-data-card" variant="bordered">
      <template #header>
        <ArtDecoHeader 
          title="通达信数据解析" 
          subtitle="TONGDAXIN DATA PARSING" 
          showStatus 
          statusText="已集成" 
        />
      </template>

      <div class="content-section">
        <section class="data-group">
          <ArtDecoHeader title="通达信数据文件格式" subtitle="DATA FILE FORMATS" />
          <p class="description">通达信将股票数据存储为二进制文件, 不同周期对应不同的文件扩展名:</p>

          <el-table :data="fileFormatData" class="obsidian-table data-table-spaced">
            <el-table-column prop="type" label="数据类型" width="120" />
            <el-table-column prop="extension" label="文件扩展名" width="120" />
            <el-table-column prop="recordSize" label="记录大小" width="120" />
            <el-table-column prop="description" label="说明" />
          </el-table>
        </section>

        <section class="data-group">
          <ArtDecoHeader title="日线数据结构 (.day 文件)" subtitle="DAILY DATA STRUCTURE" />
          <p class="description">每条日K线记录占用 32 字节, 结构如下:</p>

          <el-table :data="dayStructureData" class="obsidian-table data-table-spaced">
            <el-table-column prop="offset" label="偏移量" width="100" />
            <el-table-column prop="size" label="字节数" width="100" />
            <el-table-column prop="type" label="数据类型" width="120" />
            <el-table-column prop="field" label="字段名" width="120" />
            <el-table-column prop="description" label="说明" />
          </el-table>
        </section>

        <section class="data-group">
          <ArtDecoHeader title="数据解析代码示例" subtitle="CODE EXAMPLES" />
          <el-tabs type="border-card" class="artdeco-tabs tabs-spaced">
            <el-tab-pane label="日线数据解析" name="daily">
              <textarea readonly class="code-block" v-text="dayParserCode"></textarea>
            </el-tab-pane>

            <el-tab-pane label="分钟线数据解析" name="minute">
              <textarea readonly class="code-block">
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
    return df</textarea>
            </el-tab-pane>

            <el-tab-pane label="批量读取" name="batch">
              <textarea readonly class="code-block">
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
print(f"深圳市场: {len(sz_stocks)} 只股票")</textarea>
            </el-tab-pane>
          </el-tabs>
        </section>

        <el-alert
          type="warning"
          title="⚠️ 注意事项"
          :closable="false"
          class="artdeco-alert artdeco-alert-spaced"
        >
          <ul class="alert-list">
            <li><strong>数据路径</strong>: 需要正确配置通达信数据目录路径</li>
            <li><strong>文件编码</strong>: 通达信数据为小端序 (little-endian)</li>
            <li><strong>价格处理</strong>: 价格数据需要除以 100 转换为实际价格</li>
            <li><strong>日期格式</strong>: 日期存储为整数, 需要转换为 datetime 对象</li>
            <li><strong>数据完整性</strong>: 检查文件大小是否为 32 的整数倍</li>
          </ul>
        </el-alert>
      </div>
    </ArtDecoCard>
</template>

<script setup lang="ts">
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'

interface FileFormatItem {
  type: string
  extension: string
  recordSize: string
  description: string
}

interface DayStructureItem {
  offset: string
  size: string
  type: string
  field: string
  description: string
}

const props = defineProps<{
  activeTab: string
  fileFormatData: FileFormatItem[]
  dayStructureData: DayStructureItem[]
  dayParserCode: string
}>()

// Expose props for template usage
const { activeTab, fileFormatData, dayStructureData, dayParserCode } = props
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.monolithic-data-card {
  border-color: var(--artdeco-border-default); // 30% transparency by token
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-8);
  padding: var(--artdeco-spacing-4);
}

.data-group {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
}

.description {
  color: var(--artdeco-fg-muted);
  font-family: var(--font-body);
  margin: 0;
}

/* Obsidian Table Theme */
.obsidian-table {
  --el-table-bg-color: var(--artdeco-bg-global);
  --el-table-tr-bg-color: var(--artdeco-bg-global);
  --el-table-header-bg-color: var(--artdeco-bg-card);
  --el-table-border-color: var(--artdeco-border-default);
  --el-table-text-color: var(--artdeco-fg-primary);
  --el-table-header-text-color: var(--artdeco-gold-primary);
  --el-table-row-hover-bg-color: var(--artdeco-gold-opacity-05);
  
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);

  :deep(.el-table__cell) {
    border-bottom: 1px solid var(--artdeco-border-default);
    font-family: var(--font-mono) !important;
    font-variant-numeric: tabular-nums;
  }

  :deep(th.el-table__cell) {
    font-family: var(--font-display) !important;
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
  }
}

.data-table-spaced,
.tabs-spaced {
  margin-top: var(--artdeco-spacing-4);
}

.artdeco-alert-spaced {
  margin-top: var(--artdeco-spacing-6);
}

.artdeco-tabs {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  
  :deep(.el-tabs__header) {
    background-color: var(--artdeco-bg-global);
    border-bottom: 1px solid var(--artdeco-border-default);
  }
  
  :deep(.el-tabs__item) {
    color: var(--artdeco-fg-muted);
    font-family: var(--font-display);
    text-transform: uppercase;
    
    &.is-active {
      color: var(--artdeco-gold-primary);
      background-color: var(--artdeco-bg-card);
    }
  }
}

.code-block {
  width: 100%;
  height: calc(var(--artdeco-spacing-32) * 2 + var(--artdeco-spacing-10));
  background-color: var(--artdeco-bg-global);
  color: var(--artdeco-gold-primary);
  border: 1px solid var(--artdeco-border-default);
  padding: var(--artdeco-spacing-4);
  font-family: var(--font-mono);
  font-size: var(--artdeco-text-sm);
  line-height: 1.5;
  resize: vertical;
  outline: none;
}

.artdeco-alert {
  background-color: var(--artdeco-gold-opacity-05);
  border: 1px solid var(--artdeco-gold-dim);
  color: var(--artdeco-gold-primary);
  
  :deep(.el-alert__title) {
    font-family: var(--font-display);
    font-weight: 700;
  }
}

.alert-list {
  margin: var(--artdeco-spacing-2) 0 0 0;
  padding-left: var(--artdeco-spacing-4);
  
  li {
    margin-bottom: var(--artdeco-spacing-1);
    
    strong {
      color: var(--artdeco-gold-light);
    }
  }
}
</style>
