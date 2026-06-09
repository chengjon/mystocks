# Mock/Real数据文档索引

> **导航说明**:
> 本文件主要用于为当前目录下的文档、资料或专题内容提供导航入口，方便快速定位相关材料。
> 目录项和链接关系仅反映整理时结构；判断当前事实时，仍应以 `architecture/STANDARDS.md`、当前实现与最新主线文档为准。


**最后更新**: 2026-04-25
**维护者**: Main CLI (Claude Code)

---

## 📋 快速导航

### 🎯 我想要...

| 需求 | 推荐文档 |
|------|---------|
| 了解当前 Mock 使用边界 | [Mock数据使用规则](#1-mock数据使用规则) |
| 了解如何切换Mock/Real模式 | [Mock/Real数据切换指南](#2-mockreal数据切换指南) |
| 了解前端环境切换 | [前端环境切换指南](#前端环境切换指南) |
| 了解Mock数据使用规范 | [Mock数据使用规则](#1-mock数据使用规则) |
| 查看所有相关文档列表 | [本文档](#mockreal数据文档索引) |
| 了解环境切换实现细节 | [环境切换实现报告](#环境切换实现报告) |
| 了解Real数据集成原则 | [Real数据集成原则](#real数据集成原则-历史参考) |

---

## 📚 核心文档

### 1. Mock数据使用规则

**路径**: `docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md`
**类型**: 当前专题执行细则
**适用人群**: 开发人员、评审人员、文档维护者

**内容概览**:
- ✅ Mock 的允许场景与禁止场景
- ✅ `verified / pending` 页面行为边界
- ✅ 为什么 Mock 不能作为默认静默兜底
- ✅ 当前仓库中多层 Mock 资产的角色划分

---

### 2. Mock/Real数据切换指南

**路径**: `docs/guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md`
**类型**: 核心用户指南
**适用人群**: 开发人员、测试人员、运维人员

**内容概览**:
- ✅ 当前 Mock/Real 运行模式说明
- ✅ 后端数据源切换（USE_MOCK_DATA）
- ✅ 前端切换与 readiness / `VITE_USE_MOCK_DATA`
- ✅ 真实联调与显式 Mock 验收的判定边界
- ✅ `verified / pending` 页面与切换策略关系

**快速链接**:
```bash
# 查看文档
cat docs/guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md

# 或使用代码编辑器打开
code docs/guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md
```

---

### 3. 前端环境切换指南

**路径**: `web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md`
**类型**: 前端开发指南
**大小**: 5KB
**最后更新**: 2026-01-02
**阅读时间**: 5分钟
**适用人群**: 前端开发人员

**内容概览**:
- ✅ 前端本地切换方法
- ✅ 当前模式验证
- ✅ `VITE_USE_MOCK_DATA` 与后端 `USE_MOCK_DATA` 的配合
- ✅ 常见排障

**快速切换**:
```bash
# 切换到Mock模式
cd web/frontend
cp .env.mock .env
npm run dev

# 切换到Real模式
cd web/frontend
cp .env.real .env
npm run dev
```

---

### 4. 环境切换实现报告

**路径**: `docs/reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md`
**类型**: 技术实现报告
**大小**: 20KB
**最后更新**: 2026-01-02
**阅读时间**: 15分钟
**适用人群**: 架构师、技术负责人

**内容概览**:
- ✅ 实现任务概述
- ✅ 后端配置更新
- ✅ 前端服务更新
- ✅ NPM脚本添加
- ✅ 环境配置文件
- ✅ 架构分析
- ✅ 测试验证结果

**技术亮点**:
- 后端通过 `USE_MOCK_DATA` 控制 Mock API 注册
- 前端文档存在历史 `VITE_APP_MODE` 口径，执行时应回到当前代码复核
- 文内结论属于历史实现报告，不应直接替代当前 repo-truth

---

## 📌 历史参考文档

### 5. Real数据集成原则

**路径**: `docs/guides/mock-data/REAL_DATA_INTEGRATION_PRINCIPLES.md`
**类型**: 历史参考文档
**大小**: 27KB
**最后更新**: 2025-12-21
**状态**: ⚠️ 部分内容已被新指南替代

**说明**:
本文档包含更早期的 Real 数据集成设想与架构思路。建议优先阅读 `MOCK_DATA_USAGE_RULES.md` 与 `MOCK_REAL_DATA_SWITCHING_GUIDE.md`，本文档仅保留作为历史参考。

**相关内容**:
- 数据分类体系
- 数据存储策略
- 质量保证机制
- 性能优化方案

---

## 🎓 按角色分类的文档推荐

### 前端开发人员
1. **必读**: [Mock数据使用规则](./MOCK_DATA_USAGE_RULES.md)
2. **必读**: [前端环境切换指南](../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)
3. **推荐**: [Mock/Real数据切换指南](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)

### 后端开发人员
1. **必读**: [Mock数据使用规则](./MOCK_DATA_USAGE_RULES.md)
2. **必读**: [Mock/Real数据切换指南](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)
3. **推荐**: [环境切换实现报告](../reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md)

### 测试人员
1. **必读**: [Mock数据使用规则](./MOCK_DATA_USAGE_RULES.md)
2. **必读**: [前端环境切换指南](../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)
3. **推荐**: [Mock/Real数据切换指南](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)

### 运维人员
1. **必读**: [Mock/Real数据切换指南](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)
2. **推荐**: [环境切换实现报告](../reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md) - 第6节"使用方法"

### 架构师
1. **推荐**: [环境切换实现报告](../reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md)
2. **参考**: [Real数据集成原则](./REAL_DATA_INTEGRATION_PRINCIPLES.md) - 历史参考

### 6. Real数据对接路线图

**路径**: `docs/guides/mock-data/REAL_DATA_INTEGRATION_ROADMAP.md`
**类型**: 历史路线图文档
**状态**: ⚠️ 历史参考

### 7. Phase 2 Real Data Integration Plan

**路径**: `docs/guides/mock-data/PHASE_2_REAL_DATA_INTEGRATION_PLAN.md`
**类型**: 阶段实施计划
**状态**: 📌 历史执行方案

---

## 🔍 文档关键词索引

### 快速查找关键词

| 关键词 | 相关文档 | 章节 |
|--------|---------|------|
| Mock 使用边界 | Mock数据使用规则 | 全文 |
| 环境切换 | Mock/Real数据切换指南 | 全文 |
| USE_MOCK_DATA | Mock/Real数据切换指南 | 当前主要开关 |
| VITE_USE_MOCK_DATA | Mock/Real数据切换指南 | 当前主要开关 |
| VITE_APP_MODE | 前端环境切换指南 | 历史口径，需与当前代码复核 |
| Mock数据规范 | Mock数据使用规则 | 全文 |
| verified / pending | Mock数据使用规则 | 当前主线规则 |
| API端点切换 | 环境切换实现报告 | 历史实现说明 |
| 故障排除 | 前端环境切换指南 | 第6节 |
| 数据源架构 | Mock/Real数据切换指南 | 第2节 |
| 实现细节 | 环境切换实现报告 | 全文 |

---

## 📊 文档统计

| 类型 | 数量 | 总大小 |
|------|------|--------|
| 核心指南 | 3 | 31KB |
| 前端指南 | 1 | 5KB |
| 实现报告 | 1 | 20KB |
| 历史参考 | 1 | 27KB |
| **总计** | **6** | **83KB** |

---

## 🔄 文档更新历史
### 2026-04-25
- ✅ 调整 family 入口顺序为“规则优先，切换其次”
- ✅ 将旧 `README_MOCK_DATA.md` 明确降级为历史快照
- ✅ 更新索引文案，避免继续把旧主指南表述成“当前最新真相”

### 2026-01-02
- ✅ 创建前端环境切换指南
- ✅ 创建环境切换实现报告
- ✅ 删除10个过时/重复文档
- ✅ 创建本文档索引

### 2025-12-21
- ✅ 更新Mock数据使用规则
- ✅ 更新Real数据集成原则

### 2025-01-21
- ✅ 创建Mock/Real数据切换指南（初版）

---

## ❓ 常见问题

### Q: 如何判断某个页面还能不能继续用 Mock 兜底？
**A**: 先看[Mock数据使用规则](./MOCK_DATA_USAGE_RULES.md)。如果该页面已经进入 `verified` 主线，默认不允许对同一路径静默回退 mock。

### Q: 如何快速切换到Mock模式？
**A**: 先看[Mock/Real数据切换指南](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)，再结合[前端环境切换指南](../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)执行当前代码支持的切换方式。

### Q: Mock数据使用有哪些规则？
**A**: 参考[Mock数据使用规则](./MOCK_DATA_USAGE_RULES.md)的核心原则章节。

### Q: 环境切换如何实现的？
**A**: 参考[环境切换实现报告](../reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md)的技术实现部分。

### Q: 遇到问题如何排查？
**A**: 参考[前端环境切换指南](../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)的故障排除章节。

---

## 📞 反馈与贡献

如果您发现文档有任何问题或有改进建议，请：
1. 提交Issue描述问题
2. 提交PR直接修改文档
3. 联系维护者：Main CLI (Claude Code)

---

**文档版本**: 1.0
**维护周期**: 按需更新
**文档状态**: supporting family index
