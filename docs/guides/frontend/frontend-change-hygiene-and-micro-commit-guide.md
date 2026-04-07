# Frontend Change Hygiene and Micro-Commit Guide

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 目的

本指南用于约束前端改动在多人 / 多 CLI / 多线程并行环境下的变更卫生（change hygiene），降低主线污染、回归扩散、误删功能、以及“一个文件混入多个意图”带来的治理成本。

适用范围：

- `web/frontend/` 下的路由、页面、组件、API 客户端、类型、测试
- Main CLI 向多个 worker CLI 分发任务前的主线整理
- 需要 selective staging、micro-commit、cherry-pick、回滚、bisect 的场景

---

## 为什么要拆成独立微提交

独立微提交的核心价值不是“提交更小”，而是“**一次提交只表达一个意图**”。

### 直接收益

1. **更容易审查**
   - reviewer 可以快速看出：这是路由语义变更、测试对齐、导入规范化，还是功能删除。
   - 避免“同一提交里既改首页语义，又顺手重构 E2E，又夹带生成文件漂移”。

2. **更容易回滚**
   - 如果某条变更有问题，可以精确回滚一条 commit，而不是回滚一整包混合修改。

3. **更容易拣选 / 合并**
   - 在 `main` 需要给 worker CLI 分发干净基线时，可按需 `cherry-pick` 某一条小提交。

4. **更容易定位回归**
   - `git bisect`、对比 CI、定位行为变化时，一条 commit 只对应一个意图，问题定位速度更快。

5. **更适合脏工作区**
   - 当仓库同时存在来自其他线程、其他 CLI、用户本地开发的改动时，小提交更适合 selective staging。

6. **更容易区分“功能变更”与“治理动作”**
   - 例如：
     - `restore dashboard as canonical home route`
     - `align artdeco integration home route`
     - `normalize api import extensions`
   - 三者都很小，但语义完全不同，应该分开。

### 何时不该过度拆分

- 如果多处改动共同构成一个不可分割的功能语义，应该保持在同一提交中。
- 判断标准不是“文件数”，而是“**意图是否单一**”。

---

## 近期工作的经验总结

以下经验来自近期对 `main` 分支的整理、路由 canonical 回滚、测试对齐以及小批次提交实践。

### 1. 先整理语义，再整理样式

优先处理“影响行为和入口语义”的改动，例如：

- 首页 canonical 路径
- legacy redirect
- 菜单 / breadcrumb / hardcoded links
- 与 canonical 绑定的验证测试

这类变更应该先独立落地，避免和导入格式、时间戳、注释更新混在一起。

### 2. 生成文件不能只看结果，要看生成源

像 `pageConfig.ts` 这类文件，如果只改生成结果、不改生成器或校验器，后面很容易再次漂移。

建议：

- 若语义来自生成源，优先修改生成源
- 若只需局部修正，必须说明为什么没有全量重生成
- 若校验器不理解新语义，要一并修补校验链路

### 3. 一个文件经常承载多个意图，不能整文件提交

典型场景：

- `router/index.ts` 里同时存在首页路由调整和其他长期未整理的大块变动
- E2E 文件里同时存在目标路径修正和无关测试重构

处理原则：

- 默认先 `git diff` 分析
- 必要时使用 `git add -p`
- 只把当前意图对应的 hunk 纳入提交

### 4. “命中字符串”不等于“还要改”

例如 `dealing-room` 命中结果可能属于：

- 兼容跳转路径
- 兼容测试用例
- 文档示例
- 运行时常量
- 真正的旧入口残留

必须先分类，再改动。

### 5. 主线要保持可分发，不要把实验态和治理态混在一起

当 `main` 将作为多 CLI 分发基线时，应优先做到：

- 首页入口语义明确
- 路由兼容关系明确
- 测试含义明确
- 提交边界清楚

否则 worker CLI 拿到的是“看似能跑，实际语义混乱”的基线。

---

## 推荐的提交粒度

### 推荐

- 1 个明确语义目标 = 1 条提交
- 例子：
  - 恢复 `/dashboard` 为 canonical 首页
  - 让单个 E2E 文件跟随 canonical 路径
  - 统一一个服务层文件的本地导入扩展名
  - 补一条校验器规则以支持新常量语义

### 不推荐

- 在同一提交里混入：
  - canonical 路由变更
  - unrelated test refactor
  - generator 全量漂移
  - import cleanup
  - comment / timestamp 更新

---

## 开发人员事前应遵守的行为规范

以下规范的目标是：**尽量在开发时就保持整洁，而不是事后由主 CLI 清理。**

### A. 提交前先给改动分类

每次准备提交前，先自问当前改动属于哪一类：

- 功能语义变更
- 兼容层修正
- 测试对齐
- 生成链路修正
- 导入 / 格式规范化
- 技术债治理
- 删除 / 下线

**不同类别默认不要混在同一提交中。**

### B. 不要把“顺手修一下”混进主任务

如果你正在做首页路由修复，就不要顺手把：

- unrelated import path
- unrelated E2E 重构
- unrelated mock 替换
- unrelated 时间戳生成

一起放进来。

### C. 改生成结果时，必须检查生成源与校验器

如果你改了：

- 自动生成类型
- 路由派生配置
- 校验器 / hook / lint 规则

就必须同步检查：

- 源头脚本是否要改
- 校验链是否理解新语义
- 是否会下次重生成时被冲掉

### D. 路由 canonical 改动必须显式声明兼容关系

若涉及首页 / 主入口 / 路由别名变更，必须明确写出：

- canonical route 是谁
- legacy route 是谁
- redirect 方向是什么
- 哪些测试验证 canonical
- 哪些测试验证 compatibility

### E. 删除前必须做“代码路径 + 功能树”双判定

这是强制规则，详见：

- `AGENTS.md`
- `CLAUDE.md`

简化版要求：

- 先判断它是否仍在运行链路中
- 再判断它在功能树里的状态
- 无法证明安全时，默认不删

### F. 对混杂文件优先使用 selective staging

当一个文件里混有多个意图时：

1. 先保留工作区改动
2. 使用 `git add -p`
3. 只 stage 当前语义对应的 hunk
4. 提交说明只描述当前意图

### G. 提交信息要体现“语义边界”

好的提交信息应该能直接回答：

- 改了哪个功能节点
- 这次是功能变更、测试对齐还是规范化
- 是否影响兼容关系

例如：

- `refactor(frontend): restore dashboard as canonical home route`
- `test(frontend): align artdeco integration home route`
- `style(frontend): normalize strategy service imports`

---

## Main CLI / Worker CLI 协作建议

### 对 Main CLI

- 在 `main` 上优先做“基线整理型”改动
- 将可独立拣选的小语义修正拆成微提交
- 分发给 worker CLI 前，优先确保主线的路由、命名、入口语义清晰

### 对 Worker CLI

- 一个 worktree 最好只承载一个主题
- 若发现工作区里有别的线程产生的混杂改动，不要整包提交
- 在 `TASK-REPORT` 中明确：
  - 改动属于哪个功能节点
  - 是功能、测试、规范化还是清理
  - 是否存在未纳入本次提交的旁支改动

---

## 实操检查清单

提交前建议至少检查以下 8 项：

1. 这次提交是否只有一个明确意图？
2. 是否混入了 unrelated test refactor？
3. 是否混入了 unrelated import cleanup？
4. 是否改了生成结果但没改生成源？
5. 是否改了生成源但没验证校验器？
6. 是否把 compatibility path 误当成旧垃圾删除？
7. 是否需要 `git add -p` 而不是整文件 `git add`？
8. 提交信息是否足够表达功能边界？

---

## 建议作为团队默认约定

建议开发者在开始编码前默认遵守以下约定：

- 一次任务尽量只动一个功能语义
- 发现旁支问题先记下来，不要顺手混入
- 修改路由时同步写清 canonical / legacy 关系
- 修改生成物时同步检查生成器和校验器
- 删除前做功能树判定，不凭“未引用”直接删除
- 在脏工作区中优先 selective staging，不做整包提交

---

## 结论

微提交不是形式主义，而是为了让：

- `main` 更干净
- 多 CLI 协作更稳定
- review / rollback / cherry-pick 更便宜
- 误删功能和语义混乱更少

如果开发人员能在编码阶段就遵守这些规则，主 CLI 后续就不需要花大量时间做“事后整理桌子”的工作。
