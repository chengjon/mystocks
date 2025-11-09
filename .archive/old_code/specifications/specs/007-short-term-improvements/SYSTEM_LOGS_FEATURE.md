# 系统运行日志功能说明

**功能编号**: Feature 007 补充 - System Logs
**版本**: v1.0
**创建日期**: 2025-10-16
**状态**: ✅ 已完成

---

## 📋 功能概述

在系统设置中新增**运行日志**标签页，提供系统运行日志的查询和筛选功能。用户可以查看所有日志，也可以通过筛选按钮只查看有问题的日志（WARNING/ERROR/CRITICAL级别）。

### 核心功能

1. **日志查询** - 查看系统运行日志，记录关键操作点
2. **问题筛选** - 一键筛选有问题的日志
3. **多维筛选** - 按级别、分类、时间等维度筛选
4. **日志统计** - 查看日志分布和趋势统计

---

## 🌐 API端点

### 1. GET /api/system/logs

获取系统运行日志列表

**请求参数:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| filter_errors | boolean | 否 | false | 是否只显示有问题的日志 (WARNING/ERROR/CRITICAL) |
| limit | integer | 否 | 100 | 返回条数限制 (1-1000) |
| offset | integer | 否 | 0 | 偏移量，用于分页 |
| level | string | 否 | null | 日志级别筛选 (INFO/WARNING/ERROR/CRITICAL) |
| category | string | 否 | null | 日志分类筛选 (database/api/adapter/system) |

**响应示例:**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "timestamp": "2025-10-16T10:30:00",
      "level": "INFO",
      "category": "database",
      "operation": "数据库连接",
      "message": "MySQL数据库连接成功",
      "details": {
        "host": "localhost",
        "port": 3306
      },
      "duration_ms": 125,
      "has_error": false
    },
    {
      "id": 2,
      "timestamp": "2025-10-16T10:28:00",
      "level": "ERROR",
      "category": "adapter",
      "operation": "数据获取",
      "message": "AkShare适配器获取财务数据失败",
      "details": {
        "symbol": "600519",
        "error": "Connection timeout"
      },
      "duration_ms": 5000,
      "has_error": true
    }
  ],
  "total": 150,
  "filtered": 2,
  "timestamp": "2025-10-16T10:35:00"
}
```

### 2. GET /api/system/logs/summary

获取日志统计摘要

**响应示例:**

```json
{
  "success": true,
  "data": {
    "total_logs": 150,
    "level_counts": {
      "INFO": 120,
      "WARNING": 20,
      "ERROR": 8,
      "CRITICAL": 2
    },
    "category_counts": {
      "database": 45,
      "api": 60,
      "adapter": 30,
      "system": 15
    },
    "recent_errors_1h": 10,
    "last_update": "2025-10-16T10:35:00"
  },
  "timestamp": "2025-10-16T10:35:00"
}
```

---

## 📊 日志数据结构

### SystemLog 模型

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 日志ID |
| timestamp | string | 时间戳 (ISO 8601格式) |
| level | string | 日志级别 (INFO/WARNING/ERROR/CRITICAL) |
| category | string | 日志分类 (database/api/adapter/system) |
| operation | string | 操作名称 |
| message | string | 日志消息 |
| details | object | 详细信息 (可选) |
| duration_ms | integer | 操作耗时 (毫秒，可选) |
| has_error | boolean | 是否为问题日志 |

### 日志级别说明

| 级别 | 说明 | 示例 |
|------|------|------|
| **INFO** | 正常运行信息 | 数据库连接成功、API请求成功 |
| **WARNING** | 警告信息，需要关注 | 查询响应时间过长、API请求频率过高 |
| **ERROR** | 错误信息，需要处理 | 数据获取失败、连接超时 |
| **CRITICAL** | 严重错误，需要立即处理 | 数据库连接失败、服务崩溃 |

### 日志分类说明

| 分类 | 说明 | 示例操作 |
|------|------|---------|
| **database** | 数据库相关 | 连接、查询、事务 |
| **api** | API请求相关 | HTTP请求、响应、认证 |
| **adapter** | 数据适配器相关 | 数据获取、格式转换 |
| **system** | 系统级别 | 启动、停止、配置 |

---

## 🔍 使用示例

### 1. 基本查询

```bash
# 获取所有日志
curl http://localhost:8000/api/system/logs

# 获取最新10条日志
curl http://localhost:8000/api/system/logs?limit=10
```

### 2. 问题日志筛选

```bash
# 只获取有问题的日志 (筛选按钮功能)
curl http://localhost:8000/api/system/logs?filter_errors=true

# 等价于按级别筛选
curl http://localhost:8000/api/system/logs?level=WARNING
curl http://localhost:8000/api/system/logs?level=ERROR
curl http://localhost:8000/api/system/logs?level=CRITICAL
```

### 3. 分类筛选

```bash
# 只看数据库相关日志
curl http://localhost:8000/api/system/logs?category=database

# 只看API请求日志
curl http://localhost:8000/api/system/logs?category=api

# 只看适配器日志
curl http://localhost:8000/api/system/logs?category=adapter
```

### 4. 组合筛选

```bash
# 数据库相关的错误日志
curl http://localhost:8000/api/system/logs?category=database&level=ERROR

# 最近20条问题日志
curl http://localhost:8000/api/system/logs?filter_errors=true&limit=20
```

### 5. 分页查询

```bash
# 第一页 (每页20条)
curl http://localhost:8000/api/system/logs?limit=20&offset=0

# 第二页
curl http://localhost:8000/api/system/logs?limit=20&offset=20

# 第三页
curl http://localhost:8000/api/system/logs?limit=20&offset=40
```

### 6. 统计信息

```bash
# 获取日志统计摘要
curl http://localhost:8000/api/system/logs/summary
```

---

## 💻 前端实现建议

### UI设计

```vue
<template>
  <div class="system-logs">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button
        :type="filterErrors ? 'danger' : 'default'"
        @click="toggleFilter"
        icon="el-icon-warning"
      >
        {{ filterErrors ? '显示全部日志' : '只看问题日志' }}
      </el-button>

      <el-select v-model="selectedLevel" placeholder="日志级别" clearable>
        <el-option label="INFO" value="INFO"></el-option>
        <el-option label="WARNING" value="WARNING"></el-option>
        <el-option label="ERROR" value="ERROR"></el-option>
        <el-option label="CRITICAL" value="CRITICAL"></el-option>
      </el-select>

      <el-select v-model="selectedCategory" placeholder="日志分类" clearable>
        <el-option label="数据库" value="database"></el-option>
        <el-option label="API" value="api"></el-option>
        <el-option label="适配器" value="adapter"></el-option>
        <el-option label="系统" value="system"></el-option>
      </el-select>

      <el-button @click="refreshLogs" icon="el-icon-refresh">刷新</el-button>
    </div>

    <!-- 日志统计 -->
    <div class="log-summary">
      <el-card>
        <div class="summary-item">
          <span>总日志数:</span>
          <strong>{{ summary.total_logs }}</strong>
        </div>
        <div class="summary-item">
          <span>最近错误:</span>
          <strong class="error">{{ summary.recent_errors_1h }}</strong>
        </div>
      </el-card>
    </div>

    <!-- 日志列表 -->
    <el-table :data="logs" stripe>
      <el-table-column prop="timestamp" label="时间" width="180">
        <template slot-scope="scope">
          {{ formatTime(scope.row.timestamp) }}
        </template>
      </el-table-column>

      <el-table-column prop="level" label="级别" width="100">
        <template slot-scope="scope">
          <el-tag
            :type="getLevelType(scope.row.level)"
            size="small"
          >
            {{ scope.row.level }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="category" label="分类" width="100">
        <template slot-scope="scope">
          <el-tag size="small">{{ scope.row.category }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="operation" label="操作" width="150"></el-table-column>
      <el-table-column prop="message" label="消息"></el-table-column>

      <el-table-column prop="duration_ms" label="耗时" width="100">
        <template slot-scope="scope">
          <span v-if="scope.row.duration_ms">
            {{ scope.row.duration_ms }}ms
          </span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="100">
        <template slot-scope="scope">
          <el-button
            type="text"
            size="small"
            @click="showDetails(scope.row)"
          >
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-sizes="[20, 50, 100, 200]"
      :page-size="pageSize"
      :total="totalLogs"
      layout="total, sizes, prev, pager, next, jumper"
    >
    </el-pagination>
  </div>
</template>

<script>
export default {
  data() {
    return {
      logs: [],
      summary: {},
      filterErrors: false,
      selectedLevel: null,
      selectedCategory: null,
      currentPage: 1,
      pageSize: 20,
      totalLogs: 0
    }
  },
  methods: {
    async fetchLogs() {
      const params = {
        limit: this.pageSize,
        offset: (this.currentPage - 1) * this.pageSize,
        filter_errors: this.filterErrors
      }

      if (this.selectedLevel) params.level = this.selectedLevel
      if (this.selectedCategory) params.category = this.selectedCategory

      const response = await this.$http.get('/api/system/logs', { params })
      this.logs = response.data.data
      this.totalLogs = response.data.total
    },

    async fetchSummary() {
      const response = await this.$http.get('/api/system/logs/summary')
      this.summary = response.data.data
    },

    toggleFilter() {
      this.filterErrors = !this.filterErrors
      this.currentPage = 1
      this.fetchLogs()
    },

    refreshLogs() {
      this.fetchLogs()
      this.fetchSummary()
    },

    getLevelType(level) {
      const types = {
        'INFO': 'info',
        'WARNING': 'warning',
        'ERROR': 'danger',
        'CRITICAL': 'danger'
      }
      return types[level] || 'info'
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN')
    },

    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.fetchLogs()
    },

    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchLogs()
    },

    showDetails(row) {
      this.$alert(
        JSON.stringify(row.details, null, 2),
        '日志详情',
        { confirmButtonText: '确定' }
      )
    }
  },
  mounted() {
    this.fetchLogs()
    this.fetchSummary()

    // 自动刷新 (每30秒)
    this.autoRefreshTimer = setInterval(() => {
      this.fetchLogs()
      this.fetchSummary()
    }, 30000)
  },
  beforeDestroy() {
    if (this.autoRefreshTimer) {
      clearInterval(this.autoRefreshTimer)
    }
  }
}
</script>
```

---

## 🗄️ 数据来源

### 数据库模式

日志数据来自 PostgreSQL 监控数据库 `mystocks_monitoring` 的 `operation_log` 表：

```sql
-- operation_log 表结构
CREATE TABLE operation_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(20),           -- 映射到 level
    operation_type VARCHAR(50),   -- 映射到 category
    operation VARCHAR(100),
    message TEXT,
    error_message TEXT,
    execution_time_ms INTEGER,    -- 映射到 duration_ms
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 数据映射关系

| operation_log字段 | SystemLog字段 | 说明 |
|-------------------|---------------|------|
| id | id | 日志ID |
| timestamp | timestamp | 时间戳 |
| status | level | 状态映射到级别 |
| operation_type | category | 操作类型映射到分类 |
| operation | operation | 操作名称 |
| error_message / message | message | 消息内容 |
| execution_time_ms | duration_ms | 执行时间 |
| status in ('failed','error') | has_error | 是否错误 |

### 备用模式

如果数据库不可用，系统会自动返回模拟日志数据，确保功能正常演示。

---

## 🧪 测试

### 运行测试脚本

```bash
# 确保Backend服务正在运行
cd web/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 在另一个终端运行测试
python utils/test_logs_api.py
```

### 测试覆盖

测试脚本包含6个测试用例:

1. ✅ 获取所有日志
2. ✅ 筛选问题日志 (filter_errors=true)
3. ✅ 按级别筛选 (level=ERROR)
4. ✅ 按分类筛选 (category=database)
5. ✅ 分页功能 (limit/offset)
6. ✅ 日志统计摘要

### 手动测试

```bash
# 1. 访问Swagger文档
open http://localhost:8000/docs

# 2. 测试日志端点
# 找到 "system" 标签下的:
# - GET /api/system/logs
# - GET /api/system/logs/summary

# 3. 点击 "Try it out" 并测试各种参数组合
```

---

## 📝 更新记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2025-10-16 | v1.0 | 初始版本，实现基本日志查询和筛选功能 |

---

## 🎯 后续优化建议

### 短期 (1-2周)
- [ ] 添加日志导出功能 (CSV/Excel)
- [ ] 实现日志搜索功能 (关键词搜索)
- [ ] 添加日志详情弹窗

### 中期 (1个月)
- [ ] 实现日志实时推送 (WebSocket)
- [ ] 添加日志图表可视化
- [ ] 实现日志归档和清理策略

### 长期 (3个月)
- [ ] 集成ELK栈 (Elasticsearch + Logstash + Kibana)
- [ ] 实现分布式日志收集
- [ ] 添加日志分析和告警

---

**文档版本**: v1.0
**最后更新**: 2025-10-16
**维护者**: MyStocks开发团队
