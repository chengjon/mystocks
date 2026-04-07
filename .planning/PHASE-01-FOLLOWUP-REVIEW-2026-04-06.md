# Phase 1 Follow-up Review

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现、验证结果与主线文档使用。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。

**Date:** 2026-04-06
**Scope:**
- Commits: `3f7f7703f`, `f3b4261f6`, `d6c7ba2d2`, `a6868b661`, `b0dfffa0c`
- Files: `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/PROJECT.md`, `.planning/phases/01-python-lint-baseline/01-VERIFICATION.md`, `.planning/phases/01-python-lint-baseline/01-SUMMARY.md`

## Overall

前一轮 review 中关于 `LINT-02` 门控、`LINT-03` 规则范围、`STATE.md` 正文同步、`REQUIREMENTS.md` traceability 的修复，当前文档已经基本落地。

但“所有发现已解决、文档现已完全一致”这个结论仍然站不住。至少还有 3 个问题，其中 1 个是阻塞级：Phase 1 仍然不能被标成 “approved and verified”。

## Findings

### 1. [High] FastAPI 冒烟测试仍未通过，`ROADMAP` / `01-VERIFICATION` 的“已验证通过”结论不成立

涉及位置：
- `.planning/ROADMAP.md:12`
- `.planning/ROADMAP.md:56`
- `.planning/phases/01-python-lint-baseline/01-VERIFICATION.md:92`
- `web/backend/app/main.py:37`
- `web/backend/app/core/socketio_manager.py:28`

实际复核命令：

```bash
cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"
```

实际结果：
- 命令退出码为 `1`
- 失败原因为 `ImportError: cannot import name 'get_socketio_manager' from 'app.core.socketio_manager'`

这说明前述修复并没有把问题稳定消掉。当前仓库里 `main.py` 仍从 `app.core.socketio_manager` 导入 `get_socketio_manager`，但当前 `socketio_manager.py` 顶部并没有重新导出该符号；文档把失败归因为“错误 PYTHONPATH”并宣称“correct invocation passes”，与实测不符。

影响：
- `ROADMAP.md` 不能把 Phase 1 状态写成 `execution approved and verified`
- `01-VERIFICATION.md` 不能继续维持 `status: passed`

建议：
- 先修复实际导入链，再重新执行该命令
- 在 fresh evidence 出来之前，把相关文档状态降回“部分完成 / smoke blocked”

### 2. [Medium] `PROJECT.md` 仍把已完成的 LINT-01 作为 Active 工作项，跨文档一致性还没闭合

涉及位置：
- `.planning/PROJECT.md:30`
- `.planning/PROJECT.md:36`

问题：
- `Validated` 段落已经写明 `LINT-01: src/interfaces/adapters/ deleted`
- 但 `Active` 段落仍保留 `Eliminate duplicate adapter layer (src/interfaces/adapters/ → resolve vs src/adapters/)`

这与 “ROADMAP / REQUIREMENTS / STATE / VERIFICATION / SUMMARY / PROJECT 保持一致” 的结论冲突。当前 `PROJECT.md` 仍然把同一事项同时标成“已验证完成”和“待做”。

建议：
- 从 `Active` 中删除这条，或改写成真正的后续工作项

### 3. [Low] `ROADMAP.md` 的 smoke gate 文案仍有残留错误，说明修复没有完全传播

涉及位置：
- `.planning/ROADMAP.md:56`
- `.planning/ROADMAP.md:133`

问题：
- Phase 1 的 smoke command 行尾仍有一个多余反引号
- Phase 2 success criteria 仍保留旧命令：`python -c "from web.backend.app.main import app; print('OK')"`

即使不考虑当前真实导入错误，这两处也说明 smoke gate 的修订没有在 `ROADMAP` 内部完全同步。

建议：
- 在代码修复后，统一全文件的 smoke command 口径
- 顺手清掉 line 56 的格式噪音，避免后续执行者复制错误命令

## Verified Resolutions

以下修复本次已复核，可以保留：

- `LINT-02` Phase 1 门控已从 `<50` 校准为 `<900`
- `LINT-03` 已缩窄为 `W293,F841,W291`
- `REQUIREMENTS.md` 中 `LINT-01/02/03` 的 checkbox 与 traceability 已同步为 `✓ Done`
- `STATE.md` frontmatter 与正文已基本一致，Phase 1 显示为完成、当前焦点切到 Phase 2

补充验证：

```bash
ruff check src/ web/backend/app/ --statistics
```

结果摘要：
- `805 F821`
- `21 F401`
- `15 E701`
- 总计 `877`，满足 `<900`

```bash
ruff check src/ web/backend/app/ --select W293,F841,W291
```

结果摘要：
- `All checks passed!`

## Final Assessment

这轮 follow-up 不是“全部通过”，而是“多数文档修复已到位，但一个关键 smoke gate 仍是假阳性”。在修掉 `get_socketio_manager` 导入链并重新验证前，不建议继续对外宣称 Phase 1 已完整验证通过。
