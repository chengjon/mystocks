# 项目目录重组执行指南

生成时间: 2025-11-08
状态: ✅ 准备就绪

---

## 📋 重组概览

### 主要改进
1. **统一源代码**: 所有Python模块集中到 `src/` 目录
2. **整合文档**: 文档统一到 `docs/` 目录
3. **清理缓存**: 删除测试覆盖报告、Python缓存等
4. **归档旧代码**: 移动到隐藏的 `.archive/` 目录
5. **优化.gitignore**: 排除开发工具目录和临时文件

### 保持不变的目录
- ✅ `.claude/` - Claude工具配置
- ✅ `.taskmaster/` - TaskMaster配置
- ✅ `.specify/` - Specify配置
- ✅ `.benchmarks/` - 性能基准
- ✅ `temp/` - 临时文件（已在.gitignore中）
- ✅ `web/` - Web应用
- ✅ `tests/` - 测试代码
- ✅ `scripts/` - 脚本工具（已整理）

---

## 🚀 快速开始

### 方式1: 自动执行（推荐）

```bash
# 1. 切换到项目根目录
cd /opt/claude/mystocks_spec

# 2. 运行重组脚本
bash reorganize_project.sh

# 3. 更新import路径
python3 update_imports.py

# 4. 验证
pytest tests/
```

### 方式2: 手动执行（逐步）

详见下方"详细步骤"章节

---

## 📝 详细步骤

### 步骤1: 备份（必须！）

```bash
cd /opt/claude/mystocks_spec

# 创建Git备份标签
git add -A
git commit -m "backup: before directory reorganization"
git tag backup-$(date +%Y%m%d-%H%M%S)

# 确认备份
git tag | grep backup
```

### 步骤2: 清理缓存和临时文件

```bash
# 清理Python缓存
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

# 清理测试覆盖报告
rm -rf htmlcov/
rm -rf .pytest_cache/

# 清理空目录
rmdir worktrees 2>/dev/null || true

echo "✓ 缓存清理完成"
```

**预期效果**: 释放约50-100MB空间

### 步骤3: 创建新目录结构

```bash
# 创建主目录
mkdir -p src
mkdir -p docs/{api,architecture,guides,archived}
mkdir -p data/{models,cache}
mkdir -p .archive/{old_code,old_docs}

echo "✓ 目录结构创建完成"
```

### 步骤4: 移动源代码到src/

```bash
# 核心模块
git mv adapters src/adapters 2>/dev/null || true
git mv core src/core 2>/dev/null || true
git mv data_access src/data_access 2>/dev/null || true
git mv data_sources src/data_sources 2>/dev/null || true
git mv db_manager src/db_manager 2>/dev/null || true
git mv monitoring src/monitoring 2>/dev/null || true
git mv ml_strategy src/ml_strategy 2>/dev/null || true
git mv reporting src/reporting 2>/dev/null || true
git mv visualization src/visualization 2>/dev/null || true
git mv utils src/utils 2>/dev/null || true
git mv interfaces src/interfaces 2>/dev/null || true

# GPU模块合并
mkdir -p src/gpu
git mv gpu_accelerated src/gpu/accelerated 2>/dev/null || true
git mv gpu_api_system src/gpu/api_system 2>/dev/null || true

echo "✓ 源代码移动完成"
```

### 步骤5: 整合文档

```bash
# 移动文档到docs/
find mystocks -name "*.md" -exec git mv {} docs/architecture/ \; 2>/dev/null || true
git mv temp_docs/* docs/archived/ 2>/dev/null || true
git mv reports/* docs/archived/ 2>/dev/null || true

# 清理空目录
rmdir mystocks temp_docs reports 2>/dev/null || true

echo "✓ 文档整合完成"
```

### 步骤6: 整理数据和模型

```bash
# 移动模型文件
git mv models/* data/models/ 2>/dev/null || true
rmdir models 2>/dev/null || true

echo "✓ 数据整理完成"
```

### 步骤7: 归档旧代码

```bash
# 移动archive
git mv archive/* .archive/old_code/ 2>/dev/null || true
rmdir archive 2>/dev/null || true

# 创建归档索引
cat > .archive/ARCHIVE_INDEX.md << 'EOF'
# 归档目录索引

创建时间: $(date)

## 目录说明
- `old_code/` - 归档的旧代码
- `old_docs/` - 归档的旧文档

## 注意
归档内容仅供参考，不应被引用。
如需恢复文件，请使用Git历史记录。
EOF

echo "✓ 归档完成"
```

### 步骤8: 更新import路径

```bash
# 使用自动工具更新
python3 update_imports.py

# 或手动查找需要更新的文件
find . -name "*.py" -type f ! -path "./temp/*" ! -path "./.git/*" \
  -exec grep -l "from core\|from adapters\|from data_access" {} \;
```

**重要**: 所有import语句需要更新，例如：
```python
# 旧的
from core import ConfigDrivenTableManager
from adapters.akshare_adapter import AkshareDataSource

# 新的
from src.core import ConfigDrivenTableManager
from src.adapters.akshare_adapter import AkshareDataSource
```

### 步骤9: 验证和测试

```bash
# 1. 检查Git状态
git status

# 2. 运行测试
pytest tests/ -v

# 3. 检查import错误
python -c "from src.core import ConfigDrivenTableManager"
python -c "from src.adapters.akshare_adapter import AkshareDataSource"

# 4. 启动Web应用测试
cd web && bash start_dev.sh
```

### 步骤10: 提交更改

```bash
# 查看更改
git status
git diff --stat

# 提交
git add -A
git commit -m "refactor: reorganize project directory structure

- Consolidate all source code to src/ directory
- Merge documentation to docs/ directory
- Archive old code to .archive/
- Clean up cache and temporary files
- Update import paths from old modules to src.*
"

echo "✓ 重组完成！"
```

---

## 🔍 验证清单

重组完成后，逐项检查：

- [ ] **Git历史保留**: `git log --follow src/core/data_manager.py`
- [ ] **所有测试通过**: `pytest tests/ -v`
- [ ] **导入路径正确**: 无 `ModuleNotFoundError`
- [ ] **Web应用正常**: 前后端都能启动
- [ ] **文档可访问**: `docs/` 目录结构清晰
- [ ] **.gitignore生效**: `git status` 不显示temp/、.claude/等
- [ ] **配置文件正常**: 应用能加载配置
- [ ] **日志正常写入**: `logs/` 目录有新日志

---

## 📊 重组前后对比

### 根目录文件夹数量
- **重组前**: 42个目录
- **重组后**: 约15个目录
- **减少**: 约65%

### 空间优化
- **清理缓存**: ~50-100MB
- **temp目录**: 保留但在.gitignore中
- **归档整理**: 旧代码移至隐藏目录

### 目录结构
```
Before:                    After:
├── adapters/              ├── src/
├── core/                  │   ├── adapters/
├── data_access/           │   ├── core/
├── data_sources/          │   ├── data_access/
├── db_manager/            │   ├── data_sources/
├── monitoring/            │   ├── db_manager/
├── ml_strategy/           │   ├── monitoring/
├── reporting/             │   ├── ml_strategy/
├── visualization/         │   ├── reporting/
├── utils/                 │   ├── visualization/
├── interfaces/            │   ├── utils/
├── gpu_accelerated/       │   ├── interfaces/
├── gpu_api_system/        │   └── gpu/
├── mystocks/              ├── docs/
├── temp_docs/             │   ├── api/
├── reports/               │   ├── architecture/
├── archive/               │   ├── guides/
├── models/                │   └── archived/
└── ...                    ├── data/
                           │   ├── models/
                           │   └── cache/
                           ├── .archive/
                           │   ├── old_code/
                           │   └── old_docs/
                           └── ...
```

---

## ⚠️ 常见问题

### Q1: 如果重组失败怎么办？

**回滚方法**:
```bash
# 方式1: 使用备份标签
git tag | grep backup
git reset --hard backup-YYYYMMDD-HHMMSS

# 方式2: 取消所有未提交的更改
git reset --hard HEAD
git clean -fd
```

### Q2: import路径更新遗漏了怎么办？

**检查方法**:
```bash
# 查找可能遗漏的import
grep -r "from core\|from adapters\|from data_access" \
  --include="*.py" \
  --exclude-dir={.git,temp,.archive} \
  .

# 手动修复或重新运行
python3 update_imports.py
```

### Q3: 测试失败怎么办？

**排查步骤**:
1. 检查import路径是否全部更新
2. 检查`__init__.py`文件是否存在
3. 检查PYTHONPATH环境变量
4. 逐个运行失败的测试查看详细错误

### Q4: Web应用启动失败？

**检查**:
1. Web目录没有被移动（应该保持原样）
2. 后端代码的import路径是否更新
3. 配置文件路径是否正确

---

## 🎯 完成后的下一步

1. **更新文档**: 修改README.md中的目录结构说明
2. **通知团队**: 如果是团队项目，通知其他开发者拉取最新代码
3. **CI/CD更新**: 如果有CI/CD配置，更新相关路径
4. **IDE配置**: 更新IDE的源代码根目录配置

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 `git status` 和 `git log` 了解当前状态
2. 查看 `git diff` 了解具体更改
3. 使用备份标签回滚到安全状态
4. 检查 PROJECT_REORGANIZATION_PLAN.md 获取详细信息

---

**生成工具**: Claude Code
**脚本位置**:
- 重组脚本: `reorganize_project.sh`
- Import更新: `update_imports.py`
- 详细方案: `PROJECT_REORGANIZATION_PLAN.md`
