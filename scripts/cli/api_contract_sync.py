#!/usr/bin/env python3
"""API契约管理CLI工具
提供命令行接口管理API契约版本、差异检测、验证和同步
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import click
import requests
import yaml
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table


# API配置
BACKEND_PORT = os.getenv("BACKEND_PORT", "").strip()
if not BACKEND_PORT:
    raise RuntimeError("Missing BACKEND_PORT in environment")
API_BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{BACKEND_PORT}")
API_PREFIX = "/api/contracts"

console = Console()


def print_success(message: str):
    """打印成功消息"""
    console.print(f"✅ {message}", style="bold green")


def print_error(message: str):
    """打印错误消息"""
    console.print(f"❌ {message}", style="bold red")


def print_warning(message: str):
    """打印警告消息"""
    console.print(f"⚠️  {message}", style="bold yellow")


def print_info(message: str):
    """打印信息消息"""
    console.print(f"ℹ️  {message}", style="bold blue")


def get_csrf_token() -> str:
    """获取CSRF token"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/csrf-token")
        response.raise_for_status()
        data = response.json()
        return data["data"]["csrf_token"]
    except Exception as e:
        print_warning(f"无法获取CSRF token: {e}")
        return ""


def api_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """发送API请求"""
    url = f"{API_BASE_URL}{API_PREFIX}{endpoint}"
    headers = {"Content-Type": "application/json"}

    # 对于需要CSRF保护的请求，获取并添加token
    if method.upper() in ["POST", "PUT", "DELETE", "PATCH"]:
        csrf_token = get_csrf_token()
        if csrf_token:
            headers["X-CSRF-Token"] = csrf_token

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        print_error(f"无法连接到API服务器: {url}")
        print_info("请确保后端服务正在运行")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print_error(f"HTTP错误: {e.response.status_code}")
        try:
            error_data = e.response.json()
            console.print(JSON(error_data))
        except:
            console.print(e.response.text)
        sys.exit(1)
    except Exception as e:
        print_error(f"请求失败: {e!s}")
        sys.exit(1)


def is_success(result: Any) -> bool:
    """判断API请求是否成功"""
    if not isinstance(result, dict):
        return False
    # 支持旧格式 (字符串代码)
    if result.get("code") == "SUCCESS":
        return True
    # 支持新格式 (布尔标志)
    if result.get("success") is True:
        return True
    # 支持 HTTP 状态码作为业务代码
    if result.get("code") in [200, 201]:
        return True
    # 支持未包装的契约响应 (兜底逻辑)
    if "id" in result and "name" in result and "version" in result:
        return True
    return False


def get_data(result: Any) -> Any:
    """提取响应中的业务数据"""
    if not isinstance(result, dict):
        return result
    # 如果有 data 字段且不为 None，则返回 data
    if "data" in result and result["data"] is not None:
        return result["data"]
    # 否则返回整个字典 (针对未包装响应)
    return result


def load_openapi_spec(file_path: str) -> Dict[str, Any]:
    """加载OpenAPI规范文件"""
    path = Path(file_path)

    if not path.exists():
        print_error(f"文件不存在: {file_path}")
        sys.exit(1)

    try:
        with open(path, encoding="utf-8") as f:
            if path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            if path.suffix == ".json":
                return json.load(f)
            print_error(f"不支持的文件格式: {path.suffix}")
            print_info("支持的格式: .yaml, .yml, .json")
            sys.exit(1)
    except Exception as e:
        print_error(f"加载文件失败: {e!s}")
        sys.exit(1)


# ==================== CLI命令 ====================


@click.group()
@click.version_option(version="1.0.0")
@click.option("--api-url", default=API_BASE_URL, help="API服务器地址", envvar="API_CONTRACT_API_URL")
@click.pass_context
def cli(ctx, api_url):
    """API契约管理CLI工具

    管理OpenAPI契约版本、差异检测、验证和同步
    """
    ctx.ensure_object(dict)
    ctx.obj["API_BASE_URL"] = api_url


# ==================== 契约版本管理 ====================


@cli.command("create")
@click.argument("name", required=True)
@click.argument("version", required=True)
@click.option("--spec", "-s", required=True, help="OpenAPI规范文件路径")
@click.option("--commit-hash", "-c", help="Git commit hash")
@click.option("--author", "-a", help="作者或团队名称")
@click.option("--description", "-d", help="版本描述")
@click.option("--tag", "-t", multiple=True, help="版本标签 (可多次使用)")
@click.option("--activate", is_flag=True, help="创建后自动激活")
def create_version(name, version, spec, commit_hash, author, description, tag, activate):
    """创建新的契约版本

    示例:
        api-contract-sync create market-api 1.0.0 -s openapi.yaml -a "team" -d "初始版本"
    """
    print_info(f"创建契约版本: {name} {version}")

    # 加载OpenAPI规范
    spec_data = load_openapi_spec(spec)

    # 构建请求数据
    data = {
        "name": name,
        "version": version,
        "spec": spec_data,
        "commit_hash": commit_hash,
        "author": author,
        "description": description,
        "tags": list(tag),
    }

    # 发送请求
    result = api_request("POST", "/versions", data)

    if is_success(result):
        version_data = get_data(result)
        print_success(f"契约版本创建成功 (ID: {version_data.get('id')})")

        # 显示版本信息
        console.print(
            Panel(
                f"""
契约名称: {version_data.get("name")}
版本号: {version_data.get("version")}
作者: {version_data.get("author", "N/A")}
描述: {version_data.get("description", "N/A")}
激活状态: {"是" if version_data.get("is_active") else "否"}
创建时间: {version_data.get("created_at")}
            """.strip(),
                title="✨ 版本创建成功",
                border_style="green",
            )
        )

        # 自动激活
        if activate and not version_data.get("is_active"):
            print_info("正在激活版本...")
            activate_result = api_request("POST", f"/versions/{version_data.get('id')}/activate")
            if is_success(activate_result):
                print_success("版本已激活")
    else:
        print_error(f"创建失败: {result.get('message')}")
        sys.exit(1)


@cli.command("list")
@click.option("--name", "-n", help="按契约名称过滤")
@click.option("--limit", "-l", default=20, help="每页数量 (默认: 20)")
@click.option("--offset", "-o", default=0, help="偏移量 (默认: 0)")
def list_versions(name, limit, offset):
    """列出契约版本

    示例:
        api-contract-sync list --name market-api --limit 10
    """
    print_info("查询契约版本列表...")

    params = {"limit": limit, "offset": offset}
    if name:
        params["name"] = name

    result = api_request("GET", "/versions", params)

    versions = []
    if isinstance(result, list):
        versions = result
    elif is_success(result):
        versions = get_data(result)
    elif isinstance(result, dict):
        print_error(f"查询失败: {result.get('message')}")
        return

    if not versions:
        print_warning("未找到契约版本")
        return

    # 创建表格
    table = Table(title=f"契约版本列表 ({len(versions)} 条)")
    table.add_column("ID", style="cyan", width=6)
    table.add_column("名称", style="green", width=20)
    table.add_column("版本", style="yellow", width=10)
    table.add_column("作者", style="blue", width=15)
    table.add_column("激活", style="red", width=6)
    table.add_column("创建时间", style="dim", width=20)

    for v in versions:
        table.add_row(
            str(v.get("id")),
            v.get("name"),
            v.get("version"),
            v.get("author", "N/A"),
            "✅" if v.get("is_active") else "❌",
            v.get("created_at", "")[:19],
        )

    console.print(table)


@cli.command("show")
@click.argument("version_id", type=int)
def show_version(version_id):
    """显示契约版本详情

    示例:
        api-contract-sync show 1
    """
    print_info(f"查询契约版本详情 (ID: {version_id})...")

    result = api_request("GET", f"/versions/{version_id}")

    if is_success(result):
        version_data = get_data(result)

        # 显示版本信息
        console.print(
            Panel(
                f"""
契约名称: {version_data.get("name")}
版本号: {version_data.get("version")}
Git Commit: {version_data.get("commit_hash", "N/A")}
作者: {version_data.get("author", "N/A")}
描述: {version_data.get("description", "N/A")}
标签: {", ".join(version_data.get("tags", []))}
激活状态: {"是" if version_data.get("is_active") else "否"}
创建时间: {version_data.get("created_at")}
            """.strip(),
                title=f"📄 契约版本详情 (ID: {version_id})",
                border_style="blue",
            )
        )

        # 询问是否显示OpenAPI规范
        if console.input("\n是否显示OpenAPI规范? [y/N]: ").lower() == "y":
            console.print("\n[bold]OpenAPI规范:[/bold]")
            console.print(JSON(version_data.get("spec", {})))
    else:
        print_error(f"查询失败: {result.get('message')}")


@cli.command("active")
@click.argument("name")
def get_active_version(name):
    """获取契约的当前激活版本

    示例:
        api-contract-sync active market-api
    """
    print_info(f"查询激活版本: {name}")

    result = api_request("GET", f"/versions/{name}/active")

    if is_success(result):
        version_data = get_data(result)

        console.print(
            Panel(
                f"""
契约名称: {version_data.get("name")}
版本号: {version_data.get("version")}
Git Commit: {version_data.get("commit_hash", "N/A")}
作者: {version_data.get("author", "N/A")}
描述: {version_data.get("description", "N/A")}
标签: {", ".join(version_data.get("tags", []))}
创建时间: {version_data.get("created_at")}
            """.strip(),
                title="⭐ 当前激活版本",
                border_style="green",
            )
        )
    else:
        print_error(f"查询失败: {result.get('message')}")


@cli.command("activate")
@click.argument("version_id", type=int)
def activate_version(version_id):
    """激活指定契约版本

    示例:
        api-contract-sync activate 2
    """
    print_info(f"激活契约版本 (ID: {version_id})...")

    result = api_request("POST", f"/versions/{version_id}/activate")

    if is_success(result):
        print_success("版本已激活")
    else:
        print_error(f"激活失败: {result.get('message')}")


@cli.command("delete")
@click.argument("version_id", type=int)
@click.option("--force", "-f", is_flag=True, help="强制删除 (跳过确认)")
def delete_version(version_id, force):
    """删除契约版本

    示例:
        api-contract-sync delete 1 --force
    """
    # 确认删除
    if not force:
        console.print(f"[yellow]即将删除契约版本 (ID: {version_id})[/yellow]")
        console.print("[red]此操作不可逆！[/red]")
        confirm = console.input("\n确认删除? [y/N]: ")
        if confirm.lower() != "y":
            print_info("已取消删除")
            return

    print_info(f"删除契约版本 (ID: {version_id})...")

    result = api_request("DELETE", f"/versions/{version_id}")

    if is_success(result):
        print_success("版本已删除")
    else:
        print_error(f"删除失败: {result.get('message')}")


# ==================== 契约列表 ====================


@cli.command("contracts")
def list_contracts():
    """列出所有契约及其元数据

    示例:
        api-contract-sync contracts
    """
    print_info("查询契约列表...")

    result = api_request("GET", "/contracts")

    if is_success(result):
        data = get_data(result)
        contracts = data.get("contracts", [])

        if not contracts:
            print_warning("未找到契约")
            return

        # 创建表格
        table = Table(title=f"契约列表 ({data.get('total', 0)} 个)")
        table.add_column("契约名称", style="cyan", width=25)
        table.add_column("激活版本", style="green", width=12)
        table.add_column("版本总数", style="yellow", width=10)
        table.add_column("最后更新", style="blue", width=20)
        table.add_column("标签", style="dim", width=20)

        for c in contracts:
            table.add_row(
                c.get("name"),
                c.get("active_version", "N/A"),
                str(c.get("total_versions", 0)),
                c.get("last_updated", "")[:19],
                ", ".join(c.get("tags", [])),
            )

        console.print(table)
    else:
        print_error(f"查询失败: {result.get('message')}")


# ==================== 差异检测 ====================


@cli.command("diff")
@click.argument("from_version", type=int)
@click.argument("to_version", type=int)
@click.option("--json-output", "-j", is_flag=True, help="以JSON格式输出")
def compare_versions(from_version, to_version, json_output):
    """对比两个契约版本的差异

    示例:
        api-contract-sync diff 1 2
    """
    print_info(f"对比契约版本: {from_version} → {to_version}")

    data = {
        "from_version_id": from_version,
        "to_version_id": to_version,
    }

    result = api_request("POST", "/diff", data)

    if is_success(result):
        diff_data = get_data(result)

        if json_output:
            console.print(JSON(diff_data))
            return

        # 显示差异摘要
        console.print(
            Panel(
                f"""
源版本: {diff_data.get("from_version")}
目标版本: {diff_data.get("to_version")}
总变更数: {diff_data.get("total_changes")}
破坏性变更: [red]{diff_data.get("breaking_changes")}[/red]
非破坏性变更: [green]{diff_data.get("non_breaking_changes")}[/green]

摘要: {diff_data.get("summary")}
            """.strip(),
                title="📊 差异检测结果",
                border_style="yellow",
            )
        )

        # 显示详细差异
        diffs = diff_data.get("diffs", [])
        if diffs:
            console.print(f"\n[bold]详细差异 ({len(diffs)} 条):[/bold]")

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("类型", style="red", width=12)
            table.add_column("变更", style="yellow", width=10)
            table.add_column("路径", style="cyan", width=40)
            table.add_column("说明", width=50)

            for d in diffs:
                type_style = "red" if d.get("type") == "breaking" else "green"
                table.add_row(
                    f"[{type_style}]{d.get('type')}[/{type_style}]",
                    d.get("change"),
                    d.get("path"),
                    d.get("message"),
                )

            console.print(table)

            # 如果有破坏性变更，显示警告
            if diff_data.get("breaking_changes", 0) > 0:
                console.print("\n[red bold]⚠️  检测到破坏性变更，请谨慎评估影响！[/red bold]")
    else:
        print_error(f"对比失败: {result.get('message')}")


# ==================== 契约验证 ====================


@cli.command("validate")
@click.argument("spec_file", required=True)
@click.option("--check-breaking", "-b", is_flag=True, help="检查破坏性变更")
@click.option("--compare-to", "-c", type=int, help="对比的版本ID")
def validate_contract(spec_file, check_breaking, compare_to):
    """验证OpenAPI规范

    示例:
        api-contract-sync validate openapi.yaml --check-breaking --compare-to 1
    """
    print_info(f"验证OpenAPI规范: {spec_file}")

    # 加载OpenAPI规范
    spec_data = load_openapi_spec(spec_file)

    # 构建请求数据
    data = {
        "spec": spec_data,
        "check_breaking_changes": check_breaking,
        "compare_to_version_id": compare_to,
    }

    # 发送请求
    result = api_request("POST", "/validate", data)

    if is_success(result):
        validation_data = get_data(result)

        # 显示验证结果
        is_valid = validation_data.get("is_valid")
        errors = validation_data.get("errors", 0)
        warnings = validation_data.get("warnings", 0)

        if is_valid:
            console.print(
                Panel(
                    f"✅ 验证通过\n错误: {errors}\n警告: {warnings}",
                    title="✨ 验证成功",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"❌ 验证失败\n错误: {errors}\n警告: {warnings}",
                    title="❌ 验证失败",
                    border_style="red",
                )
            )

        # 显示详细验证结果
        validation_results = validation_data.get("validation_results", [])
        if validation_results:
            console.print(f"\n[bold]验证结果 ({len(validation_results)} 条):[/bold]")

            for vr in validation_results:
                level = vr.get("level")
                level_style = {
                    "error": "red",
                    "warning": "yellow",
                    "info": "blue",
                }.get(level, "white")

                console.print(f"\n[{level_style}]{level.upper()}[/{level_style}] [{vr.get('category')}]")
                console.print(f"  路径: {vr.get('path')}")
                console.print(f"  说明: {vr.get('message')}")

        # 显示破坏性变更
        breaking_changes = validation_data.get("breaking_changes", [])
        if breaking_changes:
            console.print(f"\n[red bold]⚠️  破坏性变更 ({len(breaking_changes)} 条):[/red bold]")
            for bc in breaking_changes:
                console.print(f"  • {bc.get('path')}: {bc.get('message')}")
    else:
        print_error(f"验证失败: {result.get('message')}")


# ==================== 契约同步 ====================


@cli.command("sync")
@click.argument("name", required=True)
@click.option("--source", "-s", required=True, help="源文件路径")
@click.option(
    "--direction", "-d", type=click.Choice(["code-to-db", "db-to-code"]), default="code-to-db", help="同步方向"
)
@click.option("--version", "-v", help="指定版本号")
@click.option("--commit", is_flag=True, help="提交到Git")
def sync_contract(name, source, direction, version, commit):
    """同步契约

    示例:
        api-contract-sync sync market-api -s openapi.yaml -d code-to-db -v 1.2.0
    """
    print_info(f"同步契约: {name} ({direction})")

    # 构建请求数据
    data = {
        "name": name,
        "source_path": source,
        "direction": direction,
        "version": version,
        "commit": commit,
    }

    # 发送请求
    result = api_request("POST", "/sync", data)

    if is_success(result):
        sync_data = get_data(result)

        console.print(
            Panel(
                f"""
同步ID: {sync_data.get("sync_id")}
状态: {sync_data.get("status")}
开始时间: {sync_data.get("started_at")}
完成时间: {sync_data.get("completed_at")}
            """.strip(),
                title="✅ 同步完成",
                border_style="green",
            )
        )

        # 显示详细结果
        results = sync_data.get("results", [])
        if results:
            console.print(f"\n[bold]同步结果 ({len(results)} 条):[/bold]")
            for r in results:
                status_style = "green" if r.get("success") else "red"
                console.print(f"  [{status_style}]✓[/{status_style}] {r.get('file')}: {r.get('action')}")
    else:
        print_error(f"同步失败: {result.get('message')}")


# ==================== 导入/导出 ====================


@cli.command("export")
@click.argument("version_id", type=int)
@click.option("--output", "-o", required=True, help="输出文件路径")
@click.option("--format", "-f", type=click.Choice(["yaml", "json"]), default="yaml", help="输出格式")
def export_version(version_id, output, format):
    """导出契约版本到文件

    示例:
        api-contract-sync export 1 -o openapi.yaml -f yaml
    """
    print_info(f"导出契约版本 (ID: {version_id})...")

    # 获取版本详情
    result = api_request("GET", f"/versions/{version_id}")

    if not is_success(result):
        print_error(f"获取版本失败: {result.get('message')}")
        return

    version_data = result.get("data", {})
    spec = version_data.get("spec", {})

    # 导出文件
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            if format == "yaml":
                yaml.dump(spec, f, allow_unicode=True, sort_keys=False)
            else:
                json.dump(spec, f, indent=2, ensure_ascii=False)

        print_success(f"契约已导出到: {output}")
    except Exception as e:
        print_error(f"导出失败: {e!s}")


@cli.command("import")
@click.argument("name", required=True)
@click.argument("version", required=True)
@click.option("--file", "-f", required=True, help="导入文件路径")
@click.option("--activate", is_flag=True, help="导入后自动激活")
def import_version(name, version, file, activate):
    """从文件导入契约版本

    示例:
        api-contract-sync import market-api 1.0.0 -f openapi.yaml --activate
    """
    print_info(f"导入契约版本: {name} {version}")

    # 加载文件
    spec_data = load_openapi_spec(file)

    # 创建版本
    data = {
        "name": name,
        "version": version,
        "spec": spec_data,
    }

    result = api_request("POST", "/versions", data)

    if is_success(result):
        version_data = get_data(result)
        print_success(f"契约版本导入成功 (ID: {version_data.get('id')})")

        if activate:
            print_info("正在激活版本...")
            activate_result = api_request("POST", f"/versions/{version_data.get('id')}/activate")
            if is_success(activate_result):
                print_success("版本已激活")
    else:
        print_error(f"导入失败: {result.get('message')}")


if __name__ == "__main__":
    # 设置API URL
    api_url_from_env = None
    # if hasattr(sys, '_argv'):  # 检查是否在测试环境
    #     api_url_from_env = os.environ.get("API_CONTRACT_API_URL")

    cli(obj={})
