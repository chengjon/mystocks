# canonical-entrypoints（Phase A 决策草案）

## 目标
在不改变业务契约的前提下，确定并固化“唯一入口”，把兼容层从默认路径降级为过渡路径。

## 1) Frontend 候选入口与建议

### 候选 A：`web/frontend/src/api/apiClient`
- 优势：
  - 已被 `httpClient.js` 和部分入口文件直接依赖。
  - 与 `unifiedApiClient.ts` 的桥接关系清晰（`unifiedApiClient = apiClient`）。
- 风险：
  - `services/api-client` 仍有在用调用方（`WencaiQueryEngine.ts`）。
  - `@/api` barrel 覆盖面较大，迁移需要分批推进。

### 候选 B：`web/frontend/src/services/api-client`
- 优势：
  - 现存业务链路仍在用（证明并非死代码路径）。
- 风险：
  - 与 `src/api/*` 体系并行，长期会放大认知与维护成本。

### 当前建议
- **建议将 `web/frontend/src/api/apiClient` 设为 canonical client**，
- 并将 `web/frontend/src/services/api-client` 作为过渡别名层，在迁移窗口内逐步下线。
- **Phase B 执行默认按该方向推进**（除非架构评审明确改判）。

> 注：若架构评审决定相反方向（以 `services/api-client` 为 canonical），需同步重写本清单与迁移批次。

---

## 2) Backend canonical 口径

- 运行态仅允许“无后缀正式文件”参与路由与服务加载。
- `.old/.new/.bak/.backup*` 一律视为非运行态历史副本：
  - 有引用：先迁移再删除；
  - 零引用：可直接归档删除（保留变更记录）。

---

## 3) 迁移批次建议（Frontend）

1. **Batch 1（高风险）**
   - `web/frontend/src/services/httpClient.js`
   - `web/frontend/src/api/unifiedApiClient.ts`
   - 验证重点：认证、CSRF、错误包装链路一致性。

2. **Batch 2（中风险）**
   - `web/frontend/src/services/WencaiQueryEngine.ts`
   - `web/frontend/src/services/TradingApiManager.ts`
   - `web/frontend/src/composables/useStrategy.ts`
   - 验证重点：业务查询链路、分页/筛选与异常提示。

3. **Batch 3（广覆盖）**
   - `@/api` barrel 大面积调用方（按模块拆 PR）
   - 验证重点：页面级回归 + 类型基线不劣化。

---

## 4) 退出兼容层（sunset）判定

满足以下条件后，才允许删除过渡入口：
1. 迁移目标入口引用数归零；
2. baseline + PM2 + E2E 门禁连续通过；
3. 已完成一个发布窗口观测，无关键回归。
