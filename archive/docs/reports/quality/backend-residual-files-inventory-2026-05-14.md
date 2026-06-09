# MyStocks 后端备份/残留文件清册

> **权威来源声明**:
> 本文档是 `web/backend/app/` 下备份、过渡和疑似残留对象的事实清册，不是删除指令。
> 清理、删除、兼容层退役和 `_new.py` 收口必须以 `architecture/STANDARDS.md` 的“双判定”规则为准：同时完成代码路径判定和功能树判定，且对象状态明确为重复冗余或正式下线后，才能进入单独实施批次。
> 涉及 API 路由、兼容导出、目录合并、canonical 切换或对外契约变化时，必须先走 `openspec/AGENTS.md` 的 proposal-first 流程，审批后再实施。

> **复核入口**: `docs/reports/quality/backend-audit-documents-review-2026-05-15.md`

---

## 一、2026-05-15 当前扫描结论

扫描范围：`web/backend/app/**/*.py` 与 `web/backend/app/**/` 中具有残留特征的文件或目录。

| 类别 | 当前数量 | 当前结论 |
|------|----------|----------|
| `.bak` / `.backup` / `.old.py` / `.before_*` 文件 | 0 | 当前工作树未发现此类备份文件 |
| `_new.py` 过渡文件 | 4 | 仍存在，需逐项判定 canonical 与兼容职责 |
| `*_old/` 目录 | 1 | `api/monitoring_old/` 仍存在，需判定是否为未注册历史路由 |
| 功能性兼容 shim | 1 | `api/auth_compat.py` 存在，但不属于残留文件，不纳入删除候选 |

上一版文档中列出的 9 个备份文件当前均未在工作树中发现：

| 旧清单对象 | 2026-05-15 当前状态 |
|------------|---------------------|
| `web/backend/app/api/mystocks_complete.py.bak` | 不存在 |
| `web/backend/app/api/risk_management.py.bak` | 不存在 |
| `web/backend/app/api/strategy_management.py.backup` | 不存在 |
| `web/backend/app/api/data_source_config.py.backup` | 不存在 |
| `web/backend/app/api/data_source_config.old.py` | 不存在 |
| `web/backend/app/services/data_adapter.py.backup.20260130` | 不存在 |
| `web/backend/app/services/watchlist_service.py.bak2` | 不存在 |
| `web/backend/app/services/watchlist_service.py.bak3` | 不存在 |
| `web/backend/app/services/watchlist_service.py.before_schema_update` | 不存在 |

结论：B 文档不应再声称这些文件“当前存在”“可删除”或“已完成删除”。它们只能作为历史快照记录；当前可执行的工作是对剩余 5 个候选对象补判定，而不是删除旧清单对象。

---

## 二、当前候选对象清册

### 2.1 `_new.py` 过渡文件

| # | 当前对象 | 大小 | canonical / 关联对象 | 当前依赖证据 | 判定状态 |
|---|----------|------|----------------------|--------------|----------|
| 1 | `web/backend/app/services/data_adapter_new.py` | 约 6KB | `web/backend/app/services/data_adapter.py` 存在 | GitNexus upstream impact: LOW，未发现直接上游 | 待判定。不能仅凭无上游删除，需确认是否为兼容实现或迁移桥接层 |
| 2 | `web/backend/app/services/data_api_new.py` | 约 1KB | `web/backend/app/api/data/data_api_new.py` 存在；`services/data_api.py` 不存在 | `services/__init__.py` 导入 `DataApiService`；文件内部动态加载 `api/data/data_api_new.py` | 待判定。当前更像服务层 wrapper，不是普通备份 |
| 3 | `web/backend/app/api/data/data_api_new.py` | 约 11KB | `services/data_api_new.py` 动态加载它 | GitNexus upstream impact: LOW；文本证据显示被 wrapper 通过文件路径加载 | 待判定。可能是当前兼容实现，不能按文件名删除 |
| 4 | `web/backend/app/services/risk_management_new.py` | 约 9KB | `services/risk_management.py` 不存在；`api/risk_management.py` 属于 API 层对象 | GitNexus upstream impact: LOW；`services/__init__.py` 中存在风险服务初始化逻辑，但导入路径写成 `.risk_management.risk_management_new` | 待判定。需先确认导入路径、实际运行路径和风险域 canonical |

### 2.2 旧目录候选

| # | 当前对象 | 内容 | 当前依赖证据 | 判定状态 |
|---|----------|------|--------------|----------|
| 5 | `web/backend/app/api/monitoring_old/` | `__init__.py`、`routes.py` | 文本扫描未发现外部引用；GitNexus 对 `routes.py` 的 upstream impact 为 LOW | 待判定。若确认未注册且功能树状态为重复冗余，可进入清理 proposal 或独立清理批次 |

`monitoring_old/routes.py` 内部仍定义 `APIRouter(prefix="/monitoring")` 和多个 endpoint。即使当前未发现注册引用，也不能只按“未引用”删除；需要确认它是否承担历史兼容、测试 fixture、文档约定或后续恢复职责。

### 2.3 明确排除对象

| 对象 | 排除原因 |
|------|----------|
| `web/backend/app/api/auth_compat.py` | 文件名包含 `compat`，属于功能性兼容 shim；没有完成兼容职责判定和退役方案前，不纳入残留删除候选 |

---

## 三、GitNexus 预检摘要

| 目标 | 结果 | 说明 |
|------|------|------|
| `web/backend/app/services/data_adapter_new.py` | LOW，0 direct upstream | 可继续做判定，不代表可删除 |
| `web/backend/app/services/data_api_new.py` | LOW，1 direct upstream | 直接上游为 `web/backend/app/services/__init__.py` |
| `web/backend/app/api/data/data_api_new.py` | LOW，0 direct upstream | 文本证据显示被 `services/data_api_new.py` 动态加载，需按运行时路径判定 |
| `web/backend/app/services/risk_management_new.py` | LOW，0 direct upstream | 仍需核对 `services/__init__.py` 中风险服务导入路径 |
| `web/backend/app/api/monitoring_old/routes.py` | LOW，0 direct upstream | 仍需完成 route table 与功能树判定 |

解释：GitNexus 的 LOW 风险只说明当前索引中的静态上游较少，不能替代 `architecture/STANDARDS.md` 要求的代码路径判定和功能树判定。

---

## 四、双判定模板

每个候选对象进入删除或迁移实施前，必须补齐下表。

| 字段 | 填写要求 |
|------|----------|
| 候选对象 | 文件或目录的完整路径 |
| 代码路径判定 | 是否被 import、动态加载、router 注册、构建脚本、测试、文档约定、字符串映射或兼容分支使用 |
| 功能树状态 | `有效`、`失效但兼容保留`、`实验/灰度`、`重复冗余`、`待判定` |
| canonical 对象 | 当前唯一主实现、主入口或主注册点 |
| 保留兼容面 | 若保留，说明兼容职责、调用方和退场条件 |
| 删除或迁移条件 | 需要满足的验证命令、OpenSpec 审批和回滚条件 |
| 最终动作 | `保留`、`标记 deprecated`、`迁移`、`删除候选`、`不处理` |

---

## 五、执行建议

### Step 1：先补事实，不删除

对 5 个当前候选对象逐项补齐双判定表。当前没有任何对象达到可执行清理的证明标准。

### Step 2：分流处理

| 对象类型 | 建议处理方式 |
|----------|--------------|
| 纯历史备份文件 | 当前扫描为 0，无需处理 |
| `_new.py` wrapper / 兼容实现 | 先确认 canonical；若涉及目录或导出面切换，进入 OpenSpec |
| 旧 API 路由目录 | 先确认是否注册、是否被测试或文档约定引用；若涉及 endpoint 下线，进入 OpenSpec |
| `compat` shim | 默认保留，除非有明确兼容退役方案 |

### Step 3：验证门禁

建议在实施批次前至少保留以下证据：

| 验证项 | 目的 |
|--------|------|
| 当前候选扫描 | 证明备份和过渡对象数量 |
| 全仓 import / 文本引用扫描 | 捕捉静态 import、动态路径和字符串映射 |
| route table 或 FastAPI 注册检查 | 确认旧路由是否实际暴露 |
| GitNexus upstream impact | 了解静态上游和受影响模块 |
| 相关测试或 smoke | 证明删除或迁移未破坏业务路径 |

---

## 六、当前结论

1. 旧版 B 文档中关于 9 个文件处理完成和 6 个文件清理许可的结论不再作为当前执行依据。
2. 当前工作树没有 `.bak`、`.backup`、`.old.py`、`.before_*` 类备份文件。
3. 当前仍需治理的是 4 个 `_new.py` 过渡文件和 1 个 `monitoring_old/` 旧目录。
4. `services/data_api_new.py`、`api/data/data_api_new.py`、`services/risk_management_new.py` 更像兼容层或 wrapper，不应被当作普通残留文件处理。
5. 后续若要删除、迁移或重命名上述对象，必须先完成双判定；若改变 API、导出面或 canonical 结构，必须先完成 OpenSpec 审批。
