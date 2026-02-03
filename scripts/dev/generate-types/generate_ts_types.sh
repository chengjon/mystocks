#!/bin/bash
# 从OpenAPI契约自动生成TypeScript类型定义
# 支持使用openapi-typescript或dtsgenerator

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
CONTRACTS_DIR="docs/api/contracts"
OUTPUT_DIR="web/frontend/src/types/api"
TOOL="${TOOL:-openapi-typescript}" # openapi-typescript | dtsgenerator

echo "🔧 TypeScript类型定义生成工具"
echo "使用工具: $TOOL"
echo ""

# 检查依赖
check_dependencies() {
    echo "🔍 检查依赖..."

    if [ "$TOOL" = "openapi-typescript" ]; then
        if ! command -v npx &> /dev/null; then
            echo -e "${RED}❌ npx未安装${NC}"
            echo "请安装Node.js和npm: https://nodejs.org/"
            exit 1
        fi
    elif [ "$TOOL" = "dtsgenerator" ]; then
        if ! command -v dtsgen &> /dev/null; then
            echo -e "${YELLOW}⚠️  dtsgenerator未安装，正在安装...${NC}"
            npm install -g dtsgenerator
        fi
    fi

    echo -e "${GREEN}✅ 依赖检查通过${NC}"
}

# 创建输出目录
create_output_dir() {
    echo "📁 创建输出目录: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
}

# 使用openapi-typescript生成类型
generate_with_openapi_typescript() {
    local contract_file=$1
    local output_file=$2

    echo "🔄 生成类型定义: $(basename $contract_file)"

    # 使用openapi-typescript-codegen
    npx openapi-typescript-codegen "$contract_file" -o "$output_file" || {
        echo -e "${RED}❌ 生成失败: $contract_file${NC}"
        return 1
    }

    echo -e "${GREEN}✅ 生成成功: $output_file${NC}"
}

# 使用dtsgenerator生成类型
generate_with_dtsgenerator() {
    local contract_file=$1
    local output_file=$2

    echo "🔄 生成类型定义: $(basename $contract_file)"

    dtsgen --input "$contract_file" --out "$output_file" || {
        echo -e "${RED}❌ 生成失败: $contract_file${NC}"
        return 1
    }

    echo -e "${GREEN}✅ 生成成功: $output_file${NC}"
}

# 主生成流程
main() {
    check_dependencies
    create_output_dir

    # 查找所有契约文件
    CONTRACT_FILES=$(find "$CONTRACTS_DIR" -type f \( -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) 2>/dev/null || true)

    if [ -z "$CONTRACT_FILES" ]; then
        echo -e "${YELLOW}⚠️  未找到契约文件${NC}"
        exit 0
    fi

    echo ""
    echo "📝 找到以下契约文件:"
    echo "$CONTRACT_FILES"
    echo ""

    # 生成类型定义
    for contract in $CONTRACT_FILES; do
        # 获取契约名称 (去掉扩展名)
        contract_name=$(basename "$contract" | sed 's/\.[^.]*$//')

        # 输出文件
        output_file="$OUTPUT_DIR/${contract_name}.ts"

        # 根据选择的工具生成
        if [ "$TOOL" = "openapi-typescript" ]; then
            generate_with_openapi_typescript "$contract" "$output_file"
        elif [ "$TOOL" = "dtsgenerator" ]; then
            generate_with_dtsgenerator "$contract" "$output_file"
        fi
    done

    # 生成索引文件
    echo ""
    echo "📝 生成索引文件..."
    generate_index_file

    echo ""
    echo -e "${GREEN}✅ TypeScript类型定义生成完成${NC}"
    echo "输出目录: $OUTPUT_DIR"
}

# 生成索引文件
generate_index_file() {
    cat > "$OUTPUT_DIR/index.ts" <<'EOF'
/**
 * API类型定义
 * 从OpenAPI契约自动生成
 *
 * 生成时间: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
 * 生成工具: ${TOOL}
 *
 * 警告: 此文件由脚本自动生成，请勿手动编辑
 */

EOF

    # 导出所有类型文件
    for contract in $CONTRACT_FILES; do
        contract_name=$(basename "$contract" | sed 's/\.[^.]*$//')
        echo "export * from './${contract_name}';" >> "$OUTPUT_DIR/index.ts"
    done

    echo -e "${GREEN}✅ 索引文件生成完成${NC}"
}

# 运行主函数
main "$@"
