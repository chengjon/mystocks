# Entry Variant Caller Matrix

> **历史文档说明**:
> 本文档用于完成 `govern-phase3-phase4-frontend-closure` 的任务 `2.1`，
> 把 `main-*.js/ts` 与 `verify-mount.js` 的 caller 状态分层固化。
> 它不是运行时代码改动批准，也不替代 `architecture/STANDARDS.md` 的删除/迁移门禁。

**Generated:** 2026-04-07  
**Change:** `govern-phase3-phase4-frontend-closure`  
**Task:** `2.1 Produce and approve the entry variant caller matrix for main-*.js/ts and verify-mount.js`

## 1. Locked Conclusion

当前前端入口真相源仍然是：

```text
web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts
```

同时，`web/frontend/src/main.js` 不是当前 HTML 运行入口，但仍然被工具脚本
`web/frontend/verify-mount.js` 直接读取；在该脚本完成收口前，`main.js` 不能被归为可删文件。

此外，`scripts/debug_vite.js` 仍把 `/src/main.js` 作为调试探测目标之一，因此 `main.js`
还存在一个历史调试脚本层面的引用，需要在后续批次里一起判定其保留或下线方式。

## 2. Evidence Snapshot

### 2.1 Runtime Truth

- `web/frontend/index.html:67` 加载 `/src/main-standard.ts`
- `web/frontend/src/main-standard.ts:4` 导入 `./router/index.ts`
- `web/frontend/src/main-standard.ts:43` 执行 `app.mount('#app')`

### 2.2 Script / Tooling Consumers

- `web/frontend/verify-mount.js:5` 直接读取 `web/frontend/src/main.js`
- `web/frontend/verify-mount.js:8` 验证 `main.js` 中是否包含 `app.mount`
- `scripts/debug_vite.js:7` 仍把 `/src/main.js` 作为 Vite 调试探测目标

### 2.3 Archived Zero-Consumer Variants

以下文件已位于 `web/frontend/src/_entry-archive/`：

- `main-debug.js`
- `main-enhanced.ts`
- `main-minimal.ts`
- `main-original.js`
- `main-simplified.js`
- `main-test.js`

`web/frontend/src/_entry-archive/README.md` 已将它们记录为零消费者归档变体。

## 3. Current Caller Matrix

| Entry / Script | Current Role | Current Caller Type | Current Caller | Evidence | Lifecycle Decision |
|---|---|---|---|---|---|
| `web/frontend/src/main-standard.ts` | canonical runtime entry | runtime | `web/frontend/index.html` | `index.html:67` | 必须保留 |
| `web/frontend/src/main.js` | non-canonical legacy boot file | tooling read | `web/frontend/verify-mount.js` | `verify-mount.js:5-8` | 暂不归档，不可删除 |
| `web/frontend/src/main.js` | non-canonical legacy boot file | debug script target | `scripts/debug_vite.js` | `scripts/debug_vite.js:4-9` | 需在后续批次判定脚本是否保留 |
| `web/frontend/src/_entry-archive/main-debug.js` | archived historical variant | none | none in current code/script search | repo search + archive README | 保持归档 |
| `web/frontend/src/_entry-archive/main-enhanced.ts` | archived historical variant | none | none in current code/script search | repo search + archive README | 保持归档 |
| `web/frontend/src/_entry-archive/main-minimal.ts` | archived historical variant | none | none in current code/script search | repo search + archive README | 保持归档 |
| `web/frontend/src/_entry-archive/main-original.js` | archived historical variant | none | none in current code/script search | repo search + archive README | 保持归档 |
| `web/frontend/src/_entry-archive/main-simplified.js` | archived historical variant | none | none in current code/script search | repo search + archive README | 保持归档 |
| `web/frontend/src/_entry-archive/main-test.js` | archived historical variant | none | none in current code/script search | repo search + archive README | 保持归档 |
| `web/frontend/verify-mount.js` | tooling validation script | direct file read | reads `src/main.js` | `verify-mount.js:4-30` | 后续若要收口 `main.js`，必须先改它 |

## 4. Historical References vs Active Callers

本次区分三类引用，避免误判：

1. **Active runtime caller**
   - 只有 `web/frontend/index.html -> /src/main-standard.ts`

2. **Active script/tooling caller**
   - `web/frontend/verify-mount.js`
   - `scripts/debug_vite.js`

3. **Historical / planning / documentation references**
   - `.planning/ROADMAP.md`
   - `.planning/phases/03-structural-consolidation/*`
   - `web/frontend/ENTRY-TRUTH.md`
   - 多份 `docs/reports/*` 与 `docs/guides/*`

第 3 类引用会影响“文档真相一致性”，但不单独构成 runtime blocker；
不过在 `E2` 及后续收口批次中，仍需要同步治理，避免继续把 `main.js` 或历史变体写成现役入口。

## 5. Decision Output for Batch E1

### 5.1 Must Keep

- `web/frontend/src/main-standard.ts`
  - 原因：当前 HTML 真入口
- `web/frontend/src/main.js`
  - 原因：仍被 `verify-mount.js` 直接读取，且被 `scripts/debug_vite.js` 当作调试目标
- `web/frontend/verify-mount.js`
  - 原因：当前仍承担挂载校验脚本职责

### 5.2 Keep Archived

- `web/frontend/src/_entry-archive/main-debug.js`
- `web/frontend/src/_entry-archive/main-enhanced.ts`
- `web/frontend/src/_entry-archive/main-minimal.ts`
- `web/frontend/src/_entry-archive/main-original.js`
- `web/frontend/src/_entry-archive/main-simplified.js`
- `web/frontend/src/_entry-archive/main-test.js`

### 5.3 Required Before Any Further Entry Cleanup

若后续要推进 `main.js` 的归档、迁移或删除，必须先完成以下前置动作：

1. 明确 `verify-mount.js` 的去向：
   - 更新为读取 `main-standard.ts`
   - 或确认废弃并下线
2. 明确 `scripts/debug_vite.js` 是否仍为有效调试脚本：
   - 若保留，需更新探测目标
   - 若失效，需归类为历史调试资产
3. 同步收口历史文档 / 规划文本中把 `main.js` 写成现役入口的表述

## 6. Approval Record

本矩阵作为已批准 OpenSpec change 的执行产物落盘，当前批准范围仅覆盖：

- caller 分类
- 生命周期判断
- 后续批次的收口前置条件

**不覆盖**：

- 删除 `main.js`
- 修改 `verify-mount.js`
- 迁移 `main-standard.ts`
- 批量重写历史文档

这些仍需在后续具体批次中按 `architecture/STANDARDS.md` 单独审批。
