# 文档整理执行指南

**创建日期**: 2026-01-07
**状态**: ✅ 已就绪

---

## 📋 快速开始

### 第一步：审阅报告

首先阅读详细的审阅报告：
```bash
cat docs/reports/DOCUMENT_ORGANIZATION_PLAN_REVIEW.md
```

**核心发现**:
- 🔴 实际有 **1,589个文档**（而非计划中的150+）
- 🔴 **95个子目录**（而非计划中的42个）
- ⚠️ 需要删除 **50%+ 的文档**

---

## 🛠️ 使用自动化工具

### 工具1：文档清单生成器

**功能**: 扫描所有文档，生成详细清单

**使用方法**:
```bash
# 基本使用
python scripts/tools/docs_inventory.py

# 指定路径
python scripts/tools/docs_inventory.py --path docs/

# 输出JSON和Markdown
python scripts/tools/docs_inventory.py --output docs-inventory

# 仅JSON格式
python scripts/tools/docs_inventory.py --output inventory.json --format json
```

**输出**:
- `docs-inventory.json` - 机器可读的清单
- `docs-inventory.md` - 人类可读的报告

**报告内容**:
- 📊 文档总数和大小
- 🔤 命名规范问题
- 📦 大文件检测（>1MB）
- 📅 旧文件检测（>180天）
- 📁 空目录检测

### 工具2：文档规范检查器

**功能**: 检查文档命名规范和结构问题

**使用方法**:
```bash
# 基本检查
python scripts/tools/docs_check.py

# 指定路径
python scripts/tools/docs_check.py --path docs/

# 保存报告
python scripts/tools/docs_check.py --output docs-check-report.md

# 自动删除空目录
python scripts/tools/docs_check.py --fix-empty-dirs

# 建议文件重命名
python scripts/tools/docs_check.py --suggest-renames
```

**检查项目**:
- 🔤 中文文件名/目录名
- 🔤 空格和特殊字符
- 📁 空目录
- 🔄 重复文档
- 📂 深层嵌套（>3层）
- 📋 缺失索引文件

### 工具3：文档索引生成器

**功能**: 自动生成文档索引

**使用方法**:
```bash
# 生成全局索引
python scripts/tools/docs_indexer.py

# 指定输出路径
python scripts/tools/docs_indexer.py --output docs/INDEX.md

# 同时生成各分类索引
python scripts/tools/docs_indexer.py --categories
```

**输出**:
- `docs/INDEX.md` - 全局文档索引
- `docs/*/INDEX.md` - 各分类索引（如果使用 `--categories`）

---

## 📅 分阶段执行计划

### 阶段0：准备与分析（2小时）

**目标**: 全面了解现状

**任务清单**:
- [ ] 1. 生成文档清单
  ```bash
  python scripts/tools/docs_inventory.py --output reports/docs-inventory
  ```

- [ ] 2. 执行规范检查
  ```bash
  python scripts/tools/docs_check.py --output reports/docs-check-report.md
  ```

- [ ] 3. 审阅报告
  - `reports/docs-inventory.md` - 文档清单
  - `reports/docs-check-report.md` - 规范检查

- [ ] 4. 创建备份分支
  ```bash
  git checkout -b docs-reorg-backup
  git push origin docs-reorg-backup
  ```

**预期输出**:
- 完整的文档清单（JSON + Markdown）
- 规范检查报告
- Git备份分支

---

### 阶段1：激进清理（1-2小时）

**目标**: 删除50%+的过时文档

**任务清单**:
- [ ] 1. 删除空目录
  ```bash
  python scripts/tools/docs_check.py --fix-empty-dirs
  ```

- [ ] 2. 手动审核重复文档
  - 查看 `docs-check-report.md` 中的 "重复文档" 部分
  - 保留最新版本，删除旧版本

- [ ] 3. 删除临时文件
  ```bash
  find docs/ -name "*~" -delete
  find docs/ -name "*.swp" -delete
  find docs/ -name ".DS_Store" -delete
  ```

- [ ] 4. 归档旧文档（>180天）
  ```bash
  # 创建归档目录
  mkdir -p docs/archive/old-docs

  # 移动旧文档（需手动审核）
  find docs/ -name "*.md" -mtime +180 -not -path "*/archive/*" -exec mv {} docs/archive/old-docs/ \;
  ```

**验收标准**:
- 文档数量减少50%+
- 无空目录
- 无明显重复文档

---

### 阶段2：目录重组（2-3小时）

**目标**: 按8大分类重新组织文档

**使用映射表**: 参见 `docs/reports/DOCUMENT_ORGANIZATION_PLAN_REVIEW.md` 第三章

**任务清单**:
- [ ] 1. 创建目标目录
  ```bash
  cd docs/
  mkdir -p overview guides api architecture operations testing reports archive
  ```

- [ ] 2. 迁移核心文档（P0）
  ```bash
  # 示例：迁移项目总览
  git mv "01-项目总览与核心规范/" overview/

  # 示例：清理根目录
  git mv HANDOVER_TASK.md overview/handover-tasks.md
  git mv TASK.md overview/task-tracker.md
  ```

- [ ] 3. 合并重复目录
  ```bash
  # 示例：合并architecture目录
  git mv architecture/* architecture/
  git mv "02-架构与设计文档/"* architecture/

  # 删除空目录
  rmdir "02-架构与设计文档/"
  ```

- [ ] 4. 重复步骤2-3，完成所有分类迁移

**重要提示**:
- **始终使用 `git mv`**（保留文件历史）
- **先迁移，后删除**
- **及时提交进度**

---

### 阶段3：索引创建（2小时）

**目标**: 生成完整的文档索引

**任务清单**:
- [ ] 1. 生成全局索引
  ```bash
  python scripts/tools/docs_indexer.py --output docs/INDEX.md
  ```

- [ ] 2. 生成分类索引
  ```bash
  python scripts/tools/docs_indexer.py --categories
  ```

- [ ] 3. 审阅索引
  ```bash
  cat docs/INDEX.md
  ```

- [ ] 4. 更新链接（如果需要）
  ```bash
  # TODO: 开发链接更新脚本
  ```

---

### 阶段4：最终验证（1小时）

**目标**: 确保所有文档可访问

**验收标准**:
- [ ] 1. 文档数量检查
  ```bash
  find docs/ -name "*.md" | wc -l
  ```
  **预期**: 500-800个（50%+减少）

- [ ] 2. 目录深度检查
  ```bash
  find docs/ -name "*.md" -printf "%d\n" | sort -n | tail -1
  ```
  **预期**: ≤3层

- [ ] 3. 空目录检查
  ```bash
  find docs/ -type d -empty | wc -l
  ```
  **预期**: 0个

- [ ] 4. 命名规范检查
  ```bash
  python scripts/tools/docs_check.py --path docs/
  ```
  **预期**: 0个命名问题

- [ ] 5. 索引完整性检查
  ```bash
  grep -r "\[.*\](.*\.md)" docs/INDEX.md | wc -l
  ```
  **预期**: 所有文档都被索引

- [ ] 6. 手动浏览索引
  ```bash
  # 在Markdown编辑器或浏览器中打开
  docs/INDEX.md
  ```

---

## 🚨 风险管理

### 备份策略

**在开始前执行**:
```bash
# 1. 完整备份
git add -A
git commit -m "backup: before docs reorganization"
git tag docs-reorg-backup-$(date +%Y%m%d)

# 2. 创建备份分支
git checkout -b docs-reorg-backup
git push origin docs-reorg-backup

# 3. 压缩归档
tar -czf docs-backup-$(date +%Y%m%d).tar.gz docs/

# 4. 返回主分支
git checkout main
```

### 回滚策略

**如果出现问题**:
```bash
# 方法1: 从备份分支恢复
git checkout docs-reorg-backup
git merge main

# 方法2: 从标签恢复
git checkout docs-reorg-backup-YYYYMMDD

# 方法3: 从压缩归档恢复
tar -xzf docs-backup-YYYYMMDD.tar.gz
```

---

## 📊 进度跟踪

**使用TodoWrite工具跟踪进度**:
```
- [ ] 阶段0：准备与分析
- [ ] 阶段1：激进清理
- [ ] 阶段2：目录重组
- [ ] 阶段3：索引创建
- [ ] 阶段4：最终验证
```

---

## 💡 最佳实践

1. **分阶段执行**: 不要一次性完成所有工作
2. **频繁提交**: 每完成一个任务就提交
3. **使用git mv**: 保留文件历史
4. **及时备份**: 定期创建备份点
5. **逐步验证**: 每阶段完成后验证

---

## 🆘 常见问题

### Q1: 如何确定哪些文档应该删除？

**A**: 使用以下标准：
- 📅 超过6个月未更新
- 🔄 内容完全重复
- 🗑️ 明显的临时文件
- 📦 旧的完成报告（已被新报告替代）

### Q2: 中文文件名如何处理？

**A**:
- **翻译成英文**: `用户指南.md` → `user-guide.md`
- **使用拼音**: `Wencai集成.md` → `wencai-integration.md`
- **保留在归档**: 如果不常用，移到 `archive/legacy-zh/`

### Q3: 如何处理深层嵌套？

**A**:
- **扁平化**: 将深层文件移到更浅的目录
- **重新组织**: 调整目录结构，减少层级
- **使用索引**: 通过索引导航，而非依赖目录层级

### Q4: 链接失效怎么办？

**A**:
1. 使用映射表记录路径变更
2. 批量更新文档内的链接
3. 在旧位置创建重定向文件

---

## 📞 获取帮助

如果遇到问题：
1. 查阅 `docs/reports/DOCUMENT_ORGANIZATION_PLAN_REVIEW.md`
2. 运行 `python scripts/tools/docs_check.py` 获取诊断
3. 检查Git历史: `git log --oneline --all`

---

**祝文档整理顺利！** 🎉
