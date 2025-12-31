#!/usr/bin/env python3
"""
Web端运行准备状态检查
"""

import sys
from pathlib import Path


def check_basic_syntax():
    """检查Python语法错误"""
    print("🔍 检查Python语法...")

    # 检查关键文件的语法
    critical_files = [
        "web/backend/app/main.py",
        "web/backend/app/core/config.py",
        "web/backend/app/services/data_service_enhanced.py",
        "src/data_access/postgresql_access.py",
    ]

    syntax_errors = []
    for file_path in critical_files:
        if Path(file_path).exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    compile(f.read(), file_path, "exec")
                print(f"  ✅ {file_path}")
            except SyntaxError as e:
                syntax_errors.append(f"  ❌ {file_path}: {e}")
            except Exception as e:
                syntax_errors.append(f"  ⚠️ {file_path}: {e}")
        else:
            syntax_errors.append(f"  ⚠️ {file_path}: 文件不存在")

    return len(syntax_errors) == 0, syntax_errors


def check_environment_variables():
    """检查环境变量"""
    print("\n🔍 检查环境变量...")

    # 从.env文件读取
    env_file = Path(".env")
    if not env_file.exists():
        return False, ["❌ .env文件不存在"]

    env_content = env_file.read_text()

    required_vars = {
        "POSTGRESQL_PASSWORD": "数据库密码",
        "JWT_SECRET_KEY": "JWT密钥",
        "ADMIN_INITIAL_PASSWORD": "管理员密码",
        "TDENGINE_HOST": "TDengine主机",
        "POSTGRESQL_HOST": "PostgreSQL主机",
    }

    missing_vars = []
    for var, desc in required_vars.items():
        if var in env_content and env_content.split(var)[1].split("=")[1].strip():
            print(f"  ✅ {var}: {desc}")
        else:
            missing_vars.append(f"  ❌ {var}: {desc}")

    return len(missing_vars) == 0, missing_vars


def check_file_permissions():
    """检查文件权限"""
    print("\n🔍 检查文件权限...")

    env_file = Path(".env")
    if env_file.exists():
        stat = env_file.stat()
        permissions = oct(stat.st_mode)[-3:]

        if permissions == "600":
            print(f"  ✅ .env权限: {permissions} (安全)")
            return True, []
        else:
            print(f"  ⚠️ .env权限: {permissions} (建议设置为600)")
            return False, [f"  ⚠️ .env权限应为600，当前为{permissions}"]

    return False, ["❌ .env文件不存在"]


def check_frontend_build():
    """检查前端构建"""
    print("\n🔍 检查前端构建...")

    frontend_dir = Path("web/frontend")
    if not frontend_dir.exists():
        return False, ["❌ 前端目录不存在"]

    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        return False, ["❌ package.json不存在"]

    # 检查node_modules
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print(f"  ✅ 依赖已安装: {node_modules}")
    else:
        print("  ⚠️ 依赖未安装: 需要运行 npm install")

    return True, []


def check_database_connections():
    """检查数据库连接配置"""
    print("\n🔍 检查数据库连接配置...")

    # 这里只检查配置文件，不实际连接数据库
    try:
        # 尝试导入数据访问层
        sys.path.insert(0, ".")
        from src.data_access.postgresql_access import PostgreSQLDataAccess

        print("  ✅ PostgreSQL数据访问层导入成功")

        from src.data_access.tdengine_access import TDengineDataAccess

        print("  ✅ TDengine数据访问层导入成功")

        return True, []
    except ImportError as e:
        return False, [f"  ❌ 数据访问层导入失败: {e}"]
    except Exception as e:
        return False, [f"  ❌ 数据库配置检查失败: {e}"]


def main():
    """主检查函数"""
    print("=" * 50)
    print("🚀 MyStocks Web端运行准备状态检查")
    print("=" * 50)

    checks = [
        ("Python语法检查", check_basic_syntax),
        ("环境变量检查", check_environment_variables),
        ("文件权限检查", check_file_permissions),
        ("前端构建检查", check_frontend_build),
        ("数据库连接检查", check_database_connections),
    ]

    all_passed = True
    all_issues = []

    for check_name, check_func in checks:
        try:
            passed, issues = check_func()
            if passed:
                print(f"✅ {check_name}: 通过")
            else:
                print(f"❌ {check_name}: 失败")
                all_passed = False
                all_issues.extend(issues)
        except Exception as e:
            print(f"❌ {check_name}: 检查异常 - {e}")
            all_passed = False
            all_issues.append(f"  ❌ {check_name}: {e}")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有检查通过！系统已准备就绪，可以启动Web端")
        print("\n📋 启动命令:")
        print("  后端: cd web/backend && python main.py")
        print("  前端: cd web/frontend && npm run dev")
    else:
        print("❌ 发现问题，需要修复后才能启动Web端")
        print("\n🔧 需要修复的问题:")
        for issue in all_issues:
            print(issue)

    print("=" * 50)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
