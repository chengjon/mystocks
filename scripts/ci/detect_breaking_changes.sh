#!/bin/bash
# API破坏性变更检测脚本
# 用于pre-commit hooks和CI流水线

set -e

echo "🔍 检测API破坏性变更..."

# 获取基准分支 (通常是main或develop)
BASE_BRANCH="${BASE_BRANCH:-main}"

# 临时存储目录
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# 检测修改的契约文件
CHANGED_FILES=$(git diff --name-only $BASE_BRANCH | grep -E '^docs/api/contracts/.*\.(yaml|yml|json)$' || true)

if [ -z "$CHANGED_FILES" ]; then
    echo "ℹ️  未检测到契约文件变更"
    exit 0
fi

echo "📝 修改的契约文件:"
echo "$CHANGED_FILES"
echo ""

# 对比每个修改的文件
for file in $CHANGED_FILES; do
    echo "🔍 检测文件: $file"

    # 从基准分支提取旧版本
    git show $BASE_BRANCH:$file > "$TEMP_DIR/base.yaml" 2>/dev/null || {
        echo "⚠️  文件在基准分支中不存在 (新增文件)"
        continue
    }

    # 当前版本
    cp "$file" "$TEMP_DIR/head.yaml"

    # 使用Python对比脚本
    if [ -f "scripts/ci/compare_contracts.py" ]; then
        python3 scripts/ci/compare_contracts.py \
            "$TEMP_DIR/base.yaml" \
            "$TEMP_DIR/head.yaml" \
            --output "$TEMP_DIR/diff.json" || true

        # 检查破坏性变更
        if [ -f "$TEMP_DIR/diff.json" ]; then
            BREAKING_COUNT=$(python3 -c "
import json
with open('$TEMP_DIR/diff.json') as f:
    data = json.load(f)
print(data.get('breaking_changes_count', 0))
")

            if [ "$BREAKING_COUNT" -gt "0" ]; then
                echo ""
                echo "⚠️  检测到 $BREAKING_COUNT 个破坏性变更:"
                python3 -c "
import json
with open('$TEMP_DIR/diff.json') as f:
    data = json.load(f)
for change in data.get('breaking_changes', []):
    print(f\"  • [{change['severity']}] {change['message']}\")
"
                echo ""
                echo "❌ 请确认这些变更是预期的，并获得技术负责人批准"
                # 注意: 不阻断提交，但会显示警告
            else
                echo "✅ 未检测到破坏性变更"
            fi
        fi
    else
        echo "⚠️  对比脚本不存在，跳过深度检测"
    fi

    echo ""
done

echo "✅ 破坏性变更检测完成"
