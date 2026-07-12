#!/usr/bin/env python3
"""配置验证脚本
验证项目配置文件的一致性和正确性
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

import toml


def load_pyproject_config() -> Dict[str, Any]:
    """加载pyproject.toml配置"""
    try:
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "pyproject.toml"
        return toml.load(config_path)
    except Exception as e:
        print(f"❌ 无法加载pyproject.toml: {e}")
        return {}


def check_python_version_compatibility() -> bool:
    """检查Python版本兼容性"""
    config = load_pyproject_config()
    required_version = config.get("project", {}).get("requires-python", ">=3.9")

    # 解析版本要求
    if ">=3.9" in required_version:
        min_version = (3, 9)
    elif ">=3.10" in required_version:
        min_version = (3, 10)
    elif ">=3.11" in required_version:
        min_version = (3, 11)
    elif ">=3.12" in required_version:
        min_version = (3, 12)
    else:
        min_version = (3, 9)

    current_version = sys.version_info[:2]

    if current_version >= min_version:
        print(f"✅ Python版本兼容: {current_version} >= {min_version}")
        return True
    print(f"❌ Python版本不兼容: {current_version} < {min_version}")
    return False


def check_mypy_config() -> bool:
    """检查mypy配置"""
    config = load_pyproject_config()
    mypy_config = config.get("tool", {}).get("mypy", {})

    if not mypy_config:
        print("❌ 未找到mypy配置")
        return False

    mypy_python_version = mypy_config.get("python_version")
    config_mypy_path = Path(__file__).parent.parent.parent / "config" / "mypy.ini"

    # 检查mypy配置文件是否还存在
    if config_mypy_path.exists():
        print("⚠️  检测到旧的mypy.ini文件，建议删除以避免冲突")
        return False

    print(f"✅ mypy配置正常，Python版本: {mypy_python_version}")
    return True


def check_pytest_config() -> bool:
    """检查pytest配置"""
    config = load_pyproject_config()
    pytest_config = config.get("tool", {}).get("pytest", {}).get("ini_options", {})

    if not pytest_config:
        print("❌ 未找到pytest配置")
        return False

    minversion = pytest_config.get("minversion", "")
    testpaths = pytest_config.get("testpaths", [])

    # 检查测试路径是否存在
    project_root = Path(__file__).parent.parent.parent
    existing_paths = []
    for path in testpaths:
        if (project_root / path).exists():
            existing_paths.append(path)
        else:
            print(f"⚠️  测试路径不存在: {path}")

    if existing_paths:
        print(f"✅ pytest配置正常，最小版本: {minversion}, 测试路径: {existing_paths}")
        return True
    print("❌ 没有有效的测试路径")
    return False


def check_dependency_conflicts() -> bool:
    """检查依赖版本冲突"""
    config = load_pyproject_config()
    deps = config.get("project", {}).get("dependencies", [])
    dev_deps = config.get("project", {}).get("optional-dependencies", {}).get("dev", [])

    all_deps = deps + dev_deps
    conflict_found = False

    # 检查常见冲突
    version_ranges = {}
    for dep in all_deps:
        if ">=" in dep and "<" in dep:
            # 提取包名
            pkg_name = dep.split(">=")[0].split("<")[0].split("==")[0]
            version_range = dep[len(pkg_name) :]

            if pkg_name in version_ranges:
                if version_ranges[pkg_name] != version_range:
                    print(f"❌ 依赖版本冲突: {pkg_name}")
                    print(f"   版本1: {version_ranges[pkg_name]}")
                    print(f"   版本2: {version_range}")
                    conflict_found = True
            else:
                version_ranges[pkg_name] = version_range

    if not conflict_found:
        print("✅ 未发现依赖版本冲突")
        return True
    return False


def check_removed_config_files() -> List[str]:
    """检查是否还有遗留的配置文件"""
    project_root = Path(__file__).parent.parent.parent
    removed_files = [
        "config/pytest.ini",
        "tests/pytest.ini",
        "src/gpu/api_system/pytest.ini",
    ]

    existing_removed_files = []
    for file_path in removed_files:
        full_path = project_root / file_path
        if full_path.exists():
            existing_removed_files.append(file_path)

    return existing_removed_files


def main():
    """主函数"""
    print("🔧 MyStocks 配置验证开始...")
    print("=" * 50)

    all_checks_pass = True

    # 检查Python版本兼容性
    all_checks_pass &= check_python_version_compatibility()

    # 检查mypy配置
    all_checks_pass &= check_mypy_config()

    # 检查pytest配置
    all_checks_pass &= check_pytest_config()

    # 检查依赖冲突
    all_checks_pass &= check_dependency_conflicts()

    # 检查遗留配置文件
    removed_files = check_removed_config_files()
    if removed_files:
        print("⚠️  发现遗留的配置文件:")
        for file_path in removed_files:
            print(f"   - {file_path}")
        print("   建议删除这些文件以避免配置冲突")
        all_checks_pass = False
    else:
        print("✅ 未发现遗留的配置文件")

    print("=" * 50)
    if all_checks_pass:
        print("🎉 所有配置检查通过!")
        return 0
    print("❌ 存在配置问题，请检查上述错误")
    return 1


if __name__ == "__main__":
    sys.exit(main())
