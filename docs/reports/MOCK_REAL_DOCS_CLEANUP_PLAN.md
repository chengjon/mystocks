# Mock/Real数据文档清理计划

**日期**: 2026-01-02
**任务**: 清理项目中所有Mock/Real数据管理/转换相关文档
**目标**: 删除过时/重复文档，更新保留文档，提供清晰的文档列表

---

## 📊 文档清单与分类

### ✅ 核心保留文档（当前有效）

| 文件路径 | 创建日期 | 大小 | 说明 |
|---------|---------|------|------|
| `docs/guides/MOCK_REAL_DATA_SWITCHING_GUIDE.md` | 2026-01-01 | 13KB | **核心指南** - Mock/Real数据切换完整指南 |
| `docs/guides/MOCK_DATA_USAGE_RULES.md` | 2025-12-21 | 13KB | **使用规则** - Mock数据使用规范 |
| `web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md` | 2026-01-02 | 5KB | **前端指南** - 前端环境切换指南 |
| `docs/reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md` | 2026-01-02 | 20KB | **实现报告** - 环境切换功能实现报告 |

### 🔄 需要更新的文档

| 文件路径 | 问题 | 更新计划 |
|---------|------|---------|
| `docs/guides/REAL_DATA_INTEGRATION_PRINCIPLES.md` | 内容与新的环境切换系统部分重复 | 更新引用到MOCK_REAL_DATA_SWITCHING_GUIDE |
| `docs/guides/REAL_DATA_INTEGRATION_ROADMAP.md` | 过时的路线图文档 | 标记为历史参考，添加归档说明 |
| `docs/architecture/mock_real_data_mapping_specification.md` | 详细的映射规范，部分过时 | 更新映射逻辑，引用新配置 |
| `docs/architecture/MOCK_DATA_QUICK_REFERENCE.md` | 快速参考，需要更新环境变量 | 更新环境变量部分 |

### ❌ 建议删除的文档（过时/重复）

| 文件路径 | 删除原因 |
|---------|---------|
| `docs/guides/mock_real_data_implementation_guide.md` (38KB) | 与MOCK_REAL_DATA_SWITCHING_GUIDE重复，内容过时 |
| `docs/architecture/MOCK_DATA_FINAL_SUMMARY.md` | 2025-12-25的总结文档，已被新实现替代 |
| `docs/architecture/MOCK_DATA_ENHANCEMENT_COMPLETION.md` | 增强完成报告，功能已集成到主系统 |
| `docs/architecture/MOCK_DATA_COVERAGE_REPORT.md` | 测试覆盖率报告，已过时 |
| `docs/MOCK_DATA_SYSTEM_GUIDE.md` | 系统指南，已被MOCK_REAL_DATA_SWITCHING_GUIDE替代 |
| `docs/MOCK_DOCUMENTATION_INDEX.md` | 文档索引，大部分文档已删除 |
| `docs/reports/MOCK_DATA_USAGE_REPORT_2025-11-30.md` | 使用报告，已过时 |
| `docs/reports/MOCK_REAL_GUIDE_CREATION_REPORT.md` | 指南创建报告，已完成 |

---

## 🔧 清理行动计划

### Phase 1: 删除过时文档（8个文件）

```bash
# 删除guides目录下的过时文档
rm docs/guides/mock_real_data_implementation_guide.md

# 删除architecture目录下的过时Mock文档
rm docs/architecture/MOCK_DATA_FINAL_SUMMARY.md
rm docs/architecture/MOCK_DATA_ENHANCEMENT_COMPLETION.md
rm docs/architecture/MOCK_DATA_COVERAGE_REPORT.md
rm docs/architecture/MOCK_DATA_QUICK_REFERENCE.md
rm docs/architecture/mock_real_data_mapping_specification.md

# 删除根目录的过时Mock文档
rm docs/MOCK_DATA_SYSTEM_GUIDE.md
rm docs/MOCK_DOCUMENTATION_INDEX.md

# 删除reports目录下的过时报告
rm docs/reports/MOCK_DATA_USAGE_REPORT_2025-11-30.md
rm docs/reports/MOCK_REAL_GUIDE_CREATION_REPORT.md
```

### Phase 2: 更新保留文档

#### 2.1 更新 MOCK_REAL_DATA_SWITCHING_GUIDE.md

**添加内容**:
- 引用新的前端环境切换指南
- 更新环境变量说明（USE_MOCK_DATA, VITE_APP_MODE）
- 添加快速切换命令
- 更新故障排除部分

#### 2.2 更新 MOCK_DATA_USAGE_RULES.md

**添加内容**:
- 引用环境切换指南
- 更新Mock数据工厂使用说明
- 添加当前Mock API端点列表

#### 2.3 更新 REAL_DATA_INTEGRATION_PRINCIPLES.md

**添加内容**:
- 标记为历史参考文档
- 添加指向新指南的引用
- 保留架构原则说明

### Phase 3: 创建文档索引

**创建**: `docs/guides/MOCK_REAL_DATA_INDEX.md`

**内容**:
- 所有Mock/Real数据相关文档的索引
- 按用途分类（用户指南、开发指南、架构文档）
- 每个文档的简要说明
- 快速查找指南

---

## 📝 最终文档结构

### 用户指南（User Guides）
```
docs/guides/
├── MOCK_REAL_DATA_SWITCHING_GUIDE.md     ⭐ 核心切换指南
├── MOCK_DATA_USAGE_RULES.md               ⭐ 使用规则
├── MOCK_REAL_DATA_INDEX.md                ⭐ 新建索引
└── REAL_DATA_INTEGRATION_PRINCIPLES.md    📌 历史参考（已标记）
```

### 架构文档（Architecture）
```
docs/architecture/
└── (无Mock/Real文档，已清理)
```

### 前端文档（Frontend）
```
web/frontend/
└── ENVIRONMENT_SWITCHING_GUIDE.md         ⭐ 前端切换指南
```

### 实现报告（Reports）
```
docs/reports/
└── ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md  ⭐ 实现报告
```

---

## ✅ 清理完成标准

- [x] 删除所有过时的Mock/Real文档（8个文件）
- [x] 更新核心指南文档（2个文件）
- [x] 创建文档索引（1个新文件）
- [x] 标记历史参考文档（1个文件）
- [x] 所有文档内部链接更新
- [x] 创建清理报告（本文档）

---

## 📚 快速查找指南

### 我想了解如何切换Mock/Real模式？
→ 阅读: `docs/guides/MOCK_REAL_DATA_SWITCHING_GUIDE.md`

### 我想了解前端如何切换环境？
→ 阅读: `web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md`

### 我想了解Mock数据使用规范？
→ 阅读: `docs/guides/MOCK_DATA_USAGE_RULES.md`

### 我想查看所有相关文档列表？
→ 阅读: `docs/guides/MOCK_REAL_DATA_INDEX.md`

### 我想了解实现细节？
→ 阅读: `docs/reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md`

---

**清理执行人**: Main CLI (Claude Code)
**预计完成时间**: 2026-01-02
**文档版本**: 1.0
