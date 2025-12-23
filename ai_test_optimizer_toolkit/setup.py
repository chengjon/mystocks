#!/usr/bin/env python3
"""
AI Test Optimizer Toolkit 安装脚本
自动化安装和配置AI测试优化工具包
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class ToolkitInstaller:
    """AI测试优化器工具包安装器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.toolkit_root = project_root / "ai_test_optimizer_toolkit"
        self.scripts_dir = project_root / "scripts"

    def check_requirements(self) -> bool:
        """检查系统要求"""
        print("🔍 检查系统要求...")

        # 检查Python版本
        if sys.version_info < (3, 8):
            print(
                f"❌ Python版本过低: {sys.version_info.major}.{sys.version_info.minor}"
            )
            print("   要求: Python 3.8+")
            return False

        print(
            f"✅ Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )

        # 检查必要目录
        required_dirs = ["scripts", "src"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                print(f"❌ 缺少必要目录: {dir_path}")
                return False
            print(f"✅ 找到目录: {dir_path}")

        return True

    def create_toolkit_structure(self) -> bool:
        """创建工具包目录结构"""
        print("🏗️ 创建工具包目录结构...")

        toolkit_dirs = [
            "bin",
            "config",
            "docs",
            "examples",
            "plugins",
            "templates",
            "tests",
            "reports",
            "cache",
            "logs",
        ]

        try:
            for dir_name in toolkit_dirs:
                dir_path = self.toolkit_root / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ 创建目录: {dir_path}")

            return True
        except Exception as e:
            print(f"❌ 创建目录失败: {e}")
            return False

    def copy_core_scripts(self) -> bool:
        """复制核心脚本文件"""
        print("📋 复制核心脚本文件...")

        core_scripts = {
            "smart_ai_analyzer.py": "bin/",
            "ai_test_optimizer.py": "bin/",
            "ai_test_optimizer_simple.py": "bin/",
            "ai_optimizer_monitor.py": "plugins/monitoring/",
            "usage_feedback_analyzer.py": "plugins/analysis/",
            "check_coverage.py": "plugins/quality/",
            "regression_test.py": "plugins/performance/",
        }

        try:
            for script_name, target_dir in core_scripts.items():
                source_path = self.scripts_dir / script_name
                if source_path.exists():
                    target_path = self.toolkit_root / target_dir / script_name

                    # 创建目标目录
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # 复制文件
                    shutil.copy2(source_path, target_path)

                    # 设置执行权限
                    os.chmod(target_path, 0o755)

                    print(f"✅ 复制脚本: {script_name} -> {target_dir}")
                else:
                    print(f"⚠️ 脚本不存在: {source_path}")

            return True
        except Exception as e:
            print(f"❌ 复制脚本失败: {e}")
            return False

    def create_config_files(self) -> bool:
        """创建配置文件"""
        print("⚙️ 创建配置文件...")

        # 主配置文件
        main_config = """# AI Test Optimizer 配置文件
# 专业级智能测试优化工具包配置

project:
  name: "MyStocks"
  version: "2.0"
  description: "量化交易系统智能测试优化"

source_paths:
  - "src/"
  - "web/backend/"

test_paths:
  - "tests/"
  - "scripts/tests/"

exclude_patterns:
  - "*/migrations/*"
  - "*/venv/*"
  - "*/.venv/*"
  - "*/node_modules/*"
  - "*/__pycache__/*"

analysis:
  complexity_threshold: 10
  security_scan: true
  performance_analysis: true
  bug_detection:
    sql_injection: true
    xss: true
    resource_leaks: true
    null_pointer: true
    off_by_one: true

test_generation:
  max_tests_per_file: 20
  include_security_tests: true
  include_performance_tests: true
  include_boundary_tests: true
  mock_framework: "unittest.mock"

quality_gates:
  coverage_threshold: 80
  complexity_threshold: 10
  bug_threshold: 0
  security_threshold: 0

reporting:
  output_format: ["html", "json", "markdown"]
  auto_generate: true
  include_trends: true
  include_recommendations: true

monitoring:
  enabled: true
  metrics_collection: true
  performance_tracking: true
  usage_analytics: true

integrations:
  github_actions: true
  code_coverage: "codecov"
  security_scan: "bandit"
"""

        # CI/CD配置文件
        ci_config = """# CI/CD集成配置
name: "AI Test Optimizer CI"
on: [push, pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install Dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov bandit safety

    - name: Run AI Quality Check
      run: |
        python ai_test_optimizer_toolkit/bin/ai_test_optimizer_simple.py auto

    - name: Security Scan
      run: bandit -r src/ -f json -o bandit-report.json

    - name: Coverage Analysis
      run: |
        pytest --cov=src --cov-report=xml --cov-report=html
        python ai_test_optimizer_toolkit/plugins/quality/check_coverage.py --threshold 80

    - name: Performance Tests
      run: |
        python ai_test_optimizer_toolkit/plugins/performance/regression_test.py

    - name: Upload Reports
      uses: actions/upload-artifact@v3
      with:
        name: quality-reports
        path: |
          smart_analysis_reports/
          coverage.xml
          htmlcov/
          bandit-report.json
"""

        # 开发者配置文件
        dev_config = """# 开发者配置
# IDE集成和开发工具配置

ide_integration:
  vscode:
    extensions:
      - "ms-python.python"
      - "ms-python.flake8"
      - "ms-python.pylint"
      - "bradlc.vscode-tailwindcss"
    settings:
      "python.linting.enabled": true
      "python.linting.pylintEnabled": true
      "python.testing.pytestEnabled": true
      "python.testing.unittestEnabled": true

  pycharm:
    inspections:
      "PyPep8Inspection": true
      "PyUnusedLocalInspection": true
      "PyClassHasNoInitInspection": true
      "PyMethodMayBeStaticInspection": true

pre_commit:
  hooks:
    - id: ai-quality-check
      entry: python ai_test_optimizer_toolkit/bin/smart_ai_analyzer.py
      language: system
      files: ".*\\.py$"
      pass_filenames: true
"""

        try:
            # 创建配置目录
            config_dir = self.toolkit_root / "config"
            config_dir.mkdir(exist_ok=True)

            # 写入配置文件
            config_files = {
                "ai_toolkit_config.yaml": main_config,
                "github_actions.yml": ci_config,
                "development_config.yaml": dev_config,
            }

            for filename, content in config_files.items():
                config_path = config_dir / filename
                with open(config_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ 创建配置: {filename}")

            return True
        except Exception as e:
            print(f"❌ 创建配置文件失败: {e}")
            return False

    def create_cli_scripts(self) -> bool:
        """创建命令行工具"""
        print("🔧 创建命令行工具...")

        # 主CLI工具
        cli_script = """#!/usr/bin/env python3
\"\"\"
AI Test Optimizer CLI
命令行工具入口点
\"\"\"

import sys
import os
from pathlib import Path

# 添加工具包路径
toolkit_root = Path(__file__).parent
sys.path.insert(0, str(toolkit_root))

try:
    from bin.ai_test_optimizer_simple import main
    main()
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)
"""

        # 健康检查脚本
        health_script = """#!/usr/bin/env python3
\"\"\"
AI Test Optimizer 健康检查
验证工具包安装和配置
\"\"\"

import sys
import os
from pathlib import Path

def check_installation():
    \"\"\"检查工具包安装状态\"\"\"
    print("🔍 AI Test Optimizer 健康检查")
    print("=" * 40)

    # 检查核心组件
    components = {
        "Smart AI Analyzer": "bin/smart_ai_analyzer.py",
        "AI Test Optimizer": "bin/ai_test_optimizer.py",
        "Simple Optimizer": "bin/ai_test_optimizer_simple.py",
        "Monitor": "plugins/monitoring/ai_optimizer_monitor.py",
        "Analyzer": "plugins/analysis/usage_feedback_analyzer.py"
    }

    toolkit_root = Path(__file__).parent
    all_ok = True

    for name, path in components.items():
        component_path = toolkit_root / path
        if component_path.exists():
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - 缺少: {path}")
            all_ok = False

    # 检查配置
    config_path = toolkit_root / "config" / "ai_toolkit_config.yaml"
    if config_path.exists():
        print("✅ 配置文件")
    else:
        print("❌ 配置文件 - 缺少: config/ai_toolkit_config.yaml")
        all_ok = False

    print("=" * 40)

    if all_ok:
        print("🎉 工具包安装完成!")
        return True
    else:
        print("⚠️ 工具包安装不完整，请重新安装")
        return False

if __name__ == "__main__":
    success = check_installation()
    sys.exit(0 if success else 1)
"""

        try:
            bin_dir = self.toolkit_root / "bin"

            # 创建CLI工具
            with open(bin_dir / "ai-toolkit", "w") as f:
                f.write(cli_script)
            os.chmod(bin_dir / "ai-toolkit", 0o755)
            print("✅ 创建CLI工具: ai-toolkit")

            # 创建健康检查
            with open(self.toolkit_root / "health_check.py", "w") as f:
                f.write(health_script)
            os.chmod(self.toolkit_root / "health_check.py", 0o755)
            print("✅ 创建健康检查: health_check.py")

            return True
        except Exception as e:
            print(f"❌ 创建CLI工具失败: {e}")
            return False

    def create_documentation(self) -> bool:
        """创建文档模板"""
        print("📚 创建文档模板...")

        docs = {
            "QUICKSTART.md": """# 快速开始指南

## 1. 基础使用
```bash
# 分析代码质量
python ai_toolkit.py analyze src/

# 生成智能测试
python ai_toolkit.py test-generate

# 检查覆盖率
python ai_toolkit.py coverage-check
```

## 2. 集成到CI/CD
参考 `config/github_actions.yml`

## 3. 配置选项
编辑 `config/ai_toolkit_config.yaml`
""",
            "USER_GUIDE.md": """# 用户指南

## 1. 配置文件详解
## 2. 命令行选项
## 3. 输出报告解读
## 4. 最佳实践
""",
            "TROUBLESHOOTING.md": """# 故障排除

## 常见问题

### 1. 安装问题
### 2. 性能问题
### 3. 配置问题
### 4. 集成问题
""",
        }

        try:
            docs_dir = self.toolkit_root / "docs"
            docs_dir.mkdir(exist_ok=True)

            for filename, content in docs.items():
                with open(docs_dir / filename, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ 创建文档: {filename}")

            return True
        except Exception as e:
            print(f"❌ 创建文档失败: {e}")
            return False

    def create_requirements(self) -> bool:
        """创建依赖文件"""
        print("📦 创建依赖文件...")

        requirements = """# AI Test Optimizer Toolkit 依赖

# 核心依赖
ast>=3.8.0
pytest>=8.0.0
pytest-cov>=4.0.0
coverage>=7.0.0

# 代码质量
bandit>=1.7.0
safety>=2.3.0
pylint>=3.0.0
mypy>=1.5.0

# 数据分析
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0

# 报告生成
jinja2>=3.1.0
markdown>=3.4.0
pyyaml>=6.0.0

# 开发工具
click>=8.1.0
rich>=13.0.0
tqdm>=4.65.0

# 可选依赖 (AI功能)
# torch>=2.0.0
# scikit-learn>=1.3.0
# transformers>=4.30.0
"""

        try:
            with open(self.toolkit_root / "requirements.txt", "w") as f:
                f.write(requirements)
            print("✅ 创建依赖文件: requirements.txt")
            return True
        except Exception as e:
            print(f"❌ 创建依赖文件失败: {e}")
            return False

    def install(self) -> bool:
        """执行完整安装流程"""
        print("🚀 开始安装 AI Test Optimizer Toolkit")
        print("=" * 50)

        # 安装步骤
        steps = [
            ("检查系统要求", self.check_requirements),
            ("创建工具包结构", self.create_toolkit_structure),
            ("复制核心脚本", self.copy_core_scripts),
            ("创建配置文件", self.create_config_files),
            ("创建命令行工具", self.create_cli_scripts),
            ("创建文档模板", self.create_documentation),
            ("创建依赖文件", self.create_requirements),
        ]

        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ 安装失败: {step_name}")
                return False

        print("\n" + "=" * 50)
        print("🎉 AI Test Optimizer Toolkit 安装完成!")
        print("\n📝 下一步:")
        print("1. 运行健康检查: python ai_test_optimizer_toolkit/health_check.py")
        print(
            "2. 查看配置: cat ai_test_optimizer_toolkit/config/ai_toolkit_config.yaml"
        )
        print("3. 快速开始: python ai_test_optimizer_toolkit/health_check.py")
        print("4. 阅读文档: ls ai_test_optimizer_toolkit/docs/")

        return True


def main():
    """主安装函数"""
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        # 默认使用当前目录的父目录（项目根目录）
        project_root = Path(__file__).parent.parent

    installer = ToolkitInstaller(project_root)
    success = installer.install()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
