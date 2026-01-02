# 数据源管理工具使用指南

> **版本**: v1.0
> **日期**: 2026-01-02
> **状态**: ✅ 生产就绪

本指南提供数据源管理V2.0工具的完整使用说明，包括手动测试工具和FastAPI管理接口。

---

## 目录

1. [工具概览](#工具概览)
2. [手动测试工具](#手动测试工具)
3. [FastAPI管理接口](#fastapi管理接口)
4. [Web集成示例](#web集成示例)
5. [故障排除](#故障排除)

---

## 工具概览

数据源管理V2.0提供两个主要工具：

| 工具 | 用途 | 文件位置 |
|------|------|----------|
| **手动测试工具** | 命令行交互式测试，数据质量分析 | `scripts/tools/manual_data_source_tester.py` |
| **FastAPI管理接口** | RESTful API，支持搜索、测试、配置更新 | `web/backend/app/api/data_source_registry.py` |

**核心功能**：
- ✅ 数据源搜索和筛选（5层分类、关键词搜索）
- ✅ 手动测试和数据质量分析
- ✅ 健康检查（单个/批量）
- ✅ 配置更新（优先级、质量评分、状态）
- ✅ 分类统计和监控

---

## 手动测试工具

### 快速开始

```bash
# 交互式模式
python scripts/tools/manual_data_source_tester.py --interactive

# 命令行模式
python scripts/tools/manual_data_source_tester.py \
    --endpoint akshare.stock_zh_a_hist \
    --symbol 000001 \
    --start-date 20240101 \
    --end-date 20240131 \
    --verbose
```

### 1. 交互式模式

交互式模式提供友好的菜单导航，适合探索性测试。

**启动命令**:
```bash
python scripts/tools/manual_data_source_tester.py --interactive
```

**操作流程**:
1. 查看可用数据源（按分类分组）
2. 选择要测试的数据源接口
3. 输入测试参数（JSON格式或使用默认参数）
4. 查看测试结果和数据质量分析
5. 生成测试报告（可选）

**示例交互**:
```
╔══════════════════════════════════════════════════════╗
║       MyStocks 数据源手动测试工具 v1.0              ║
╚══════════════════════════════════════════════════════╝

✅ 已加载 6 个数据源接口

📂 按分类分组 (共2个分类):

[1] DAILY_KLINE (2个接口):
    [1] akshare.stock_zh_a_hist
    [2] tushare.daily

[2] FINANCIAL_DATA (4个接口):
    [1] akshare.stock_financial_analysis
    [2] akshare.stock_profit_sheet
    ... 还有 2 个接口

请选择:
  [1-2] 按分类选择
  [0] 直接输入接口名称
  [q] 退出

请输入选择: 1

DAILY_KLINE 的接口列表:
  [1] akshare.stock_zh_a_hist
  [2] tushare.daily

请选择接口编号 [1-2]: 1

🔧 请输入测试参数
   格式: JSON格式的参数字典
   示例: {"symbol": "000001", "start_date": "20240101", "end_date": "20240131"}

请输入参数 (留空使用默认参数):
```

**输出示例**:
```
============================================================
测试数据源: akshare.stock_zh_a_hist
============================================================

📋 接口配置:
   数据源: akshare
   数据分类: DAILY_KLINE
   目标数据库: PostgreSQL
   质量评分: 8.5
   健康状态: healthy
   优先级: 1

🔧 测试参数:
   symbol: 000001
   start_date: 20240101
   end_date: 20240131

⏳ 正在调用接口...
✅ 调用成功
   响应时间: 1.234秒
   返回数据量: 22条

📊 数据预览:
    date    open   high    low  close  volume
 0 2024-01-01  10.50  10.80  10.45  10.75  123456
 1 2024-01-02  10.75  10.90  10.70  10.85  234567
 2 2024-01-03  10.85  11.00  10.80  10.95  345678

📈 数据质量分析:
   列完整性:
     date: ✅ 存在
     open: ✅ 存在
     high: ✅ 存在
     low: ✅ 存在
     close: ✅ 存在
     volume: ✅ 存在

   数据范围 (前5列):
     open:
       范围: 10.50 ~ 12.30
       均值: 11.40
       空值率: 0.00%
     close:
       范围: 10.75 ~ 12.50
       均值: 11.65
       空值率: 0.00%

   重复数据:
     ✅ 无重复

✅ 测试通过

是否继续测试其他接口？ [y/n]: n

是否保存测试报告？ [y/n]: y

✅ 测试报告已保存: docs/reports/data_source_test_report_20260102_143022.json
```

### 2. 命令行模式

命令行模式适合自动化测试和批量操作。

**基本用法**:
```bash
python scripts/tools/manual_data_source_tester.py \
    --endpoint <接口名称> \
    [--symbol <股票代码>] \
    [--start-date <开始日期>] \
    [--end-date <结束日期>] \
    [--params <JSON参数>] \
    [--verbose] \
    [--report]
```

**参数说明**:
| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--endpoint` | `-e` | 接口名称（必需） | `akshare.stock_zh_a_hist` |
| `--symbol` | `-s` | 股票代码 | `000001` |
| `--start-date` | | 开始日期 (YYYYMMDD) | `20240101` |
| `--end-date` | | 结束日期 (YYYYMMDD) | `20240131` |
| `--params` | `-p` | 额外参数 (JSON格式) | `'{"period":"daily"}'` |
| `--verbose` | `-v` | 详细输出 | - |
| `--report` | `-r` | 生成测试报告文件 | - |
| `--interactive` | `-i` | 交互式模式 | - |

**使用示例**:

**示例1**: 测试日线数据接口
```bash
python scripts/tools/manual_data_source_tester.py \
    --endpoint akshare.stock_zh_a_hist \
    --symbol 600519 \
    --start-date 20240101 \
    --end-date 20240131 \
    --verbose
```

**示例2**: 使用自定义JSON参数
```bash
python scripts/tools/manual_data_source_tester.py \
    --endpoint akshare.stock_zh_a_hist \
    --params '{"symbol":"000001","period":"daily","adjust":"qfq"}' \
    --report
```

**示例3**: 快速测试（不显示详细信息）
```bash
python scripts/tools/manual_data_source_tester.py \
    --endpoint akshare.stock_financial_analysis \
    --symbol 000001 \
    --params '{"report_type":"profit"}'
```

### 3. 数据质量分析

测试工具自动执行以下数据质量检查：

**检查项**:
1. **列完整性**: 检查配置的参数列是否在返回数据中存在
2. **数据范围**: 统计数值列的最小值、最大值、均值、空值率
3. **重复数据**: 检测并统计重复数据量
4. **类型一致性**: 验证数据类型是否匹配预期

**质量指标**:
```python
{
    'has_data': True,           # 是否有数据
    'is_empty': False,          # 是否为空
    'column_completeness': {    # 列完整性
        'date': {'present': True, 'status': 'exists'},
        'close': {'present': True, 'status': 'exists'}
    },
    'data_range': {             # 数据范围
        'close': {
            'min': 10.50,
            'max': 12.30,
            'mean': 11.40,
            'null_count': 0,
            'null_rate': 0.0
        }
    },
    'duplicate_check': {        # 重复检查
        'duplicate_count': 0,
        'duplicate_rate': 0.0
    }
}
```

### 4. 测试报告

测试报告以JSON格式保存，包含以下信息：

**报告结构**:
```json
{
  "generated_at": "2026-01-02T14:30:22",
  "total_tests": 3,
  "successful_tests": 2,
  "failed_tests": 1,
  "tests": [
    {
      "endpoint_name": "akshare.stock_zh_a_hist",
      "success": true,
      "duration": 1.234,
      "row_count": 22,
      "quality_checks": {...},
      "start_time": "2026-01-02T14:28:00",
      "end_time": "2026-01-02T14:28:01.234"
    }
  ]
}
```

**查看报告**:
```bash
# 查看最新报告
cat docs/reports/data_source_test_report_*.json | jq .

# 或者使用Python查看
python -m json.tool docs/reports/data_source_test_report_20260102_143022.json
```

---

## FastAPI管理接口

### API概览

**Base URL**: `http://localhost:8000/api/v1/data-sources`

**端点列表**:
| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 搜索和筛选数据源 |
| `/categories` | GET | 获取分类统计信息 |
| `/{endpoint_name}` | GET | 获取单个数据源详情 |
| `/{endpoint_name}` | PUT | 更新数据源配置 |
| `/{endpoint_name}/test` | POST | 手动测试数据源 |
| `/{endpoint_name}/health-check` | POST | 健康检查单个数据源 |
| `/health-check/all` | POST | 健康检查所有数据源 |

**Swagger文档**: `http://localhost:8000/api/docs`
**ReDoc文档**: `http://localhost:8000/api/redoc`

### 1. 搜索数据源

**端点**: `GET /api/v1/data-sources/`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `data_category` | string | 否 | 5层数据分类 | `DAILY_KLINE` |
| `classification_level` | int | 否 | 分类层级(1-5) | `1` |
| `source_type` | string | 否 | 数据源类型 | `akshare` |
| `only_healthy` | boolean | 否 | 仅返回健康的 | `true` |
| `keyword` | string | 否 | 模糊搜索关键词 | `日线` |
| `status` | string | 否 | 数据源状态 | `active` (默认) |

**请求示例**:

```bash
# 搜索所有日线数据接口
curl -X GET "http://localhost:8000/api/v1/data-sources/?data_category=DAILY_KLINE" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索akshare数据源
curl -X GET "http://localhost:8000/api/v1/data-sources/?source_type=akshare" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 关键词搜索
curl -X GET "http://localhost:8000/api/v1/data-sources/?keyword=日线" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 仅搜索健康的接口
curl -X GET "http://localhost:8000/api/v1/data-sources/?only_healthy=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "total": 2,
  "data_sources": [
    {
      "endpoint_name": "akshare.stock_zh_a_hist",
      "source_name": "akshare",
      "data_category": "DAILY_KLINE",
      "classification_level": 1,
      "priority": 1,
      "health_status": "healthy",
      "data_quality_score": 8.5,
      "avg_response_time": 1.2,
      "description": "A股日线行情数据",
      "target_db": "PostgreSQL"
    },
    {
      "endpoint_name": "tushare.daily",
      "source_name": "tushare",
      "data_category": "DAILY_KLINE",
      "classification_level": 1,
      "priority": 2,
      "health_status": "healthy",
      "data_quality_score": 9.0,
      "avg_response_time": 0.8,
      "description": "日线行情数据",
      "target_db": "PostgreSQL"
    }
  ]
}
```

### 2. 获取分类统计

**端点**: `GET /api/v1/data-sources/categories`

**功能**: 获取所有5层数据分类的统计信息

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/data-sources/categories" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
[
  {
    "category": "DAILY_KLINE",
    "display_name": "日线K线数据",
    "total": 2,
    "healthy": 2,
    "unhealthy": 0,
    "avg_quality_score": 8.75,
    "avg_response_time": 1.0
  },
  {
    "category": "FINANCIAL_DATA",
    "display_name": "财务数据",
    "total": 4,
    "healthy": 3,
    "unhealthy": 1,
    "avg_quality_score": 7.8,
    "avg_response_time": 2.3
  }
]
```

### 3. 获取单个数据源详情

**端点**: `GET /api/v1/data-sources/{endpoint_name}`

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/data-sources/akshare.stock_zh_a_hist" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "endpoint_name": "akshare.stock_zh_a_hist",
  "source_name": "akshare",
  "data_category": "DAILY_KLINE",
  "classification_level": 1,
  "priority": 1,
  "health_status": "healthy",
  "data_quality_score": 8.5,
  "avg_response_time": 1.2,
  "description": "A股日线行情数据",
  "target_db": "PostgreSQL",
  "parameters": {
    "symbol": {"type": "string", "required": true, "description": "股票代码"},
    "start_date": {"type": "string", "required": true, "description": "开始日期"},
    "end_date": {"type": "string", "required": true, "description": "结束日期"}
  },
  "test_parameters": {
    "symbol": "000001",
    "start_date": "20240101",
    "end_date": "20240131"
  },
  "last_call": "2026-01-02T14:30:00",
  "call_count": 1250
}
```

### 4. 更新数据源配置

**端点**: `PUT /api/v1/data-sources/{endpoint_name}`

**请求体**:
```json
{
  "priority": 1,
  "data_quality_score": 9.0,
  "status": "active",
  "description": "更新后的描述"
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `priority` | int | 否 | 优先级(1-10)，数字越小优先级越高 |
| `data_quality_score` | float | 否 | 质量评分(0-10) |
| `status` | string | 否 | 状态: `active`/`maintenance`/`deprecated` |
| `description` | string | 否 | 描述信息 |

**请求示例**:
```bash
curl -X PUT "http://localhost:8000/api/v1/data-sources/akshare.stock_zh_a_hist" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "priority": 1,
    "data_quality_score": 9.0,
    "description": "高质量A股日线数据"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "配置已更新",
  "endpoint_name": "akshare.stock_zh_a_hist",
  "updated_fields": ["priority", "data_quality_score", "description"]
}
```

### 5. 手动测试数据源

**端点**: `POST /api/v1/data-sources/{endpoint_name}/test`

**请求体**:
```json
{
  "test_params": {
    "symbol": "000001",
    "start_date": "20240101",
    "end_date": "20240131"
  }
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/data-sources/akshare.stock_zh_a_hist/test" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "test_params": {
      "symbol": "000001",
      "start_date": "20240101",
      "end_date": "20240131"
    }
  }'
```

**响应示例** (成功):
```json
{
  "success": true,
  "endpoint_name": "akshare.stock_zh_a_hist",
  "test_params": {
    "symbol": "000001",
    "start_date": "20240101",
    "end_date": "20240131"
  },
  "duration": 1.234,
  "row_count": 22,
  "data_preview": [
    {"date": "2024-01-01", "open": 10.50, "close": 10.75},
    {"date": "2024-01-02", "open": 10.75, "close": 10.85},
    {"date": "2024-01-03", "open": 10.85, "close": 10.95}
  ],
  "quality_checks": {
    "has_data": true,
    "is_empty": false,
    "column_completeness": {...},
    "data_range": {...},
    "duplicate_check": {...}
  }
}
```

**响应示例** (失败):
```json
{
  "success": false,
  "endpoint_name": "akshare.stock_zh_a_hist",
  "test_params": {...},
  "duration": 0.456,
  "error": "Connection timeout"
}
```

### 6. 健康检查

**单个数据源健康检查**: `POST /api/v1/data-sources/{endpoint_name}/health-check`

```bash
curl -X POST "http://localhost:8000/api/v1/data-sources/akshare.stock_zh_a_hist/health-check" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**批量健康检查**: `POST /api/v1/data-sources/health-check/all`

```bash
curl -X POST "http://localhost:8000/api/v1/data-sources/health-check/all" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "timestamp": "2026-01-02T14:30:00",
  "total": 6,
  "healthy": 5,
  "unhealthy": 1,
  "results": [
    {
      "endpoint_name": "akshare.stock_zh_a_hist",
      "status": "healthy",
      "response_time": 1.2,
      "row_count": 22
    },
    {
      "endpoint_name": "tushare.profit",
      "status": "unhealthy",
      "error": "API key not configured"
    }
  ]
}
```

---

## Web集成示例

### 1. Vue.js前端集成

**安装依赖**:
```bash
npm install axios
```

**API服务模块** (`src/api/dataSourceService.js`):
```javascript
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const dataSourceService = {
  /**
   * 搜索数据源
   */
  async searchDataSources(filters = {}) {
    const params = new URLSearchParams()

    if (filters.dataCategory) params.append('data_category', filters.dataCategory)
    if (filters.sourceType) params.append('source_type', filters.sourceType)
    if (filters.onlyHealthy !== undefined) params.append('only_healthy', filters.onlyHealthy)
    if (filters.keyword) params.append('keyword', filters.keyword)
    if (filters.status) params.append('status', filters.status)

    const response = await axios.get(`${API_BASE_URL}/api/v1/data-sources/?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    return response.data
  },

  /**
   * 获取分类统计
   */
  async getCategoryStats() {
    const response = await axios.get(`${API_BASE_URL}/api/v1/data-sources/categories`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    return response.data
  },

  /**
   * 获取单个数据源详情
   */
  async getDataSource(endpointName) {
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/data-sources/${endpointName}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    return response.data
  },

  /**
   * 更新数据源配置
   */
  async updateDataSource(endpointName, updates) {
    const response = await axios.put(
      `${API_BASE_URL}/api/v1/data-sources/${endpointName}`,
      updates,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    return response.data
  },

  /**
   * 测试数据源
   */
  async testDataSource(endpointName, testParams) {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/data-sources/${endpointName}/test`,
      { test_params: testParams },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    return response.data
  },

  /**
   * 健康检查
   */
  async healthCheckAll() {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/data-sources/health-check/all`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    return response.data
  }
}

export default dataSourceService
```

**Vue组件示例** (`src/views/DataSourceManagement.vue`):
```vue
<template>
  <div class="data-source-management">
    <h2>数据源管理</h2>

    <!-- 搜索过滤器 -->
    <div class="filters">
      <el-form :inline="true">
        <el-form-item label="数据分类">
          <el-select v-model="filters.dataCategory" clearable placeholder="选择分类">
            <el-option label="日线K线" value="DAILY_KLINE" />
            <el-option label="分钟K线" value="MINUTE_KLINE" />
            <el-option label="财务数据" value="FINANCIAL_DATA" />
          </el-select>
        </el-form-item>

        <el-form-item label="数据源类型">
          <el-input v-model="filters.sourceType" placeholder="如: akshare" />
        </el-form-item>

        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索接口名称或描述" />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="filters.onlyHealthy">仅健康的</el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="searchDataSources">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 分类统计 -->
    <div class="category-stats">
      <el-card>
        <template #header>
          <span>分类统计</span>
          <el-button style="float: right" @click="loadCategoryStats">刷新</el-button>
        </template>

        <el-table :data="categoryStats" stripe>
          <el-table-column prop="display_name" label="分类" />
          <el-table-column prop="total" label="总数" />
          <el-table-column prop="healthy" label="健康" />
          <el-table-column prop="unhealthy" label="异常" />
          <el-table-column prop="avg_quality_score" label="平均质量分" />
          <el-table-column prop="avg_response_time" label="平均响应时间(s)" />
        </el-table>
      </el-card>
    </div>

    <!-- 数据源列表 -->
    <div class="data-sources-list">
      <el-table :data="dataSources" stripe>
        <el-table-column prop="endpoint_name" label="接口名称" width="300" />
        <el-table-column prop="source_name" label="数据源" width="120" />
        <el-table-column prop="data_category" label="分类" width="150" />
        <el-table-column prop="health_status" label="健康状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.health_status === 'healthy' ? 'success' : 'danger'">
              {{ scope.row.health_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="data_quality_score" label="质量评分" width="120" />
        <el-table-column prop="priority" label="优先级" width="100" />
        <el-table-column label="操作" width="300">
          <template #default="scope">
            <el-button size="small" @click="viewDetails(scope.row)">详情</el-button>
            <el-button size="small" type="primary" @click="testDataSource(scope.row)">
              测试
            </el-button>
            <el-button size="small" @click="editDataSource(scope.row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="数据源详情" width="70%">
      <div v-if="selectedDataSource">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="接口名称">
            {{ selectedDataSource.endpoint_name }}
          </el-descriptions-item>
          <el-descriptions-item label="数据源">
            {{ selectedDataSource.source_name }}
          </el-descriptions-item>
          <el-descriptions-item label="数据分类">
            {{ selectedDataSource.data_category }}
          </el-descriptions-item>
          <el-descriptions-item label="目标数据库">
            {{ selectedDataSource.target_db }}
          </el-descriptions-item>
          <el-descriptions-item label="健康状态">
            <el-tag :type="selectedDataSource.health_status === 'healthy' ? 'success' : 'danger'">
              {{ selectedDataSource.health_status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="质量评分">
            {{ selectedDataSource.data_quality_score }}
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            {{ selectedDataSource.priority }}
          </el-descriptions-item>
          <el-descriptions-item label="平均响应时间">
            {{ selectedDataSource.avg_response_time }}s
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ selectedDataSource.description }}
          </el-descriptions-item>
        </el-descriptions>

        <h4>测试参数</h4>
        <pre>{{ JSON.stringify(selectedDataSource.test_parameters, null, 2) }}</pre>
      </div>
    </el-dialog>

    <!-- 测试对话框 -->
    <el-dialog v-model="testDialogVisible" title="测试数据源" width="60%">
      <div v-if="selectedDataSource">
        <el-form :model="testParams">
          <el-form-item label="股票代码">
            <el-input v-model="testParams.symbol" />
          </el-form-item>
          <el-form-item label="开始日期">
            <el-input v-model="testParams.start_date" placeholder="YYYYMMDD" />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-input v-model="testParams.end_date" placeholder="YYYYMMDD" />
          </el-form-item>
        </el-form>

        <div v-if="testResult">
          <h4>测试结果</h4>
          <el-alert
            :type="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? '测试成功' : '测试失败'"
            show-icon
          />

          <div v-if="testResult.success">
            <p>响应时间: {{ testResult.duration }}秒</p>
            <p>返回数据量: {{ testResult.row_count }}条</p>

            <h5>数据预览</h5>
            <el-table :data="testResult.data_preview" stripe max-height="300">
              <el-table-column
                v-for="(value, key) in (testResult.data_preview[0] || {})"
                :key="key"
                :prop="key"
                :label="key"
              />
            </el-table>

            <h5>数据质量检查</h5>
            <pre>{{ JSON.stringify(testResult.quality_checks, null, 2) }}</pre>
          </div>

          <div v-else>
            <p>错误: {{ testResult.error }}</p>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="testDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="runTest">执行测试</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dataSourceService from '@/api/dataSourceService'

const filters = ref({
  dataCategory: '',
  sourceType: '',
  keyword: '',
  onlyHealthy: false
})

const categoryStats = ref([])
const dataSources = ref([])
const detailDialogVisible = ref(false)
const testDialogVisible = ref(false)
const selectedDataSource = ref(null)
const testParams = ref({})
const testResult = ref(null)

onMounted(() => {
  loadCategoryStats()
  searchDataSources()
})

async function loadCategoryStats() {
  try {
    categoryStats.value = await dataSourceService.getCategoryStats()
  } catch (error) {
    console.error('Failed to load category stats:', error)
  }
}

async function searchDataSources() {
  try {
    dataSources.value = await dataSourceService.searchDataSources(filters.value)
  } catch (error) {
    console.error('Failed to search data sources:', error)
  }
}

function resetFilters() {
  filters.value = {
    dataCategory: '',
    sourceType: '',
    keyword: '',
    onlyHealthy: false
  }
  searchDataSources()
}

function viewDetails(dataSource) {
  selectedDataSource.value = dataSource
  detailDialogVisible.value = true
}

function testDataSource(dataSource) {
  selectedDataSource.value = dataSource
  testParams.value = { ...dataSource.test_parameters }
  testResult.value = null
  testDialogVisible.value = true
}

async function runTest() {
  try {
    testResult.value = await dataSourceService.testDataSource(
      selectedDataSource.value.endpoint_name,
      testParams.value
    )
  } catch (error) {
    testResult.value = {
      success: false,
      error: error.message
    }
  }
}

function editDataSource(dataSource) {
  // TODO: 实现编辑功能
  console.log('Edit data source:', dataSource)
}
</script>

<style scoped>
.data-source-management {
  padding: 20px;
}

.filters {
  margin-bottom: 20px;
}

.category-stats {
  margin-bottom: 20px;
}

.data-sources-list {
  margin-top: 20px;
}
</style>
```

### 2. Python集成示例

```python
import requests
from typing import Dict, Any, List

class DataSourceClient:
    """数据源管理API客户端"""

    def __init__(self, base_url: str = "http://localhost:8000", token: str = None):
        self.base_url = base_url
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def search_data_sources(
        self,
        data_category: str = None,
        source_type: str = None,
        only_healthy: bool = False,
        keyword: str = None,
        status: str = "active"
    ) -> Dict[str, Any]:
        """搜索数据源"""
        params = {}
        if data_category:
            params["data_category"] = data_category
        if source_type:
            params["source_type"] = source_type
        if only_healthy:
            params["only_healthy"] = "true"
        if keyword:
            params["keyword"] = keyword
        if status:
            params["status"] = status

        response = requests.get(
            f"{self.base_url}/api/v1/data-sources/",
            params=params,
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()

    def get_category_stats(self) -> List[Dict[str, Any]]:
        """获取分类统计"""
        response = requests.get(
            f"{self.base_url}/api/v1/data-sources/categories",
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()

    def get_data_source(self, endpoint_name: str) -> Dict[str, Any]:
        """获取单个数据源详情"""
        response = requests.get(
            f"{self.base_url}/api/v1/data-sources/{endpoint_name}",
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()

    def update_data_source(
        self,
        endpoint_name: str,
        priority: int = None,
        data_quality_score: float = None,
        status: str = None,
        description: str = None
    ) -> Dict[str, Any]:
        """更新数据源配置"""
        data = {}
        if priority is not None:
            data["priority"] = priority
        if data_quality_score is not None:
            data["data_quality_score"] = data_quality_score
        if status:
            data["status"] = status
        if description:
            data["description"] = description

        response = requests.put(
            f"{self.base_url}/api/v1/data-sources/{endpoint_name}",
            json=data,
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()

    def test_data_source(
        self,
        endpoint_name: str,
        test_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """测试数据源"""
        response = requests.post(
            f"{self.base_url}/api/v1/data-sources/{endpoint_name}/test",
            json={"test_params": test_params},
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()

    def health_check_all(self) -> Dict[str, Any]:
        """批量健康检查"""
        response = requests.post(
            f"{self.base_url}/api/v1/data-sources/health-check/all",
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()


# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    client = DataSourceClient(token="your-token-here")

    # 搜索数据源
    print("=== 搜索日线数据接口 ===")
    result = client.search_data_sources(data_category="DAILY_KLINE")
    print(f"找到 {result['total']} 个接口")

    for ds in result['data_sources']:
        print(f"  - {ds['endpoint_name']}: 质量={ds['data_quality_score']}, 状态={ds['health_status']}")

    # 获取分类统计
    print("\n=== 分类统计 ===")
    stats = client.get_category_stats()
    for stat in stats:
        print(f"{stat['display_name']}: 总数={stat['total']}, 健康={stat['healthy']}")

    # 测试数据源
    print("\n=== 测试数据源 ===")
    test_result = client.test_data_source(
        "akshare.stock_zh_a_hist",
        {
            "symbol": "000001",
            "start_date": "20240101",
            "end_date": "20240131"
        }
    )

    if test_result['success']:
        print(f"✅ 测试成功")
        print(f"   响应时间: {test_result['duration']}秒")
        print(f"   返回数据: {test_result['row_count']}条")
    else:
        print(f"❌ 测试失败: {test_result['error']}")

    # 健康检查
    print("\n=== 健康检查 ===")
    health = client.health_check_all()
    print(f"总计: {health['total']}, 健康: {health['healthy']}, 异常: {health['unhealthy']}")
```

---

## 故障排除

### 常见问题

#### 1. 模块导入错误

**错误**:
```
ModuleNotFoundError: No module named 'src.adapters.tdx_adapter'
```

**原因**: TDX适配器已重组到子目录

**解决**: 已在 `src/adapters/data_source_manager.py` 中修复导入路径

#### 2. YAML语法错误

**错误**:
```
ERROR: while parsing a block mapping
  in "config/data_sources_registry.yaml", line 401
```

**原因**: YAML配置中缺少闭合引号

**解决**: 已修复 `config/data_sources_registry.yaml` 中的语法错误

#### 3. 数据库连接超时

**错误**:
```
Connection timeout: timeout expired
```

**原因**: PostgreSQL连接初始化延迟

**解决**:
- 系统已添加 `connect_timeout=10` 参数
- 启用优雅降级：自动从YAML加载配置
- 检查数据库服务状态

#### 4. API返回401 Unauthorized

**原因**: 缺少或无效的认证token

**解决**:
```bash
# 1. 获取token
curl -X GET "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# 2. 在后续请求中使用token
curl -X GET "http://localhost:8000/api/v1/data-sources/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 调试技巧

#### 1. 启用详细日志

```bash
# 手动测试工具
python scripts/tools/manual_data_source_tester.py \
    --endpoint akshare.stock_zh_a_hist \
    --symbol 000001 \
    --start-date 20240101 \
    --end-date 20240131 \
    --verbose
```

#### 2. 检查API响应

```bash
# 使用curl -v 查看详细请求/响应
curl -v -X GET "http://localhost:8000/api/v1/data-sources/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3. 查看FastAPI日志

```bash
# 后端日志位置
tail -f /path/to/backend/logs/app.log

# 或者查看systemd日志
journalctl -u mystocks-backend -f
```

#### 4. 数据库连接验证

```bash
# 测试PostgreSQL连接
psql -h localhost -p 5438 -U postgres -d mystocks

# 查看数据源注册表
SELECT endpoint_name, source_name, health_status, data_quality_score
FROM data_source_registry
ORDER BY priority;
```

---

## 附录

### A. 5层数据分类完整列表

| 分类代码 | 显示名称 | 层级 | 说明 |
|---------|---------|------|------|
| `DAILY_KLINE` | 日线K线数据 | 1 | 每日K线数据 |
| `MINUTE_KLINE` | 分钟K线数据 | 2 | 分钟级K线数据 |
| `TICK_DATA` | Tick逐笔数据 | 3 | 逐笔交易数据 |
| `REALTIME_QUOTES` | 实时行情 | 4 | 实时报价数据 |
| `REFERENCE_DATA` | 参考数据 | 5 | 静态参考数据 |
| `FINANCIAL_DATA` | 财务数据 | - | 财务报表数据 |
| `INDEX_DATA` | 指数数据 | - | 指数行情数据 |
| `SECTOR_DATA` | 板块数据 | - | 板块分类数据 |

### B. 数据源状态值

| 状态值 | 说明 |
|-------|------|
| `active` | 活跃（正常使用） |
| `maintenance` | 维护中（暂时不可用） |
| `deprecated` | 已弃用（不推荐使用） |

### C. 健康状态值

| 状态值 | 说明 |
|-------|------|
| `healthy` | 健康（可用） |
| `unhealthy` | 不健康（异常） |
| `unknown` | 未知（未测试） |

### D. 相关文档

- **数据源V2.0架构**: `docs/architecture/DATA_SOURCE_MANAGEMENT_V2.md`
- **实施报告**: `docs/reports/DATA_SOURCE_V2_FINAL_VERIFICATION_REPORT.md`
- **增强提案**: `docs/reports/DATA_SOURCE_V2_ENHANCEMENT_PROPOSAL.md`
- **配置文件**: `config/data_sources_registry.yaml`

---

**文档版本**: v1.0
**最后更新**: 2026-01-02
**维护者**: Main CLI (Claude Code)
**状态**: ✅ 生产就绪
