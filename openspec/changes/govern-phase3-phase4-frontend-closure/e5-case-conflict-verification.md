# E5 Case-Conflict Verification

> **历史文档说明**:
> 本文档记录 `govern-phase3-phase4-frontend-closure` 在 `3.2` 阶段的验证结果。
> 目标是确认真正的 case-conflict 是否仍存在，并给出 build / stylelint / route-smoke 的实际结果。
> 当前文档已作为 `3.2` 完成证据的一部分。

**Generated:** 2026-04-08  
**Change:** `govern-phase3-phase4-frontend-closure`  
**Task:** `3.2 Execute case-conflict directory merge batch E5 with build / stylelint / route-smoke verification`

## 1. Structural Verdict

当前 `web/frontend/src/components/` 下未发现仍然存在的大小写同名目录冲突。

本次验证结论：

- `find web/frontend/src/components -type d | rg '/[A-Z]'` 返回空
- 基于 `os.walk` 的按父目录大小写归并检查，未发现 `Charts/charts`、`Common/common`、`Market/market` 这类仍并存的目录

因此，原始意义上的 `case-conflict directories` 在当前 repo truth 中已不存在。

## 2. Remaining Structural Overlap

虽然真正的大小写冲突已消失，但仍存在功能重叠目录，需要与 E5 区分：

| Area | Current State | Judgment |
|---|---|---|
| `components/chart/` vs `components/charts/` | 不是大小写冲突，而是单数/复数并行结构 | `structural overlap`, not case-conflict |
| `components/menu/` vs `components/menu_root/` | 不是大小写冲突，而是 legacy/alternate implementation 并存 | `structural overlap`, not case-conflict |
| `components/market/ProKLineChart.vue` vs `components/charts/ProKLineChart.vue` | 并行组件实现 | `duplicate-candidate`, not case-conflict |

这意味着：

- E5 的原始 case-conflict merge 很可能已在更早批次被部分落地
- 当前剩余问题更像 `post-E5 structural overlap governance`，不能再按“大小写目录合并”直接处理

## 3. Verification Results

### 3.1 PM2 Service Status

执行：

```bash
npm run pm2:status
```

结果：

- `mystocks-backend` = `online`
- `mystocks-frontend` = `online`

访问地址：

- Frontend: `http://localhost:3020`
- Backend: `http://localhost:8020`

附加探测：

- `curl -I http://localhost:3020` -> `200 OK`
- `curl -I http://localhost:8020/health/ready` -> `405 Method Not Allowed`
  - 原因：该健康检查端点要求 `GET`，不是服务离线

### 3.2 Route Smoke

执行：

```bash
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
npm run test:e2e:stable
```

结果：

- Project: `chromium`
- Suite:
  - `tests/e2e/critical/menu-navigation-fixed.spec.ts`
  - `tests/e2e/kline-chart.spec.ts`
- Actual result: `10 passed (18.2s)`

判定：

- route smoke 通过
- 当前大小写目录收口状态未引入明显导航回归

### 3.3 Frontend Build

执行：

```bash
npm run build
```

结果：

- `generate-types` 成功
- `vue-tsc --noEmit` 通过
- `vite build` 通过

本轮收口内容：

1. `src/_entry-archive/**/*` 从当前运行时 typecheck 真相源中排除
2. `src/components/charts/composables/useProKLineChart.ts` 收口 KLineCharts 第三方类型断言与释放逻辑
3. `src/components/charts/OscillatorChart.vue` 修正 chart data / action typing
4. `src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue` 收口 snapshot parameter value 的类型归一
5. `npx vue-tsc --noEmit --pretty false` 返回 `0`
6. `npm run build` 返回 `0`

判定：

- 当前 build 通过
- 本轮 E5 范围内的 type/build 阻塞已完成收口
- 先前记录为既有债务的 `_entry-archive` 与 chart typing 问题，不再阻塞 `3.2`

### 3.4 Stylelint

执行：

```bash
npx stylelint "src/**/*.{vue,scss,css}"
```

结果：

- `126` errors
- `0` warnings
- 其中 `51` 条可通过 `--fix` 自动处理

主要分布：

- `src/App.vue`
- `src/layouts/ArtDecoLayoutEnhanced.vue`
- `src/layouts/BaseLayout.vue`
- `src/styles/*.scss`
- `src/components/common/*`
- `src/components/layout/*`
- `src/components/market/*`
- `src/views/*`

判定：

- stylelint 未通过
- 失败是 repo-wide 样式债务，不是本轮 case-conflict 变更引入的新问题

### 3.5 E5-Scoped Stylelint

为区分仓库全局样式债与 E5 目标目录状态，额外执行：

```bash
npx stylelint \
  "src/components/chart/**/*.{vue,scss,css}" \
  "src/components/charts/**/*.{vue,scss,css}" \
  "src/components/menu/**/*.{vue,scss,css}" \
  "src/components/menu_root/**/*.{vue,scss,css}"
```

结果：

- 命令返回 `0`
- E5 相关目录的样式检查通过

判定：

- `chart/`、`charts/`、`menu/`、`menu_root/` 当前不存在新增样式门禁问题
- `3.2` 的剩余阻塞已收缩为 build/type 债，而不是 E5 目标目录的 stylelint 问题

## 4. E5 Status Decision

当前 `3.2` 可以标记完成，依据如下：

1. 真正的 case-conflict 现象已经消失
2. route smoke 已通过
3. E5 相关目录的 scoped stylelint 已通过
4. `vue-tsc --noEmit` 已通过
5. `npm run build` 已通过

因此，当前结论是：

```text
E5 structural state verified and the required build / stylelint / route-smoke gates now pass.
```

## 5. Recommended Next Step

下一步不再重复做“目录大小写合并”，而应进入 `3.3`：

1. 继续执行 naming / shim / backup closure batch E6
2. 对 `_entry-archive`、legacy shims、backup 文件执行 trunk-first / retirement-gated 收尾
3. repo-wide stylelint 债务若需要治理，应作为独立后续批次处理，而不是回退 `3.2`
