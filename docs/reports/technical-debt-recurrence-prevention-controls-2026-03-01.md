# 防重复发生机制清单（技术债治理）

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


- 日期：2026-03-01
- 关联 OpenSpec：`refactor-technical-debt-remediation-wave1`
- 目标：将“已暴露问题”转化为“可预防、可检测、可追责、可复盘”的闭环控制。

---

## 1. 根因 → 预防控制 → 验证方式

| 根因类型 | 预防控制（Preventive） | 检测控制（Detective） | 验证证据 |
|---|---|---|---|
| 固定阈值与真实基线脱节 | 基线 SoT 迁移到 `tech-debt-baseline.json` | CI gate 读取 baseline 文件并比对 | `type-check-gate` 日志、基线 JSON |
| 抑制注释无约束扩散 | no-new-debt 阻断 + debt-exception 元数据强制 | PR 扫描新增行 suppressions | workflow job 输出、PR检查记录 |
| 例外审批口头化 | 双签字段强制（Tech Lead + 模块负责人） | PR body 校验器 | PR body 审计、失败日志 |
| 例外长期滞留 | TTL 到期自动失败 | ttl-gate 扫描过期项 | `ttl-gate-report.json` |
| 占位测试掩盖质量 | 禁止 `assert True` 占位（测试目录门禁） | test-placeholder 统计与周报追踪 | `test_placeholder_assert_count` 趋势 |
| 后端占位逻辑噪声过高 | placeholder 口径收窄（去 `pass` 粗匹配） | 口径版本化 + 抽样复核 | baseline 字段与抽样记录 |
| 文档状态与任务状态不一致 | OpenSpec tasks 为唯一进度源 | 发布前一致性检查 | `tasks.md` + 报告状态对照表 |

---

## 2. 必须执行的“防重复”守则

1. **先定 SoT，再定门禁**：所有阈值来源必须是单一基线文件，不得硬编码。
2. **先试点，再放量**：任何新门禁先在 4.1 范围运行两周。
3. **先记录，再豁免**：例外必须 owner/issue/ttl/reason/remediation 完整后才允许。
4. **先复盘，再更新基线**：基线更新必须附复盘结论，默认只降不升。
5. **先证据，再结论**：周报结论必须绑定命令输出/JSON 报告。
6. **先看 drift，再判回归**：涉及基线波动的结论必须同时附 `baseline-drift-report`，明确区分 `gated drift` 与 `observed drift`。

---

## 3. 周报必须包含的防重复指标

- 新增 suppressions 数
- 新增裸 TODO/FIXME/HACK 数
- 例外双签合规率
- TTL 到期未清理数
- test_placeholder_assert_count
- 误伤率（误伤/总阻断）

---

## 4. 触发器与处置剧本（Runbook）

### 触发器 A：误伤率 > 10%
- 处置：冻结新门禁范围扩张，24h 内完成误伤样本复盘。
- 责任：QA/效能 + 模块负责人。

### 触发器 B：双签合规率 < 95%
- 处置：暂停例外放行，仅保留紧急修复通道。
- 责任：Tech Lead。

### 触发器 C：基线指标连续两周上升
- 处置：进入“清债冲刺周”，暂停新增非关键特性。
- 责任：项目负责人 + Tech Lead。
- 复核要求：必须先核对 `reports/analysis/tech-debt-baseline-drift-report.json`，确认上升项属于真实回归而非口径修正或观察项波动。

---

## 5. 审计清单（每周）

- [ ] 本周是否存在硬编码阈值回流？
- [ ] 本周是否存在无 issue/ttl 的例外？
- [ ] 本周是否有“报告完成但 tasks 未回填”的状态漂移？
- [ ] 本周是否完成误伤样本复盘并形成修复项？
- [ ] 本周是否更新了下一周的风险热点 Top 清单？

---

## 6. 与 OpenSpec 任务关联建议

- 4.1：使用本清单第1~3节作为试点周执行标准。
- 4.2：使用第4~5节作为评审会输入材料。
- 4.3：将第4节触发器作为推广期回滚条件。
