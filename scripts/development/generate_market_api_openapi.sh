#!/bin/bash
# 导出市场数据API的OpenAPI规范

set -e

PROJECT_ROOT="/opt/claude/mystocks_spec"
OUTPUT_DIR="$PROJECT_ROOT/docs/api/openapi"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 开始导出市场数据API的OpenAPI规范..."

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 导出完整API规范
echo "📝 导出完整API规范..."
cd "$PROJECT_ROOT/web/backend"
python3 - <<'PYTHON_SCRIPT'
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path.cwd()))

from app.main import app

# 导出OpenAPI规范
openapi_schema = app.openapi()

# 保存完整规范
output_path = Path("../../docs/api/openapi/market-data-api-full.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

print(f"✅ 完整API规范已导出: {output_path}")
print(f"   - Title: {openapi_schema['info']['title']}")
print(f"   - Version: {openapi_schema['info']['version']}")
print(f"   - 端点数量: {len(openapi_schema['paths'])}")

# 统计各标签的端点数量
tags_count = {}
for path, methods in openapi_schema['paths'].items():
    for method, details in methods.items():
        if method != 'parameters':  # 跳过共享参数
            tags = details.get('tags', ['default'])
            for tag in tags:
                tags_count[tag] = tags_count.get(tag, 0) + 1

print(f"\n📊 端点分类统计:")
for tag, count in sorted(tags_count.items()):
    print(f"   - {tag}: {count}个端点")
PYTHON_SCRIPT

# 返回项目根目录
cd "$PROJECT_ROOT"

echo ""
echo "✅ OpenAPI规范导出完成！"
echo "📂 输出目录: $OUTPUT_DIR"
echo ""
echo "📋 生成的文件:"
ls -lh "$OUTPUT_DIR"/*.json 2>/dev/null || echo "   (暂无JSON文件)"
echo ""
echo "🔗 下一步: 注册到API契约管理平台"
echo "   cd /opt/claude/mystocks_phase6_api_contract"
echo "   api-contract-sync create market-data 1.0.0 -s docs/api/openapi/market-data-api-full.json"
