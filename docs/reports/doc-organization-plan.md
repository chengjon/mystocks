# MyStocks 项目文档整理方案

**版本**: 1.0
**创建日期**: 2026-01-07
**状态**: 待审批

---

## 一、现状分析

### 1.1 文档分布统计

| 目录 | 大小 | 文件数 | 主要问题 |
|------|------|--------|----------|
| `docs/` | 58M | ~150+ | 42个子目录，结构混乱，命名不一致 |
| `openspec/` | 1.3M | ~20 | 规范的spec/changes结构，缺少索引 |
| `reports/` | 98M | ~200+ | 生成物未分类，混有临时文件 |
| `monitoring_data/` | 212K | ~10 | 监控相关数据，可独立归档 |
| `specs/` | 996K | ~15 | OpenSpec规范文档 |
| `smart_analysis_reports/` | 48K | ~10 | 分析报告，可整合 |
| `load_test_reports/` | 36K | ~5 | 压测报告，可整合 |
| 根目录残留 | - | 7+ | HANDOVER_TASK.md等遗留文档 |
| 测试目录 | - | 3 | `test-directory-org/`等需清理 |

### 1.2 文档分类现状

**docs/目录结构（现状）：**
```
docs/
├── 01-项目总览与核心规范/
├── 02-架构与设计文档/
├── 03-API与功能文档/
├── 04-测试与质量保障文档/
├── 05-部署与运维监控文档/
├── 06-项目管理与报告/
├── 07-归档文档/
├── api/
├── architecture/
├── design/
├── guides/
├── monitoring/
├── operations/
├── performance/
├── security/
├── standards/
├── testing/
├── web/
├── web-dev/
├── archived/
├── archive/
├── completion_reports/
├── deployment/
├── e2e/
├── features/
├── frontend/
├── function-classification-manual/
├── monitoring_reports/
├── phase_reports/
├── project_management/
├── reviews/
├── security/
├── tdx_integration/
├── technical_debt/
├── test_reports/
├── testing/
├── 归档文档/
├── ai_tools/
├── archive/
├── archived/
├── buger/
├── cli_reports/
├── completion_reports/
├── design-references/
├── monitoring/
├── monitoring_reports/
├── operations/
├── performance/
├── phase_reports/
├── project_management/
├── reviews/
├── security/
├── technical_debt/
├── test_reports/
├── testing/
└── tasks/
```

### 1.3 主要问题

1. **目录过深**: 部分文档路径达到4-5层嵌套
2. **命名混乱**: 中英文混杂，数字前缀不统一
3. **内容重复**: 多处存在相似或相同的文档
4. **职责不清**: `docs/`与`specs/`、`openspec/`边界模糊
5. **归档缺失**: 历史版本和临时文件未及时清理
6. **索引缺失**: 无法快速定位所需文档

---

## 二、目标状态

### 2.1 标准化目录结构

```
Project_Root/
├── README.md                    # 项目入口
├── CLAUDE.md                    # AI助手配置
├── AGENTS.md                    # 编码规范
│
├── src/                         # 源代码
├── config/                      # 配置
├── tests/                       # 测试
│
├── docs/                        # 主文档目录
│   ├── INDEX.md                 # 文档总索引
│   ├── 01-overview/             # 项目概述
│   │   ├── README.md            # 项目说明
│   │   ├── QUICK_START.md       # 快速开始
│   │   ├── ARCHITECTURE.md      # 架构总览
│   │   └── GLOSSARY.md          # 术语表
│   │
│   ├── 02-guides/               # 开发指南
│   │   ├── DEVELOPMENT.md       # 开发规范
│   │   ├── CODING_STYLE.md      # 代码风格
│   │   ├── GIT_WORKFLOW.md      # Git工作流
│   │   ├── DEBUGGING.md         # 调试指南
│   │   └── CONTRIBUTING.md      # 贡献指南
│   │
│   ├── 03-api/                  # API文档
│   │   ├── REFERENCE.md         # API参考
│   │   ├── ENDPOINTS.md         # 端点说明
│   │   └── CHANGELOG.md         # 变更日志
│   │
│   ├── 04-architecture/         # 架构设计
│   │   ├── OVERVIEW.md          # 架构概述
│   │   ├── COMPONENTS.md        # 组件设计
│   │   ├── DATABASE.md          # 数据库设计
│   │   └── PATTERNS.md          # 设计模式
│   │
│   ├── 05-deployment/           # 部署运维
│   │   ├── DEPLOYMENT.md        # 部署指南
│   │   ├── MONITORING.md        # 监控配置
│   │   ├── TROUBLESHOOTING.md   # 故障排查
│   │   └── SECURITY.md          # 安全指南
│   │
│   ├── 06-testing/              # 测试文档
│   │   ├── STRATEGY.md          # 测试策略
│   │   ├── E2E_GUIDE.md         # E2E测试指南
│   │   ├── UNIT_TESTS.md        # 单元测试
│   │   └── COVERAGE.md          # 覆盖率报告
│   │
│   ├── 07-reports/              # 分析报告
│   │   ├── PERFORMANCE/         # 性能报告
│   │   ├── SECURITY/            # 安全审计
│   │   └── QUALITY/             # 质量报告
│   │
│   └── 08-archive/              # 归档文档
│       ├── deprecated/          # 废弃文档
│       ├── legacy/              # 历史版本
│       └── migrations/          # 迁移记录
│
├── openspec/                    # OpenSpec规范（保持原结构）
│   ├── project.md
│   ├── AGENTS.md
│   ├── specs/
│   │   └── [capability]/
│   └── changes/
│       └── [change-name]/
│
├── monitoring_data/             # 监控数据（保留）
├── load_test_reports/           # 压测报告（保留）
└── reports/                     # 生成物
    ├── analysis/                # 分析结果
    ├── coverage/                # 覆盖率
    └── logs/                    # 运行日志
```

### 2.2 命名规范

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 目录 | 2位数字-英文描述 | `01-overview/`, `02-guides/` |
| 文档 | 英文命名，PascalCase或kebab-case | `DEPLOYMENT_GUIDE.md` |
| 索引 | `INDEX.md` | 每个目录顶层放置 |
| 归档 | `YYYY-MM/`, `archive/` | `2024-12/`, `archive/` |

---

## 三、实施计划

### 3.1 阶段一：准备与规划（预计1小时）

- [ ] 确认方案审批
- [ ] 创建目标目录结构
- [ ] 备份现有文档

### 3.2 阶段二：文档迁移（预计2-3小时）

| 优先级 | 任务 | 操作 |
|--------|------|------|
| P0 | 根目录残留文档 | 移动到 `docs/01-overview/` |
| P0 | `docs/01-项目总览与核心规范/*` | 重命名为英文 |
| P1 | `docs/02-架构与设计文档/*` | 移动到 `docs/04-architecture/` |
| P1 | `docs/03-API与功能文档/*` | 移动到 `docs/03-api/` |
| P1 | `docs/04-测试与质量保障文档/*` | 移动到 `docs/06-testing/` |
| P1 | `docs/05-部署与运维监控文档/*` | 移动到 `docs/05-deployment/` |
| P2 | `docs/06-项目管理与报告/*` | 移动到 `docs/07-reports/` |
| P2 | `docs/07-归档文档/*` | 合并到 `docs/08-archive/` |
| P3 | `docs/api/*` | 合并到 `docs/03-api/` |
| P3 | `docs/guides/*` | 合并到 `docs/02-guides/` |
| P3 | `docs/design/*` | 合并到 `docs/04-architecture/` |
| P4 | `openspec/` | 添加 `INDEX.md` |
| P4 | `reports/` | 按类型分档 |

### 3.3 阶段三：清理与优化（预计1小时）

- [ ] 删除空目录
- [ ] 合并重复文档
- [ ] 更新文档内部链接
- [ ] 创建各目录INDEX.md

### 3.4 阶段四：验证与收尾（预计1小时）

- [ ] 验证文档可访问性
- [ ] 更新AGENTS.md文档路径
- [ ] 创建全局INDEX.md
- [ ] 提交变更

---

## 四、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 文档链接失效 | 文档不可用 | 使用grep检查所有内部链接，批量更新 |
| 内容丢失 | 重要文档丢失 | 迁移前完整备份 |
| 耗时超预期 | 影响其他工作 | 分阶段执行，可暂停 |

---

## 五、验收标准

1. 所有文档迁移到目标目录
2. 根目录无.md文件残留（除README/AGENTS/CLAUDE外）
3. 文档命名符合规范
4. 全局INDEX.md可正常浏览
5. 无死链接

---

## 六、待确认事项

- [ ] 文档命名是否全部使用英文？
- [ ] 是否接受当前目录结构设计？
- [ ] 是否需要在迁移后删除原目录？
- [ ] 是否需要保留历史版本（中文文档）？

---

**审批人**: ____________

**审批日期**: ____________

**审批状态**: ☐ 批准 ☐ 批准但有修改 ☐ 拒绝
