#!/usr/bin/env python3
"""从OpenAPI契约自动生成TypeScript类型定义

支持工具:
- openapi-typescript-codegen
- dtsgenerator
- openapi-generator

使用方法:
    python scripts/generate-types/generate_ts_types.py --tool openapi-typescript
    python scripts/generate-types/generate_ts_types.py --contracts-dir docs/api/contracts
    python scripts/generate-types/generate_ts_types.py --output-dir web/frontend/src/types/api
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class TypeScriptTypesGenerator:
    """TypeScript类型定义生成器"""

    def __init__(
        self,
        contracts_dir: str = "docs/api/contracts",
        output_dir: str = "web/frontend/src/types/api",
        tool: str = "openapi-typescript",
    ):
        self.contracts_dir = Path(contracts_dir)
        self.output_dir = Path(output_dir)
        self.tool = tool

        # 支持的生成工具
        self.supported_tools = [
            "openapi-typescript",
            "dtsgenerator",
            "openapi-generator",
        ]

        if tool not in self.supported_tools:
            print(f"❌ 不支持的生成工具: {tool}")
            print(f"支持的工具: {', '.join(self.supported_tools)}")
            sys.exit(1)

    def check_dependencies(self) -> bool:
        """检查依赖是否安装"""
        print("🔍 检查依赖...")

        if self.tool == "openapi-typescript":
            if not self._command_exists("npx"):
                print("❌ npx未安装")
                print("请安装Node.js和npm: https://nodejs.org/")
                return False

            # 检查openapi-typescript-codegen是否已安装
            result = subprocess.run(
                ["npm", "list", "-g", "openapi-typescript-codegen"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print("⚠️  openapi-typescript-codeg未全局安装")
                print("正在安装...")
                subprocess.run(
                    ["npm", "install", "-g", "openapi-typescript-codegen"],
                    check=True,
                )

        elif self.tool == "dtsgenerator":
            if not self._command_exists("dtsgen"):
                print("⚠️  dtsgenerator未安装，正在安装...")
                subprocess.run(
                    ["npm", "install", "-g", "dtsgenerator"],
                    check=True,
                )

        elif self.tool == "openapi-generator":
            if not self._command_exists("openapi-generator"):
                print("⚠️  openapi-generator未安装，正在安装...")
                subprocess.run(
                    ["npm", "install", "-g", "@openapitools/openapi-generator-cli"],
                    check=True,
                )

        print("✅ 依赖检查通过")
        return True

    def _command_exists(self, command: str) -> bool:
        """检查命令是否存在"""
        try:
            subprocess.run(
                ["which", command],
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def create_output_dir(self):
        """创建输出目录"""
        print(f"📁 创建输出目录: {self.output_dir}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def find_contract_files(self) -> List[Path]:
        """查找所有契约文件"""
        print("🔍 查找契约文件...")

        if not self.contracts_dir.exists():
            print(f"❌ 契约目录不存在: {self.contracts_dir}")
            return []

        # 查找YAML和JSON文件
        contract_files = []
        for ext in ["*.yaml", "*.yml", "*.json"]:
            contract_files.extend(self.contracts_dir.glob(ext))

        if not contract_files:
            print("⚠️  未找到契约文件")
            return []

        print(f"✅ 找到 {len(contract_files)} 个契约文件")
        return contract_files

    def generate_types(self, contract_file: Path) -> Optional[Path]:
        """生成单个契约的类型定义"""
        contract_name = contract_file.stem
        output_file = self.output_dir / f"{contract_name}.ts"

        print(f"🔄 生成类型定义: {contract_file.name}")

        try:
            if self.tool == "openapi-typescript":
                self._generate_with_openapi_typescript(contract_file, output_file)
            elif self.tool == "dtsgenerator":
                self._generate_with_dtsgenerator(contract_file, output_file)
            elif self.tool == "openapi-generator":
                self._generate_with_openapi_generator(contract_file, output_file)

            print(f"✅ 生成成功: {output_file}")
            return output_file

        except subprocess.CalledProcessError as e:
            print(f"❌ 生成失败: {contract_file.name}")
            print(f"错误: {e}")
            return None

    def _generate_with_openapi_typescript(self, input_file: Path, output_file: Path):
        """使用openapi-typescript-codegen生成"""
        subprocess.run(
            ["npx", "openapi-typescript-codegen", str(input_file), "-o", str(output_file)],
            check=True,
            capture_output=True,
        )

    def _generate_with_dtsgenerator(self, input_file: Path, output_file: Path):
        """使用dtsgenerator生成"""
        subprocess.run(
            ["dtsgen", "--input", str(input_file), "--out", str(output_file)],
            check=True,
            capture_output=True,
        )

    def _generate_with_openapi_generator(self, input_file: Path, output_file: Path):
        """使用openapi-generator生成TypeScript类型"""
        subprocess.run(
            [
                "openapi-generator",
                "generate",
                "-i",
                str(input_file),
                "-g",
                "typescript-fetch",
                "-o",
                str(self.output_dir / f"temp_{input_file.stem}"),
                "--additional-properties="
                "supportsES6=true,"
                "withSeparateModelsAndApi=true,"
                "modelPackage=models,"
                "apiPackage=api",
            ],
            check=True,
            capture_output=True,
        )

        # 移动生成的文件
        temp_dir = self.output_dir / f"temp_{input_file.stem}"
        models_file = temp_dir / "models" / "index.ts"
        if models_file.exists():
            import shutil

            shutil.copy(models_file, output_file)
            shutil.rmtree(temp_dir)

    def generate_index_file(self, contract_files: List[Path]):
        """生成索引文件"""
        print("📝 生成索引文件...")

        index_file = self.output_dir / "index.ts"

        with open(index_file, "w", encoding="utf-8") as f:
            # 文件头
            f.write("/**\n")
            f.write(" * API类型定义\n")
            f.write(" * 从OpenAPI契约自动生成\n")
            f.write(" *\n")
            f.write(f" * 生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write(f" * 生成工具: {self.tool}\n")
            f.write(f" * 契约目录: {self.contracts_dir}\n")
            f.write(" *\n")
            f.write(" * 警告: 此文件由脚本自动生成，请勿手动编辑\n")
            f.write(" */\n\n")

            # 导出所有类型文件
            for contract in contract_files:
                contract_name = contract.stem
                f.write(f"export * from './{contract_name}';\n")

        print(f"✅ 索引文件生成完成: {index_file}")

    def generate_readme(self):
        """生成README文档"""
        readme_file = self.output_dir / "README.md"

        with open(readme_file, "w", encoding="utf-8") as f:
            f.write("# API类型定义\n\n")
            f.write("此目录包含从OpenAPI契约自动生成的TypeScript类型定义。\n\n")
            f.write("## 生成工具\n\n")
            f.write(f"- 工具: {self.tool}\n")
            f.write(f"- 生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("## 使用方法\n\n")
            f.write("```typescript\n")
            f.write("// 导入所有API类型\n")
            f.write("import * as API from '@/types/api';\n\n")
            f.write("// 使用类型\n")
            f.write("const stock: API.StockSymbol = {\n")
            f.write("  symbol: '000001.SZ',\n")
            f.write("  name: '平安银行'\n")
            f.write("};\n")
            f.write("```\n\n")
            f.write("## 重新生成\n\n")
            f.write("```bash\n")
            f.write("# 使用默认工具 (openapi-typescript)\n")
            f.write("python scripts/generate-types/generate_ts_types.py\n\n")
            f.write(f"# 使用{self.tool}\n")
            f.write(f"python scripts/generate-types/generate_ts_types.py --tool {self.tool}\n")
            f.write("```\n")

        print(f"✅ README生成完成: {readme_file}")

    def run(self):
        """运行生成流程"""
        print("🚀 TypeScript类型定义生成器")
        print(f"使用工具: {self.tool}")
        print()

        # 检查依赖
        if not self.check_dependencies():
            return False

        # 创建输出目录
        self.create_output_dir()

        # 查找契约文件
        contract_files = self.find_contract_files()
        if not contract_files:
            print("⚠️  未找到契约文件，退出")
            return False

        print()
        print("📝 找到以下契约文件:")
        for contract in contract_files:
            print(f"  - {contract}")
        print()

        # 生成类型定义
        generated_files = []
        for contract in contract_files:
            output_file = self.generate_types(contract)
            if output_file:
                generated_files.append(contract)

        # 生成索引文件
        if generated_files:
            self.generate_index_file(generated_files)

            # 生成README
            self.generate_readme()

        print()
        print("✅ TypeScript类型定义生成完成")
        print(f"输出目录: {self.output_dir}")
        print(f"生成文件数: {len(generated_files)}")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="从OpenAPI契约自动生成TypeScript类型定义",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认工具 (openapi-typescript)
  python scripts/generate-types/generate_ts_types.py

  # 使用dtsgenerator
  python scripts/generate-types/generate_ts_types.py --tool dtsgenerator

  # 指定契约目录
  python scripts/generate-types/generate_ts_types.py --contracts-dir docs/api/contracts

  # 指定输出目录
  python scripts/generate-types/generate_ts_types.py --output-dir web/frontend/src/types/api

  # 组合使用
  python scripts/generate-types/generate_ts_types.py \\
    --tool openapi-typescript \\
    --contracts-dir docs/api/contracts \\
    --output-dir web/frontend/src/types/api
        """,
    )

    parser.add_argument(
        "--contracts-dir",
        default="docs/api/contracts",
        help="OpenAPI契约目录 (默认: docs/api/contracts)",
    )

    parser.add_argument(
        "--output-dir",
        default="web/frontend/src/types/api",
        help="TypeScript类型输出目录 (默认: web/frontend/src/types/api)",
    )

    parser.add_argument(
        "--tool",
        default="openapi-typescript",
        choices=["openapi-typescript", "dtsgenerator", "openapi-generator"],
        help="生成工具 (默认: openapi-typescript)",
    )

    args = parser.parse_args()

    # 创建生成器并运行
    generator = TypeScriptTypesGenerator(
        contracts_dir=args.contracts_dir,
        output_dir=args.output_dir,
        tool=args.tool,
    )

    success = generator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
