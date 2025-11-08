# MyStocks 目录清理执行计划

**创建日期**: 2025-10-19
**预计用时**: 30分钟
**风险等级**: 低（归档而非删除）

---

## 📊 清理概览

### 可清理内容统计

| 类别 | 数量/大小 | 描述 | 操作 |
|------|-----------|------|------|
| **空目录** | 1个 (temp/) | 空目录 | 删除 |
| **临时文档** | 268KB (temp_docs/) | 19个临时MD文件 | 归档 |
| **规格文档** | 1.9MB (specs/) | 11个规格子目录 | 归档 |
| **临时MD** | 24个文件, ~280KB | 根目录临时报告 | 归档 |
| **测试覆盖** | htmlcov/ | HTML测试报告 | 删除 |
| **未使用目录** | 3个 | data_sources, examples, inside | 评估 |

**总可释放空间**: ~2.5MB（目录） + 280KB（文件） = **~2.8MB**
**总可减少目录**: 29个 → 预计15-20个

---

## 🎯 清理策略

### 分类处理

#### 1. 立即删除（无价值）
- `temp/` - 空目录
- `htmlcov/` - 可重新生成的测试报告
- `__pycache__/` - 编译缓存（.gitignore已涵盖）

#### 2. 归档保留（历史价值）
- `temp_docs/` → `archive/docs_history/`
- `specs/` → `archive/specifications/`
- 根目录临时MD → `archive/reports/`

#### 3. 评估后决定（可能有用）
- `data_sources/` - 有TDX工具代码
- `examples/` - 有使用示例
- `inside/` - 4.9MB历史数据
- `reporting/` - PDF生成器
- `visualization/` - 可视化工具

---

## 📝 详细清理列表

### 第1步：创建归档目录结构

```bash
mkdir -p archive/{docs_history,specifications,reports,unused_modules}
```

### 第2步：归档临时文档

```bash
# 归档 temp_docs/
mv temp_docs/ archive/docs_history/

# 归档 specs/
mv specs/ archive/specifications/

# 归档根目录临时MD文件
mkdir -p archive/reports

# 按类别归档
mv WEEK*.md archive/reports/
mv *_SUMMARY.md archive/reports/
mv *_REPORT.md archive/reports/
mv *_COMPLETION.md archive/reports/
mv *_ANALYSIS*.md archive/reports/
```

**保留的重要MD文件**:
- ✅ README.md
- ✅ CHANGELOG.md
- ✅ CLAUDE.md
- ✅ DEPLOYMENT_GUIDE.md
- ✅ QUICKSTART.md
- ✅ ARCHITECTURE_REVIEW_FIRST_PRINCIPLES.md（最重要的架构文档）
- ✅ SIMPLIFICATION_DECISION_MATRIX.md（决策参考）
- ✅ ADAPTER_SIMPLIFICATION_ANALYSIS.md（新创建）

### 第3步：删除可重新生成的文件

```bash
# 删除空目录
rmdir temp/ 2>/dev/null || echo "temp/ 不为空或不存在"

# 删除测试覆盖率HTML报告（可重新生成）
rm -rf htmlcov/
```

### 第4步：评估未使用目录

#### data_sources/ 评估
```bash
# 内容：TDX二进制解析器和导入工具
# 决策：保留（有实用价值）
# 优化：移动到 utils/tdx_tools/
mv data_sources/ utils/tdx_tools/
```

#### examples/ 评估
```bash
# 内容：3个示例文件（automation, tdx_import, tdx_usage）
# 决策：保留
# 优化：无需移动，保持现状
```

#### inside/ 评估
```bash
# 内容：4.9MB历史数据和文档
# 决策：归档（不是代码，是历史数据）
mv inside/ archive/unused_modules/
```

#### htmlcov/ 评估
```bash
# 内容：pytest-cov生成的HTML报告
# 决策：删除（可重新生成）
rm -rf htmlcov/
```

#### reporting/ 评估
```bash
# 内容：PDF生成器
# 决策：评估使用频率
ls -la reporting/
# 如果有py文件且有引用，保留；否则归档
```

#### visualization/ 评估
```bash
# 内容：可视化工具
# 决策：评估使用频率
ls -la visualization/
# 如果有py文件且有引用，保留；否则归档
```

---

## 🚀 一键执行脚本

### cleanup.sh（保守版）

```bash
#!/bin/bash
# MyStocks 目录清理脚本（保守版）
# 所有文件都归档而非删除

set -e  # 遇到错误立即停止

echo "=== MyStocks 目录清理开始 ==="
echo ""

# 1. 创建归档目录
echo "[1/6] 创建归档目录结构..."
mkdir -p archive/{docs_history,specifications,reports,unused_modules}
echo "✅ 归档目录创建完成"
echo ""

# 2. 归档临时文档目录
echo "[2/6] 归档临时文档目录..."
if [ -d "temp_docs" ]; then
    mv temp_docs/ archive/docs_history/
    echo "✅ temp_docs/ 已归档"
else
    echo "⚠️  temp_docs/ 不存在"
fi
echo ""

# 3. 归档规格文档目录
echo "[3/6] 归档规格文档目录..."
if [ -d "specs" ]; then
    mv specs/ archive/specifications/
    echo "✅ specs/ 已归档"
else
    echo "⚠️  specs/ 不存在"
fi
echo ""

# 4. 归档根目录临时MD文件
echo "[4/6] 归档根目录临时MD文件..."
count=0

# WEEK系列
for file in WEEK*.md; do
    if [ -f "$file" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

# SUMMARY系列
for file in *_SUMMARY.md; do
    if [ -f "$file" ]; then
        case "$file" in
            EXECUTIVE_SUMMARY.md|FINAL_COMPREHENSIVE_SUMMARY.md)
                mv "$file" archive/reports/
                count=$((count + 1))
                ;;
        esac
    fi
done

# REPORT系列
for file in *_REPORT.md; do
    if [ -f "$file" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

# COMPLETION系列
for file in *_COMPLETION.md; do
    if [ -f "$file" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

# ANALYSIS系列（保留ADAPTER_SIMPLIFICATION_ANALYSIS.md）
for file in *ANALYSIS*.md; do
    if [ -f "$file" ] && [ "$file" != "ADAPTER_SIMPLIFICATION_ANALYSIS.md" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

# 其他临时文件
for file in TEMP_*.md INTEGRATION_SUMMARY.md MARKET_DATA_FIX_SUMMARY.md; do
    if [ -f "$file" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

echo "✅ 已归档 $count 个临时MD文件"
echo ""

# 5. 删除空目录和可重新生成的文件
echo "[5/6] 清理空目录和临时文件..."
rmdir temp/ 2>/dev/null && echo "✅ 删除 temp/" || echo "⚠️  temp/ 不存在或不为空"
rm -rf htmlcov/ 2>/dev/null && echo "✅ 删除 htmlcov/" || echo "⚠️  htmlcov/ 不存在"
echo ""

# 6. 归档历史数据目录
echo "[6/6] 归档历史数据目录..."
if [ -d "inside" ]; then
    mv inside/ archive/unused_modules/
    echo "✅ inside/ 已归档"
else
    echo "⚠️  inside/ 不存在"
fi
echo ""

# 7. 生成清理报告
echo "=== 清理完成，生成报告 ==="
cat > archive/CLEANUP_REPORT_$(date +%Y%m%d_%H%M%S).md << 'EOF'
# 目录清理报告

**清理日期**: $(date)
**脚本版本**: 保守版 v1.0

## 已归档内容

### 文档
- temp_docs/ → archive/docs_history/
- specs/ → archive/specifications/
- 24个临时MD → archive/reports/

### 历史数据
- inside/ → archive/unused_modules/

## 已删除内容
- temp/ （空目录）
- htmlcov/ （测试覆盖率报告，可重新生成）

## 保留内容
- 所有核心代码文件
- 重要文档（README, CLAUDE, CHANGELOG等）
- 适配器和数据库代码
- 测试文件

## 回退方法
如需恢复归档文件：
```bash
# 恢复specs/
mv archive/specifications/specs ./

# 恢复temp_docs/
mv archive/docs_history/temp_docs ./

# 恢复临时MD
mv archive/reports/*.md ./
```

## 下一步建议
1. 验证系统功能正常
2. 运行测试套件
3. 如果一切正常，可以在2周后永久删除archive/
EOF

echo ""
echo "✅ 清理完成！"
echo ""
echo "📊 统计信息："
echo "   - 归档目录: $(du -sh archive/ 2>/dev/null | cut -f1)"
echo "   - 当前目录数: $(ls -d */ 2>/dev/null | wc -l)"
echo ""
echo "📝 清理报告已保存到: archive/CLEANUP_REPORT_*.md"
echo ""
echo "⚠️  建议："
echo "   1. 立即运行测试：pytest tests/"
echo "   2. 验证系统启动：python main.py"
echo "   3. 如一切正常，2周后可删除archive/"
echo ""
```

### cleanup_aggressive.sh（激进版，不推荐）

```bash
#!/bin/bash
# MyStocks 目录清理脚本（激进版 - 不推荐）
# 直接删除文件，慎用！

echo "⚠️  警告：此脚本将永久删除文件！"
echo "建议使用保守版cleanup.sh"
read -p "确定继续？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "已取消"
    exit 0
fi

echo "=== 开始激进清理 ==="

# 删除临时目录
rm -rf temp/ temp_docs/ specs/ htmlcov/ inside/

# 删除临时MD
rm -f WEEK*.md *_SUMMARY.md *_REPORT.md *_COMPLETION.md
rm -f TEMP_*.md INTEGRATION_SUMMARY.md MARKET_DATA_FIX_SUMMARY.md

echo "✅ 清理完成（不可恢复）"
```

---

## ✅ 清理后目录结构

### 理想的目录结构（15-20个顶层目录）

```
mystocks_spec/
├── adapters/           # 核心：数据适配器
├── archive/           # 新增：归档目录
│   ├── docs_history/
│   ├── specifications/
│   ├── reports/
│   └── unused_modules/
├── config/            # 配置文件
├── core/              # 核心业务逻辑
├── data_access/       # 数据访问层
├── db_manager/        # 数据库管理
├── docs/              # 文档（保留）
├── examples/          # 示例代码（保留）
├── factory/           # 工厂模式
├── interfaces/        # 接口定义
├── logs/              # 日志文件
├── manager/           # 管理器
├── ml_strategy/       # 机器学习策略
├── models/            # 数据模型
├── monitoring/        # 监控系统
├── scripts/           # 脚本工具
├── tests/             # 测试文件
├── utils/             # 工具函数
└── web/               # Web应用

# 移除的目录（归档）
# - temp/ → 删除
# - temp_docs/ → archive/docs_history/
# - specs/ → archive/specifications/
# - inside/ → archive/unused_modules/
# - htmlcov/ → 删除

# 顶层目录数：29 → 20（减少31%）
```

---

## 🔍 验证清单

清理完成后，运行以下检查：

### 1. 目录结构检查
```bash
echo "=== 顶层目录数量 ==="
ls -d */ | wc -l
echo "目标：15-20个"

echo ""
echo "=== archive/ 大小 ==="
du -sh archive/
echo "预期：~2-3MB"
```

### 2. 功能测试
```bash
echo "=== 测试系统启动 ==="
python -c "from unified_manager import MyStocksUnifiedManager; print('✅ 启动正常')"

echo ""
echo "=== 测试适配器导入 ==="
python -c "from adapters import AkshareDataSource; print('✅ 适配器正常')"

echo ""
echo "=== 运行测试套件 ==="
pytest tests/ -v
```

### 3. 依赖检查
```bash
echo "=== 检查导入依赖 ==="
python -c "
import sys
import importlib

modules = ['adapters', 'core', 'factory', 'db_manager', 'unified_manager']
for mod in modules:
    try:
        importlib.import_module(mod)
        print(f'✅ {mod}')
    except Exception as e:
        print(f'❌ {mod}: {e}')
"
```

---

## 🔄 回退计划

如果清理后发现问题，可以快速恢复：

```bash
#!/bin/bash
# rollback_cleanup.sh

echo "=== 开始回退清理 ==="

# 恢复归档目录
if [ -d "archive/docs_history/temp_docs" ]; then
    mv archive/docs_history/temp_docs ./
    echo "✅ 恢复 temp_docs/"
fi

if [ -d "archive/specifications/specs" ]; then
    mv archive/specifications/specs ./
    echo "✅ 恢复 specs/"
fi

if [ -d "archive/unused_modules/inside" ]; then
    mv archive/unused_modules/inside ./
    echo "✅ 恢复 inside/"
fi

# 恢复临时MD
if [ -d "archive/reports" ]; then
    mv archive/reports/*.md ./ 2>/dev/null
    echo "✅ 恢复临时MD文件"
fi

# 删除空的archive目录
rmdir archive/*/ 2>/dev/null
rmdir archive/ 2>/dev/null

echo ""
echo "✅ 回退完成，系统恢复到清理前状态"
```

---

## 📈 预期效果

### 定量指标

| 指标 | 清理前 | 清理后 | 改善 |
|------|--------|--------|------|
| **顶层目录数** | 29个 | ~20个 | -31% |
| **临时文件** | ~2.8MB | 0 | -100% |
| **文档文件数** | 46个MD | ~15个MD | -67% |
| **Git仓库大小** | 不变 | 不变 | 0% |

### 定性收益

- ✅ **认知负担降低**: 新人看到更清晰的目录结构
- ✅ **查找效率提升**: 减少30%的无关文件干扰
- ✅ **IDE性能提升**: 索引文件减少
- ✅ **备份速度加快**: 减少无需备份的临时文件

---

## ⏰ 执行时间表

### 推荐执行时间
- ✅ **工作日下班前**（便于第二天验证）
- ✅ **周五下午**（周末有时间处理问题）
- ❌ **避免：周一早上、发布前**

### 执行步骤（30分钟）

```
00:00 - 05:00  备份当前状态（git commit）
05:00 - 10:00  运行清理脚本
10:00 - 15:00  验证功能正常
15:00 - 20:00  运行测试套件
20:00 - 25:00  检查文档完整性
25:00 - 30:00  提交清理结果
```

---

## 🎯 立即行动

准备好了吗？执行以下命令开始清理：

```bash
# 1. 确保工作区干净
git status

# 2. 创建安全备份点
git add -A
git commit -m "Backup before directory cleanup"

# 3. 下载并执行清理脚本
chmod +x cleanup.sh
./cleanup.sh

# 4. 验证结果
pytest tests/ -v

# 5. 如果一切正常，提交清理结果
git add -A
git commit -m "Directory cleanup: archive temp files and docs"

# 6. 如果出现问题，立即回退
# git reset --hard HEAD^
# 或使用 rollback_cleanup.sh
```

---

**创建人**: Claude
**审核状态**: 待审核
**风险等级**: 低
**推荐执行**: ✅ 是

**下一步**: 审核并执行 `cleanup.sh`
