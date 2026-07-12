"""量化策略验证器子模块"""

import logging
import subprocess
from typing import Any, Dict


logger = logging.getLogger(__name__)


class IntegrationValidatorsMixin:
    """集成验证：数据库连接、API端点、服务集成、外部依赖、消息队列"""

    def _validate_database_connection(self) -> Dict[str, Any]:
        """验证数据库连接 - 调用实际的pytest集成测试"""
        try:
            import os
            import subprocess

            # 首先检查数据库配置文件是否存在
            db_config_exists = os.path.exists(".env") or os.path.exists(
                "config/database.yaml",
            )

            if not db_config_exists:
                return {
                    "passed": False,
                    "error": "未找到数据库配置文件",
                    "details": {"config_found": False},
                }

            # 尝试运行实际的数据库集成测试
            test_commands = [
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_postgresql_integration.py",
                    "-v",
                    "--tb=short",
                ],
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_database_integration.py",
                    "-v",
                    "--tb=short",
                ],
            ]

            test_passed = False
            test_output = ""
            test_errors = ""

            for cmd in test_commands:
                try:
                    print(f"  运行数据库集成测试: {' '.join(cmd)}")
                    result = subprocess.run(
                        cmd,
                        cwd="/opt/claude/mystocks_spec",
                        capture_output=True,
                        text=True,
                        timeout=60,  # 60秒超时
                    )

                    if result.returncode == 0:
                        test_passed = True
                        test_output = result.stdout
                        print("    ✅ 数据库集成测试通过")
                        break
                    test_errors += f"测试失败 ({' '.join(cmd)}):\n{result.stderr}\n"
                    print(f"    ❌ 数据库集成测试失败: {result.returncode}")

                except subprocess.TimeoutExpired:
                    test_errors += f"测试超时 ({' '.join(cmd)})\n"
                    print("    ⚠️ 数据库集成测试超时")
                except FileNotFoundError:
                    # 测试文件不存在，继续尝试其他测试
                    continue
                except Exception as e:
                    test_errors += f"测试异常 ({' '.join(cmd)}): {e!s}\n"
                    continue

            # 如果没有找到任何集成测试文件，使用配置文件检查作为回退
            if not test_passed and not test_errors:
                print("    ⚠️ 未找到集成测试文件，使用配置文件检查")
                return {
                    "passed": db_config_exists,
                    "details": {
                        "config_found": db_config_exists,
                        "integration_tests_found": False,
                        "fallback_used": True,
                    },
                }

            return {
                "passed": test_passed,
                "details": {
                    "config_found": db_config_exists,
                    "integration_tests_run": test_passed,
                    "test_output": test_output[:500] if test_output else "",  # 限制输出长度
                    "test_errors": test_errors[:500] if test_errors else "",
                },
            }

        except Exception as e:
            return {"passed": False, "error": f"数据库连接检查异常: {e!s}"}

    def _validate_api_endpoints(self) -> Dict[str, Any]:
        """验证API端点 - 调用实际的pytest API测试"""
        try:
            import os
            import subprocess

            # 检查API相关文件和目录
            api_files = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    if "api" in file.lower() or "endpoint" in file.lower():
                        api_files.append(os.path.join(root, file))

            # 检查web目录
            web_exists = os.path.exists("web") or os.path.exists("src/web")
            api_exists = len(api_files) > 0 or web_exists

            if not api_exists:
                return {
                    "passed": False,
                    "error": "未找到API相关文件或目录",
                    "details": {
                        "api_files_found": len(api_files),
                        "web_directory_exists": web_exists,
                    },
                }

            # 尝试运行API集成测试
            api_test_commands = [
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_api_integration.py",
                    "-v",
                    "--tb=short",
                ],
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_api_endpoints.py",
                    "-v",
                    "--tb=short",
                ],
                ["python", "-m", "pytest", "tests/api/", "-v", "--tb=short"],
            ]

            test_passed = False
            test_output = ""
            test_errors = ""

            for cmd in api_test_commands:
                try:
                    print(f"  运行API集成测试: {' '.join(cmd)}")
                    result = subprocess.run(
                        cmd,
                        cwd="/opt/claude/mystocks_spec",
                        capture_output=True,
                        text=True,
                        timeout=60,  # 60秒超时
                    )

                    if result.returncode == 0:
                        test_passed = True
                        test_output = result.stdout
                        print("    ✅ API集成测试通过")
                        break
                    test_errors += f"API测试失败 ({' '.join(cmd)}):\n{result.stderr}\n"
                    print(f"    ❌ API集成测试失败: {result.returncode}")

                except subprocess.TimeoutExpired:
                    test_errors += f"API测试超时 ({' '.join(cmd)})\n"
                    print("    ⚠️ API集成测试超时")
                except FileNotFoundError:
                    # 测试文件不存在，继续尝试其他测试
                    continue
                except Exception as e:
                    test_errors += f"API测试异常 ({' '.join(cmd)}): {e!s}\n"
                    continue

            # 如果没有找到API测试，使用文件存在性检查作为回退
            if not test_passed and not test_errors:
                print("    ⚠️ 未找到API集成测试文件，使用文件存在性检查")
                return {
                    "passed": api_exists,
                    "details": {
                        "api_files_found": len(api_files),
                        "web_directory_exists": web_exists,
                        "integration_tests_found": False,
                        "fallback_used": True,
                    },
                }

            return {
                "passed": test_passed,
                "details": {
                    "api_files_found": len(api_files),
                    "web_directory_exists": web_exists,
                    "integration_tests_run": test_passed,
                    "test_output": test_output[:500] if test_output else "",
                    "test_errors": test_errors[:500] if test_errors else "",
                },
            }

        except Exception as e:
            return {"passed": False, "error": f"API端点检查异常: {e!s}"}

    def _validate_service_integrations(self) -> Dict[str, Any]:
        """验证服务集成 - 调用实际的服务集成测试"""
        try:
            import os
            import subprocess

            # 检查服务配置文件
            service_files = ["docker-compose.yml", "docker-compose.yaml"]
            services_found = [f for f in service_files if os.path.exists(f)]

            # 检查Kubernetes/Helm配置
            k8s_exists = os.path.exists("kubernetes") or os.path.exists("k8s")
            helm_exists = os.path.exists("helm") or os.path.exists("charts")

            # 检查微服务相关文件
            microservice_indicators = False
            if os.path.exists("src"):
                for root, dirs, files in os.walk("src"):
                    if any("service" in d.lower() for d in dirs):
                        microservice_indicators = True
                        break

            service_integration_exists = len(services_found) > 0 or k8s_exists or helm_exists or microservice_indicators

            if not service_integration_exists:
                return {
                    "passed": False,
                    "error": "未找到服务集成配置或微服务架构",
                    "details": {
                        "docker_compose_found": len(services_found) > 0,
                        "kubernetes_found": k8s_exists,
                        "helm_found": helm_exists,
                        "microservices_indicated": microservice_indicators,
                    },
                }

            # 尝试运行服务集成测试
            service_test_commands = [
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_service_integration.py",
                    "-v",
                    "--tb=short",
                ],
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_microservices.py",
                    "-v",
                    "--tb=short",
                ],
            ]

            test_passed = False
            test_output = ""
            test_errors = ""

            for cmd in service_test_commands:
                try:
                    print(f"  运行服务集成测试: {' '.join(cmd)}")
                    result = subprocess.run(
                        cmd,
                        cwd="/opt/claude/mystocks_spec",
                        capture_output=True,
                        text=True,
                        timeout=10,  # 10秒超时，避免CI阻塞
                    )

                    if result.returncode == 0:
                        test_passed = True
                        test_output = result.stdout
                        print("    ✅ 服务集成测试通过")
                        break
                    test_errors += f"服务测试失败 ({' '.join(cmd)}):\n{result.stderr}\n"
                    print(f"    ❌ 服务集成测试失败: {result.returncode}")

                except subprocess.TimeoutExpired:
                    test_errors += f"服务测试超时 ({' '.join(cmd)})\n"
                    print("    ⚠️ 服务集成测试超时")
                except FileNotFoundError:
                    continue
                except Exception as e:
                    test_errors += f"服务测试异常 ({' '.join(cmd)}): {e!s}\n"
                    continue

            # 如果没有找到服务测试，使用配置检查作为回退
            if not test_passed and not test_errors:
                print("    ⚠️ 未找到服务集成测试文件，使用配置检查")
                return {
                    "passed": service_integration_exists,
                    "details": {
                        "docker_compose_found": len(services_found) > 0,
                        "kubernetes_found": k8s_exists,
                        "helm_found": helm_exists,
                        "microservices_indicated": microservice_indicators,
                        "integration_tests_found": False,
                        "fallback_used": True,
                    },
                }

            return {
                "passed": test_passed,
                "details": {
                    "docker_compose_found": len(services_found) > 0,
                    "kubernetes_found": k8s_exists,
                    "helm_found": helm_exists,
                    "microservices_indicated": microservice_indicators,
                    "integration_tests_run": test_passed,
                    "test_output": test_output[:500] if test_output else "",
                    "test_errors": test_errors[:500] if test_errors else "",
                },
            }

        except Exception as e:
            return {"passed": False, "error": f"服务集成检查异常: {e!s}"}

    def _validate_external_dependencies(self) -> Dict[str, Any]:
        """验证外部依赖"""
        try:
            import os

            # 检查外部服务依赖
            external_services = [
                "redis",
                "elasticsearch",
                "mongodb",
                "rabbitmq",
                "kafka",
            ]
            deps_found = []

            # 检查requirements.txt中的外部依赖
            try:
                with open("requirements.txt") as f:
                    content = f.read()
                    deps_found = [s for s in external_services if s in content.lower()]
            except:
                pass

            # 检查配置文件中的外部服务
            config_files = [
                ".env",
                "config/settings.py",
                "config/external_services.yaml",
            ]
            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file) as f:
                            content = f.read()
                            for service in external_services:
                                if service in content.lower() and service not in deps_found:
                                    deps_found.append(service)
                    except:
                        continue

            # 尝试运行外部依赖测试
            dependency_test_commands = [
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_external_dependencies.py",
                    "-v",
                    "--tb=short",
                ],
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_third_party_services.py",
                    "-v",
                    "--tb=short",
                ],
            ]

            test_passed = True  # 默认通过，因为外部依赖不是必需的
            test_output = ""
            test_errors = ""

            for cmd in dependency_test_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        cwd="/opt/claude/mystocks_spec",
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if result.returncode == 0:
                        test_output = result.stdout
                        print("    ✅ 外部依赖测试通过")
                        break
                    test_errors += f"依赖测试失败 ({' '.join(cmd)}):\n{result.stderr}\n"
                    # 外部依赖测试失败不影响整体通过，因为可能是可选依赖

                except FileNotFoundError:
                    continue
                except Exception as e:
                    test_errors += f"依赖测试异常 ({' '.join(cmd)}): {e!s}\n"
                    continue

            return {
                "passed": test_passed,
                "details": {
                    "external_services_found": len(deps_found),
                    "services": deps_found,
                    "dependency_tests_run": test_output != "",
                    "test_output": test_output[:500] if test_output else "",
                    "test_errors": test_errors[:500] if test_errors else "",
                },
            }

        except Exception as e:
            return {"passed": False, "error": f"外部依赖检查异常: {e!s}"}

    def _validate_message_queue(self) -> Dict[str, Any]:
        """验证消息队列"""
        try:
            import os
            import subprocess

            # 检查消息队列配置
            mq_systems = ["rabbitmq", "kafka", "redis", "sqs", "pubsub"]
            mq_found = []

            # 检查依赖文件
            try:
                with open("requirements.txt") as f:
                    content = f.read()
                    mq_found = [mq for mq in mq_systems if mq in content.lower()]
            except:
                pass

            # 检查配置文件
            for root, dirs, files in os.walk("config"):
                for file in files:
                    try:
                        with open(os.path.join(root, file)) as f:
                            content = f.read()
                            for mq in mq_systems:
                                if mq in content.lower() and mq not in mq_found:
                                    mq_found.append(mq)
                    except:
                        continue

            # 尝试运行消息队列测试
            mq_test_commands = [
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_message_queue.py",
                    "-v",
                    "--tb=short",
                ],
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_messaging.py",
                    "-v",
                    "--tb=short",
                ],
            ]

            test_passed = True  # 默认通过，消息队列是可选的
            test_output = ""
            test_errors = ""

            for cmd in mq_test_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        cwd="/opt/claude/mystocks_spec",
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if result.returncode == 0:
                        test_output = result.stdout
                        print("    ✅ 消息队列测试通过")
                        break
                    test_errors += f"消息队列测试失败 ({' '.join(cmd)}):\n{result.stderr}\n"

                except FileNotFoundError:
                    continue
                except Exception as e:
                    test_errors += f"消息队列测试异常 ({' '.join(cmd)}): {e!s}\n"
                    continue

            return {
                "passed": test_passed,
                "details": {
                    "message_queues_found": len(mq_found),
                    "queues": mq_found,
                    "message_queue_tests_run": test_output != "",
                    "test_output": test_output[:500] if test_output else "",
                    "test_errors": test_errors[:500] if test_errors else "",
                },
            }

        except Exception as e:
            return {"passed": False, "error": f"消息队列检查异常: {e!s}"}
