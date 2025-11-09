#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库测试工具 - 交互式菜单版本
整合了路径查找、配置检查、连通性测试功能
"""

import os
import sys
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class DatabaseTestTool:
    """数据库测试工具类"""

    def __init__(self):
        """初始化测试工具"""
        self.env_file_path = None
        self.config = {}
        self.test_results = {}

        # 数据库连接库导入状态
        self.db_libs = {
            "pymysql": None,
            "psycopg2": None,
            "redis": None,
            "tdengine": None,  # TDengine使用统一的键名
            "sqlalchemy": None,
        }

    def find_env_file(self) -> bool:
        """查找.env文件路径"""
        print("\n" + "=" * 60)
        print("🔍 查找 .env 文件路径")
        print("=" * 60)

        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 检查路径列表：当前目录、上级目录、项目根目录
        search_paths = [
            os.path.join(current_dir, ".env"),  # db_manager/.env
            os.path.join(os.path.dirname(current_dir), ".env"),  # mystocks/.env
            os.path.join(
                os.path.dirname(os.path.dirname(current_dir)), ".env"
            ),  # GITHUB/.env
        ]

        print(f"当前脚本位置: {current_dir}")
        print("\n正在搜索 .env 文件...")

        for i, path in enumerate(search_paths, 1):
            print(f"{i}. 检查路径: {path}")
            if os.path.exists(path):
                print(f"   ✅ 找到文件!")
                self.env_file_path = path

                # 加载环境变量
                load_dotenv(path)
                print(f"\n✅ 已加载环境配置文件: {path}")

                # 测试几个关键配置变量
                test_vars = [
                    "MYSQL_HOST",
                    "POSTGRESQL_HOST",
                    "REDIS_HOST",
                    "TDENGINE_HOST",
                    "MONITOR_DB_URL",
                ]
                print("\n配置变量验证:")
                found_vars = 0
                for var in test_vars:
                    value = os.getenv(var)
                    if value:
                        print(f"  ✅ {var}: {value}")
                        found_vars += 1
                    else:
                        print(f"  ❌ {var}: 未设置")

                print(f"\n📊 找到 {found_vars}/{len(test_vars)} 个配置变量")
                return True
            else:
                print(f"   ❌ 文件不存在")

        print("\n❌ 未找到 .env 文件")
        return False

    def load_config(self) -> Dict[str, Any]:
        """从环境变量加载数据库配置"""
        return {
            "monitor_mysql": {
                "url": os.getenv("MONITOR_DB_URL", ""),
                "type": "MySQL Monitor",
            },
            "tdengine": {
                "host": os.getenv("TDENGINE_HOST", ""),
                "user": os.getenv("TDENGINE_USER", "root"),
                "password": os.getenv("TDENGINE_PASSWORD", "taosdata"),
                "port": int(os.getenv("TDENGINE_PORT", 6030)),
                "type": "TDengine",
            },
            "postgresql": {
                "host": os.getenv("POSTGRESQL_HOST", ""),
                "user": os.getenv("POSTGRESQL_USER", "postgres"),
                "password": os.getenv("POSTGRESQL_PASSWORD", ""),
                "port": int(os.getenv("POSTGRESQL_PORT", 5432)),
                "type": "PostgreSQL",
            },
            "redis": {
                "host": os.getenv("REDIS_HOST", ""),
                "port": int(os.getenv("REDIS_PORT", 6379)),
                "password": os.getenv("REDIS_PASSWORD", ""),
                "db": int(os.getenv("REDIS_DB", 0)),
                "type": "Redis",
            },
            "mysql": {
                "host": os.getenv("MYSQL_HOST", ""),
                "user": os.getenv("MYSQL_USER", "root"),
                "password": os.getenv("MYSQL_PASSWORD", ""),
                "port": int(os.getenv("MYSQL_PORT", 3306)),
                "type": "MySQL",
            },
            "mariadb": {
                "host": os.getenv("MARIADB_HOST", ""),
                "user": os.getenv("MARIADB_USER", "root"),
                "password": os.getenv("MARIADB_PASSWORD", ""),
                "port": int(os.getenv("MARIADB_PORT", 3306)),
                "type": "MariaDB",
            },
        }

    def test_config_integrity(self) -> bool:
        """测试数据库配置完整性"""
        print("\n" + "=" * 60)
        print("⚙️ 数据库配置完整性测试")
        print("=" * 60)

        if not self.env_file_path:
            print("❌ 请先查找 .env 文件路径!")
            return False

        # 加载配置
        self.config = self.load_config()

        print("正在检查所有数据库配置...")
        config_complete = 0
        self.test_results = {}

        for db_name, config in self.config.items():
            print(f"\n🔍 检查 {config['type']} 配置...")

            if db_name == "monitor_mysql":
                # MySQL Monitor使用URL格式
                if config["url"]:
                    print(f"  ✅ 连接URL: {config['url']}")
                    self.test_results[db_name] = True
                    config_complete += 1
                else:
                    print(f"  ❌ 缺少配置: MONITOR_DB_URL")
                    self.test_results[db_name] = False
            else:
                # 其他数据库使用host/port格式
                if config["host"]:
                    print(f"  ✅ 主机: {config['host']}")
                    print(f"  ✅ 端口: {config['port']}")
                    if "user" in config:
                        print(f"  ✅ 用户: {config['user']}")
                    if "password" in config:
                        print(
                            f"  ✅ 密码: {'已设置' if config.get('password') else '未设置'}"
                        )
                    if db_name == "redis":
                        print(f"  ✅ 数据库: {config['db']}")
                    self.test_results[db_name] = True
                    config_complete += 1
                else:
                    print(f"  ❌ 缺少配置: {config['type'].upper()}_HOST")
                    self.test_results[db_name] = False

        # 显示总结
        self._print_config_summary(config_complete)
        return config_complete == len(self.config)

    def check_database_drivers(self) -> bool:
        """检查数据库驱动安装情况"""
        print("\n" + "=" * 60)
        print("🔌 数据库驱动检查")
        print("=" * 60)

        print("正在检查数据库驱动安装情况...")

        # 检查各种数据库驱动
        drivers_info = [
            ("pymysql", "MySQL/MariaDB 驱动"),
            ("psycopg2", "PostgreSQL 驱动"),
            ("redis", "Redis 驱动"),
            ("tdengine", "TDengine 驱动 (多种连接方式)"),  # 特殊处理，检测多种连接方式
            ("sqlalchemy", "SQL 数据库引擎"),
        ]

        installed_count = 0

        for driver_name, description in drivers_info:
            try:
                if driver_name == "sqlalchemy":
                    exec("from sqlalchemy import create_engine, text")
                    self.db_libs[driver_name] = True  # 简化存储
                elif driver_name == "tdengine":
                    # TDengine 多种连接方式检测
                    try:
                        success_methods = self._check_tdengine_drivers()
                        if success_methods:
                            self.db_libs[driver_name] = success_methods
                            method_names = ", ".join(success_methods)
                            print(f"  ✅ {description}: 已安装 ({method_names})")
                            installed_count += 1
                        else:
                            self.db_libs[driver_name] = None
                            print(f"  ❌ {description}: 未安装")
                            print(f"      提示: 请安装以下任意一种 TDengine 驱动:")
                            print(f"      - WebSocket(推荐): pip install taos-ws-py")
                            print(f"      - REST连接: pip install taospy")
                            print(
                                f"      - 原生连接: pip install taospy + 安装TDengine客户端"
                            )
                    except Exception as e:
                        print(f"  ❌ {description}: 检查时出错 ({str(e)})")
                        self.db_libs[driver_name] = None
                    continue
                else:
                    exec(f"import {driver_name}")
                    self.db_libs[driver_name] = True
                print(f"  ✅ {description}: 已安装")
                installed_count += 1
            except ImportError:
                print(f"  ❌ {description}: 未安装")
                self.db_libs[driver_name] = None
            except Exception as e:
                print(f"  ❌ {description}: 检查时出错 ({str(e)})")
                self.db_libs[driver_name] = None

        print(f"\n📊 驱动安装情况: {installed_count}/{len(drivers_info)} 个已安装")

        if installed_count < len(drivers_info):
            print("\n💡 安装缺失驱动的命令:")
            print("pip install pymysql psycopg2-binary redis sqlalchemy python-dotenv")
            print("\n📝 TDengine 驱动选择 (任选一种):")
            print("  - WebSocket(推荐): pip install taos-ws-py")
            print("  - REST连接:        pip install taospy")
            print("  - 原生连接:        pip install taospy + 安装TDengine客户端")

        return installed_count == len(drivers_info)

    def _check_tdengine_drivers(self) -> list:
        """检测 TDengine 的各种连接方式"""
        available_methods = []

        # 1. 检测 WebSocket 连接 (taos-ws-py包)
        try:
            exec("import taosws")
            available_methods.append("WebSocket(taos-ws-py)")
        except ImportError:
            pass
        except Exception:
            # 忽略其他类型的异常，避免干扰检测流程
            pass

        # 2. 检测 REST 连接 (taospy包的taosrest模块)
        try:
            exec("import taosrest")
            available_methods.append("REST(taosrest)")
        except ImportError:
            pass
        except Exception:
            # 忽略其他类型的异常
            pass

        # 3. 检测原生连接 (taospy包的taos模块)
        try:
            exec("import taos")
            available_methods.append("原生(taos)")
        except ImportError:
            pass
        except Exception:
            # 忽略其他类型的异常（如客户端库加载失败）
            pass

        # 4. 通过pip检测taospy包
        try:
            import subprocess
            import sys

            # 检查pip show taospy
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "taospy"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and "Name: taospy" in result.stdout:
                # 从输出中提取版本信息
                lines = result.stdout.strip().split("\n")
                version = "Unknown"
                for line in lines:
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                        break
                available_methods.append(f"taospy(v{version})")
        except Exception:
            pass

        # 5. 检测taos-ws-py包
        try:
            import subprocess
            import sys

            # 检查pip show taos-ws-py
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "taos-ws-py"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and "Name: taos-ws-py" in result.stdout:
                # 从输出中提取版本信息
                lines = result.stdout.strip().split("\n")
                version = "Unknown"
                for line in lines:
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                        break
                # 避免重复（如果WebSocket已经通过import检测到）
                websocket_found = any(
                    "WebSocket" in method for method in available_methods
                )
                if not websocket_found:
                    available_methods.append(f"taos-ws-py(v{version})")
        except Exception:
            pass

        return available_methods

    def test_database_connectivity(self) -> bool:
        """测试数据库连通性"""
        print("\n" + "=" * 60)
        print("🌐 数据库连通性测试")
        print("=" * 60)

        if not self.config:
            print("❌ 请先进行配置完整性测试!")
            return False

        # 检查必要的驱动
        missing_drivers = []
        for name, lib in self.db_libs.items():
            if name == "tdengine":
                # TDengine特殊处理：如果有任何连接方式可用就认为可用
                if not lib or (isinstance(lib, list) and len(lib) == 0):
                    missing_drivers.append(name)
            else:
                # 其他驱动的常规检查
                if lib is None:
                    missing_drivers.append(name)

        if missing_drivers:
            print(f"❌ 缺少必要的数据库驱动: {', '.join(missing_drivers)}")
            print("请先安装缺失的驱动后再进行连通性测试")
            return False

        print("开始测试数据库连接...")
        successful_connections = 0

        # 重新导入需要的模块（用于实际连接测试）
        try:
            import pymysql
            import redis
            from sqlalchemy import create_engine, text

            # 检测 TDengine 可用的连接方式（安全导入）
            tdengine_methods = {}
            try:
                import taosws

                tdengine_methods["WebSocket"] = taosws
            except ImportError:
                pass
            except Exception:
                # 忽略其他异常，避免中断测试流程
                pass

            try:
                import taosrest

                tdengine_methods["REST"] = taosrest
            except ImportError:
                pass
            except Exception:
                # 忽略其他异常
                pass

            try:
                import taos

                tdengine_methods["原生"] = taos
            except ImportError:
                pass
            except Exception:
                # 忽略其他异常（如客户端库加载失败）
                pass

            # 测试每个数据库连接
            for db_name, config in self.config.items():
                if not self.test_results.get(db_name, False):
                    print(f"\n⏭️ 跳过 {config['type']}: 配置不完整")
                    continue

                print(f"\n🔍 测试 {config['type']} 连接...")

                try:
                    if db_name == "monitor_mysql":
                        success = self._test_mysql_monitor_simple(
                            config, create_engine, text
                        )
                    elif db_name in ["mysql", "mariadb"]:
                        success = self._test_mysql_simple(config, pymysql)
                    elif db_name == "redis":
                        success = self._test_redis_simple(config, redis)
                    elif db_name == "tdengine":
                        # 检查是否有可用的TDengine连接方式
                        tdengine_lib_status = self.db_libs.get("tdengine")
                        if tdengine_methods:
                            # 有可导入的模块，进行实际连接测试
                            success = self._test_tdengine_multi(
                                config, tdengine_methods
                            )
                        elif (
                            tdengine_lib_status
                            and isinstance(tdengine_lib_status, list)
                            and len(tdengine_lib_status) > 0
                        ):
                            # 检测到TDengine包但无法导入模块，提示安装问题
                            print(
                                f"  ⚠️ 检测到TDengine包 ({', '.join(tdengine_lib_status)})，但无法导入模块"
                            )
                            print(f"  提示: 可能缺少TDengine客户端或环境配置问题")
                            success = False
                        else:
                            print(f"  ⚠️ 跳过连接测试: 未安装 TDengine 驱动")
                            success = False
                    else:
                        # 对于没有安装驱动的数据库，只显示配置信息
                        print(f"  ⚠️ 跳过连接测试: 缺少 {db_name} 驱动")
                        success = False

                    if success:
                        successful_connections += 1

                except Exception as e:
                    print(f"  ❌ 连接失败: {str(e)}")

        except ImportError as e:
            print(f"❌ 导入驱动失败: {str(e)}")
            return False

        print(
            f"\n📊 连接测试结果: {successful_connections}/{len([k for k, v in self.test_results.items() if v])} 个数据库连接成功"
        )
        return successful_connections > 0

    def _test_mysql_monitor_simple(
        self, config: Dict[str, Any], create_engine, text
    ) -> bool:
        """简化版MySQL监控数据库测试"""
        try:
            start_time = time.time()
            engine = create_engine(config["url"], pool_timeout=5)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            response_time = round((time.time() - start_time) * 1000, 2)
            print(f"  ✅ 连接成功 ({response_time}ms)")
            return True
        except Exception as e:
            print(f"  ❌ 连接失败: {str(e)}")
            return False

    def _test_mysql_simple(self, config: Dict[str, Any], pymysql) -> bool:
        """简化版MySQL连接测试"""
        try:
            start_time = time.time()
            conn = pymysql.connect(
                host=config["host"],
                user=config["user"],
                password=config["password"],
                port=config["port"],
                connect_timeout=5,
            )

            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()

            cursor.close()
            conn.close()

            response_time = round((time.time() - start_time) * 1000, 2)
            print(
                f"  ✅ 连接成功 ({response_time}ms), 版本: {version[0] if version else 'Unknown'}"
            )
            return True
        except Exception as e:
            print(f"  ❌ 连接失败: {str(e)}")
            return False

    def _test_redis_simple(self, config: Dict[str, Any], redis_lib) -> bool:
        """简化版Redis连接测试"""
        try:
            start_time = time.time()
            r = redis_lib.Redis(
                host=config["host"],
                port=config["port"],
                password=config["password"] if config["password"] else None,
                db=config["db"],
                socket_timeout=5,
                socket_connect_timeout=5,
            )

            r.ping()
            info = r.info("server")

            response_time = round((time.time() - start_time) * 1000, 2)
            version = info.get("redis_version", "Unknown")
            print(f"  ✅ 连接成功 ({response_time}ms), 版本: {version}")
            return True
        except Exception as e:
            print(f"  ❌ 连接失败: {str(e)}")
            return False

    def _test_tdengine_multi(
        self, config: Dict[str, Any], methods: Dict[str, Any]
    ) -> bool:
        """多种连接方式测试TDengine，只要有一种成功即可"""
        print(
            f"  🔍 检测到 {len(methods)} 种 TDengine 连接方式: {', '.join(methods.keys())}"
        )

        success_count = 0
        total_methods = len(methods)

        # 按优先级测试：WebSocket > REST > 原生
        priority_order = ["WebSocket", "REST", "原生"]
        ordered_methods = []

        # 按优先级排序
        for method in priority_order:
            if method in methods:
                ordered_methods.append((method, methods[method]))

        # 添加其他可能的方式
        for method, module in methods.items():
            if method not in priority_order:
                ordered_methods.append((method, module))

        for method_name, module in ordered_methods:
            print(f"    • 测试 {method_name} 连接...")
            try:
                if method_name == "WebSocket":
                    success = self._test_tdengine_websocket(config, module)
                elif method_name == "REST":
                    success = self._test_tdengine_rest(config, module)
                elif method_name == "原生":
                    success = self._test_tdengine_native(config, module)
                else:
                    print(f"      ⚠️ 未知连接方式: {method_name}")
                    continue

                if success:
                    success_count += 1
                    print(f"      ✅ {method_name} 连接成功")
                else:
                    print(f"      ❌ {method_name} 连接失败")

            except Exception as e:
                print(f"      ❌ {method_name} 连接失败: {str(e)}")

        if success_count > 0:
            print(
                f"  ✅ TDengine 连接成功 ({success_count}/{total_methods} 种方式可用)"
            )
            return True
        else:
            print(f"  ❌ 所有 TDengine 连接方式都失败")
            return False

    def _test_tdengine_websocket(self, config: Dict[str, Any], taosws) -> bool:
        """测试TDengine WebSocket连接"""
        try:
            start_time = time.time()
            dsn = f"ws://{config['user']}:{config['password']}@{config['host']}:{config['port']}"

            conn = taosws.connect(dsn)
            cursor = conn.cursor()
            cursor.execute("SELECT server_version()")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            response_time = round((time.time() - start_time) * 1000, 2)
            version = result[0] if result else "Unknown"
            print(f"        → 版本: {version}, 响应时间: {response_time}ms")
            return True
        except Exception:
            return False

    def _test_tdengine_rest(self, config: Dict[str, Any], taosrest) -> bool:
        """测试TDengine REST连接"""
        try:
            start_time = time.time()

            conn = taosrest.connect(
                url=f"http://{config['host']}:{config['port']}",
                user=config["user"],
                password=config["password"],
                timeout=5,
            )

            cursor = conn.cursor()
            cursor.execute("SELECT server_version()")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            response_time = round((time.time() - start_time) * 1000, 2)
            version = result[0] if result else "Unknown"
            print(f"        → 版本: {version}, 响应时间: {response_time}ms")
            return True
        except Exception:
            return False

    def _test_tdengine_native(self, config: Dict[str, Any], taos) -> bool:
        """测试TDengine原生连接"""
        try:
            start_time = time.time()

            conn = taos.connect(
                host=config["host"],
                user=config["user"],
                password=config["password"],
                port=config["port"],
            )

            cursor = conn.cursor()
            cursor.execute("SELECT server_version()")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            response_time = round((time.time() - start_time) * 1000, 2)
            version = result[0] if result else "Unknown"
            print(f"        → 版本: {version}, 响应时间: {response_time}ms")
            return True
        except Exception:
            return False

    def _print_config_summary(self, successful: int) -> None:
        """打印配置测试总结"""
        print("\n" + "=" * 50)
        print("📊 配置测试总结")
        print("=" * 50)

        total = len(self.test_results)
        print(f"总数据库数量: {total}")
        print(f"配置完整: {successful}")
        print(f"配置缺失: {total - successful}")
        print(f"完整率: {(successful/total*100):.1f}%")

        print("\n详细结果:")
        print("-" * 50)
        print(f"{'数据库':<15} {'状态':<10}")
        print("-" * 50)

        for db_name, result in self.test_results.items():
            status = "✅ 配置完整" if result else "❌ 配置缺失"
            db_type = self.config[db_name]["type"]
            print(f"{db_type:<15} {status:<10}")

    def run_all_tests(self) -> None:
        """运行所有测试"""
        print("\n" + "=" * 60)
        print("🔄 运行所有测试")
        print("=" * 60)

        print("1️⃣ 步骤1: 查找 .env 文件路径")
        path_ok = self.find_env_file()

        if path_ok:
            print("\n2️⃣ 步骤2: 数据库配置完整性测试")
            config_ok = self.test_config_integrity()

            print("\n3️⃣ 步骤3: 数据库驱动检查")
            drivers_ok = self.check_database_drivers()

            if drivers_ok:
                print("\n4️⃣ 步骤4: 数据库连通性测试")
                connectivity_ok = self.test_database_connectivity()

                print("\n" + "=" * 60)
                print("🎯 全部测试完成")
                print("=" * 60)
                print(f"✅ .env文件查找: {'成功' if path_ok else '失败'}")
                print(f"✅ 配置完整性: {'通过' if config_ok else '未通过'}")
                print(f"✅ 驱动安装: {'完整' if drivers_ok else '不完整'}")
                print(f"✅ 连通性测试: {'成功' if connectivity_ok else '失败'}")
            else:
                print("\n⚠️ 由于缺少数据库驱动，跳过连通性测试")
        else:
            print("\n⚠️ 由于未找到 .env 文件，跳过后续测试")


def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("🔧 数据库测试工具")
    print("=" * 60)
    print("请选择要执行的操作:")
    print()
    print("1️⃣  查找 .env 文件路径")
    print("2️⃣  数据库配置完整性测试")
    print("3️⃣  数据库连通性测试（包括驱动检查）")
    print("4️⃣  以上全部")
    print("5️⃣  退出")
    print()
    return input("请输入选项 (1-5): ").strip()


def main():
    """主函数"""
    tool = DatabaseTestTool()

    print("=" * 60)
    print("🎉 欢迎使用数据库测试工具!")
    print("=" * 60)
    print("本工具可以帮您:")
    print("• 查找 .env 配置文件位置")
    print("• 验证数据库配置完整性")
    print("• 检查数据库驱动安装情况")
    print("• 测试数据库连接可用性")

    while True:
        try:
            choice = show_menu()

            if choice == "1":
                tool.find_env_file()
            elif choice == "2":
                tool.test_config_integrity()
            elif choice == "3":
                # 先检查驱动，再测试连通性
                tool.check_database_drivers()
                tool.test_database_connectivity()
            elif choice == "4":
                tool.run_all_tests()
            elif choice == "5":
                print("\n👋 感谢使用！再见!")
                break
            else:
                print("\n❌ 无效选项，请输入 1-5 之间的数字")

            # 等待用户按键继续
            input("\n按 Enter 键继续...")

        except KeyboardInterrupt:
            print("\n\n👋 程序已被用户中断，再见!")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            input("\n按 Enter 键继续...")


if __name__ == "__main__":
    main()
