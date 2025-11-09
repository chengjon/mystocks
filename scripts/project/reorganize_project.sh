#!/bin/bash

# 项目目录重组执行脚本
# 生成时间: 2025-11-08 23:15
# 注意：执行前请先备份！

set -e  # 遇到错误立即退出

echo "========================================="
echo " MyStocks 项目目录重组脚本"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_step() {
    echo -e "${GREEN}[步骤]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 检查当前目录
if [ ! -f "CLAUDE.md" ]; then
    print_error "请在项目根目录 (/opt/claude/mystocks_spec) 执行此脚本"
    exit 1
fi

# 询问是否创建备份
echo "是否创建Git备份标签? (推荐) [y/N]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    print_step "创建备份标签..."
    git add -A
    git commit -m "backup: before directory reorganization" || true
    git tag "backup-$(date +%Y%m%d-%H%M%S)"
    print_step "备份已创建"
fi

echo ""
echo "========================================="
echo " 开始重组"
echo "========================================="
echo ""

# ===== 阶段1: 清理缓存和临时文件 =====
print_step "阶段1: 清理缓存和临时文件"

# 清理Python缓存
print_step "清理 Python 缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# 清理pytest缓存
print_step "清理 pytest 缓存..."
rm -rf .pytest_cache/

# 清理测试覆盖报告
print_step "清理测试覆盖报告..."
rm -rf htmlcov/

# 清理空目录
print_step "清理空目录..."
rmdir worktrees 2>/dev/null || true

print_step "阶段1完成 ✓"
echo ""

# ===== 阶段2: 创建新的目录结构 =====
print_step "阶段2: 创建新的目录结构"

# 创建src主目录（如果不存在）
mkdir -p src

# 创建docs子目录
mkdir -p docs/{api,architecture,guides,archived}

# 创建data子目录
mkdir -p data/{models,cache}

# 创建.archive目录
mkdir -p .archive/{old_code,old_docs}

print_step "阶段2完成 ✓"
echo ""

# ===== 阶段3: 移动源代码到src目录 =====
print_step "阶段3: 整合源代码目录"

# 移动adapters（如果src/adapters不存在）
if [ -d "adapters" ] && [ ! -d "src/adapters" ]; then
    print_step "移动 adapters/ -> src/adapters/"
    git mv adapters src/adapters
fi

# 移动core
if [ -d "core" ] && [ ! -d "src/core" ]; then
    print_step "移动 core/ -> src/core/"
    git mv core src/core
fi

# 移动data_access
if [ -d "data_access" ] && [ ! -d "src/data_access" ]; then
    print_step "移动 data_access/ -> src/data_access/"
    git mv data_access src/data_access
fi

# 移动data_sources
if [ -d "data_sources" ] && [ ! -d "src/data_sources" ]; then
    print_step "移动 data_sources/ -> src/data_sources/"
    git mv data_sources src/data_sources
fi

# 移动db_manager
if [ -d "db_manager" ] && [ ! -d "src/db_manager" ]; then
    print_step "移动 db_manager/ -> src/db_manager/"
    git mv db_manager src/db_manager
fi

# 移动monitoring
if [ -d "monitoring" ] && [ ! -d "src/monitoring" ]; then
    print_step "移动 monitoring/ -> src/monitoring/"
    git mv monitoring src/monitoring
fi

# 移动ml_strategy
if [ -d "ml_strategy" ] && [ ! -d "src/ml_strategy" ]; then
    print_step "移动 ml_strategy/ -> src/ml_strategy/"
    git mv ml_strategy src/ml_strategy
fi

# 移动reporting
if [ -d "reporting" ] && [ ! -d "src/reporting" ]; then
    print_step "移动 reporting/ -> src/reporting/"
    git mv reporting src/reporting
fi

# 移动visualization
if [ -d "visualization" ] && [ ! -d "src/visualization" ]; then
    print_step "移动 visualization/ -> src/visualization/"
    git mv visualization src/visualization
fi

# 移动utils
if [ -d "utils" ] && [ ! -d "src/utils" ]; then
    print_step "移动 utils/ -> src/utils/"
    git mv utils src/utils
fi

# 移动interfaces
if [ -d "interfaces" ] && [ ! -d "src/interfaces" ]; then
    print_step "移动 interfaces/ -> src/interfaces/"
    git mv interfaces src/interfaces
fi

# 合并GPU相关代码
if [ ! -d "src/gpu" ]; then
    mkdir -p src/gpu
fi

if [ -d "gpu_accelerated" ]; then
    print_step "移动 gpu_accelerated/ -> src/gpu/accelerated/"
    git mv gpu_accelerated src/gpu/accelerated
fi

if [ -d "gpu_api_system" ]; then
    print_step "移动 gpu_api_system/ -> src/gpu/api_system/"
    git mv gpu_api_system src/gpu/api_system
fi

print_step "阶段3完成 ✓"
echo ""

# ===== 阶段4: 整合文档 =====
print_step "阶段4: 整合文档目录"

# 移动mystocks文档
if [ -d "mystocks" ]; then
    print_step "移动 mystocks/ 下的文档到 docs/architecture/"
    find mystocks -name "*.md" -exec git mv {} docs/architecture/ \; 2>/dev/null || true
    # 移动剩余文件到归档
    if [ "$(ls -A mystocks 2>/dev/null)" ]; then
        git mv mystocks/* .archive/old_docs/ 2>/dev/null || true
    fi
    rmdir mystocks 2>/dev/null || true
fi

# 移动temp_docs
if [ -d "temp_docs" ]; then
    print_step "移动 temp_docs/ -> docs/archived/"
    git mv temp_docs/* docs/archived/ 2>/dev/null || true
    rmdir temp_docs 2>/dev/null || true
fi

# 移动reports
if [ -d "reports" ]; then
    print_step "移动 reports/ -> docs/archived/"
    git mv reports/* docs/archived/ 2>/dev/null || true
    rmdir reports 2>/dev/null || true
fi

print_step "阶段4完成 ✓"
echo ""

# ===== 阶段5: 移动数据和模型 =====
print_step "阶段5: 整理数据和模型"

# 移动models
if [ -d "models" ]; then
    print_step "移动 models/ -> data/models/"
    git mv models/* data/models/ 2>/dev/null || true
    rmdir models 2>/dev/null || true
fi

print_step "阶段5完成 ✓"
echo ""

# ===== 阶段6: 归档旧代码 =====
print_step "阶段6: 归档旧代码和文档"

# 移动archive
if [ -d "archive" ]; then
    print_step "移动 archive/ -> .archive/old_code/"
    git mv archive/* .archive/old_code/ 2>/dev/null || true
    rmdir archive 2>/dev/null || true
fi

# 创建归档索引
print_step "创建归档索引..."
cat > .archive/ARCHIVE_INDEX.md << 'EOF'
# 归档目录索引

**创建时间**: $(date)
**说明**: 本目录包含项目重组前的旧代码和文档

## 目录结构

- `old_code/` - 归档的旧代码
- `old_docs/` - 归档的旧文档

## 注意事项

- 归档内容仅供参考，不应被引用
- 如需恢复某些文件，请使用 Git 历史记录
- 定期清理归档内容，避免占用过多空间

EOF

print_step "阶段6完成 ✓"
echo ""

# ===== 完成 =====
echo "========================================="
echo " 重组完成！"
echo "========================================="
echo ""

print_step "接下来的步骤："
echo "  1. 检查 git status 确认更改"
echo "  2. 更新代码中的import路径（从旧路径改为src.xxx）"
echo "  3. 运行测试: pytest tests/"
echo "  4. 提交更改: git commit -m 'refactor: reorganize project directory structure'"
echo ""

print_warning "重要提醒:"
echo "  - 所有import路径需要更新（例如: from core import X -> from src.core import X）"
echo "  - 运行 find . -name '*.py' | xargs grep 'from core\\|from adapters\\|from data_access' 检查需要更新的文件"
echo "  - 如果遇到问题，使用 git reset --hard backup-XXXXXX 回退"
echo ""

print_step "查看重组后的目录结构:"
tree -L 2 -d -I 'web|node_modules|__pycache__|.git|temp' || ls -la
