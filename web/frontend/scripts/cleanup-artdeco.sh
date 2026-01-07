#!/bin/bash

# ArtDeco完全清理脚本
# 移除所有ArtDeco相关的类名、样式导入和组件引用

set -e

FRONTEND_DIR="/opt/claude/mystocks_spec/web/frontend"
VIEWS_DIR="$FRONTEND_DIR/src/views"
COMPONENTS_DIR="$FRONTEND_DIR/src/components"

echo "=== ArtDeco完全清理开始 ==="
echo ""

# Step 1: 删除ArtDeco样式导入
echo "Step 1: 删除ArtDeco样式导入..."
find "$VIEWS_DIR" -name "*.vue" -exec sed -i '
/@import.*artdeco.*\.css/d
/@import.*artdeco.*\.scss/d
/@import.*artdeco.*\.less/d
' {} \;

# 也处理components目录
find "$COMPONENTS_DIR" -name "*.vue" -exec sed -i '
/@import.*artdeco.*\.css/d
/@import.*artdeco.*\.scss/d
/@import.*artdeco.*\.less/d
' {} \;

echo "✓ ArtDeco样式导入已删除"

# Step 2: 移除ArtDeco CSS类名前缀
echo ""
echo "Step 2: 移除ArtDeco CSS类名前缀..."
find "$VIEWS_DIR" -name "*.vue" -exec sed -i '
s/class="artdeco-/class="/g
s/class='"'"'artdeco-/class='"'"'/g
s/:class="["'"'"'\[]*artdeco-/:class="/g
s/artdeco-dashboard/dashboard/g
s/artdeco-stats-grid/stats-grid/g
s/artdeco-stat-card/stat-card/g
s/artdeco-main-grid/main-grid/g
s/artdeco-tabs/tabs/g
s/artdeco-tab/tab/g
s/artdeco-chart/chart/g
s/artdeco-select/select/g
s/artdeco-card/card/g
s/artdeco-header/header/g
s/artdeco-section/section/g
s/artdeco-container/container/g
s/artdeco-panel/panel/g
s/artdeco-table/table/g
s/artdeco-button/button/g
s/artdeco-input/input/g
s/artdeco-badge/badge/g
s/artdeco-tag/tag/g
s/artdeco-loader/loader/g
s/artdeco-modal/modal/g
s/artdeco-dialog/dialog/g
s/artdeco-overlay/overlay/g
s/artdeco-background/background/g
s/artdeco-content/content/g
' {} \;

echo "✓ ArtDeco CSS类名已清理"

# Step 3: 删除ArtDeco组件引用
echo ""
echo "Step 3: 删除ArtDeco组件引用..."
find "$VIEWS_DIR" -name "*.vue" -exec sed -i '
/import.*ArtDeco.*from.*artdeco/d
s/<ArtDecoButton/<el-button/g
s/<\/ArtDecoButton>/<\/el-button>/g
s/<ArtDecoCard/<el-card/g
s/<\/ArtDecoCard>/<\/el-card>/g
s/<ArtDecoBadge/<el-tag/g
s/<\/ArtDecoBadge>/<\/el-tag>/g
s/<ArtDecoInput/<el-input/g
s/<\/ArtDecoInput>/<\/el-input>/g
s/<ArtDecoTable/<el-table/g
s/<\/ArtDecoTable>/<\/el-table>/g
s/<ArtDecoLoader/<div v-loading/g
s/<\/ArtDecoLoader>/<\/div>/g
s/<ArtDecoSelect/<el-select/g
s/<\/ArtDecoSelect>/<\/el-select>/g
s/<ArtDecoSwitch/<el-switch/g
s/<\/ArtDecoSwitch>/<\/el-switch>/g
s/<ArtDecoSlider/<el-slider/g
s/<\/ArtDecoSlider>/<\/el-slider>/g
' {} \;

echo "✓ ArtDeco组件引用已删除"

# Step 4: 删除ArtDeco CSS变量引用
echo ""
echo "Step 4: 删除ArtDeco CSS变量引用..."
find "$VIEWS_DIR" -name "*.vue" -exec sed -i '
s/var(--artdeco-/var(--/g
s/var(--artdeco_/var(--/g
' {} \;

echo "✓ ArtDeco CSS变量已清理"

# Step 5: 删除ArtDeco特定注释
echo ""
echo "Step 5: 删除ArtDeco特定注释..."
find "$VIEWS_DIR" -name "*.vue" -exec sed -i '
/.*ArtDeco.*/d
/.*artdeco.*/d
/.*装饰艺术.*/d
' {} \;

echo "✓ ArtDeco相关注释已删除"

# Step 6: 删除空的ArtDeco背景div
echo ""
echo "Step 6: 删除空的ArtDeco背景元素..."
find "$VIEWS_DIR" -name "*.vue" -exec sed -i '
/<div class="bg-pattern"><\/div>/d
/<div class="artdeco-bg-pattern"><\/div>/d
' {} \;

echo "✓ ArtDeco背景元素已删除"

echo ""
echo "=== ArtDeco清理完成 ==="
echo ""
echo "统计信息："
echo "  - 剩余ArtDeco类名: $(grep -rh 'class="artdeco' "$VIEWS_DIR" --include="*.vue" 2>/dev/null | wc -l)"
echo "  - 剩余ArtDeco导入: $(grep -rh 'artdeco.*\.css\|artdeco.*\.scss' "$VIEWS_DIR" --include="*.vue" 2>/dev/null | wc -l)"
echo "  - 剩余ArtDeco组件: $(grep -rh '<ArtDeco' "$VIEWS_DIR" --include="*.vue" 2>/dev/null | wc -l)"
echo ""
echo "下一步："
echo "  1. 运行TypeScript编译检查"
echo "  2. 启动开发服务器验证功能"
echo "  3. 测试klinechart K线图功能"
