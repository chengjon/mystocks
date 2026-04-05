<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">📂 通达信数据解析</span>
      <span class="badge badge-success">已集成</span>
    </div>

    <div class="content-section">
      <div class="section">
        <h3>📁 通达信数据文件格式</h3>
        <p>通达信将股票数据存储为二进制文件,不同周期对应不同的文件扩展名:</p>

        <table class="table table-spacing">
          <thead>
            <tr>
              <th width="120">数据类型</th>
              <th width="120">文件扩展名</th>
              <th width="120">记录大小</th>
              <th>说明</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in fileFormatData" :key="index">
              <td>{{ item.type }}</td>
              <td><code>{{ item.extension }}</code></td>
              <td>{{ item.recordSize }}</td>
              <td>{{ item.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section">
        <h3>🔢 日线数据结构 (.day 文件)</h3>
        <p>每条日K线记录占用 32 字节,结构如下:</p>

        <table class="table table-spacing">
          <thead>
            <tr>
              <th width="100">偏移量</th>
              <th width="100">字节数</th>
              <th width="120">数据类型</th>
              <th width="120">字段名</th>
              <th>说明</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in dayStructureData" :key="index">
              <td><code>{{ item.offset }}</code></td>
              <td>{{ item.size }}</td>
              <td>{{ item.type }}</td>
              <td><code>{{ item.field }}</code></td>
              <td>{{ item.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section">
        <h3>💻 数据解析代码示例</h3>
        <div class="tabs">
          <div class="tab-headers">
            <button
              v-for="(label, key) in tabLabels"
              :key="key"
              class="tab-btn"
              :class="{ active: activeTab === key }"
              @click="activeTab = key"
            >
              {{ label }}
            </button>
          </div>
          <div class="tab-content">
            <textarea readonly class="code-block" :value="codeExamples[activeTab]"></textarea>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="alert-card">
          <div class="alert-content">
            <strong>⚠️ 注意事项</strong>
            <ul class="warning-list">
              <li><strong>数据路径</strong>: 需要正确配置通达信数据目录路径</li>
              <li><strong>文件编码</strong>: 通达信数据为小端序 (little-endian)</li>
              <li><strong>价格处理</strong>: 价格数据需要除以 100 转换为实际价格</li>
              <li><strong>日期格式</strong>: 日期存储为整数,需要转换为 datetime 对象</li>
              <li><strong>数据完整性</strong>: 检查文件大小是否为 32 的整数倍</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { FILE_FORMAT_DATA, DAY_STRUCTURE_DATA } from '../config'
import { DAY_PARSER_CODE, MINUTE_PARSER_CODE, BATCH_LOAD_CODE } from '../code-examples'

const fileFormatData = FILE_FORMAT_DATA
const dayStructureData = DAY_STRUCTURE_DATA

const activeTab = ref('day')

const tabLabels = {
  day: '日线数据解析',
  minute: '分钟线数据解析',
  batch: '批量读取'
}

const codeExamples = computed<Record<string, string>>(() => ({
  day: DAY_PARSER_CODE,
  minute: MINUTE_PARSER_CODE,
  batch: BATCH_LOAD_CODE
}))
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.content-section {
  padding: var(--artdeco-spacing-3) 0;
  line-height: 1.8;
}

.section {
  margin-bottom: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    margin: 0 0 calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) 0;
    padding-left: var(--artdeco-spacing-3);
    border-left: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    font-size: calc(var(--artdeco-text-base) + (var(--artdeco-spacing-px) * 2));
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wide);
  }

  p {
    margin: 0;
    color: var(--artdeco-fg-muted);
  }
}

.table-spacing {
  margin-top: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
}

.tabs {
  margin-top: var(--artdeco-spacing-5);
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
}

.tab-headers {
  display: flex;
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent);
}

.tab-btn {
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
  border: none;
  border-right: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent);
  background: none;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  cursor: pointer;
  transition:
    background var(--artdeco-transition-quick) var(--artdeco-ease-out),
    color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:last-child {
    border-right: none;
  }

  &:hover {
    background: var(--artdeco-bg-elevated);
  }

  &.active {
    background: var(--artdeco-bg-global);
    color: var(--artdeco-gold-primary);
    font-weight: var(--artdeco-font-medium);
  }
}

.tab-content {
  background: var(--artdeco-bg-global);
}

.code-block {
  display: block;
  width: 100%;
  min-height: calc((var(--artdeco-spacing-20) * 4) + var(--artdeco-spacing-10));
  padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  overflow-x: auto;
  resize: vertical;
  white-space: pre;
  border: none;
  border-radius: var(--artdeco-radius-none);
  background: var(--artdeco-bg-elevated);
  color: var(--artdeco-fg-primary);
  font-family: var(--font-mono);
  font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
  line-height: 1.6;
}

.alert-card {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
}

.alert-content {
  padding: var(--artdeco-spacing-4);

  strong {
    display: block;
    margin-bottom: calc(var(--artdeco-spacing-3) - (var(--artdeco-spacing-px) * 2));
    color: var(--artdeco-fg-primary);
  }
}

.warning-list {
  margin: 0;
  padding-left: var(--artdeco-spacing-5);
  color: var(--artdeco-fg-muted);

  li {
    margin: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2)) 0;

    strong {
      color: var(--artdeco-fg-primary);
      font-weight: var(--artdeco-font-semibold);
    }
  }
}
</style>
