# Web端适配器依赖分析报告

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


**分析日期**: 2025-10-20
**目的**: 明确Web端功能对各适配器的依赖关系，为精简决策提供数据支持

---

## 📊 执行摘要

### 核心发现

**Web端共依赖4个适配器**:
- ✅ **2个主库适配器** (来自 `/adapters/`)
  - `akshare_adapter` - 财务数据、K线数据
  - `tdx_adapter` - 实时行情

- ✅ **2个Web专用适配器** (来自 `/web/backend/app/adapters/`)
  - `wencai_adapter` - 问财选股功能
  - `tqlex_adapter` - 竞价抢筹数据

### 关键洞察

1. **主库适配器（akshare, tdx）**:
   - 属于三层架构的**核心层**
   - Web端高度依赖，**不可精简**
   - 影响多个核心功能

2. **Web专用适配器（wencai, tqlex）**:
   - **独立于主库**适配器体系
   - 仅供Web端使用，CLI/Jupyter不依赖
   - 可以**独立决策**是否保留

---

## 第1部分：主库适配器依赖分析

### 1.1 Akshare适配器

**依赖位置**: `/adapters/akshare_adapter.py`

**Web端使用文件**:
```
/web/backend/app/api/data.py:316
/web/backend/app/services/data_service.py:36
```

**提供功能**:

#### 功能1: 财务报表查询
**文件**: `app/api/data.py`
**代码示例**:
```python
from adapters.akshare_adapter import AkshareDataSource
ak = AkshareDataSource()

# 支持的报表类型
if report_type == "balance":
    df = ak.get_balance_sheet(symbol)       # 资产负债表
elif report_type == "income":
    df = ak.get_income_statement(symbol)    # 利润表
elif report_type == "cashflow":
    df = ak.get_cashflow_statement(symbol)  # 现金流量表
```

**影响范围**:
- API端点: `/api/v1/data/financial-reports/{symbol}`
- 前端功能: 财务报表查看器

#### 功能2: 历史K线数据
**文件**: `app/services/data_service.py`
**代码示例**:
```python
from adapters.akshare_adapter import AkshareDataSource
ak = AkshareDataSource()

# 获取日K线数据
df = ak.get_daily_data(
    symbol=symbol,
    start_date=start_date,
    end_date=end_date
)
```

**影响范围**:
- API端点: `/api/v1/data/kline`
- 前端功能: K线图表、技术分析

#### 精简影响评估

| 维度 | 评估结果 |
|------|---------|
| **依赖程度** | ⚠️ 高度依赖 |
| **功能重要性** | 🔥 核心功能 |
| **可替代性** | ❌ 难以替代 |
| **用户影响** | 🚨 重大影响 - 财务分析和K线功能完全失效 |
| **精简建议** | ❌ **不可精简** - 属于核心层，必须保留 |

---

### 1.2 TDX适配器

**依赖位置**: `/adapters/tdx_adapter.py`

**Web端使用文件**:
```
/web/backend/app/api/market.py:240
/web/backend/app/services/tdx_service.py:16
```

**提供功能**:

#### 功能1: 实时行情查询
**文件**: `app/api/market.py`
**代码示例**:
```python
from adapters.tdx_adapter import TDXDataSource
tdx = TDXDataSource()

# 获取实时行情
quote_data = tdx.get_real_time_data(symbol)
```

**影响范围**:
- API端点: `/api/v1/market/quotes/realtime`
- 前端功能: 实时行情展示、涨跌幅监控

#### 功能2: 批量行情查询
**文件**: `app/services/tdx_service.py`
**用途**:
- 热门股票监控
- 自选股实时更新
- 行情推送服务

#### 精简影响评估

| 维度 | 评估结果 |
|------|---------|
| **依赖程度** | ⚠️ 高度依赖 |
| **功能重要性** | 🔥 核心功能 |
| **可替代性** | ⚠️ 可替代但需要开发 |
| **用户影响** | 🚨 重大影响 - 实时行情功能完全失效 |
| **精简建议** | ❌ **不可精简** - 属于核心层，必须保留 |

**替代方案**（如必须替代）:
- 使用 `akshare` 的实时行情接口（延迟可能更高）
- 使用 `financial_adapter` 的双数据源（efinance + easyquotation）

---

## 第2部分：Web专用适配器依赖分析

### 2.1 Wencai适配器 ⭐

**依赖位置**: `/web/backend/app/adapters/wencai_adapter.py`

**特点**:
- ✅ **Web专用** - CLI/Jupyter不依赖
- ✅ **独立实现** - 不在主库适配器中
- ✅ **可选功能** - 非核心交易数据

**Web端使用文件**:
```
/web/backend/app/services/wencai_service.py:25
/web/backend/app/api/wencai.py
/web/backend/app/tasks/wencai_tasks.py
```

**提供功能**:

#### 功能1: 问财选股
**API端点**: `/api/v1/wencai/query`

**功能描述**:
```python
from app.adapters.wencai_adapter import WencaiDataSource

wencai = WencaiDataSource()
# 使用自然语言查询股票
result = wencai.query(
    query_text="市盈率小于20且ROE大于15%的股票",
    pages=1
)
```

**支持的查询模式**:
- 自然语言选股（"市盈率小于20"）
- 技术指标筛选（"MACD金叉且成交量放大"）
- 基本面筛选（"ROE大于15%且负债率小于50%"）

**数据存储**:
- 数据库: PostgreSQL (mystocks)
- 表名: `wencai_qs_1` ~ `wencai_qs_9` (9个查询结果表)

#### 功能2: 查询历史记录
**API端点**: `/api/v1/wencai/history`

**功能描述**:
- 保存用户的问财查询历史
- 支持重复执行历史查询
- 提供查询结果缓存

#### 功能3: 定时任务
**文件**: `app/tasks/wencai_tasks.py`

**功能描述**:
- 定期执行预设查询
- 自动更新选股结果
- 发送变化提醒

#### 精简影响评估

| 维度 | 评估结果 |
|------|---------|
| **依赖程度** | ✅ Web专用，主系统不依赖 |
| **功能重要性** | ⚠️ 增强功能（非核心） |
| **可替代性** | ✅ 可用其他选股方式替代 |
| **用户影响** | ⚠️ 中等影响 - 失去便捷选股工具 |
| **精简建议** | ⚠️ **可考虑精简** - 需调研用户使用频率 |

**精简选项**:

**选项A: 完全保留**
- ✅ 保持当前功能
- ❌ 维护成本持续
- 适用于：高频使用用户

**选项B: 简化保留**
- ✅ 保留核心查询功能
- ❌ 取消定时任务、历史记录
- ✅ 减少50%维护成本

**选项C: 归档**
- ✅ 代码保留
- ❌ 功能暂停
- ✅ 可快速恢复
- 适用于：低频使用场景

---

### 2.2 TQlex适配器 ⭐

**依赖位置**: `/web/backend/app/adapters/tqlex_adapter.py`

**特点**:
- ✅ **Web专用** - CLI/Jupyter不依赖
- ✅ **独立实现** - 不在主库适配器中
- ⚠️ **需要Token** - 依赖外部服务认证

**Web端使用文件**:
```
/web/backend/app/services/market_data_service.py:24
```

**提供功能**:

#### 功能1: 竞价抢筹数据
**API端点**: `/api/v1/market/chip-race`

**功能描述**:
```python
from app.adapters.tqlex_adapter import TqlexDataSource

tqlex = TqlexDataSource(token=os.getenv('TQLEX_TOKEN'))
# 获取早盘抢筹数据
df = tqlex.get_chip_race_open(date='2025-10-20')
```

**数据特点**:
- 竞价阶段资金流向
- 大单追踪
- 抢筹强度分析

**外部依赖**:
- API: `http://excalc.icfqs.com:7616/TQLEX`
- 认证: 需要 `TQLEX_TOKEN` 环境变量
- 费用: 可能需要付费订阅

#### 精简影响评估

| 维度 | 评估结果 |
|------|---------|
| **依赖程度** | ✅ Web专用，主系统不依赖 |
| **功能重要性** | ⚠️ 高级功能（小众需求） |
| **可替代性** | ✅ 不影响基础交易功能 |
| **用户影响** | ✅ 低影响 - 失去高级分析工具 |
| **外部依赖** | ❌ 需要Token和外部API |
| **精简建议** | ✅ **优先考虑精简** - 使用率需验证 |

**精简选项**:

**选项A: 条件保留**
- ✅ 有Token且高频使用 → 保留
- ❌ 无Token或低频使用 → 归档

**选项B: 归档**
- ✅ 代码保留在 `/web/backend/app/adapters/archived/`
- ✅ 需要时可快速恢复（<5分钟）
- ✅ 减少外部API依赖风险

---

## 第3部分：依赖关系总览

### 3.1 适配器层级划分

```
┌─────────────────────────────────────────────────────┐
│          Web Backend 适配器依赖                      │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
    ┌────▼────┐                   ┌─────▼─────┐
    │ 主库适配器 │                   │ Web专用适配器│
    └─────────┘                   └───────────┘
         │                               │
    ┌────┴────┐                   ┌─────┴─────┐
    │         │                   │           │
┌───▼──┐  ┌──▼──┐          ┌─────▼────┐ ┌───▼────┐
│akshare│  │ tdx │          │  wencai  │ │ tqlex  │
└──────┘  └─────┘          └──────────┘ └────────┘
   │          │                  │           │
   │          │                  │           │
核心层     核心层            可选层       可选层
不可精简   不可精简          可考虑      优先精简
```

### 3.2 功能-适配器映射表

| Web功能 | 依赖适配器 | 重要性 | 精简建议 |
|---------|-----------|--------|---------|
| 财务报表查询 | akshare | 🔥 核心 | ❌ 必须保留 |
| 历史K线图表 | akshare | 🔥 核心 | ❌ 必须保留 |
| 实时行情展示 | tdx | 🔥 核心 | ❌ 必须保留 |
| 批量行情监控 | tdx | 🔥 核心 | ❌ 必须保留 |
| 问财选股 | wencai | ⚠️ 增强 | ⚠️ 需调研 |
| 选股历史记录 | wencai | ⚠️ 增强 | ⚠️ 可简化 |
| 竞价抢筹分析 | tqlex | ✅ 高级 | ✅ 可精简 |

---

## 第4部分：精简决策框架

### 4.1 决策矩阵

根据以下维度评估每个适配器：

| 适配器 | 使用范围 | 功能重要性 | 替代难度 | 维护成本 | **决策建议** |
|--------|---------|-----------|---------|---------|-------------|
| **akshare** | 主库+Web | 核心 | 高 | 中 | ❌ **必须保留（核心层）** |
| **tdx** | 主库+Web | 核心 | 中 | 中 | ❌ **必须保留（核心层）** |
| **wencai** | 仅Web | 增强 | 低 | 中 | ⚠️ **需用户调研** |
| **tqlex** | 仅Web | 高级 | 低 | 低 | ✅ **建议归档（可选层）** |

### 4.2 用户调研问题（针对Web专用适配器）

#### Wencai适配器决策问题

**Q1: 您使用问财选股功能吗？**
- [ ] 经常使用（每天/每周）→ **建议保留**
- [ ] 偶尔使用（每月）→ **可简化保留**
- [ ] 很少使用 → **建议归档**
- [ ] 从不使用 → **优先归档**

**Q2: 如果取消问财功能，是否可接受？**
- [ ] 不可接受，核心功能 → **必须保留**
- [ ] 有影响，但可用其他方式 → **可考虑归档**
- [ ] 无影响 → **优先归档**

**Q3: 您主要用问财做什么？**
- [ ] 基本面筛选（ROE、市盈率等）→ 可用DataFrame过滤替代
- [ ] 技术指标筛选（MACD、均线等）→ 可用技术分析库替代
- [ ] 复杂自然语言查询 → 较难替代，建议保留

#### TQlex适配器决策问题

**Q1: 您使用竞价抢筹功能吗？**
- [ ] 经常使用 → **建议保留**
- [ ] 偶尔使用 → **可保留**
- [ ] 从不使用 → **优先归档**

**Q2: 您有TQLEX_TOKEN吗？**
- [ ] 有，且在使用 → **建议保留**
- [ ] 有，但不常用 → **可归档**
- [ ] 没有 → **优先归档**

**Q3: 如果取消此功能，是否可接受？**
- [ ] 不可接受 → **保留**
- [ ] 可接受 → **归档**

---

## 第5部分：精简方案建议

### 方案A: 激进精简（推荐）⭐

**主库适配器**:
- ✅ akshare - 保留（核心层）
- ✅ tdx - 保留（核心层）

**Web专用适配器**:
- ⚠️ wencai - **归档**
  - 移动到 `/web/backend/app/adapters/archived/`
  - 代码保留，功能禁用
  - 需要时可快速恢复

- ✅ tqlex - **归档**
  - 移动到 `/web/backend/app/adapters/archived/`
  - 代码保留，功能禁用

**收益**:
- 减少2个Web专用适配器维护
- 减少外部API依赖（TQLEX）
- 降低复杂度

**风险**:
- 失去问财选股便捷性
- 失去竞价抢筹分析

**适用场景**:
- 用户很少使用问财和竞价功能
- 优先考虑系统简洁性

---

### 方案B: 保守精简

**主库适配器**:
- ✅ akshare - 保留（核心层）
- ✅ tdx - 保留（核心层）

**Web专用适配器**:
- ✅ wencai - **保留**（简化版）
  - 保留核心查询功能
  - 取消定时任务
  - 取消历史记录功能

- ⚠️ tqlex - **归档**
  - 使用频率低，优先归档

**收益**:
- 保留常用的问财功能
- 减少1个外部API依赖

**风险**:
- wencai维护成本持续
- 问财API可能变化需要适配

**适用场景**:
- 用户经常使用问财功能
- 不使用竞价抢筹

---

### 方案C: 最小精简（保守）

**主库适配器**:
- ✅ akshare - 保留（核心层）
- ✅ tdx - 保留（核心层）

**Web专用适配器**:
- ✅ wencai - **完全保留**
- ✅ tqlex - **完全保留**

**收益**:
- 100%功能保留
- 用户体验无变化

**风险**:
- 维护成本不变
- 系统复杂度不变

**适用场景**:
- 所有功能都有高频使用
- 不考虑精简

---

## 第6部分：实施指南

### 6.1 如果归档wencai适配器

**步骤1: 代码移动**
```bash
cd /opt/claude/mystocks_spec/web/backend/app/adapters
mkdir -p archived
mv wencai_adapter.py archived/
```

**步骤2: 禁用相关API**
```python
# 在 app/api/wencai.py 中添加
@router.get("/status")
def wencai_status():
    return {
        "available": False,
        "message": "问财功能已归档，如需使用请联系管理员"
    }
```

**步骤3: 前端提示**
```javascript
// 在前端显示功能已禁用
if (response.available === false) {
  showMessage("问财选股功能暂不可用");
}
```

**回滚**: 移回原位置即可，<5分钟

---

### 6.2 如果归档tqlex适配器

**步骤1: 代码移动**
```bash
cd /opt/claude/mystocks_spec/web/backend/app/adapters
mv tqlex_adapter.py archived/
```

**步骤2: 移除环境变量（可选）**
```bash
# 从 .env 中移除
# TQLEX_TOKEN=xxx
```

**步骤3: 禁用相关API**
```python
# 在 app/api/market.py 中
@router.get("/chip-race")
def chip_race_status():
    return {
        "available": False,
        "message": "竞价抢筹功能已归档"
    }
```

**回滚**: 移回原位置 + 恢复环境变量，<5分钟

---

## 第7部分：决策检查清单

### Web专用适配器决策清单

**Wencai适配器决策**:
- [ ] 已调研用户使用频率
- [ ] 已评估替代方案可行性
- [ ] 已确认前端UI调整方案
- [ ] 已准备回滚方案
- [ ] **决策**: [ ] 保留 [ ] 简化 [ ] 归档

**TQlex适配器决策**:
- [ ] 已确认Token配置状态
- [ ] 已评估使用频率
- [ ] 已确认外部API依赖风险
- [ ] 已准备回滚方案
- [ ] **决策**: [ ] 保留 [ ] 归档

**主库适配器确认**:
- [x] akshare - 核心层，不精简
- [x] tdx - 核心层，不精简

---

## 📊 总结

### 核心结论

1. **主库适配器（akshare, tdx）**:
   - ❌ **不可精简** - Web端核心功能强依赖
   - 属于三层架构的核心层
   - 影响财务分析、K线、实时行情等核心功能

2. **Web专用适配器（wencai, tqlex）**:
   - ✅ **可独立决策** - 不影响主系统
   - 需基于用户实际使用频率决策
   - 归档后可快速恢复（<5分钟）

### 推荐路径

**第1步**: 先精简TQlex（风险低）
- 使用率低
- 有外部依赖
- 功能非核心

**第2步**: 调研Wencai使用情况
- 发放用户调研问卷
- 根据结果决定保留/简化/归档

**第3步**: 持续保持主库适配器
- akshare和tdx必须保留
- 定期维护和更新

---

**报告版本**: v1.0
**创建日期**: 2025-10-20
**维护者**: 技术团队

**下一步行动**:
1. 阅读 `ADAPTER_FUNCTION_SURVEY.md` 准备用户调研
2. 填写决策检查清单
3. 团队讨论并决策
