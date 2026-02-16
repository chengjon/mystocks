#!/usr/bin/env python3
"""
Pydantic Schema 自动生成脚本

功能:
1. 从OpenAPI 3.0 YAML生成Pydantic v2模型
2. 支持批量生成多个模块的Schema
3. 自动添加导入和类型提示

用法:
    python scripts/dev/generate_pydantic_schemas.py --module market
    python scripts/dev/generate_pydantic_schemas.py --all
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional
import argparse


# 项目根目录(脚本位于scripts/dev/,需要向上2级)
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_APP = PROJECT_ROOT / "web" / "backend" / "app"
SCHEMAS_DIR = BACKEND_APP / "schemas"
CONTRACTS_DIR = PROJECT_ROOT / "docs" / "api" / "contracts"


def generate_schemas_from_openapi(
    openapi_file: Path,
    output_file: Path,
    module_name: str
) -> bool:
    """
    从OpenAPI YAML生成Pydantic模型

    Args:
        openapi_file: OpenAPI契约文件路径
        output_file: 输出的Pydantic模型文件路径
        module_name: 模块名称(用于文件头注释)

    Returns:
        是否成功生成
    """
    if not openapi_file.exists():
        print(f"❌ 契约文件不存在: {openapi_file}")
        return False

    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 构建datamodel-codegen命令
    cmd = [
        "datamodel-codegen",
        "--input", str(openapi_file),
        "--output", str(output_file),
        "--input-file-type", "openapi",
        "--output-model-type", "pydantic_v2.BaseModel",
        "--use-schema-description",
        "--use-field-description",
        "--field-constraints",
        "--strict-types",
        "--enable-version-header"
    ]

    print(f"🔧 正在生成 {module_name} Pydantic模型...")
    print(f"   输入: {openapi_file}")
    print(f"   输出: {output_file}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ 成功生成: {output_file.name}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 生成失败: {e}")
        print(f"   stderr: {e.stderr}")
        return False


def add_module_header(output_file: Path, module_name: str) -> None:
    """
    为生成的Pydantic模型添加模块头注释

    Args:
        output_file: 生成的Pydantic模型文件
        module_name: 模块名称
    """
    if not output_file.exists():
        return

    # 读取现有内容
    content = output_file.read_text(encoding='utf-8')

    # 构建文件头
    header = f'''"""
{module_name.capitalize()} API Pydantic模型

此文件由 `scripts/dev/generate_pydantic_schemas.py` 自动生成,
请勿手动编辑!如需修改,请更新OpenAPI契约后重新生成。

生成时间: 2025-12-29
模块: {module_name}
"""
'''

    # 检查是否已有文件头
    if not content.startswith('"""'):
        # 添加文件头
        output_file.write_text(header + content, encoding='utf-8')
        print(f"✅ 已添加模块头注释: {output_file.name}")


def generate_market_schemas() -> bool:
    """生成Market模块的Pydantic模型"""
    contract_file = CONTRACTS_DIR / "market_api.yaml"
    output_file = SCHEMAS_DIR / "market_schemas_generated.py"

    success = generate_schemas_from_openapi(
        contract_file,
        output_file,
        "market"
    )

    if success:
        add_module_header(output_file, "market")

    return success


def generate_technical_schemas() -> bool:
    """生成Technical模块的Pydantic模型"""
    contract_file = CONTRACTS_DIR / "technical_api.yaml"
    output_file = SCHEMAS_DIR / "technical_schemas_generated.py"

    success = generate_schemas_from_openapi(
        contract_file,
        output_file,
        "technical"
    )

    if success:
        add_module_header(output_file, "technical")

    return success


def generate_trade_schemas() -> bool:
    """生成Trade模块的Pydantic模型"""
    contract_file = CONTRACTS_DIR / "trade_api.yaml"
    output_file = SCHEMAS_DIR / "trade_schemas_generated.py"

    success = generate_schemas_from_openapi(
        contract_file,
        output_file,
        "trade"
    )

    if success:
        add_module_header(output_file, "trade")

    return success


def generate_all_schemas() -> None:
    """生成所有模块的Pydantic模型"""
    print("🚀 开始生成所有模块的Pydantic模型...")

    modules = [
        ("market", generate_market_schemas),
        ("technical", generate_technical_schemas),
        ("trade", generate_trade_schemas),
    ]

    success_count = 0
    for module_name, generator_func in modules:
        print(f"\n{'='*60}")
        print(f"模块: {module_name.upper()}")
        print('='*60)
        if generator_func():
            success_count += 1

    print(f"\n{'='*60}")
    print(f"✅ 生成完成: {success_count}/{len(modules)} 个模块")
    print('='*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="从OpenAPI契约生成Pydantic模型"
    )
    parser.add_argument(
        "--module",
        choices=["market", "technical", "trade"],
        help="指定要生成的模块"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="生成所有模块"
    )

    args = parser.parse_args()

    if args.all:
        generate_all_schemas()
    elif args.module:
        if args.module == "market":
            generate_market_schemas()
        elif args.module == "technical":
            generate_technical_schemas()
        elif args.module == "trade":
            generate_trade_schemas()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
