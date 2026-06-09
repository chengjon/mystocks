# Mock 数据使用规则

> **补充规范说明**:
> 本文件是 Mock 数据专题的当前执行细则，不是仓库共享规则的唯一事实来源。
> Mock 相关共享治理口径仍以 [`architecture/STANDARDS.md`](../../../architecture/STANDARDS.md) 为准；页面级 API 行为与 `verified/pending` 规则以 [`openspec/specs/api-integration/spec.md`](../../../openspec/specs/api-integration/spec.md) 为准。

## 目的

本文件回答三个问题：

1. Mock 在本项目里什么时候允许使用
2. Mock 在哪些场景下不能作为真实链路兜底
3. 当前仓库中多层 Mock 资产应如何被理解和使用

## 当前主线规则

### 1. Mock 的定位

- Mock 的首要用途是前后端解耦开发。
- Mock 的常见用途是测试稳定性、固定数据验收、自动化隔离和开发态演示。
- Mock 不是默认的线上成功路径，也不是 `verified` 页面真实接口失败后的静默替代品。

对应共享规则见：

- [`architecture/STANDARDS.md`](../../architecture/STANDARDS.md)

### 2. 页面级真相优先级

- `verified` 页面：
  - 真实 API 是主数据源。
  - 不得对同一路径静默回退到 mock。
  - 必须显式暴露 `loading / error / empty / request id` 状态。
- `pending` 页面：
  - 路由可以保持可达。
  - 允许保留壳层、加载态、错误态、空态。
  - 不得臆造真实接口契约字段。
  - 阻塞项必须记录到优化清单或任务报告。

对应专题规格见：

- [`openspec/specs/api-integration/spec.md`](../../../openspec/specs/api-integration/spec.md)

## 允许使用 Mock 的场景

### 开发解耦

- 后端接口尚未就绪，但前端需要先完成 UI/UX 视觉验收。
- 新页面、新组件或新交互仍在壳层阶段，只需要表达布局、状态和体验。

### 测试稳定性

- Vitest / 组件测试 / 前端集成测试中，需要使用 `MSW` 或固定 mock payload 保证可复现。
- 自动化场景需要避免实时数据、时间漂移、外部依赖波动。
- Smoke 或 sandbox-safe 运行器中，显式启用 `VITE_USE_MOCK_DATA=true` 进行隔离验证。

### 非主链运行时降级

- 自动化浏览器验收或显式 mock 模式下，readiness 检查允许进入“mock 验收模式”，避免开发演示完全阻塞。
- 这类 fallback 必须是显式模式或自动化专用，不得伪装成真实主链已通过。

## 禁止或默认不允许的场景

### 禁止把 Mock 当成 `verified` 页面的静默兜底

- 已标记 `verified` 的页面，不得在同一路径上“真实接口失败后默默返回 mock 数据”。
- 这类场景必须进入错误态、空态或明确的非阻塞 warning 态，而不是继续伪装成真实数据成功。

### 禁止用 Mock 臆造契约

- 不得为了让页面先跑起来而发明真实接口尚未承诺的字段。
- 不得把 page-local 假字段包装成“真实接口兼容层”。

### 禁止在业务代码中无说明地内联硬编码数据

- 业务代码中直接堆大型静态数组、随机散落的 fallback 对象、临时写死的行情/策略/持仓数据，默认视为不合规。
- 如果确实需要 mock payload，必须：
  - 放在集中 mock 模块或测试 fixture 中
  - 明确说明用途是开发、测试或显式 fallback
  - 与真实返回结构保持可比对关系

## 当前仓库中的 Mock 资产分层

当前仓库里与 Mock 相关的资产主要分为四类：

### 1. 后端 page-level / feature-level Mock

- `src/mock/`
- 作用：历史 page-level mock 数据、若干后端 fallback 或参考实现来源

### 2. 后端数据源级 Mock

- `src/data_sources/mock/`
- 作用：数据源工厂模式下的 mock timeseries / relational / business provider

### 3. 后端统一 Mock 管理与 Mock 路由

- `web/backend/app/mock/`
- `web/backend/app/api/strategy_list_mock.py`
- 作用：后端 mock manager、显式 mock API 路由和若干 fallback 接入点

### 4. 前端测试与显式 Mock 客户端

- `web/frontend/src/mock/`
- `web/frontend/src/api/mockApiClient.ts`
- 作用：前端测试数据、显式 `VITE_USE_MOCK_DATA` 模式、部分适配器/测试用例消费

这些资产同时存在并不等于“所有页面都可以自由混用 mock/real”。真正的准入边界仍由 `verified/pending` 和当前主线验证状态决定。

## 环境与开关

当前仓库里最常见的 Mock 相关开关包括：

- 后端：`USE_MOCK_DATA`
- 前端：`VITE_USE_MOCK_DATA`

补充说明：

- 某些历史文档仍提到更早的 `VITE_APP_MODE` 口径；阅读时必须以当前代码和当前运行脚本为准。
- 是否启用 mock，不应只看环境变量名，还要看页面是否已经处于 `verified` 主链、测试是否属于显式 mock 场景，以及调用链是否允许 fallback。

## 实施建议

### 新增页面或功能时

- 先判断该页面当前是 `pending` 还是 `verified` 目标。
- `pending` 阶段只做壳层和状态收口，不要发明真实字段。
- 如果需要临时数据，放入集中 mock 模块，不要把数据散落在页面里。

### 改造既有页面时

- 先确认该页面是否已经被主线文档记为 `verified`。
- 若已 `verified`，优先拆掉静默 mock fallback，保留错误态、空态和 request id。
- 若仍需 mock 验收，必须让模式显式可见，而不是默认混在真实链路里。

### 写测试时

- 单元测试和集成测试优先使用 `MSW`、集中 fixture 或 mock helper。
- E2E 若只跑 mock/sandbox-safe 子集，必须明确标注测试边界，不能表述成“真实联调已验证”。

## 反模式

以下模式应视为重点治理对象：

- 页面内 `if request failed -> return mockRows`，且对用户无显式提示
- `verified` 页面继续保留 `mixed` 假字段拼装
- 业务主链直接从历史 page mock 文件导入数据作为默认成功数据
- 文档把 mock 覆盖率、mock 文件数量、接口数量写成当前事实，但没有日期和复核来源

## 相关文档

- [`INDEX.md`](./INDEX.md)
- [`MOCK_REAL_DATA_SWITCHING_GUIDE.md`](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)
- [`MOCK_GOVERNANCE_AUDIT_LEDGER.md`](./MOCK_GOVERNANCE_AUDIT_LEDGER.md)
- [`web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md`](../../../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)
- [`architecture/STANDARDS.md`](../../architecture/STANDARDS.md)
- [`openspec/specs/api-integration/spec.md`](../../../openspec/specs/api-integration/spec.md)
