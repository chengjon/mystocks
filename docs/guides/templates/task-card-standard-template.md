# 标准化任务卡模板（开发执行版）

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> 用途：将治理计划、修复任务、优化任务转为可执行卡片，确保“目标-动作-验收-责任-风险”完整闭环。  
> 适用：不依赖 Jira/飞书系统，纯文档/IM 也可直接使用。

---

## 任务卡模板

### 1) 基本信息
- **任务标题**：
- **任务编号**：
- **所属阶段**：Stage A / Stage B / Stage C / Rollout
- **优先级**：P0 / P1 / P2
- **负责人（R）**：
- **审批人（A）**：
- **协作者（C）**：
- **知会对象（I）**：
- **计划开始/截止**：

### 2) 背景与目标
- **背景问题**（发生了什么）：
- **目标结果**（希望达成什么）：
- **不做范围**（本卡不解决什么）：

### 3) 执行项（可勾选）
- [ ] 步骤 1：
- [ ] 步骤 2：
- [ ] 步骤 3：

### 4) 验收标准（DoD）
- **功能/行为验收**：
- **质量门验收**（示例：no-new-debt、baseline-non-increase、TTL gate）：
- **证据命令**（需可复现）：
  - `openspec validate <change-id> --strict`
  - `python scripts/dev/quality_gate/collect_tech_debt_baseline.py`
  - `<项目定向测试命令>`

### 5) 风险与应对
- **主要风险**：
- **触发条件**：
- **应对方案**：
- **回滚条件**：

### 6) 依赖与阻塞
- **前置依赖**：
- **外部阻塞**：
- **解除阻塞负责人**：

### 7) 例外与审批（如涉及）
- **是否申请 debt-exception**：是 / 否
- **例外元数据**（owner/issue/ttl/reason/remediation）：
- **双签审批**：
  - debt-exception-tech-lead-approved: yes/no
  - debt-exception-module-owner-approved: yes/no

### 8) 复盘记录
- **实际完成时间**：
- **偏差说明**（计划 vs 实际）：
- **复盘结论**（防重复措施）：

---

## 快速示例（可直接复制）

- **任务标题**：清理 trade routes 日期过滤占位逻辑
- **所属阶段**：Stage B
- **负责人（R）**：后端负责人
- **目标结果**：移除 TODO/pass 占位，提供可执行过滤与错误语义
- **执行项**：
  - [ ] 实现 start_date/end_date 解析与区间过滤
  - [ ] 非法日期返回 VALIDATION_ERROR
  - [ ] 补充对应定向测试
- **验收命令**：
  - `pytest tests/api/file_tests/test_trade_routes_api.py -k trade -q -o addopts=''`
  - `openspec validate refactor-technical-debt-remediation-wave1 --strict`
