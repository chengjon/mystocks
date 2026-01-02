# API契约验证执行计划 - Phase 2前期准备

**创建日期**: 2026-01-02
**状态**: 🎯 Ready to Execute
**负责人**: Main CLI (Claude Code)
**数据守卫者**: 用户 (负责数据层问题解决)

---

## 📋 执行概览

### 目标
在Phase 2执行前，系统化验证前端使用的64个API端点，确保：
1. 后端端点已实现且可访问
2. 能够返回真实数据（非Mock）
3. 数据格式符合前端契约
4. 响应时间可接受（<500ms）

### 验证范围
- **总API端点**: 356个（后端实现）
- **前端使用**: 64个API调用
- **验证优先级**: P0 → P1 → P2 → P3
- **首批验证**: Phase 2.1 (3个P0 API)

---

## 🎯 Phase 2.1 验证清单（首批执行）

### API详细信息

| # | 前端调用 | 后端端点 | HTTP方法 | 数据源 | 文件位置 | 函数名 | 状态 |
|---|---------|---------|----------|--------|----------|--------|------|
| 2.1.1 | `dataApi.getStocksIndustries` | `/api/v1/data/stocks/industries` | GET | PostgreSQL | data.py:102 | `get_stocks_industries` | ⏳ 待验证 |
| 2.1.2 | `dataApi.getStocksConcepts` | `/api/v1/data/stocks/concepts` | GET | PostgreSQL | data.py:157 | `get_stocks_concepts` | ⏳ 待验证 |
| 2.1.3 | `dataApi.getStocksBasic` | `/api/v1/data/stocks/basic` | GET | PostgreSQL | data.py:33 | `get_stocks_basic` | ⏳ 待验证 |

### 前端调用位置

**文件**: `web/frontend/src/views/Stocks.vue`

```javascript
// Line 226
const industries = await dataApi.getStocksIndustries()

// Line 227
const concepts = await dataApi.getStocksConcepts()

// Line 228 (推测)
const stocks = await dataApi.getStocksBasic({ page: 1, page_size: 20 })
```

### 后端实现位置

**文件**: `web/backend/app/api/data.py`

```python
# Line 102
@router.get("/stocks/industries")
async def get_stocks_industries():
    """获取股票行业列表"""
    # 实现逻辑...

# Line 157
@router.get("/stocks/concepts")
async def get_stocks_concepts():
    """获取股票概念列表"""
    # 实现逻辑...

# Line 33
@router.get("/stocks/basic")
async def get_stocks_basic(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取股票基础信息（分页）"""
    # 实现逻辑...
```

---

## 🔄 验证执行流程

### 阶段1: 环境准备（Day 1上午）

#### 1.1 确认后端服务状态

```bash
# 检查后端服务是否运行
curl -s http://localhost:8000/health | jq '.'

# 预期输出:
# {
#   "status": "healthy",
#   "database": "connected",
#   "timestamp": "2026-01-02T10:00:00Z"
# }
```

#### 1.2 确认数据库准备状态

**关键问题（需用户确认）**:
- [ ] PostgreSQL数据库是否已创建？
- [ ] `stock_industries` 表是否存在且有数据？
- [ ] `stock_concepts` 表是否存在且有数据？
- [ ] `stocks_basic` 表（或等效表）是否存在且有数据？

**验证脚本**:
```bash
# 运行数据库检查脚本
cd /opt/claude/mystocks_spec
python scripts/database/check_stock_tables.py
```

**如果数据库未就绪**:
- 🔴 **立即报告用户**
- 用户角色: 数据守卫者
- 预期响应时间: 24小时
- 下一步: 等待用户确认后再继续

#### 1.3 安装验证工具

```bash
# 安装Python依赖
pip install pytest requests openapi-spec-validator

# 验证安装
pytest --version
python -c "import requests; print(requests.__version__)"
```

#### 1.4 生成OpenAPI Schema

```bash
# 获取后端OpenAPI规范
curl -s http://localhost:8000/openapi.json -o docs/api/openapi.json

# 验证OpenAPI规范
python -c "
import json
with open('docs/api/openapi.json') as f:
    schema = json.load(f)
print(f'OpenAPI Version: {schema[\"openapi\"]}')
print(f'Total Paths: {len(schema[\"paths\"])}')
"
```

---

### 阶段2: API端点验证（Day 1下午）

#### 2.1 Layer 1: 端点存在性验证

**验证目标**: 确认端点可访问，不返回404/405

**验证脚本**:
```bash
# 测试端点1: 行业列表
curl -s -w "\nHTTP Status: %{http_code}\n" \
     -H "Authorization: Bearer dev-mock-token-for-development" \
     http://localhost:8000/api/v1/data/stocks/industries

# 测试端点2: 概念列表
curl -s -w "\nHTTP Status: %{http_code}\n" \
     -H "Authorization: Bearer dev-mock-token-for-development" \
     http://localhost:8000/api/v1/data/stocks/concepts

# 测试端点3: 股票基础信息（带分页参数）
curl -s -w "\nHTTP Status: %{http_code}\n" \
     -H "Authorization: Bearer dev-mock-token-for-development" \
     "http://localhost:8000/api/v1/data/stocks/basic?page=1&page_size=20"
```

**通过标准**:
- ✅ HTTP状态码 200 (OK)
- ✅ 不返回404 (Not Found)
- ✅ 不返回405 (Method Not Allowed)

**失败处理**:
- 🔴 如果返回404/405 → 立即报告用户
- 📢 问题类型: 后端路由未实现或路径错误
- ⏸️ 暂停验证，等待用户解决

#### 2.2 Layer 2: 契约格式验证

**验证目标**: 确认响应符合UnifiedResponse格式

**预期格式**:
```json
{
  "code": null,  // 或 0
  "message": "success",
  "data": [...]  // 实际数据
}
```

**验证脚本**:
```bash
# 测试端点1: 行业列表
curl -s -H "Authorization: Bearer dev-mock-token-for-development" \
     http://localhost:8000/api/v1/data/stocks/industries | jq '.'

# 预期输出示例:
# {
#   "code": null,
#   "message": "success",
#   "data": [
#     {
#       "industry_name": "银行",
#       "industry_code": "BK0001",
#       "description": "银行业股票",
#       "stock_count": 42
#     },
#     ...
#   ]
# }
```

**通过标准**:
- ✅ 包含 `code` 字段
- ✅ 包含 `message` 字段
- ✅ 包含 `data` 字段
- ✅ `data` 字段类型正确（数组或对象）

**失败处理**:
- 🟠 如果格式不匹配 → 记录问题，继续验证其他API
- 📊 问题类型: 响应格式不符合契约
- 📝 汇总到问题报告，48小时内解决

#### 2.3 Layer 3: 性能验证

**验证目标**: 确认响应时间在可接受范围内

**验证脚本**:
```bash
# 测试响应时间（使用curl的time_total）
for endpoint in \
  "stocks/industries" \
  "stocks/concepts" \
  "stocks/basic?page=1&page_size=20"
do
  echo "Testing: /api/v1/data/$endpoint"
  curl -s -o /dev/null -w "  Response Time: %{time_total}s\n" \
       -H "Authorization: Bearer dev-mock-token-for-development" \
       "http://localhost:8000/api/v1/data/$endpoint"
done
```

**通过标准**:
- ✅ 响应时间 < 300ms (行业/概念列表)
- ✅ 响应时间 < 500ms (股票基础信息，带分页)

**失败处理**:
- 🟡 如果响应时间超标 → 记录优化建议
- 📊 问题类型: 性能优化需求
- 📝 汇总到问题报告，Phase 2执行前优化

#### 2.4 Layer 4: 数据完整性验证

**验证目标**: 确认返回真实数据，非Mock数据

**验证脚本**:
```bash
# 测试端点1: 行业列表（检查数据量）
curl -s -H "Authorization: Bearer dev-mock-token-for-development" \
     http://localhost:8000/api/v1/data/stocks/industries | \
  jq '.data | length'

# 预期: >= 50个行业（如果数据库有数据）
# 如果: 0 或空数组 → 可能是数据库表为空或查询失败

# 测试端点2: 概念列表（检查数据量）
curl -s -H "Authorization: Bearer dev-mock-token-for-development" \
     http://localhost:8000/api/v1/data/stocks/concepts | \
  jq '.data | length'

# 预期: >= 100个概念（如果数据库有数据）

# 测试端点3: 股票基础信息（检查分页）
curl -s -H "Authorization: Bearer dev-mock-token-for-development" \
     "http://localhost:8000/api/v1/data/stocks/basic?page=1&page_size=20" | \
  jq '.data | length'

# 预期: 20条记录（page_size=20）
# 或根据实际数据库记录数返回
```

**通过标准**:
- ✅ 数据不为空（除非数据库确实无数据）
- ✅ 数据字段完整（不缺少关键字段）
- ✅ 数据类型正确（字符串/数字/日期等）
- ✅ 数据内容合理（非硬编码的Mock数据）

**失败处理**:
- 🔴 如果返回空数组但预期有数据 → **立即报告用户**
- 📢 问题类型: 数据库表为空或查询错误
- 👤 用户角色: 数据守卫者
- ⏸️ 暂停验证，等待用户提供数据

---

### 阶段3: 契约匹配验证（Day 2上午）

#### 3.1 前端类型定义验证

**目标**: 确认前端TypeScript类型定义与后端响应匹配

**前端类型文件**: `web/frontend/src/api/types/generated-types.ts`

```typescript
// 预期的Industry接口
export interface Industry {
  industry_name: string;
  industry_code: string;
  description?: string;
  stock_count?: number;
}

// 预期的Concept接口
export interface Concept {
  concept_name: string;
  concept_code: string;
  description?: string;
}

// 预期的StockBasic接口
export interface StockBasic {
  symbol: string;
  name: string;
  industry?: string;
  market?: string;
  // ... 其他字段
}
```

**验证步骤**:
1. 读取前端类型定义文件
2. 对比后端实际响应字段
3. 记录不匹配的字段

**验证脚本**:
```bash
# 1. 获取后端实际响应
curl -s -H "Authorization: Bearer dev-mock-token-for-development" \
     http://localhost:8000/api/v1/data/stocks/industries | \
  jq '.data[0]' > /tmp/backend_industry_sample.json

# 2. 提取字段名称
cat /tmp/backend_industry_sample.json | jq 'keys'

# 3. 手动对比前端类型定义
cat web/frontend/src/api/types/generated-types.ts | grep -A 10 "interface Industry"
```

**通过标准**:
- ✅ 后端字段名称与前端类型定义一致
- ✅ 字段类型匹配（字符串/数字/布尔等）
- ✅ 可选字段标记正确（`?`）

**失败处理**:
- 🟠 如果字段不匹配 → 记录不匹配详情
- 📊 问题类型: 前后端契约不一致
- 📝 修复选项：
  - 修改前端类型定义（推荐）
  - 修改后端响应字段（需评估影响）
  - 添加前端Adapter适配（临时方案）

---

### 阶段4: 自动化测试脚本创建（Day 2下午）

#### 4.1 创建Pytest测试套件

**文件**: `tests/contract/test_phase21_apis.py`

```python
"""
Phase 2.1 API契约测试套件
测试行业/概念/股票基础信息API
"""

import pytest
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "dev-mock-token-for-development"

class TestPhase21IndustryConcept:
    """Phase 2.1: 行业与概念API测试"""

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    def test_2_1_1_industries_endpoint_exists(self):
        """测试: /api/v1/data/stocks/industries 端点存在性"""
        response = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/industries",
            headers=self.headers
        )

        # Layer 1: 端点存在性
        assert response.status_code != 404, "端点不存在"
        assert response.status_code != 405, "方法不支持"

    def test_2_1_1_industries_response_format(self):
        """测试: 行业列表响应格式"""
        response = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/industries",
            headers=self.headers
        )

        assert response.status_code == 200, f"Unexpected status: {response.status_code}"

        data = response.json()

        # Layer 2: 契约格式验证
        assert "code" in data, "Missing 'code' field"
        assert "message" in data, "Missing 'message' field"
        assert "data" in data, "Missing 'data' field"

        # 数据应该是数组
        assert isinstance(data["data"], list), "data should be an array"

    def test_2_1_1_industries_response_time(self):
        """测试: 行业列表响应时间"""
        import time

        start = time.time()
        response = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/industries",
            headers=self.headers
        )
        duration_ms = (time.time() - start) * 1000

        # Layer 3: 性能验证
        assert duration_ms < 300, f"响应过慢: {duration_ms}ms > 300ms"

    def test_2_1_1_industries_data_integrity(self):
        """测试: 行业列表数据完整性"""
        response = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/industries",
            headers=self.headers
        )

        data = response.json()

        # Layer 4: 数据完整性验证
        if len(data["data"]) > 0:
            first_item = data["data"][0]

            # 验证必需字段
            assert "industry_name" in first_item or "industry_code" in first_item, \
                "Missing required fields (industry_name or industry_code)"

            # 验证数据合理性
            if "industry_name" in first_item:
                assert isinstance(first_item["industry_name"], str), \
                    "industry_name should be string"
                assert len(first_item["industry_name"]) > 0, \
                    "industry_name should not be empty"

    def test_2_1_2_concepts_endpoint_exists(self):
        """测试: /api/v1/data/stocks/concepts 端点存在性"""
        response = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/concepts",
            headers=self.headers
        )

        assert response.status_code != 404, "端点不存在"
        assert response.status_code != 405, "方法不支持"

    def test_2_1_2_concepts_response_format(self):
        """测试: 概念列表响应格式"""
        response = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/concepts",
            headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "code" in data
        assert "message" in data
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_2_1_2_concepts_response_time(self):
        """测试: 概念列表响应时间"""
        import time

        start = time.time()
        response = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/concepts",
            headers=self.headers
        )
        duration_ms = (time.time() - start) * 1000

        assert duration_ms < 300, f"响应过慢: {duration_ms}ms > 300ms"

    def test_2_1_3_stocks_basic_endpoint_exists(self):
        """测试: /api/v1/data/stocks/basic 端点存在性"""
        response = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/basic?page=1&page_size=20",
            headers=self.headers
        )

        assert response.status_code != 404, "端点不存在"
        assert response.status_code != 405, "方法不支持"

    def test_2_1_3_stocks_basic_response_format(self):
        """测试: 股票基础信息响应格式"""
        response = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/basic?page=1&page_size=20",
            headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "code" in data
        assert "message" in data
        assert "data" in data

        # 验证分页信息（如果有）
        if isinstance(data["data"], dict) and "items" in data["data"]:
            assert "items" in data["data"]
            assert "total" in data["data"]

    def test_2_1_3_stocks_basic_response_time(self):
        """测试: 股票基础信息响应时间"""
        import time

        start = time.time()
        response = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/basic?page=1&page_size=20",
            headers=self.headers
        )
        duration_ms = (time.time() - start) * 1000

        assert duration_ms < 500, f"响应过慢: {duration_ms}ms > 500ms"

    def test_2_1_3_stocks_basic_pagination(self):
        """测试: 股票基础信息分页功能"""
        # 测试第一页
        response1 = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/basic?page=1&page_size=10",
            headers=self.headers
        )
        data1 = response1.json()

        # 测试第二页
        response2 = requests.get(
            f"{BASE_URL}/api/v1/data/stocks/basic?page=2&page_size=10",
            headers=self.headers
        )
        data2 = response2.json()

        # 两页数据不应该完全相同（如果有足够数据）
        if isinstance(data1["data"], list) and isinstance(data2["data"], list):
            if len(data1["data"]) > 0 and len(data2["data"]) > 0:
                assert data1["data"][0] != data2["data"][0], \
                    "Pagination not working correctly"
```

#### 4.2 执行自动化测试

```bash
# 运行Phase 2.1测试套件
pytest tests/contract/test_phase21_apis.py -v

# 生成覆盖率报告
pytest tests/contract/test_phase21_apis.py \
      --cov=web/frontend/src/api \
      --cov-report=html \
      --cov-report=term

# 查看HTML报告
firefox htmlcov/index.html
```

---

## 📊 验证结果报告

### 报告文件位置

**进度跟踪**: `docs/reports/API_VERIFICATION_PROGRESS.md`

**问题汇总**: `docs/reports/API_VERIFICATION_ISSUES.md`

### 报告模板

```markdown
# API契约验证进度报告 - Phase 2.1

**验证日期**: 2026-01-02
**验证范围**: 3个API端点
**执行者**: Main CLI (Claude Code)

## 验证结果汇总

| API端点 | Layer 1 | Layer 2 | Layer 3 | Layer 4 | 契约匹配 | 总体状态 |
|---------|---------|---------|---------|---------|----------|----------|
| /api/v1/data/stocks/industries | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ 通过 |
| /api/v1/data/stocks/concepts | ✅ | ✅ | ⚠️ | ⏳ | ⏳ | 🟡 部分通过 |
| /api/v1/data/stocks/basic | ✅ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ 进行中 |

**状态图例**:
- ✅ 通过
- ⏳ 待验证
- ⚠️ 警告（非阻塞）
- ❌ 失败（阻塞）
- 🟡 部分通过

## 详细验证结果

### API 1: /api/v1/data/stocks/industries

**Layer 1: 端点存在性**
- 状态: ✅ 通过
- HTTP状态码: 200
- 响应时间: 156ms

**Layer 2: 契约格式验证**
- 状态: ✅ 通过
- UnifiedResponse格式: 符合
- 字段完整性: 完整

**Layer 3: 性能验证**
- 状态: ✅ 通过
- 响应时间: 156ms (<300ms目标)

**Layer 4: 数据完整性验证**
- 状态: ✅ 通过
- 数据数量: 52个行业
- 数据质量: 真实数据（非Mock）
- 字段验证:
  - `industry_name`: ✅ 字符串，非空
  - `industry_code`: ✅ 字符串，格式正确
  - `description`: ✅ 可选字段
  - `stock_count`: ✅ 数字，合理范围

**契约匹配验证**
- 状态: ✅ 通过
- 前端类型: `Industry`接口
- 字段匹配: 完全一致
- 类型匹配: 完全一致

**结论**: ✅ 该API已准备好用于Phase 2.1执行

---

### API 2: /api/v1/data/stocks/concepts

**Layer 1: 端点存在性**
- 状态: ✅ 通过
- HTTP状态码: 200

**Layer 2: 契约格式验证**
- 状态: ✅ 通过

**Layer 3: 性能验证**
- 状态: ⚠️ 警告
- 响应时间: 720ms (>300ms目标)
- 优化建议: 添加数据库索引或启用缓存

**Layer 4: 数据完整性验证**
- 状态: ⏳ 待验证
- 原因: 性能问题待优化后重新测试

**结论**: 🟡 需要性能优化后重新验证

---

### API 3: /api/v1/data/stocks/basic

**Layer 1: 端点存在性**
- 状态: ✅ 通过

**Layer 2-4**: ⏳ 待验证

---

## 问题汇总

### 🔴 Critical Issues (阻塞Phase 2)

**无**

### 🟠 High Priority Issues

**Issue #1: 概念API响应时间过长**
- **端点**: `/api/v1/data/stocks/concepts`
- **发现时间**: 2026-01-02 14:30
- **问题**: 响应时间720ms (目标<300ms)
- **影响**: 用户体验较差
- **建议**: 添加数据库索引或启用Redis缓存
- **状态**: ⏳ 待优化
- **优先级**: P1

### 🟡 Medium Priority Issues

**无**

## 下一步行动

1. ✅ **已完成**: Phase 2.1 API验证执行
2. ⏳ **进行中**: 性能优化（概念API）
3. ⏳ **待办**: 优化后重新验证
4. ⏳ **待办**: 生成最终验证报告

## 成功标准确认

- [x] Phase 2.1的3个API全部通过Layer 1验证
- [x] 无Critical Issues遗留
- [x] 数据守卫者机制已建立
- [ ] 所有API响应时间<500ms
- [ ] 所有API返回真实数据
- [ ] 前后端契约完全匹配

**当前状态**: 🟡 Phase 2.1验证进行中（性能优化阶段）
**预计完成**: 优化完成后1个工作日内完成最终验证
```

---

## 🚨 数据守卫者协调机制

### Critical Issue触发条件

遇到以下情况时，**立即报告用户**：

1. **API端点不存在** (404/405)
2. **数据库表不存在或为空**
3. **认证失败** (401/403)
4. **服务器内部错误** (500/502)
5. **响应超时** (>5秒)

### 用户交互示例

```
Claude: 🔴 发现Critical Issue！
      API端点: /api/v1/data/stocks/industries
      问题: HTTP 500 - "relation 'stock_industries' does not exist"

      📢 请您确认：
      1. 数据库中是否存在stock_industries表？
      2. 是否需要运行数据导入脚本？
      3. 或者暂时使用Mock数据？

      ⏸️ 我已暂停API验证，等待您的指示。

用户: 明白了。数据库表还没创建。你先暂停验证，
      我现在运行数据导入脚本，完成后通知你继续。

Claude: ✅ 已暂停API验证。等待数据库准备完成通知...
      预计时间: 用户提示24小时内完成
      下一步: 收到通知后重新执行Layer 1验证
```

### 问题分级与响应时间

| 级别 | 症状 | 行动 | 预期响应时间 |
|------|------|------|--------------|
| 🔴 Critical | API不可用、数据缺失 | 立即报告用户，暂停验证 | 24小时 |
| 🟠 High | 性能差、格式不匹配 | 记录问题，继续验证，汇总报告 | 48小时 |
| 🟡 Medium | 缺少优化建议 | 记录优化建议，Phase 2前处理 | 72小时 |

---

## 📅 时间表与里程碑

### Week 1: Phase 2.1 API验证 (3天)

**Day 1 (2026-01-02)**:
- ✅ 上午: 环境准备，确认数据库状态
- ✅ 下午: 执行Layer 1-4验证（3个API）
- ✅ 晚上: 生成初步验证报告

**Day 2 (2026-01-03)**:
- ⏳ 上午: 契约匹配验证，创建自动化测试
- ⏳ 下午: 执行自动化测试，问题汇总

**Day 3 (2026-01-04)**:
- ⏳ 全天: 问题修复，重新验证
- ✅ 目标: Phase 2.1验证完成，进入Phase 2.2

### Week 2-3: Phase 2.2-2.3 API验证 (5-7天)

**策略**: 滚动式验证，每个Phase子模块独立验证

---

## ✅ 成功标准

Phase 2.1验证完成的成功标准：

- [ ] 所有3个API通过4层验证
- [ ] 无Critical Issues遗留
- [ ] High Priority Issues有明确的解决方案
- [ ] 自动化测试套件创建完成
- [ ] 验证报告文档完整
- [ ] 用户数据守卫者机制已验证
- [ ] 可以安全进入Phase 2.1执行

---

**文档版本**: v1.0
**创建日期**: 2026-01-02
**最后更新**: 2026-01-02
**维护者**: Main CLI (Claude Code)
**状态**: 🎯 Ready to Execute
**下一步**: 询问用户数据库准备状态，然后开始执行验证
