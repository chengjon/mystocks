# 数据源管理V2.0 - 功能增强分析与实施建议

> **日期**: 2026-01-02
> **当前版本**: v2.0 (Phase 1-4完成)
> **目的**: 分析当前实现与理想架构的差距，提供增强建议

---

## 问题1: 自动发现与注册流程实现分析

### 理想流程

```
新数据源 → 注册测试 → 质量评估 → 生产使用 → 定期巡检 → 下线归档
```

### 当前实现状态

| 阶段 | 实现状态 | 具体功能 | 差距 |
|------|---------|---------|------|
| **新数据源** | ⚠️ 部分实现 | ✅ YAML手动注册<br>✅ sync_sources.py同步<br>❌ 无自动发现 | 需要DataSourceDiscoverer |
| **注册测试** | ⚠️ 部分实现 | ✅ test_parameters字段<br>✅ health_check()方法<br>❌ 无独立测试框架 | 需要测试自动化 |
| **质量评估** | ✅ 已实现 | ✅ data_quality_score<br>✅ success_rate监控<br>✅ avg_response_time<br>✅ 智能路由选择 | 功能完整 |
| **生产使用** | ✅ 已实现 | ✅ status字段管理<br>✅ 智能路由<br>✅ 故障降级 | 功能完整 |
| **定期巡检** | ⚠️ 部分实现 | ✅ 健康检查功能<br>❌ 无自动调度<br>❌ 无巡检报告 | 需要定时任务 |
| **下线归档** | ❌ 未实现 | ❌ 无下线流程<br>❌ 无归档机制<br>❌ 无历史数据清理 | 需要完整的生命周期管理 |

---

## 问题2: Grafana管理功能实现分析

### 用户期望的核心功能

#### 2.1 接口注册表查询

**期望功能**:
- 按5层分类筛选
- 按数据源类型筛选
- 按启用状态筛选
- 支持模糊搜索（如搜索"日线"）

**当前实现**: ❌ **未实现**

**现状**: Grafana仅展示监控数据，不提供注册表查询功能

**建议方案**:

##### 方案A: FastAPI后端 + Vue前端（推荐）

```python
# web/backend/app/api/data_source_registry.py
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()

@router.get("/api/v1/data-sources")
async def search_data_sources(
    data_category: Optional[str] = Query(None, description="5层分类"),
    source_type: Optional[str] = Query(None, description="数据源类型"),
    status: Optional[str] = Query("active", description="启用状态"),
    keyword: Optional[str] = Query(None, description="模糊搜索关键词")
):
    """
    搜索数据源接口

    示例:
        GET /api/v1/data-sources?data_category=DAILY_KLINE&keyword=日线
    """
    from src.core.data_source_manager_v2 import DataSourceManagerV2

    manager = DataSourceManagerV2()

    # 使用现有查询功能
    endpoints = manager.find_endpoints(
        data_category=data_category,
        source_type=source_type,
        only_healthy=(status == "active")
    )

    # 关键词过滤
    if keyword:
        endpoints = [
            ep for ep in endpoints
            if keyword.lower() in ep['endpoint_name'].lower() or
               keyword.lower() in ep.get('description', '').lower()
        ]

    return {
        "total": len(endpoints),
        "data_sources": endpoints
    }

@router.get("/api/v1/data-sources/categories")
async def get_categories():
    """获取所有5层数据分类及统计"""
    from src.core.data_source_manager_v2 import DataSourceManagerV2

    manager = DataSourceManagerV2()

    # 按分类分组统计
    categories = {}
    for endpoint_name, source_data in manager.registry.items():
        category = source_data['config'].get('data_category', 'UNKNOWN')
        if category not in categories:
            categories[category] = {
                'category': category,
                'total': 0,
                'healthy': 0,
                'endpoints': []
            }

        categories[category]['total'] += 1
        if source_data['config'].get('health_status') == 'healthy':
            categories[category]['healthy'] += 1

        categories[category]['endpoints'].append(endpoint_name)

    # 按分类排序
    return sorted(categories.values(), key=lambda x: x['category'])
```

##### 方案B: Grafana + PostgreSQL直接查询（快速方案）

在Grafana中创建新的Panel，直接查询PostgreSQL:

```sql
-- 按分类查询数据源
SELECT
    data_category,
    endpoint_name,
    source_name,
    health_status,
    data_quality_score,
    priority,
    success_rate,
    avg_response_time
FROM data_source_registry
WHERE
    status = 'active'
    AND (${data_category:raw} IS NULL OR data_category = ${data_category})
    AND (${keyword:raw} IS NULL OR endpoint_name ILIKE '%' || ${keyword} || '%')
ORDER BY priority ASC, data_quality_score DESC
```

**Grafana变量配置**:
```yaml
variables:
  - name: data_category
    type: query
    query: "SELECT DISTINCT data_category FROM data_source_registry WHERE status='active' ORDER BY data_category"

  - name: keyword
    type: textbox
```

#### 2.2 分类分组展示

**期望功能**:
- 按5层分类折叠展示
- 展开后可见所有原始接口
- 显示接口优先级、可用状态

**当前实现**: ❌ **未实现**

**建议方案**: 使用Grafana **Table Panel** + **Repeat by Variable**

```json
{
  "type": "table",
  "title": "数据源接口列表（按分类）",
  "repeat": "data_category",
  "repeatDirection": "h",
  "targets": [
    {
      "sql": "SELECT
        endpoint_name,
        source_name,
        priority,
        health_status,
        data_quality_score,
        success_rate,
        avg_response_time
      FROM data_source_registry
      WHERE data_category = '$data_category'
        AND status = 'active'
      ORDER BY priority ASC, data_quality_score DESC"
    }
  ],
  "transformations": [
    {
      "id": "organize",
      "options": {
        "excludeByName": {},
        "indexByName": {},
        "renameByName": {
          "endpoint_name": "接口名称",
          "source_name": "数据源",
          "priority": "优先级",
          "health_status": "健康状态",
          "data_quality_score": "质量评分",
          "success_rate": "成功率(%)",
          "avg_response_time": "响应时间(s)"
        }
      }
    }
  ]
}
```

#### 2.3 监控仪表盘（已实现✅）

**期望功能**:
- 按分类展示接口可用性（成功率）
- 平均响应时间
- 数据质量评分
- 折线图/柱状图

**当前实现**: ✅ **已实现** (12个Grafana面板)

已包含的监控面板:
1. ✅ 数据源可用性状态 (Stat面板)
2. ✅ 数据源调用速率 QPS (Time Series)
3. ✅ 数据源健康状态 (Stat)
4. ✅ 响应时间分布 (Histogram)
5. ✅ 数据质量评分 (Gauge)
6. ✅ 成功率趋势 (Time Series)
7. ✅ 调用总次数 (Stat)
8. ✅ 返回数据量分布 (Heatmap)
9. ✅ 连续失败次数 (Table)
10. ✅ 接口对比 (Bar Chart)
11. ✅ 实时调用日志 (Table)
12. ✅ 数据源列表 (Table)

**当前PromQL查询示例**:
```promql
# 按数据分类的成功率
rate(data_source_calls_total{status="success"}[5m]) /
rate(data_source_calls_total[5m]) * 100

# 按数据分类的响应时间
rate(data_source_response_time_seconds_sum[5m]) /
rate(data_source_response_time_seconds_count[5m])

# 数据质量评分
data_source_quality_score
```

**增强建议**: 添加按`data_category`标签分组

```promql
# 按分类的成功率
rate(data_source_calls_total{status="success", data_category="DAILY_KLINE"}[5m]) /
rate(data_source_calls_total{data_category="DAILY_KLINE"}[5m]) * 100
```

#### 2.4 异常接口标红提示（已实现✅）

**期望功能**:
- 第1类接口成功率<90%标红
- 响应时间>1秒标红

**当前实现**: ✅ **已实现** (Grafana阈值告警)

已在Panel中配置:
```json
{
  "fieldConfig": {
    "defaults": {
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "red", "value": null},
          {"color": "yellow", "value": 90},
          {"color": "green", "value": 95}
        ]
      }
    }
  }
}
```

**Prometheus告警规则** (可添加):
```yaml
groups:
  - name: data_source_alerts
    rules:
      # 成功率告警
      - alert: DataSourceSuccessRateLow
        expr: |
          rate(data_source_calls_total{status="success"}[5m]) /
          rate(data_source_calls_total[5m]) < 0.9
        for: 10m
        labels:
          severity: warning
          category: reliability
        annotations:
          summary: "数据源 {{ $endpoint_name }} 成功率低于90%"
          description: "成功率: {{ $value | humanizePercentage }}"

      # 响应时间告警
      - alert: DataSourceResponseTimeHigh
        expr: |
          rate(data_source_response_time_seconds_sum[5m]) /
          rate(data_source_response_time_seconds_count[5m]) > 1.0
        for: 5m
        labels:
          severity: warning
          category: performance
        annotations:
          summary: "数据源 {{ $endpoint_name }} 响应时间超过1秒"
          description: "平均响应时间: {{ $value }}s"
```

#### 2.5 配置编辑（未实现❌）

**期望功能**:
- 直接在面板上修改接口配置
- 修改启用状态、优先级
- 保存后自动更新注册表

**当前实现**: ❌ **未实现**

**建议方案**:

##### 方案A: Web管理界面（推荐）

创建Vue.js管理界面:

```vue
<!-- web/frontend/src/views/DataSourceManagement.vue -->
<template>
  <div class="data-source-management">
    <!-- 搜索筛选 -->
    <el-form :inline="true">
      <el-form-item label="数据分类">
        <el-select v-model="searchForm.data_category">
          <el-option label="全部" value=""></el-option>
          <el-option
            v-for="cat in categories"
            :key="cat"
            :label="cat"
            :value="cat">
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="关键词">
        <el-input v-model="searchForm.keyword"></el-input>
      </el-form-item>

      <el-button type="primary" @click="searchDataSources">搜索</el-button>
    </el-form>

    <!-- 数据源列表 -->
    <el-table :data="dataSources" style="margin-top: 20px">
      <el-table-column prop="endpoint_name" label="接口名称"></el-table-column>
      <el-table-column prop="data_category" label="数据分类"></el-table-column>
      <el-table-column prop="priority" label="优先级">
        <template #default="scope">
          <el-input-number
            v-model="scope.row.priority"
            :min="1"
            :max="10"
            @change="updatePriority(scope.row)">
          </el-input-number>
        </template>
      </el-table-column>
      <el-table-column prop="health_status" label="状态">
        <template #default="scope">
          <el-switch
            v-model="scope.row.active"
            active-text="启用"
            inactive-text="禁用"
            @change="toggleStatus(scope.row)">
          </el-switch>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="editDataSource(scope.row)">编辑</el-button>
          <el-button size="small" @click="testDataSource(scope.row)">测试</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑数据源" width="60%">
      <el-form :model="editForm">
        <el-form-item label="接口名称">
          <el-input v-model="editForm.endpoint_name" disabled></el-input>
        </el-form-item>

        <el-form-item label="优先级">
          <el-input-number v-model="editForm.priority" :min="1" :max="10"></el-input-number>
        </el-form-item>

        <el-form-item label="质量评分">
          <el-slider v-model="editForm.data_quality_score" :min="0" :max="10"></el-slider>
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="editForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="maintenance">维护中</el-radio>
            <el-radio label="deprecated">已废弃</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="描述">
          <el-input type="textarea" v-model="editForm.description"></el-input>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDataSource">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const dataSources = ref([])
const categories = ref([])
const editDialogVisible = ref(false)
const editForm = ref({})

// 搜索数据源
const searchDataSources = async () => {
  const { data } = await axios.get('/api/v1/data-sources', {
    params: searchForm.value
  })
  dataSources.value = data.data_sources
}

// 更新优先级
const updatePriority = async (row) => {
  await axios.put(`/api/v1/data-sources/${row.endpoint_name}`, {
    priority: row.priority
  })
  ElMessage.success('优先级已更新')
}

// 切换状态
const toggleStatus = async (row) => {
  await axios.put(`/api/v1/data-sources/${row.endpoint_name}`, {
    status: row.active ? 'active' : 'maintenance'
  })
  ElMessage.success('状态已更新')
}

// 保存数据源配置
const saveDataSource = async () => {
  await axios.put(`/api/v1/data-sources/${editForm.value.endpoint_name}`, editForm.value)
  ElMessage.success('配置已保存')
  editDialogVisible.value = false
  searchDataSources()
}

onMounted(() => {
  searchDataSources()
})
</script>
```

**后端API**:
```python
# web/backend/app/api/data_source_registry.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class DataSourceUpdate(BaseModel):
    priority: Optional[int] = None
    data_quality_score: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None

@router.put("/api/v1/data-sources/{endpoint_name}")
async def update_data_source(endpoint_name: str, update: DataSourceUpdate):
    """更新数据源配置"""
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv()

    conn = psycopg2.connect(
        host=os.getenv('POSTGRESQL_HOST'),
        port=int(os.getenv('POSTGRESQL_PORT')),
        user=os.getenv('POSTGRESQL_USER'),
        password=os.getenv('POSTGRESQL_PASSWORD'),
        database=os.getenv('POSTGRESQL_DATABASE')
    )
    cursor = conn.cursor()

    # 构建更新SQL
    updates = {k: v for k, v in update.dict().items() if v is not None}

    if not updates:
        raise HTTPException(status_code=400, detail="无更新内容")

    set_clause = ", ".join([f"{k} = %({k})s" for k in updates.keys()])

    sql = f"""
        UPDATE data_source_registry
        SET {set_clause}, updated_at = NOW()
        WHERE endpoint_name = %(endpoint_name)s
    """

    cursor.execute(sql, {**updates, "endpoint_name": endpoint_name})
    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True, "message": "配置已更新"}
```

##### 方案B: Grafana + JSON API（快速方案）

使用Grafana的**Table Panel** + **Data Link**功能，在表格中添加操作列:

```json
{
  "type": "table",
  "transformations": [
    {
      "id": "links",
      "options": {
        "links": [
          {
            "title": "编辑",
            "url": "http://localhost:8000/api/v1/data-sources/edit?endpoint=${__value.fields.endpoint_name}"
          },
          {
            "title": "测试",
            "url": "http://localhost:8000/api/v1/data-sources/test?endpoint=${__value.fields.endpoint_name}"
          }
        ]
      }
    }
  ]
}
```

#### 2.6 手动测试（未实现❌）

**期望功能**:
- 管理员选择接口
- 输入测试参数（股票代码、日期范围）
- 手动触发调用
- 查看返回结果和数据质量
- 无需编写测试脚本

**当前实现**: ❌ **未实现**

**建议方案**:

创建独立的测试工具:

```python
# scripts/tools/manual_data_source_tester.py
"""
数据源手动测试工具

使用示例:
    python scripts/tools/manual_data_source_tester.py --endpoint akshare.stock_zh_a_hist --symbol 000001 --start-date 20240101 --end-date 20240131
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.data_source_manager_v2 import DataSourceManagerV2


def test_data_source(endpoint_name: str, test_params: dict, verbose: bool = True):
    """
    手动测试数据源

    Args:
        endpoint_name: 接口名称（如 akshare.stock_zh_a_hist）
        test_params: 测试参数
        verbose: 是否显示详细信息
    """
    print(f"\n{'='*60}")
    print(f"测试数据源: {endpoint_name}")
    print(f"{'='*60}")

    manager = DataSourceManagerV2()

    # 1. 检查接口是否存在
    if endpoint_name not in manager.registry:
        print(f"❌ 接口不存在: {endpoint_name}")
        print(f"   可用接口: {list(manager.registry.keys())}")
        return False

    source_config = manager.registry[endpoint_name]['config']

    # 2. 显示接口配置
    print(f"\n📋 接口配置:")
    print(f"   数据源: {source_config.get('source_name')}")
    print(f"   数据分类: {source_config.get('data_category')}")
    print(f"   目标数据库: {source_config.get('target_db')}")
    print(f"   质量评分: {source_config.get('data_quality_score')}")
    print(f"   健康状态: {source_config.get('health_status')}")

    # 3. 显示测试参数
    print(f"\n🔧 测试参数:")
    for key, value in test_params.items():
        print(f"   {key}: {value}")

    # 4. 执行测试
    print(f"\n⏳ 正在调用接口...")
    start_time = datetime.now()

    try:
        # 调用数据源
        handler = manager._get_handler(endpoint_name)
        data = handler.fetch(**test_params)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 5. 显示结果
        print(f"✅ 调用成功")
        print(f"   响应时间: {duration:.3f}秒")
        print(f"   返回数据量: {len(data) if data is not None else 0}条")

        if verbose and data is not None and len(data) > 0:
            print(f"\n📊 数据预览:")
            print(f"   {data.head(3).to_string() if hasattr(data, 'head') else str(data)[:200]}")

            # 数据质量检查
            print(f"\n📈 数据质量分析:")

            # 完整性检查
            expected_cols = source_config.get('parameters', {}).keys()
            if hasattr(data, 'columns'):
                actual_cols = data.columns.tolist()
                missing_cols = set(expected_cols) - set(actual_cols)
                if missing_cols:
                    print(f"   ⚠️  缺失列: {missing_cols}")
                else:
                    print(f"   ✅ 列完整: {len(actual_cols)}列")

            # 数据范围检查
            if hasattr(data, 'empty'):
                print(f"   {'✅ 数据非空' if not data.empty else '❌ 数据为空'}")

        # 6. 记录成功
        manager._record_success(endpoint_name, duration, len(data) if data is not None else 0)

        return True

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"❌ 调用失败")
        print(f"   响应时间: {duration:.3f}秒")
        print(f"   错误信息: {str(e)}")

        # 7. 记录失败
        manager._record_failure(endpoint_name, str(e))

        if verbose:
            import traceback
            print(f"\n详细错误堆栈:")
            traceback.print_exc()

        return False


def interactive_mode():
    """交互式测试模式"""
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║       MyStocks 数据源手动测试工具 v1.0              ║")
    print("╚══════════════════════════════════════════════════════╝")

    manager = DataSourceManagerV2()

    # 1. 选择接口
    print(f"\n可用接口列表 (共{len(manager.registry)}个):")

    # 按分类分组显示
    categories = {}
    for endpoint_name, source_data in manager.registry.items():
        category = source_data['config'].get('data_category', 'UNKNOWN')
        if category not in categories:
            categories[category] = []
        categories[category].append(endpoint_name)

    for i, (category, endpoints) in enumerate(sorted(categories.items()), 1):
        print(f"\n[{i}] {category} ({len(endpoints)}个接口):")
        for endpoint in sorted(endpoints)[:5]:  # 只显示前5个
            print(f"    - {endpoint}")
        if len(endpoints) > 5:
            print(f"    ... 还有 {len(endpoints) - 5} 个接口")

    # 2. 选择接口
    endpoint_input = input(f"\n请输入接口名称（或输入分类编号）: ").strip()

    if endpoint_input.isdigit():
        # 用户输入了分类编号
        category_list = sorted(categories.items())
        idx = int(endpoint_input) - 1
        if 0 <= idx < len(category_list):
            selected_category, endpoints = category_list[idx]
            print(f"\n{selected_category} 的接口列表:")
            for i, endpoint in enumerate(sorted(endpoints), 1):
                print(f"  [{i}] {endpoint}")

            sub_idx = int(input(f"\n请选择接口编号: ").strip()) - 1
            endpoint_name = sorted(endpoints)[sub_idx]
        else:
            print(f"❌ 无效的编号")
            return
    else:
        endpoint_name = endpoint_input

    # 3. 输入测试参数
    print(f"\n请输入测试参数 (JSON格式，留空使用默认参数):")
    param_input = input("> ").strip()

    if param_input:
        try:
            test_params = json.loads(param_input)
        except json.JSONDecodeError:
            print(f"❌ JSON格式错误")
            return
    else:
        # 使用默认测试参数
        source_config = manager.registry[endpoint_name]['config']
        test_params = source_config.get('test_parameters', {})
        print(f"使用默认参数: {test_params}")

    # 4. 执行测试
    test_data_source(endpoint_name, test_params, verbose=True)


def main():
    parser = argparse.ArgumentParser(description="数据源手动测试工具")
    parser.add_argument("--endpoint", help="接口名称")
    parser.add_argument("--symbol", help="股票代码")
    parser.add_argument("--start-date", help="开始日期")
    parser.add_argument("--end-date", help="结束日期")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式模式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.endpoint:
        test_params = {}
        if args.symbol:
            test_params['symbol'] = args.symbol
        if args.start_date:
            test_params['start_date'] = args.start_date
        if args.end_date:
            test_params['end_date'] = args.end_date

        test_data_source(args.endpoint, test_params, args.verbose)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

**集成到Web界面**:

```python
# web/backend/app/api/data_source_registry.py
@router.post("/api/v1/data-sources/{endpoint_name}/test")
async def test_data_source(endpoint_name: str, test_params: dict):
    """
    手动测试数据源

    Body示例:
        {
            "symbol": "000001",
            "start_date": "20240101",
            "end_date": "20240131"
        }
    """
    from src.core.data_source_manager_v2 import DataSourceManagerV2

    manager = DataSourceManagerV2()

    if endpoint_name not in manager.registry:
        raise HTTPException(status_code=404, detail="接口不存在")

    try:
        # 调用数据源
        handler = manager._get_handler(endpoint_name)
        data = handler.fetch(**test_params)

        return {
            "success": True,
            "endpoint_name": endpoint_name,
            "test_params": test_params,
            "result": {
                "row_count": len(data) if data is not None else 0,
                "preview": data.head(3).to_dict() if hasattr(data, 'head') and data is not None else None,
                "columns": list(data.columns) if hasattr(data, 'columns') else None
            }
        }
    except Exception as e:
        return {
            "success": False,
            "endpoint_name": endpoint_name,
            "test_params": test_params,
            "error": str(e)
        }
```

---

## 实施建议总结

### 优先级矩阵

| 功能 | 优先级 | 复杂度 | 预计工作量 | 建议 |
|------|--------|--------|-----------|------|
| **接口注册表查询** | P0 | 中 | 2-3天 | 立即实施 |
| **监控仪表盘增强** | P0 | 低 | 1天 | 立即实施 |
| **手动测试工具** | P0 | 低 | 1-2天 | 立即实施 |
| **配置编辑（Web界面）** | P1 | 高 | 5-7天 | 第二阶段 |
| **自动发现** | P2 | 中 | 3-5天 | 第三阶段 |
| **定期巡检** | P1 | 中 | 2-3天 | 第二阶段 |
| **下线归档** | P2 | 低 | 2天 | 第三阶段 |

### 第一阶段实施计划（1周）

**目标**: 实现核心管理功能

1. **Day 1-2**: 接口注册表查询
   - 实现FastAPI搜索接口
   - 添加Grafana表格面板（PostgreSQL查询）
   - 提供按分类、状态、关键词筛选

2. **Day 3**: 监控仪表盘增强
   - 添加按分类分组展示
   - 配置阈值告警
   - 优化现有12个面板

3. **Day 4-5**: 手动测试工具
   - 实现命令行测试工具
   - 集成到Web API
   - 添加测试报告功能

**交付物**:
- FastAPI搜索接口 (`/api/v1/data-sources`)
- Grafana增强仪表盘（按分类展示）
- 手动测试工具 (`scripts/tools/manual_data_source_tester.py`)

### 第二阶段实施计划（1-2周）

**目标**: 实现Web管理界面

1. **Week 1**: 配置编辑界面
   - Vue.js管理页面
   - CRUD API实现
   - 实时配置更新

2. **Week 2**: 定期巡检系统
   - 定时健康检查
   - 巡检报告生成
   - 邮件/钉钉通知

### 第三阶段实施计划（1-2周）

**目标**: 实现自动化流程

1. **Week 1**: 自动发现功能
   - DataSourceDiscoverer实现
   - akshare/tushare自动扫描
   - 自动生成测试参数

2. **Week 2**: 生命周期管理
   - 下线流程
   - 数据归档
   - 历史数据清理

---

## 技术选型建议

### 推荐方案: FastAPI + Vue.js + PostgreSQL + Grafana

**架构**:
```
┌─────────────────────────────────────────────────────────┐
│                   Vue.js 前端                          │
│  - 接口查询和筛选                                        │
│  - 配置编辑界面                                          │
│  - 实时监控展示                                          │
└────────────────┬────────────────────────────────────────┘
                 │ REST API
┌────────────────▼────────────────────────────────────────┐
│                 FastAPI 后端                            │
│  - /api/v1/data-sources (搜索、更新)                      │
│  - /api/v1/data-sources/{id}/test (手动测试)              │
│  - /api/v1/data-sources/categories (分类统计)             │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│          DataSourceManagerV2 (核心逻辑)                 │
│  - 智能路由                                               │
│  - 健康检查                                               │
│  - 监控记录                                               │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│        PostgreSQL (注册表) + Prometheus (监控)          │
└─────────────────────────────────────────────────────────┘
```

**优势**:
- ✅ 利用现有基础设施（FastAPI、PostgreSQL、Grafana）
- ✅ 前后端分离，易于维护
- ✅ RESTful API，易于扩展
- ✅ 实时监控，无需额外搭建

---

## 结论

### 当前实现总结

**已实现** ✅:
- 核心注册表和智能路由
- Prometheus监控指标导出
- Grafana基础监控仪表盘（12个面板）
- 健康检查和故障降级

**需要增强** ⚠️:
- 接口注册表查询界面
- 配置编辑功能
- 手动测试工具
- 自动发现和生命周期管理

### 推荐实施路径

**第一阶段** (1周，P0优先级):
1. 实现接口注册表查询（FastAPI + Grafana Table）
2. 增强监控仪表盘（按分类展示）
3. 实现手动测试工具（命令行 + API）

**第二阶段** (2周，P1优先级):
4. 开发Web配置管理界面（Vue.js）
5. 实现定期巡检系统

**第三阶段** (2周，P2优先级):
6. 实现自动发现功能
7. 完善生命周期管理（下线、归档）

---

**报告版本**: v1.0
**创建日期**: 2026-01-02
**作者**: Claude Code
**状态**: 待用户确认实施优先级
