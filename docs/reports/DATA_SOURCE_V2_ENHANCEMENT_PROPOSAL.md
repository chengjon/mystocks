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

## 问题3: 数据清洗与验证功能实现分析

### 当前实现状态

| 功能 | 实现状态 | 具体文件 | 差距 |
|------|---------|---------|------|
| **行业数据清洗** | ✅ 已实现 | `scripts/data_cleaning/clean_industry_data.py` | 功能完整 |
| **数据库验证脚本** | ✅ 已实现 | `scripts/data_cleaning/verify_db_data.py` | 功能完整 |
| **K线数据验证** | ✅ 已实现 | verify_db_data.py --check-structure | 功能完整 |
| **adj_factor验证** | ✅ 已实现 | verify_db_data.py --check-adj-factor | 功能完整 |
| **自动化清洗任务** | ❌ 未实现 | - | 需要定时任务 |
| **入库前验证** | ⚠️ 部分实现 | DataManager中有基础验证 | 需要增强 |
| **数据治理规则** | ❌ 未实现 | - | 需要规则引擎 |

### 短期建议（立即可实施）

#### 3.1 完善现有验证脚本

**现状**: ✅ 两个脚本已完整实现
- `scripts/data_cleaning/clean_industry_data.py` (437行)
- `scripts/data_cleaning/verify_db_data.py` (544行)

**增强点**:
1. 添加TDengine数据验证支持
2. 增加更多验证规则（数据类型、范围、重复）
3. 支持批量表验证
4. 增加性能优化（并行验证）

#### 3.2 创建自动化清洗任务

**建议**: 创建定时任务脚本

```python
# scripts/data_cleaning/auto_clean_scheduler.py
"""
自动化数据清洗调度器

功能:
1. 每日收盘后自动验证K线数据
2. 每周检查行业数据质量
3. 自动修复adj_factor缺失值
4. 生成清洗报告并告警
"""

import schedule
import time
from pathlib import Path
from datetime import datetime
from scripts.data_cleaning.verify_db_data import DatabaseVerifier
from scripts.data_cleaning.clean_industry_data import DataCleaner


class AutoCleanScheduler:
    """自动化数据清洗调度器"""

    def __init__(self):
        self.verifier = DatabaseVerifier()

    def daily_kline_check(self):
        """每日检查K线数据"""
        print(f"\n[{datetime.now()}] 执行每日K线数据检查...")

        # 检查adj_factor
        result = self.verifier.check_adj_factor("stocks_daily")

        # 如果无效率超过5%，自动修复
        if result['valid_percent'] < 95:
            print(f"⚠️ adj_factor有效率为{result['valid_percent']:.2f}%，自动修复...")
            fix_result = self.verifier.fix_adj_factor(
                "stocks_daily",
                default_value=1.0,
                dry_run=False
            )
            print(f"✅ 已修复{fix_result['fixed_count']}条记录")

    def weekly_industry_check(self):
        """每周检查行业数据"""
        print(f"\n[{datetime.now()}] 执行每周行业数据检查...")

        result = self.verifier.check_industry_data("stocks_basic")

        # 如果脏数据超过10%，告警
        if result['dirty_percent'] > 10:
            print(f"⚠️ 脏数据率为{result['dirty_percent']:.2f}%，需要人工审核")
            # 这里可以集成邮件/钉钉告警

    def run(self):
        """启动调度器"""
        print("✅ 自动化清洗调度器已启动")

        # 每日检查K线数据（收盘后）
        schedule.every().day.at("16:00").do(self.daily_kline_check)

        # 每周一检查行业数据
        schedule.every().monday.at("09:00").do(self.weekly_industry_check)

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    scheduler = AutoCleanScheduler()
    scheduler.run()
```

#### 3.3 增强入库前验证

**建议**: 在DataManager中增加验证钩子

```python
# src/core/data_validator.py
"""
数据验证器 - 入库前验证

验证规则:
1. 数据完整性检查
2. 数据类型验证
3. 数据范围验证
4. 重复数据检测
5. 业务逻辑验证（如OHLC价格合理性）
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class DataValidator:
    """数据验证器"""

    def __init__(self):
        self.rules = {}

    def register_rule(self, table_name: str, rule: Dict):
        """注册验证规则"""
        if table_name not in self.rules:
            self.rules[table_name] = []
        self.rules[table_name].append(rule)

    def validate(self, table_name: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        验证数据

        返回:
            {
                "is_valid": bool,
                "errors": List[str],
                "warnings": List[str]
            }
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        if table_name not in self.rules:
            # 没有规则，跳过验证
            return result

        for rule in self.rules[table_name]:
            rule_result = self._apply_rule(data, rule)

            if not rule_result["is_valid"]:
                result["is_valid"] = False
                result["errors"].extend(rule_result["errors"])

            if rule_result["warnings"]:
                result["warnings"].extend(rule_result["warnings"])

        return result

    def _apply_rule(self, data: pd.DataFrame, rule: Dict) -> Dict:
        """应用单个验证规则"""
        rule_type = rule.get("type")

        if rule_type == "required_columns":
            return self._check_required_columns(data, rule)
        elif rule_type == "column_types":
            return self._check_column_types(data, rule)
        elif rule_type == "ohlc_logic":
            return self._check_ohlc_logic(data, rule)
        elif rule_type == "no_duplicates":
            return self._check_no_duplicates(data, rule)
        elif rule_type == "value_range":
            return self._check_value_range(data, rule)
        else:
            return {"is_valid": True, "errors": [], "warnings": []}

    def _check_required_columns(self, data: pd.DataFrame, rule: Dict) -> Dict:
        """检查必需列"""
        required = rule.get("columns", [])
        missing = [col for col in required if col not in data.columns]

        if missing:
            return {
                "is_valid": False,
                "errors": [f"缺少必需列: {', '.join(missing)}"],
                "warnings": []
            }

        return {"is_valid": True, "errors": [], "warnings": []}

    def _check_column_types(self, data: pd.DataFrame, rule: Dict) -> Dict:
        """检查列类型"""
        type_mappings = rule.get("mappings", {})
        errors = []

        for col, expected_type in type_mappings.items():
            if col not in data.columns:
                continue

            actual_type = str(data[col].dtype)

            if expected_type == "numeric" and not pd.api.types.is_numeric_dtype(data[col]):
                errors.append(f"列 '{col}' 应为数值类型，实际为 {actual_type}")
            elif expected_type == "datetime" and not pd.api.types.is_datetime64_any_dtype(data[col]):
                errors.append(f"列 '{col}' 应为日期时间类型，实际为 {actual_type}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": []
        }

    def _check_ohlc_logic(self, data: pd.DataFrame, rule: Dict) -> Dict:
        """检查OHLC价格逻辑"""
        errors = []

        required_cols = ["open", "high", "low", "close"]
        if not all(col in data.columns for col in required_cols):
            return {"is_valid": True, "errors": [], "warnings": []}

        # high >= max(open, close)
        invalid_high = data["high"] < data[["open", "close"]].max(axis=1)
        if invalid_high.any():
            errors.append(f"发现 {invalid_high.sum()} 条记录的high < max(open, close)")

        # low <= min(open, close)
        invalid_low = data["low"] > data[["open", "close"]].min(axis=1)
        if invalid_low.any():
            errors.append(f"发现 {invalid_low.sum()} 条记录的low > min(open, close)")

        # open, high, low, close > 0
        negative_prices = (data[["open", "high", "low", "close"]] <= 0).any(axis=1)
        if negative_prices.any():
            errors.append(f"发现 {negative_prices.sum()} 条记录的价格 <= 0")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": []
        }

    def _check_no_duplicates(self, data: pd.DataFrame, rule: Dict) -> Dict:
        """检查重复数据"""
        key_columns = rule.get("keys", [])

        if not key_columns or not all(col in data.columns for col in key_columns):
            return {"is_valid": True, "errors": [], "warnings": []}

        duplicates = data.duplicated(subset=key_columns)
        dup_count = duplicates.sum()

        if dup_count > 0:
            return {
                "is_valid": False,
                "errors": [f"发现 {dup_count} 条重复数据（基于列: {', '.join(key_columns)}）"],
                "warnings": []
            }

        return {"is_valid": True, "errors": [], "warnings": []}

    def _check_value_range(self, data: pd.DataFrame, rule: Dict) -> Dict:
        """检查数值范围"""
        column = rule.get("column")
        min_val = rule.get("min")
        max_val = rule.get("max")

        if column not in data.columns:
            return {"is_valid": True, "errors": [], "warnings": []}

        out_of_range = pd.Series([False] * len(data))

        if min_val is not None:
            out_of_range |= (data[column] < min_val)

        if max_val is not None:
            out_of_range |= (data[column] > max_val)

        count = out_of_range.sum()

        if count > 0:
            return {
                "is_valid": False,
                "errors": [f"列 '{column}' 有 {count} 条数据超出范围 [{min_val}, {max_val}]"],
                "warnings": []
            }

        return {"is_valid": True, "errors": [], "warnings": []}


# 全局验证器实例
_validator = DataValidator()


# 注册常用验证规则
def setup_default_rules():
    """设置默认验证规则"""

    # K线数据规则
    _validator.register_rule("stocks_daily", {
        "type": "required_columns",
        "columns": ["symbol", "trade_date", "open", "high", "low", "close", "volume"]
    })

    _validator.register_rule("stocks_daily", {
        "type": "ohlc_logic"
    })

    _validator.register_rule("stocks_daily", {
        "type": "no_duplicates",
        "keys": ["symbol", "trade_date"]
    })

    # 行业数据规则
    _validator.register_rule("stocks_basic", {
        "type": "no_duplicates",
        "keys": ["symbol"]
    })

    # 剔除行业脏数据
    _validator.register_rule("stocks_basic", {
        "type": "custom",
        "description": "行业数据不应等于股票名称",
        "validator": lambda df: {
            "is_valid": not (df["industry"] == df["name"]).any(),
            "errors": [],
            "warnings": []
        }
    })


def get_validator() -> DataValidator:
    """获取验证器实例"""
    return _validator
```

### 中期建议（1-2周实施）

#### 3.4 数据治理规则引擎

**建议**: 创建灵活的规则引擎

```python
# src/core/data_governance_engine.py
"""
数据治理规则引擎

功能:
1. 可配置的验证规则
2. 规则优先级管理
3. 规则执行历史记录
4. 规则热更新
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path


class DataGovernanceEngine:
    """数据治理引擎"""

    def __init__(self, config_path: str = "config/data_governance_rules.json"):
        self.config_path = config_path
        self.rules = {}
        self.load_rules()

    def load_rules(self):
        """加载规则配置"""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                self.rules = json.load(f)
        else:
            # 默认规则
            self.rules = self._get_default_rules()

    def save_rules(self):
        """保存规则配置"""
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.rules, f, indent=2)

    def _get_default_rules(self) -> Dict:
        """获取默认规则"""
        return {
            "rules": [
                {
                    "id": "KLINE_001",
                    "name": "K线数据完整性检查",
                    "table": "stocks_daily",
                    "enabled": True,
                    "priority": "HIGH",
                    "actions": [
                        {
                            "type": "required_columns",
                            "columns": ["symbol", "trade_date", "open", "high", "low", "close", "volume"]
                        },
                        {
                            "type": "ohlc_logic"
                        }
                    ],
                    "on_failure": "REJECT"
                },
                {
                    "id": "INDUSTRY_001",
                    "name": "行业数据清洗",
                    "table": "stocks_basic",
                    "enabled": True,
                    "priority": "MEDIUM",
                    "actions": [
                        {
                            "type": "custom",
                            "description": "剔除 industry = name 的脏数据",
                            "operation": "SET_NULL"
                        }
                    ],
                    "on_failure": "FIX"
                },
                {
                    "id": "ADJFACTOR_001",
                    "name": "复权因子填充",
                    "table": "stocks_daily",
                    "enabled": True,
                    "priority": "LOW",
                    "actions": [
                        {
                            "type": "fill_null",
                            "column": "adj_factor",
                            "default_value": 1.0
                        }
                    ],
                    "on_failure": "FIX"
                }
            ]
        }

    def apply_rules(self, table_name: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        应用规则

        返回:
            {
                "is_valid": bool,
                "data": pd.DataFrame,
                "errors": List[str],
                "warnings": List[str]
            }
        """
        result = {
            "is_valid": True,
            "data": data,
            "errors": [],
            "warnings": []
        }

        table_rules = [r for r in self.rules.get("rules", [])
                      if r.get("table") == table_name and r.get("enabled", True)]

        for rule in sorted(table_rules, key=lambda x: self._get_priority_score(x.get("priority"))):
            rule_result = self._apply_rule(data, rule)

            if not rule_result["is_valid"]:
                on_failure = rule.get("on_failure", "REJECT")

                if on_failure == "REJECT":
                    result["is_valid"] = False
                    result["errors"].append(f"规则 {rule['id']} 失败: {rule['name']}")
                    break
                elif on_failure == "FIX":
                    # 尝试自动修复
                    data = rule_result.get("fixed_data", data)
                    result["data"] = data
                    result["warnings"].append(f"规则 {rule['id']} 已自动修复: {rule['name']}")
                elif on_failure == "WARN":
                    result["warnings"].append(f"规则 {rule['id']} 触发警告: {rule['name']}")

        return result

    def _apply_rule(self, data: pd.DataFrame, rule: Dict) -> Dict:
        """应用单个规则"""
        # 具体实现...
        pass

    def _get_priority_score(self, priority: str) -> int:
        """获取优先级分数"""
        scores = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return scores.get(priority, 0)


# 配置文件示例: config/data_governance_rules.json
"""
{
  "rules": [
    {
      "id": "KLINE_001",
      "name": "K线数据完整性检查",
      "table": "stocks_daily",
      "enabled": true,
      "priority": "HIGH",
      "actions": [...],
      "on_failure": "REJECT"
    }
  ]
}
"""
```

### 长期建议（2-4周实施）

#### 3.5 接入权威行业数据源

**建议**: 集成第三方权威数据源进行交叉验证

```python
# src/industry_data_validator.py
"""
行业数据权威验证器

功能:
1. 从权威数据源获取行业分类
2. 交叉验证本地数据
3. 修正不一致的行业信息
4. 记录数据来源和置信度
"""

import requests
import pandas as pd
from typing import Dict, List, Optional


class IndustryDataValidator:
    """行业数据权威验证器"""

    def __init__(self):
        self.authoritative_sources = {
            "eastmoney": self._fetch_eastmoney_industry,
            "tushare": self._fetch_tushare_industry,
            # 可以添加更多数据源
        }

    def validate_industry(self, symbol: str, current_industry: str) -> Dict:
        """
        验证行业数据

        返回:
            {
                "is_valid": bool,
                "suggested_industry": Optional[str],
                "confidence": float,
                "sources": List[Dict]
            }
        """
        suggestions = []

        for source_name, fetch_func in self.authoritative_sources.items():
            try:
                industry = fetch_func(symbol)
                if industry:
                    suggestions.append({
                        "source": source_name,
                        "industry": industry,
                        "matches": industry == current_industry
                    })
            except Exception as e:
                print(f"数据源 {source_name} 查询失败: {e}")

        if not suggestions:
            return {
                "is_valid": True,
                "suggested_industry": None,
                "confidence": 0.0,
                "sources": []
            }

        # 统计最一致的行业分类
        industry_votes = {}
        for s in suggestions:
            industry = s["industry"]
            industry_votes[industry] = industry_votes.get(industry, 0) + 1

        best_industry = max(industry_votes, key=industry_votes.get)
        best_count = industry_votes[best_industry]

        is_valid = best_industry == current_industry
        confidence = best_count / len(suggestions)

        return {
            "is_valid": is_valid,
            "suggested_industry": best_industry if not is_valid else None,
            "confidence": confidence,
            "sources": suggestions
        }

    def _fetch_eastmoney_industry(self, symbol: str) -> Optional[str]:
        """从东方财富获取行业信息"""
        # 实现细节...
        pass

    def _fetch_tushare_industry(self, symbol: str) -> Optional[str]:
        """从Tushare获取行业信息"""
        # 实现细节...
        pass

    def batch_validate(self, symbols: List[str]) -> pd.DataFrame:
        """批量验证"""
        results = []

        for symbol in symbols:
            # 从数据库获取当前行业
            # current_industry = ...

            # 验证
            result = self.validate_industry(symbol, "")
            result["symbol"] = symbol
            results.append(result)

        return pd.DataFrame(results)
```

#### 3.6 K线数据治理完整方案

| 方面 | 短期（1周） | 中期（2周） | 长期（4周） |
|------|-----------|-----------|-----------|
| **数据完整性** | ✅ 验证脚本<br>✅ 修复adj_factor | ✅ 入库前验证<br>✅ 自动化清洗 | ✅ 权威数据源交叉验证 |
| **复权因子** | ✅ 验证完整性<br>✅ 填充默认值 | ✅ 每日自动计算<br>✅ 历史数据回填 | ✅ 多源数据融合 |
| **数据验证** | ✅ OHLC逻辑检查<br>✅ 重复数据检测 | ✅ 规则引擎<br>✅ 可配置规则 | ✅ 机器学习异常检测 |
| **异常处理** | ✅ 记录日志<br>✅ 拒绝入库 | ✅ 自动修复<br>✅ 告警通知 | ✅ 智能修正 |

---

## 完整实施路线图（更新版）

### Phase 1: 数据质量基础设施（1周）

**目标**: 完善验证脚本和基础验证

**任务**:
1. ✅ 增强现有验证脚本
   - 添加TDengine支持
   - 增加并行验证
   - 性能优化

2. ✅ 创建数据验证器模块
   - `src/core/data_validator.py`
   - 注册默认验证规则

3. ✅ 集成到DataManager
   - 保存前自动验证
   - 验证失败处理策略

**交付物**:
- 增强的验证脚本
- DataValidator模块
- 验证规则配置文件

### Phase 2: 自动化清洗系统（1-2周）

**目标**: 建立自动化清洗和调度系统

**任务**:
1. 创建自动化清洗调度器
   - `scripts/data_cleaning/auto_clean_scheduler.py`
   - 每日K线检查
   - 每周行业检查

2. 创建数据治理引擎
   - `src/core/data_governance_engine.py`
   - 可配置规则
   - 规则优先级管理

3. 集成告警系统
   - 邮件通知
   - 钉钉通知
   - Prometheus指标

**交付物**:
- 自动化调度器
- 数据治理引擎
- 规则配置文件
- 告警集成

### Phase 3: 权威数据源集成（2-4周）

**目标**: 接入权威数据源进行交叉验证

**任务**:
1. 行业数据验证器
   - 东方财富API集成
   - Tushare API集成
   - 交叉验证逻辑

2. K线数据融合
   - 多源数据对比
   - 数据质量评分
   - 智能选择

3. 历史数据回填
   - 批量验证历史数据
   - 自动修复
   - 报告生成

**交付物**:
- IndustryDataValidator模块
- 多源数据融合系统
- 历史数据回填脚本

### Phase 4: 高级特性（4周+）

**目标**: 机器学习异常检测和智能修正

**任务**:
1. 异常检测模型
   - 基于统计的异常检测
   - 基于机器学习的异常检测

2. 智能修正
   - 自动识别异常模式
   - 智能填充缺失值
   - 自动修正错误

3. 数据血缘追踪
   - 记录数据来源
   - 追踪数据变更
   - 数据质量影响分析

---

**报告版本**: v2.0
**创建日期**: 2026-01-02
**更新日期**: 2026-01-07
**作者**: Claude Code
**状态**: ✅ 已更新，包含数据治理规划
