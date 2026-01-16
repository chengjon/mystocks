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

        <table class="table" style="margin-top: 15px;">
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

        <table class="table" style="margin-top: 15px;">
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

.content-section {
  padding: 10px 0;
  line-height: 1.8;
}

.section {
  margin-bottom: 30px;

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    margin: 0 0 15px 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--primary);
    border-left: 3px solid var(--primary);
    padding-left: 12px;
  }

  p {
    margin: 0;
    color: var(--text-secondary);
  }
}

.tabs {
  margin-top: 20px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.tab-headers {
  display: flex;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
}

.tab-btn {
  padding: 12px 24px;
  background: none;
  border: none;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  border-right: 1px solid var(--border);

  &:last-child {
    border-right: none;
  }

  &:hover {
    background: var(--bg-dark);
  }

  &.active {
    background: var(--bg-primary);
    color: var(--primary);
    font-weight: 500;
  }
}

.tab-content {
  background: var(--bg-primary);
}

.code-block {
  display: block;
  background: var(--bg-dark);
  border: none;
  border-radius: 0;
  padding: 15px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre;
  color: var(--text-primary);
  width: 100%;
  min-height: 400px;
  resize: vertical;
}

.alert-content {
  strong {
    display: block;
    margin-bottom: 10px;
    color: var(--text-primary);
  }
}

.warning-list {
  margin: 0;
  padding-left: 20px;
  color: var(--text-secondary);

  li {
    margin: 6px 0;

    strong {
      color: var(--text-primary);
      font-weight: 600;
    }
  }
}
</style>
