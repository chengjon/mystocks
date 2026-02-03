#!/bin/bash
# OpenAPI契约验证脚本
# 用于pre-commit hooks和CI流水线

set -e

echo "🔍 验证OpenAPI契约..."

# 检查依赖
if ! command -v yamllint &> /dev/null; then
    echo "❌ yamllint未安装，跳过YAML语法检查"
fi

# 遍历所有修改的契约文件
for file in "$@"; do
    echo ""
    echo "📄 验证文件: $file"

    # 1. 检查文件存在
    if [ ! -f "$file" ]; then
        echo "❌ 文件不存在: $file"
        exit 1
    fi

    # 2. Yamllint语法检查 (如果可用)
    if command -v yamllint &> /dev/null && [[ "$file" =~ \.(yaml|yml)$ ]]; then
        if ! yamllint -c .yamllint "$file"; then
            echo "❌ YAML语法错误: $file"
            exit 1
        fi
    fi

    # 3. Python验证 (如果可用)
    if command -v python3 &> /dev/null; then
        python3 -c "
import sys
import yaml
import json

try:
    with open('$file', 'r') as f:
        if '$file'.endswith('.json'):
            data = json.load(f)
        else:
            data = yaml.safe_load(f)

    # 检查必需字段
    if 'openapi' not in data:
        print('❌ 缺少openapi字段')
        sys.exit(1)

    if data['openapi'] not in ['3.0.0', '3.0.1', '3.0.2', '3.0.3', '3.1.0']:
        print(f'❌ 不支持的OpenAPI版本: {data[\"openapi\"]}')
        sys.exit(1)

    if 'info' not in data:
        print('❌ 缺少info字段')
        sys.exit(1)

    if 'paths' not in data:
        print('❌ 缺少paths字段')
        sys.exit(1)

    print('✅ OpenAPI结构验证通过')
except Exception as e:
    print(f'❌ 验证失败: {e}')
    sys.exit(1)
"

        if [ $? -ne 0 ]; then
            echo "❌ OpenAPI验证失败: $file"
            exit 1
        fi
    fi

    echo "✅ 验证通过: $file"
done

echo ""
echo "✅ 所有契约验证通过"
