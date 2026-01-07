# 文档整理工作指引

**版本**: v2.0
**最后更新**: 2026-01-07
**状态**: ✅ 已完成并验证

---

## 📋 快速参考

**新增文档时**，请遵循以下3步：
1. **确定分类** - 根据文档内容选择8大分类之一
2. **正确命名** - 使用kebab-case（小写+连字符）
3. **更新索引** - 运行索引生成工具

---

## 🗂️ 8大文档分类

### 1. Overview（项目概述）
**路径**: `docs/overview/`
**用途**: 项目总览、核心规范、宪章文档

**示例文档**:
- README.md - 项目说明
- agents.md - Agent配置
- claude.md - AI助手配置
- changelog.md - 变更日志

**放置规则**:
- ✅ 项目入口文档
- ✅ 核心配置说明
- ✅ 顶层设计文档
- ❌ 具体功能文档（放入相应分类）

### 2. Guides（开发指南）
**路径**: `docs/guides/`
**用途**: 开发规范、工作流程、最佳实践

**示例文档**:
- quick-start.md - 快速开始
- implementation-guide.md - 实现指南
- enhanced-ui-ux-guide.md - UI/UX指南

**放置规则**:
- ✅ How-to指南
- ✅ 开发规范文档
- ✅ 工作流程说明
- ❌ 架构设计（放入architecture/）

### 3. API（API文档）
**路径**: `docs/api/`
**用途**: API规范、接口文档、API契约

**示例文档**:
- API契约同步组件实现方案.md
- Web访问指南.md
- API接口对齐报告.md

**放置规则**:
- ✅ API规范文档
- ✅ 接口设计文档
- ✅ API测试文档
- ❌ 前端页面文档（放入前端分类）

### 4. Architecture（架构设计）
**路径**: `docs/architecture/`
**用途**: 系统架构、设计模式、数据架构

**示例文档**:
- ML集成完成报告.md
- Mock数据系统指南.md
- 备份策略架构优化.md

**放置规则**:
- ✅ 架构设计文档
- ✅ 数据库设计
- ✅ 系统组件设计
- ❌ 代码示例（放入代码仓库）

### 5. Operations（运维文档）
**路径**: `docs/operations/`
**用途**: 部署、监控、运维操作

**示例文档**:
- deployment-guide.md - 部署指南
- 日志查看工具集成.md
- 监控配置指南.md

**放置规则**:
- ✅ 部署文档
- ✅ 监控配置
- ✅ 运维手册
- ❌ 开发指南（放入guides/）

### 6. Testing（测试文档）
**路径**: `docs/testing/`
**用途**: 测试策略、测试计划、质量保障

**示例文档**:
- 测试策略与规范.md
- 层层测试指南.md
- BUGFIX-signals-500-error-retrospective.md

**放置规则**:
- ✅ 测试策略
- ✅ 测试用例
- ✅ 质量报告
- ❌ 测试代码（放入tests/）

### 7. Reports（分析报告）
**路径**: `docs/reports/`
**用途**: 阶段报告、分析报告、总结文档

**示例文档**:
- comprehensive-cleanup.md - 综合清理报告
- 项目进度追踪与风险管控.md
- 代码优化执行报告.md

**放置规则**:
- ✅ 阶段性报告
- ✅ 性能分析报告
- ✅ 项目总结
- ❌ 临时笔记（放入archive/）

### 8. Archive（归档文档）
**路径**: `docs/archive/`
**用途**: 历史文档、已废弃内容、参考资料

**放置规则**:
- ✅ 超过6个月的旧报告
- ✅ 已完成的项目文档
- ✅ 参考资料
- ❌ 当前活跃文档（放入相应分类）

---

## 📝 文档命名规范

### ✅ 推荐命名（kebab-case）

| 类型 | 格式 | 示例 |
|------|------|------|
| 英文 | `kebab-case.md` | `quick-start.md` |
| 拼音 | `pinyin-name.md` | `wencai-integration.md` |
| 组合 | `category-subject.md` | `api-authentication-jwt.md` |

### ❌ 不推荐命名

| 命名 | 问题 | 改为 |
|------|------|------|
| `README.md` | 太通用 | `guide-name.md` |
| `API文档.md` | 中文 | `api-documentation.md` |
| `My_Document.md` | 大写+下划线 | `my-document.md` |
| `文档名称.md` | 中文 | `document-name.md` |
| `Doc 1.md` | 空格 | `document-01.md` |

---

## 🔧 文档工作流程

### 新增文档流程

```bash
# 1. 确定文档分类
# 根据上述8大分类选择合适的位置

# 2. 创建文档（使用正确的命名）
vim docs/guides/your-new-guide.md

# 3. 编写文档内容
# 遵循Markdown最佳实践

# 4. 更新索引（自动）
python scripts/tools/docs_indexer.py --categories

# 5. 提交变更
git add docs/
git commit -m "docs: add your-new-guide documentation"
```

### 移动文档流程

```bash
# 1. 确认新位置
# 使用git mv保留历史
git mv docs/old/location.md docs/new/location.md

# 2. 更新引用
# 搜索并更新所有链接到此文档的地方

# 3. 更新索引
python scripts/tools/docs_indexer.py --categories

# 4. 提交变更
git commit -m "docs: rename and relocate document"
```

### 删除文档流程

```bash
# 1. 确认文档可以删除
# 检查是否有其他文档引用它

# 2. 删除文档
git rm docs/unwanted-doc.md

# 3. 更新索引
python scripts/tools/docs_indexer.py --categories

# 4. 提交变更
git commit -m "docs: remove unwanted-doc"
```

---

## 🚨 常见错误及修复

### 错误1：文档放在了错误的位置

**症状**: 文档难以被发现或归类不清

**修复**:
```bash
# 示例：架构文档误放在guides/
git mv docs/guides/system-design.md docs/architecture/

# 更新索引
python scripts/tools/docs_indexer.py --categories
```

### 错误2：文档命名不符合规范

**症状**: 文件名包含中文、空格或大写字母

**修复**:
```bash
# 示例：重命名为kebab-case
git mv "docs/API文档.md" docs/api/api-documentation.md

# 或使用中文拼音
git mv "docs/问财集成.md" docs/guides/wencai-integration.md
```

### 错误3：创建了大量临时文档

**症状**: docs/目录下有很多未分类的.md文件

**修复**:
```bash
# 1. 运行检查工具
python scripts/tools/docs_check.py

# 2. 查看报告
cat reports/docs-check-report.md

# 3. 根据建议整理
# - 移动到正确的分类
# - 删除临时文档
# - 重命名不符合规范的文档
```

---

## 🛠️ 自动化工具

### 日常维护工具

```bash
# 1. 检查文档规范
python scripts/tools/docs_check.py --output reports/check.md

# 2. 生成文档清单
python scripts/tools/docs_inventory.py --output reports/inventory.md

# 3. 更新文档索引
python scripts/tools/docs_indexer.py --categories

# 4. 查找重复文档
python scripts/tools/remove_duplicate_docs.py
```

### 快速检查脚本

```bash
# 一键检查所有
cat > check-docs.sh << 'EOF'
#!/bin/bash
echo "🔍 检查文档规范..."
python scripts/tools/docs_check.py --output /tmp/check-report.md

echo "📊 生成文档清单..."
python scripts/tools/docs_inventory.py --output /tmp/inventory.md

echo "🔄 更新文档索引..."
python scripts/tools/docs_indexer.py --categories

echo "✅ 检查完成！"
echo "查看报告："
echo "  - 规范检查: /tmp/check-report.md"
echo "  - 文档清单: /tmp/inventory.md"
EOF

chmod +x check-docs.sh
./check-docs.sh
```

---

## 📚 参考资源

### 相关文档

- **CLAUDE.md** - 项目开发指南
- **FILE_ORGANIZATION_RULES.md** - 文件组织规范
- **DOCUMENT_ORGANIZATION_PLAN_REVIEW.md** - 文档组织审阅报告

### 外部资源

- [Markdown最佳实践](https://guides.github.com/features/mastering-markdown/)
- [文档风格指南](https://diataxis.com/)
- [技术文档写作规范](https://developers.google.com/tech-writing/one)

---

## 🎯 最佳实践

### DO（应该做的）

✅ **新增文档时**
- 选择正确的8大分类之一
- 使用kebab-case命名
- 编写清晰的标题和描述
- 更新INDEX.md索引

✅ **编写文档时**
- 使用清晰的标题层级
- 添加代码示例
- 包含图表和截图
- 保持内容简洁明了

✅ **维护文档时**
- 定期更新过时内容
- 删除不再需要的文档
- 整理重复内容
- 更新索引

### DON'T（不应该做的）

❌ **不要**
- 在根目录创建大量.md文件
- 使用中文文件名（使用拼音或翻译）
- 创建深层嵌套目录（>3层）
- 忽略索引更新
- 将文档放在错误的位置

---

## 🔗 相关链接

### 内部链接

- [项目开发规范](../CLAUDE.md)
- [文件组织规则](standards/file-organization-rules.md)
- [文档组织完成报告](../reports/DOC_CLEANUP_COMPLETION_REPORT.md)

### 快速命令

```bash
# 查看全局索引
cat docs/INDEX.md

# 搜索特定文档
find docs/ -name "*.md" | xargs grep -l "keyword"

# 统计文档数量
find docs/ -name "*.md" | wc -l

# 运行完整检查
python scripts/tools/docs_check.py
```

---

**文档维护**: 本文档应随项目演化定期更新
**反馈渠道**: 如有问题或建议，请提交Issue或PR
**版本历史**: v1.0 (2025-12-01) → v2.0 (2026-01-07)
