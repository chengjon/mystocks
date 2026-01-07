#!/bin/bash
# 批量迁移所有组件到Element Plus
# 目标: 全面去除ArtDeco，使用Element Plus标准组件

set -e

VIEWS_DIR="/opt/claude/mystocks_spec/web/frontend/src/views"

echo "🚀 开始迁移到Element Plus..."

# 1. DataTable → el-table (保留table结构，仅替换导入和组件名)
echo "📊 迁移 DataTable → el-table..."
find "$VIEWS_DIR" -name "*.vue" -type f -exec sed -i '
s/import DataTable from.*$/import { ElTable, ElTableColumn } from '\''element-plus'\''/g
s/<DataTable/<el-table/g
s/<\/DataTable>/<\/el-table>/g
' {} \;

# 2. DataCard → el-card
echo "📦 迁移 DataCard → el-card..."
find "$VIEWS_DIR" -name "*.vue" -type f -exec sed -i '
s/import DataCard from.*$/import { ElCard } from '\''element-plus'\''/g
s/<DataCard/<el-card/g
s/<\/DataCard>/<\/el-card>/g
' {} \;

# 3. ActionButton → el-button
echo "🔘 迁移 ActionButton → el-button..."
find "$VIEWS_DIR" -name "*.vue" -type f -exec sed -i '
s/import ActionButton from.*$/import { ElButton } from '\''element-plus'\''/g
s/<ActionButton/<el-button/g
s/<\/ActionButton>/<\/el-button>/g
' {} \;

# 4. StatusBadge → el-tag
echo "🏷️ 迁移 StatusBadge → el-tag..."
find "$VIEWS_DIR" -name "*.vue" -type f -exec sed -i '
s/import StatusBadge from.*$/import { ElTag } from '\''element-plus'\''/g
s/<StatusBadge/<el-tag/g
s/<\/StatusBadge>/<\/el-tag>/g
s/:variant="success"/type="success"/g
s/:variant="warning"/type="warning"/g
s/:variant="danger"/type="danger"/g
s/:variant="info"/type="info"/g
s/:variant="primary"/type="primary"/g
s/variant="success"/type="success"/g
s/variant="warning"/type="warning"/g
s/variant="danger"/type="danger"/g
s/variant="info"/type="info"/g
s/variant="primary"/type="primary"/g
' {} \;

# 5. FormField → el-input
echo "✏️ 迁移 FormField → el-input..."
find "$VIEWS_DIR" -name "*.vue" -type f -exec sed -i '
s/import FormField from.*$/import { ElInput } from '\''element-plus'\''/g
s/<FormField/<el-input/g
s/<\/FormField>/<\/el-input>/g
s/v-model\.text/v-model/g
' {} \;

# 6. LoadingSpinner → el-loading (全局指令)
echo "⏳ 迁移 LoadingSpinner → el-loading..."
find "$VIEWS_DIR" -name "*.vue" -type f -exec sed -i '
s/import LoadingSpinner from.*$/import { ElLoading } from '\''element-plus'\''/g
s/<LoadingSpinner/<div v-loading/g
s/<\/LoadingSpinner>/<\/div>/g
' {} \;

# 7. 移除ArtDeco组件导入（如果存在）
echo "🗑️ 清理ArtDeco导入..."
find "$VIEWS_DIR" -name "*.vue" -type f -exec sed -i '
/import.*ArtDecoCard.*from.*$/d
/import.*ArtDecoButton.*from.*$/d
/import.*ArtDecoTable.*from.*$/d
/import.*ArtDecoBadge.*from.*$/d
/import.*ArtDecoInput.*from.*$/d
/import.*ArtDecoLoader.*from.*$/d
/import.*DataCard.*from.*artdeco.*$/d
/import.*ActionButton.*from.*artdeco.*$/d
/import.*DataTable.*from.*artdeco.*$/d
/import.*StatusBadge.*from.*artdeco.*$/d
/import.*FormField.*from.*artdeco.*$/d
/import.*LoadingSpinner.*from.*artdeco.*$/d
' {} \;

echo "✅ 迁移完成！"
echo ""
echo "⚠️ 注意事项："
echo "1. 需要手动调整DataTable的结构（el-table使用el-table-column）"
echo "2. variant属性已改为type（ElTag）"
echo "3. v-model.text改为v-model（ElInput）"
echo "4. 建议运行TypeScript检查验证"
