#!/usr/bin/env python3
"""
MyStocks API 自动导入到 Apifox
使用 Apifox Open API 将项目的 OpenAPI 文档导入到 Apifox 平台
"""

import json
import sys
from pathlib import Path
import requests
import os

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ApifoxImporter:
    """Apifox 导入器"""

    def __init__(self, access_token: str, project_id: str = None):
        """
        初始化导入器

        Args:
            access_token: Apifox API 访问令牌
            project_id: Apifox 项目 ID（可选，稍后设置）
        """
        self.access_token = access_token
        self.project_id = project_id
        self.base_url = "https://api.apifox.com"
        self.api_version = "2024-03-28"

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Apifox-Api-Version": self.api_version,
            "Content-Type": "application/json",
        }

    def list_projects(self):
        """列出所有可访问的项目"""
        url = f"{self.base_url}/v1/projects"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            projects = data.get("data", {}).get("items", [])

            print(f"\n📋 找到 {len(projects)} 个项目:")
            print("-" * 80)

            for idx, project in enumerate(projects, 1):
                print(f"{idx}. {project['name']}")
                print(f"   ID: {project['id']}")
                print(f"   描述: {project.get('description', '无')}")
                print(f"   成员数: {project.get('memberCount', 0)}")
                print()

            return projects

        except requests.exceptions.RequestException as e:
            print(f"❌ 获取项目列表失败: {e}")
            if hasattr(e.response, "text"):
                print(f"   错误详情: {e.response.text}")
            return []

    def create_project(self, name: str, description: str = ""):
        """
        创建新项目

        Args:
            name: 项目名称
            description: 项目描述

        Returns:
            创建的项目ID
        """
        url = f"{self.base_url}/v1/projects"

        payload = {"name": name, "description": description}

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            data = response.json()
            project_id = data["data"]["id"]

            print("✅ 项目创建成功!")
            print(f"   项目名称: {name}")
            print(f"   项目ID: {project_id}")

            return project_id

        except requests.exceptions.RequestException as e:
            print(f"❌ 创建项目失败: {e}")
            if hasattr(e.response, "text"):
                print(f"   错误详情: {e.response.text}")
            return None

    def import_openapi_from_file(self, openapi_file: str, options: dict = None):
        """
        从文件导入 OpenAPI 文档

        Args:
            openapi_file: OpenAPI 文件路径
            options: 导入选项

        Returns:
            导入结果统计
        """
        if not self.project_id:
            print("❌ 错误: 未设置项目ID")
            return None

        # 读取 OpenAPI 文件
        try:
            with open(openapi_file, "r", encoding="utf-8") as f:
                openapi_content = f.read()
        except Exception as e:
            print(f"❌ 读取 OpenAPI 文件失败: {e}")
            return None

        # 默认导入选项
        default_options = {
            "endpointOverwriteBehavior": "AUTO_MERGE",  # 自动合并
            "schemaOverwriteBehavior": "AUTO_MERGE",  # 自动合并
            "updateFolderOfChangedEndpoint": True,  # 更新目录
            "prependBasePath": False,  # 不添加基础路径前缀
        }

        if options:
            default_options.update(options)

        # 构建请求
        url = f"{self.base_url}/v1/projects/{self.project_id}/import-openapi"

        payload = {"input": openapi_content, "options": default_options}

        print("\n🚀 开始导入 OpenAPI 文档到 Apifox...")
        print(f"   项目ID: {self.project_id}")
        print(f"   文件: {openapi_file}")
        print("   导入策略: 智能合并")
        print()

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            result = response.json()
            counters = result["data"]["counters"]

            print("✅ 导入完成!")
            print("\n📊 导入统计:")
            print("-" * 80)
            print("   接口:")
            print(f"      新增: {counters['endpointCreated']}")
            print(f"      更新: {counters['endpointUpdated']}")
            print(f"      失败: {counters['endpointFailed']}")
            print(f"      忽略: {counters['endpointIgnored']}")
            print()
            print("   数据模型:")
            print(f"      新增: {counters['schemaCreated']}")
            print(f"      更新: {counters['schemaUpdated']}")
            print(f"      失败: {counters['schemaFailed']}")
            print(f"      忽略: {counters['schemaIgnored']}")
            print()
            print("   接口目录:")
            print(f"      新增: {counters['endpointFolderCreated']}")
            print(f"      更新: {counters['endpointFolderUpdated']}")
            print()
            print("   模型目录:")
            print(f"      新增: {counters['schemaFolderCreated']}")
            print(f"      更新: {counters['schemaFolderUpdated']}")
            print("-" * 80)

            # 检查错误
            errors = result["data"].get("errors", [])
            if errors:
                print("\n⚠️  导入过程中出现错误:")
                for error in errors:
                    print(f"   - {error['message']} (代码: {error['code']})")

            return counters

        except requests.exceptions.RequestException as e:
            print(f"❌ 导入失败: {e}")
            if hasattr(e.response, "text"):
                print(f"   错误详情: {e.response.text}")
            return None

    def import_openapi_from_url(self, openapi_url: str, options: dict = None):
        """
        从 URL 导入 OpenAPI 文档

        Args:
            openapi_url: OpenAPI 文档的 URL
            options: 导入选项

        Returns:
            导入结果统计
        """
        if not self.project_id:
            print("❌ 错误: 未设置项目ID")
            return None

        # 默认导入选项
        default_options = {
            "endpointOverwriteBehavior": "AUTO_MERGE",
            "schemaOverwriteBehavior": "AUTO_MERGE",
            "updateFolderOfChangedEndpoint": True,
            "prependBasePath": False,
        }

        if options:
            default_options.update(options)

        # 构建请求
        url = f"{self.base_url}/v1/projects/{self.project_id}/import-openapi"

        payload = {"input": {"url": openapi_url}, "options": default_options}

        print("\n🚀 开始从 URL 导入 OpenAPI 文档到 Apifox...")
        print(f"   项目ID: {self.project_id}")
        print(f"   URL: {openapi_url}")
        print("   导入策略: 智能合并")
        print()

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            result = response.json()
            counters = result["data"]["counters"]

            print("✅ 导入完成!")
            print("\n📊 导入统计:")
            print("-" * 80)
            print(
                f"   接口: 新增 {counters['endpointCreated']}, "
                f"更新 {counters['endpointUpdated']}, "
                f"失败 {counters['endpointFailed']}"
            )
            print(
                f"   数据模型: 新增 {counters['schemaCreated']}, "
                f"更新 {counters['schemaUpdated']}, "
                f"失败 {counters['schemaFailed']}"
            )
            print("-" * 80)

            # 检查错误
            errors = result["data"].get("errors", [])
            if errors:
                print("\n⚠️  导入过程中出现错误:")
                for error in errors:
                    print(f"   - {error['message']} (代码: {error['code']})")

            return counters

        except requests.exceptions.RequestException as e:
            print(f"❌ 导入失败: {e}")
            if hasattr(e.response, "text"):
                print(f"   错误详情: {e.response.text}")
            return None


def main():
    """主函数"""

    print("=" * 80)
    print("MyStocks API 导入 Apifox 工具")
    print("=" * 80)
    print()

    # 配置
    ACCESS_TOKEN = "APS-kN74RMte5panv5lPUjutEmulUiZEvyRh"
    PROJECT_ID = "7376246"  # MyStocks API 项目ID
    OPENAPI_FILE = project_root / "docs" / "api" / "openapi.json"
    backend_port = os.getenv("BACKEND_PORT", "8020")

    # 验证文件存在
    if not OPENAPI_FILE.exists():
        print(f"❌ OpenAPI 文件不存在: {OPENAPI_FILE}")
        print("   请先生成 OpenAPI 文档或启动后端服务:")
        print(f"   curl http://localhost:{backend_port}/openapi.json > {OPENAPI_FILE}")
        sys.exit(1)

    # 创建导入器
    importer = ApifoxImporter(ACCESS_TOKEN, PROJECT_ID)

    # 步骤1: 使用已知项目ID
    print("步骤 1/3: 配置 Apifox 项目")
    print(f"   项目ID: {PROJECT_ID}")
    print(f"   Access Token: {ACCESS_TOKEN[:20]}...")
    print("   ✅ 配置完成")

    # 步骤2: 导入 OpenAPI 文档
    print("\n步骤 2/3: 导入 OpenAPI 文档")

    # 读取文件信息
    with open(OPENAPI_FILE, "r", encoding="utf-8") as f:
        openapi_data = json.load(f)

    api_count = len(openapi_data.get("paths", {}))
    print(f"   OpenAPI 版本: {openapi_data.get('openapi')}")
    print(f"   API 版本: {openapi_data['info']['version']}")
    print(f"   API 端点数: {api_count}")

    counters = importer.import_openapi_from_file(str(OPENAPI_FILE))

    if not counters:
        print("❌ 导入失败，退出")
        sys.exit(1)

    # 步骤3: 显示结果
    print("\n步骤 3/3: 完成")
    print("=" * 80)
    print("✅ MyStocks API 已成功导入到 Apifox!")
    print()
    print("🔗 访问您的 Apifox 项目:")
    print(f"   https://app.apifox.com/project/{importer.project_id}")
    print()
    print("📚 下一步操作:")
    print("   1. 在 Apifox 中配置环境变量（开发/生产环境）")
    print("   2. 配置认证信息（JWT Token）")
    print("   3. 测试核心 API 端点")
    print("   4. 创建自动化测试用例")
    print()
    print("📖 详细文档: docs/api/APIFOX_IMPORT_GUIDE.md")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
