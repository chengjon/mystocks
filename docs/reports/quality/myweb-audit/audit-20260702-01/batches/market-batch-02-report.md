# Market Batch 02 Report — audit-20260702-01

**Generated**: 2026-07-02
**Batch**: market-batch-02
**Pages**: /data/industry, /data/concept, /data/fund-flow, /data/indicator
**Module**: data
**Audit run**: audit-20260702-01
**Verification surface**: live-audit (PM2 frontend pid 2040733 + backend pid 1888757)
**B4.014 relevance**: mixed (industry/concept legacy akshare; fund-flow P1.1 migrated; indicator orthogonal)

---

## 1. 执行摘要

| 维度 | 通过 | 警告 | 失败 | 未测试 |
|------|------|------|------|--------|
| route-inventory | 4 | 0 | 0 | 0 |
| functional-audit | 2 | 0 | 2 | 0 |
| data-state-audit | 2 | 1 | 1 | 0 |
| visual-artdeco-audit | 3 | 1 | 0 | 0 |
| responsive-a11y-audit | 4 | 0 | 0 | 0 |

**总计**: 9 findings (2 blocking, 2 high, 2 medium, 3 low)

---

## 2. B4.014 关键验证

### ✅ 已验证生效的 B4.014 fixes (batch-01 持续生效)
- LHB fix (commit af29d15d6) 仍正常工作
- 前端 trim 检查 (market-realtime-001 fix) 仍正常

### ⚠️ Data module 现状

| Page | Source chain | 状态 |
|------|-------------|------|
| /data/industry | legacy akshare (非 factory) | 数据真实 |
| /data/concept | legacy akshare (非 factory) | 数据真实,leader 字段空 |
| /data/fund-flow | P1.1 OpenStock (fund_flow.py 迁移) + legacy /akshare/market/fund-flow/* 端点 | 401 阻塞 |
| /data/indicator | N/A (页面 redirect 到 /dashboard) | 不可访问 |

**结论**: data 模块主要走 legacy akshare 链,不在 B4.014 factory 范围。
fund-flow 路由层面仍走 /akshare/* 端点(未统一到 /api/v1/market/fund-flow/*),需 trace。

---

## 3. Top 问题

### 🚫 #1 [BLOCKING] data-fund-flow-001: 401 Not authenticated
- `/api/akshare/market/fund-flow/big-deal` 和 `/hsgt-summary` 返回 401
- localStorage auth_token 存在,手动带 header 请求 → 200 OK 真实数据
- 根因:页面 apiClient 请求未注入 Authorization(需 trace exec 包装层)
- **修复成本**: medium
- **B4.014 关联**: 边缘 (P1.1 domain)

### 🚫 #2 [BLOCKING] data-indicator-001: 页面 redirect 到 /dashboard
- 访问 /data/indicator 立即跳转 /dashboard
- 无 console error,ArtDecoDataAnalysis.vue 内无 router.push
- 根因:未知 (需 trace router beforeEach + composables)
- **修复成本**: medium
- **B4.014 关联**: direct (严重 regression,页面不可访问)

### ⚠️ #3 [HIGH] data-fund-flow-002: data.data 双重嵌套
- 即使 401 修复,响应 `success+data.data` 双重嵌套
- 与 batch-01 LHB 同模式
- **B4.014 关联**: direct

### ⚠️ #4 [HIGH] data-concept-001: 概念龙头股列 N/A
- 20 行全部 leader=N/A
- 后端响应可能未含 leading_stock 字段或字段名不匹配
- **B4.014 关联**: direct (字段映射)

---

## 4. Findings 全表

| ID | Page | Severity | Dimension | Title |
|----|------|----------|-----------|-------|
| data-fund-flow-001 | data-fund-flow | BLOCKING | functional | 401 Not authenticated on 2 endpoints |
| data-fund-flow-002 | data-fund-flow | HIGH | data-state | data.data 双重嵌套 |
| data-fund-flow-003 | data-fund-flow | MEDIUM | visual | 401 错误未在 UI 显示 |
| data-indicator-001 | data-indicator | BLOCKING | functional | redirect 到 /dashboard |
| data-industry-001 | data-industry | MEDIUM | functional | 冷启动 "Backend Unavailable" 误报 |
| data-industry-002 | data-industry | LOW | data-state | "DATA: REAL" 标识误导(实为 akshare) |
| data-concept-001 | data-concept | HIGH | data-state | 龙头股列 N/A |
| data-concept-002 | data-concept | LOW | visual | StatCard 显示 "20.00" 而非 "20" |
| - | (all) | LOW | responsive-a11y | 未发现 a11y issue (本轮跳过深度审计) |

---

## 5. 验证 surface 说明

- **Backend**: PM2 mystocks-backend (pid 1888757, port 8020, /health=200, /health/ready=200)
- **Frontend**: PM2 mystocks-frontend (pid 2040733, port 3020)
- **OpenStock**: 192.168.123.104:8040 (API Key 配置生效)
- **Browser**: Playwright MCP (chromium)
- **Login**: admin/admin123 (token eyJhbGc... login @ 22:28 UTC)

---

## 6. 后续动作

- **审批**: 用户需对 findings 决定 approve/defer/reject
- **修复优先级**:
  - P0: data-indicator-001 (页面完全不可访问)
  - P0: data-fund-flow-001 (主功能阻塞)
  - P1: data-fund-flow-002, data-concept-001 (数据展示缺陷)
  - P2: 其他 LOW findings
- **建议**: 在 batch-03+ 前先修这两个 BLOCKING

---

## 7. Artifacts 清单

```
docs/reports/quality/myweb-audit/audit-20260702-01/
├── manifests/
│   ├── market-batch-01-manifest.yaml
│   └── market-batch-02-manifest.yaml  (本批)
├── findings/
│   ├── market-realtime/  (batch-01)
│   ├── market-technical/
│   ├── market-lhb/
│   ├── data-industry/raw-findings.yaml   (本批)
│   ├── data-concept/raw-findings.yaml    (本批)
│   ├── data-fund-flow/raw-findings.yaml  (本批)
│   └── data-indicator/raw-findings.yaml  (本批)
├── approvals/
│   └── repair-approval.yaml  (需更新加入 batch-02 findings)
├── batches/
│   ├── market-batch-01-report.md
│   └── market-batch-02-report.md  (本文件)
├── pages/
└── closeout/  (待最终 batch 完工)
```

---

## 8. 关键未解决问题 (供下次 session)

### data-indicator redirect 根因 trace
1. 读 `web/frontend/src/router/index.ts:315-350` (可能有动态 redirect 逻辑)
2. 读 `web/frontend/src/composables/market/useDataAnalysis.ts` (composable 可能抛错)
3. 浏览器加 console.log 在 `router.beforeEach` 内打印 to/from/authResult

### data-fund-flow 401 根因 trace
1. 在浏览器开发者工具 Network 面板看实际请求 headers(是否包含 Authorization)
2. 若不含,trace `useArtDecoApi.exec()` 与 `apiClient.interceptors.request` 交互
3. 测试是否仅 `/akshare/market/fund-flow/*` 路由的 auth middleware 不同

---

**生成人**: Claude (glm-5.2)
**生成原因**: batch-02 4 页 5 维度审计完成,2 BLOCKING + 2 HIGH findings 待审批修复
