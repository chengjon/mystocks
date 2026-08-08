# MyStocks 全页面自动化测试方案

> 版本: v1.0 | 日期: 2026-07-15
> 参考: Obsidian `全页面 Claude 自动化测试整体方案.md`
> 测试对象: 40 页面 × ~439 元素

---

## 一、测试架构

采用 **双层互补** 策略：

| 层 | 名称 | 技术 | 覆盖 | 限制 |
|---|------|------|------|------|
| L1 | API 数据探针 | Python requests → 后端 API | Stat/Chart/Table 等数据源元素 | 仅验证后端，不验证前端渲染 |
| L2 | 浏览器渲染 | 现有 Playwright E2E 测试 | DOM 渲染、交互、路由 | 需登录认证 |

### 为什么不用远程 Playwright 做全页面渲染测试

远程 Playwright 服务（`firecrawl-playwright`）通过 `/scrape` 返回渲染后 HTML，但 SPA 有 auth guard，未登录只能看到 Login 页面。远程服务不支持 cookie 注入或多步交互，无法通过认证。

**因此 L1（API 直连）是主力测试手段**，L2 依赖现有的本地 Playwright E2E 测试补充交互测试。

---

## 二、L1 API 数据探针体系

### 2.1 原理

每个元素在 `PAGE_ELEMENT_INDEX.md` 中标注了数据来源（如 `marketData.shanghai`、`heatmapOption`）。这些数据源最终通过后端 API 获取。我们直接调用后端 API，验证返回数据格式和内容。

### 2.2 元素 → API 映射规则

| 数据来源模式 | 对应 API | 示例 |
|-------------|---------|------|
| `marketData.*` | `GET /api/v1/market/overview` | A1-17 上证指数 |
| `marketData.fundFlow.*` | `GET /api/v1/market/fund-flow` | A1-11 沪股通 |
| `*Data` 结尾 | `GET /api/v1/` + 模块路径 | B1-11 indexData |
| `*Option` 结尾（图表） | 同上，检查数组非空 | A1-15 fundFlowChartOption |
| `*List` / `*Count` | 同上 | D1-02 boardData.length |
| `pageStatusText` | 页面级状态，检查 composable | B1-01 |
| 静态 | 无 API，跳过 | A1-01 |

### 2.3 故障判定（与参考方案对齐）

| 等级 | 标准 | API 探针判定 |
|------|------|-------------|
| **P0 阻断** | 核心数据完全缺失 | API 返回 4xx/5xx、`data` 字段为空数组、关键字段为 null |
| **P1 严重** | 数据存在但异常 | 数值超出合理范围、字段类型错误、图表数据为空 |
| **P2 轻微** | 部分辅助数据缺失 | 次要列表部分空、非核心字段缺失 |
| **P3 兼容** | 降级可用 | 有 fallback 值、静态兜底文案正常 |

---

## 三、分批执行计划

| 批次 | 模块 | 页面数 | 预估 API 端点 | 执行顺序 |
|------|------|--------|-------------|---------|
| 0 | **A1 试点** | 1 | ~8 | ✅ 立即执行 |
| 1 | B 市场行情 | 3 | ~5 | 第1轮 |
| 2 | C 股票 | 3 | ~4 | 第1轮 |
| 3 | D 数据分析 | 4 | ~5 | 第1轮 |
| 4 | E 自选管理 | 3 | ~4 | 第2轮 |
| 5 | F 策略管理 | 7 | ~10 | 第2轮（重型） |
| 6 | G 交易管理 | 5 | ~6 | 第2轮 |
| 7 | H 风险管理 | 6 | ~8 | 第3轮 |
| 8 | I 系统设置 | 4 | ~5 | 第3轮 |
| 9 | J 详情页 | 2 | ~3 | 第3轮 |
| 10 | K+L 独立页 | 2 | ~2 | 第3轮 |
| **合计** | | **40** | **~60** | |

---

## 四、A1 试点测试（立即执行）

### 4.1 测试对象

A1（交易室 Dashboard），48 个元素。

### 4.2 API 探针清单

| 元素 | API | 验证点 |
|------|-----|--------|
| A1-03 | `/health` 或 ws 状态 | marketStatus 非空 |
| A1-04/05 | `/api/v1/strategy/strategies?status=active` | 策略数量 > 0 |
| A1-11~14 | `/api/v1/market/fund-flow` | hgt/sgt/northTotal/mainForce 有金额 |
| A1-17~19 | `/api/v1/market/quotes?symbol=000001` | 三大指数有值 |
| A1-22 | 同上 | northFund 有值 |
| A1-25 | `/api/v1/market/overview` | stocks.up/down 有值 |
| A1-26 | 同上 | volume.amount 有值 |
| A1-28 | `/api/v1/indicators/registry` | indicatorList 非空 |
| A1-31 | `/api/akshare_market/boards` | heatmapOption 数据非空 |
| A1-39 | `/api/v1/market/lhb?limit=5` | 龙虎榜数据非空 |
| A1-40 | `/api/v2/market/blocktrade?limit=5` | 大宗交易数据非空 |

### 4.3 输出格式

```
A1 测试报告
得分: XX/100
P0: X个  P1: X个  P2: X个  P3: X个
| 元素 | API | 状态 | 详情 |
```

---

## 五、测试脚本 `scripts/dev/page_api_probe.py`

基于 `browser_smoke.py` 框架扩展：遍历 PAGE_ELEMENT_INDEX.md 中每个元素的 dataSource，映射到 API 端点并发探测，输出结构化报告。

### 用法

```bash
python scripts/dev/page_api_probe.py           # 全量 40 页
python scripts/dev/page_api_probe.py --page A1  # 单页
python scripts/dev/page_api_probe.py --group B  # 模块
python scripts/dev/page_api_probe.py --json     # CI 输出
```

### 报告归档

- `reports/test/A1-api-probe-YYYYMMDD.json`
- `reports/test/module-B-summary.md`
- `reports/test/global-all-bugs.json`

---

## 六、与现有 E2E 测试的分工

| 测试类型 | 工具 | 负责 | 频率 |
|---------|------|------|------|
| API 数据探针 | `page_api_probe.py` | 数据可用性，全量覆盖 | 每次部署 / 每日 |
| 浏览器 smoke | `browser_smoke.py` | 前端可达性 | 每次部署 |
| 浏览器 E2E | 现有 Playwright tests | 交互流程、DOM 渲染 | CI / 按需 |

---

## 七、下一步

1. **立即**: 执行 A1 试点 → 生成第一份 API 探针报告
2. **今天**: 编写 `page_api_probe.py` 通用探针脚本
3. **本周**: 分批执行 B~L 全量探针
4. **持续**: 发现问题 → 更新 PAGE_ELEMENT_INDEX.md 标注 → 回归测试
