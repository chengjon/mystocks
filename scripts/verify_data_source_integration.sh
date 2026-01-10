#!/bin/bash
# 数据源集成完整验证脚本
# 基于文档: docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md
# 用途: 验证新增数据源是否正确集成到系统

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     MyStocks 数据源集成验证脚本                          ║"
echo "║     基于: docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 步骤1: 配置文件检查
print_header "步骤1: 配置文件检查"

if [ ! -f "config/data_sources_registry.yaml" ]; then
    print_error "配置文件不存在: config/data_sources_registry.yaml"
    exit 1
fi

print_success "YAML配置文件存在"

# 检查YAML格式（如果yamllint可用）
if command -v yamllint &> /dev/null; then
    if yamllint config/data_sources_registry.yaml &> /dev/null; then
        print_success "YAML格式验证通过"
    else
        print_warning "YAML格式可能有问题（建议运行yamllint检查）"
    fi
fi

echo ""

# 步骤2: 同步到数据库
print_header "步骤2: 同步配置到数据库"

if [ ! -f "scripts/sync_sources.py" ]; then
    print_error "同步脚本不存在: scripts/sync_sources.py"
    exit 1
fi

if python scripts/sync_sources.py; then
    print_success "配置已同步到PostgreSQL数据库"
else
    print_error "同步失败"
    exit 1
fi

echo ""

# 步骤3: 验证端点加载
print_header "步骤3: 验证端点加载"

python3 << 'PYTHON_SCRIPT'
from src.core.data_source.base import DataSourceManagerV2

try:
    manager = DataSourceManagerV2()
    count = len(manager.registry)

    if count == 0:
        print(f"\n{'❌ 错误: 未加载任何端点'}")
        print("排查步骤:")
        print("1. 检查YAML配置格式")
        print("2. 运行 sync_sources.py 同步到数据库")
        print("3. 检查PostgreSQL数据库连接")
        print("4. 检查registry.py的JSONB解析逻辑（第62行）")
        exit(1)

    print(f"{'✅ 已加载端点: ' + str(count) + '个'}")

    # 显示前5个端点
    print(f"\n{'前5个端点:'}")
    for i, (name, source) in enumerate(list(manager.registry.items())[:5]):
        config = source["config"]
        print(f"  {i+1}. {name} - {config.get('source_name')} - {config.get('data_category')}")

except Exception as e:
    print(f"{'❌ 端点加载失败: ' + str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    print_success "端点加载验证通过"
else
    print_error "端点加载验证失败"
    exit 1
fi

echo ""

# 步骤4: 验证智能路由
print_header "步骤4: 验证智能路由功能"

python3 << 'PYTHON_SCRIPT'
from src.core.data_source.base import DataSourceManagerV2

try:
    manager = DataSourceManagerV2()

    # 测试DAILY_KLINE（应该有数据）
    best = manager.get_best_endpoint('DAILY_KLINE')
    if best is None:
        print("❌ DAILY_KLINE路由失败: 找不到端点")
        print("可能原因:")
        print("- router.py未实现必需函数")
        print("- 数据源未正确注册")
        print("- data_category配置错误")
        exit(1)

    print(f"{'✅ DAILY_KLINE → ' + best['endpoint_name']}")

    # 测试REALTIME_QUOTE
    best2 = manager.get_best_endpoint('REALTIME_QUOTE')
    if best2 is None:
        print("⚠️  REALTIME_QUOTE路由失败: 找不到端点（可能未注册）")
    else:
        print(f"{'✅ REALTIME_QUOTE → ' + best2['endpoint_name']}")

except ImportError as e:
    print(f"{'❌ ImportError: ' + str(e)}")
    print("解决方案:")
    print("检查 src/core/data_source/router.py 是否实现了3个必需函数:")
    print("1. find_endpoints(self, **kwargs)")
    print("2. get_best_endpoint(self, data_category)")
    print("3. list_all_endpoints(self)")
    exit(1)
except Exception as e:
    print(f"{'❌ 智能路由验证失败: ' + str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    print_success "智能路由验证通过"
else
    print_error "智能路由验证失败"
    exit 1
fi

echo ""

# 步骤5: 列出所有端点
print_header "步骤5: 列出所有已注册端点"

python3 << 'PYTHON_SCRIPT'
from src.core.data_source.base import DataSourceManagerV2

try:
    manager = DataSourceManagerV2()
    df = manager.list_all_endpoints()

    print(f"\n{'端点统计:'}")
    print(f"  总数: {len(df)}")
    print(f"\n{'按数据源分类:'}")
    if '数据源' in df.columns:
        print(df['数据源'].value_counts().to_string())

    print(f"\n{'按数据分类:'}")
    if '数据分类' in df.columns:
        print(df['数据分类'].value_counts().to_string())

    # 显示完整表格
    print(f"\n{'完整端点列表:'}")
    print(df.to_string())

    print(f"\n{'✅ 端点列表生成成功'}")

except Exception as e:
    print(f"{'❌ 生成端点列表失败: ' + str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    print_success "端点列表生成成功"
else
    print_error "端点列表生成失败"
    exit 1
fi

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              验证完成！所有检查通过 ✅                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "📖 后续步骤:"
echo "1. 阅读: docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md"
echo "2. 完成47项检查清单（文档第4章）"
echo "3. 编写单元测试和集成测试"
echo "4. 提交代码审查"
echo ""
