# MyStocks ArtDeco v3.1 入口文件瘦身与架构解耦深度分析报告

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


## 1. 概述 (Overview)
针对 MyStocks 平台中长期存在的“巨型入口文件”技术债务，本次治理通过 **Barrel Export（桶导出）模式** 与 **逻辑物理外迁** 策略，完成了对前端类型定义、运维脚本及测试套件的深度手术。本次更新标志着系统从“巨石架构”向“模块化分层”的正式转型。

---

## 2. 更新要点汇总 (Key Implementation Points)

### 2.1 物理隔离与代理化
- **前端类型系统**: [common.ts](../web/frontend/src/api/types/common.ts) 从 2251 行瘦身为 21 行，仅保留核心响应契约及 `common/all.ts` 的重定向导出。
- **运维运行器**: [web-usability-runner.js](../scripts/tests/web-usability-runner.js) 瘦身为代理脚本，核心逻辑剥离至 `runner-core.js`。
- **自动化测试**: [api-automation.spec.js](../web/frontend/tests/api-automation.spec.js) 瘦身为引用外壳，测试套件外迁至专门的 `legacy-suite.js`。

### 2.2 守护与生成策略
- **自动化红线**: 部署 [test_large_file_top5_guardrail.py](../scripts/tests/test_large_file_top5_guardrail.py) 实时监控 Top 5 风险文件。
- **契约驱动生成**: 更新了 [generate_frontend_types.py](../scripts/generate_frontend_types.py) 的拆分算法，使未来生成的类型自动符合“瘦身入口”规范。

---

## 3. 核心优势提炼 (Architectural Benefits)

### 🚀 模块加载优化 (Module Loading)
- **从“巨石解析”到“索引检索”**: 编译器和运行时无需在加载基础类型时扫描数千行无关代码。瘦身后的入口文件充当了高效的“分拣中心”，大幅提升了模块初始化的速度。

### 🔗 依赖管理与解耦 (Dependency Management)
- **切断耦合死结**: 通过“声明”与“实现”的分离，消除了入口文件由于承载过多逻辑而引发的 **Circular Dependencies（循环依赖）**。定义了清晰的单向引用链，提升了系统的鲁棒性。

### 🛡️ 架构边界划分 (Code Boundaries)
- **契约层与实现层分离**: 
    - **入口文件 = 契约**: 定义了“外部可以访问什么”。
    - **核心文件 = 实现**: 定义了“内部逻辑如何运作”。
- 为后续的 **Wave 4/5 垂直切片（Vertical Slicing）** 重构奠定了物理结构基础。

### 🛠️ 可维护性飞跃 (Maintainability)
- **消除 LSP 延迟**: 彻底解决了 IDE (VS Code) 在处理 2000+ 行复杂类型文件时的补全卡顿。
- **语义化 Git Diff**: 类型变更现在集中在 `common/all.ts`，不再与入口元数据混杂，使代码审查（Code Review）更具业务针对性。

### 📈 性能与构建提效 (Performance)
- **加快 HMR 响应**: Vite 的预构建（Pre-bundling）和热更新扫描效率与文件大小呈反比。较小的入口文件显著缩短了开发环境下的刷新反馈周期。
- **增强 Tree-Shaking**: 清晰的导出链有助于构建工具（Rollup/Esbuild）生成更精确的依赖图谱，优化最终 Bundle 的体积。

---

## 4. 关联文档索引 (Reference)
- [工程红线与架构准则 (STANDARDS.md)](../../architecture/STANDARDS.md)
- [Top 5 大文件治理执行报告](../../reports/compliance/top5_large_file_splitting_report.md)
- [大文件例外登记表 (exceptions/large_files.md)](exceptions/large_files.md)

---
**版本**: v1.0 (ArtDeco Governance)  
**日期**: 2026-02-16
