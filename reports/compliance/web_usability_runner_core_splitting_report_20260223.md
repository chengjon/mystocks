# Web Usability Runner Core Splitting Report

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


**Date:** 2026-02-23  
**Scope:** `scripts/tests/web-usability/runner-core.js` large-file remediation  
**Input Baseline:** `reports/code_inventory_report_20260223.md`

---

## 1. Summary

- Completed targeted large-file split for `scripts/tests/web-usability/runner-core.js`.
- Kept external entrypoint compatibility via `scripts/tests/web-usability-runner.js`.
- Added guardrail coverage for `runner-core.js` file-size limit.
- Registered `scripts/dev/**` as third-party large-file exception scope (no manual split).

---

## 2. Before / After

| File | Before | After | Delta |
| :--- | :---: | :---: | :---: |
| `scripts/tests/web-usability/runner-core.js` | 1289 | 142 | -1147 |
| `scripts/tests/web-usability-runner.js` | 30 | 30 | 0 |

New extracted modules:

| File | Lines |
| :--- | ---: |
| `scripts/tests/web-usability/core/environment.js` | 54 |
| `scripts/tests/web-usability/core/functional.js` | 137 |
| `scripts/tests/web-usability/core/performance.js` | 173 |
| `scripts/tests/web-usability/core/security.js` | 149 |
| `scripts/tests/web-usability/core/usability.js` | 101 |
| `scripts/tests/web-usability/core/data-quality.js` | 127 |
| `scripts/tests/web-usability/core/scoring.js` | 170 |
| `scripts/tests/web-usability/core/report-html.js` | 322 |
| `scripts/tests/web-usability/core/http-client.js` | 12 |

All split modules are below 500 lines.

---

## 3. Guardrail Changes

Updated: `scripts/tests/test_large_file_top5_guardrail.py`

- Added governed target:
  - `scripts/tests/web-usability/runner-core.js`
- Added file-specific hard limit:
  - `scripts/tests/web-usability/runner-core.js <= 500`
- Added pytest assertion entry:
  - `test_governance_targets_comply_with_size_limits`

---

## 4. Verification

### 4.1 File-size guardrail

Command:

```bash
pytest --no-cov scripts/tests/test_large_file_top5_guardrail.py -v
```

Result: `1 passed`

Command:

```bash
python scripts/tests/test_large_file_top5_guardrail.py
```

Result: Passed, `runner-core.js: 142 lines (OK)`.

### 4.2 Runtime module load compatibility

Command:

```bash
node -e "const R=require('./scripts/tests/web-usability-runner'); console.log(typeof R)"
```

Result: `function`

### 4.3 Inventory scan consistency

Command:

```bash
rg --files -uu src scripts web/backend/app -g '*.py' -g '*.vue' -g '*.ts' -g '*.tsx' -g '*.js' -g '*.jsx' | grep -Ev '^scripts/dev/' | while read -r f; do l=$(wc -l < "$f"); if [ "$l" -gt 1000 ]; then printf "%s\t%s\n" "$l" "$f"; fi; done | sort -nr
```

Result: No output (no >1000-line files outside `scripts/dev/**` in this scan scope).

---

## 5. Exception Governance Update

Updated: `reports/compliance/exceptions/large_files.md`

- Added explicit exception category for `scripts/dev/**`:
  - Current state: `70 files >1000 lines`
  - Nature: third-party/generated artifacts
  - Action: do not manually split; monitor via periodic inventory scan.

---

## 6. Notes

- Running `pytest scripts/tests/test_large_file_top5_guardrail.py -v` without `--no-cov` triggers repository-level coverage gate (`fail-under=30`), which is an existing global CI policy and not caused by this split.
- This remediation intentionally focused on the only actionable >1000-line business file found after excluding `scripts/dev/**` third-party artifacts.
