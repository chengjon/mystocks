#!/usr/bin/env python3
"""
API快速查询工具
用于快速查找和显示API端点信息
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict


def load_index():
    """加载索引文件"""
    index_file = Path("docs/reports/api_split/api_index.json")
    if not index_file.exists():
        print("❌ 错误: 索引文件不存在")
        print("   请先运行: python scripts/split_api_inventory.py")
        return None

    with open(index_file, "r", encoding="utf-8") as f:
        return json.load(f)


def search_by_path(path_pattern: str, index_data: dict):
    """按路径搜索API"""
    results = []

    for file_info in index_data["split_files"]:
        split_file = Path("docs/reports/api_split") / file_info["file"]
        try:
            with open(split_file, "r", encoding="utf-8") as f:
                split_data = json.load(f)
                for ep in split_data["endpoints"]:
                    if path_pattern.lower() in ep["path"].lower():
                        results.append(ep)
        except Exception as e:
            print(f"⚠️  读取文件失败 {split_file}: {e}")

    return results


def search_by_method(method: str, index_data: dict):
    """按HTTP方法搜索API"""
    results = []

    for file_info in index_data["split_files"]:
        split_file = Path("docs/reports/api_split") / file_info["file"]
        try:
            with open(split_file, "r", encoding="utf-8") as f:
                split_data = json.load(f)
                for ep in split_data["endpoints"]:
                    if ep["method"].upper() == method.upper():
                        results.append(ep)
        except Exception as e:
            print(f"⚠️  读取文件失败 {split_file}: {e}")

    return results


def search_by_file(filename: str, index_data: dict):
    """按后端文件名搜索API"""
    results = []

    for file_info in index_data["split_files"]:
        split_file = Path("docs/reports/api_split") / file_info["file"]
        try:
            with open(split_file, "r", encoding="utf-8") as f:
                split_data = json.load(f)
                for ep in split_data["endpoints"]:
                    if filename.lower() in ep["file"].lower():
                        results.append(ep)
        except Exception as e:
            print(f"⚠️  读取文件失败 {split_file}: {e}")

    return results


def search_by_function(function_name: str, index_data: dict):
    """按函数名搜索API"""
    results = []

    for file_info in index_data["split_files"]:
        split_file = Path("docs/reports/api_split") / file_info["file"]
        try:
            with open(split_file, "r", encoding="utf-8") as f:
                split_data = json.load(f)
                for ep in split_data["endpoints"]:
                    if function_name.lower() in ep["function"].lower():
                        results.append(ep)
        except Exception as e:
            print(f"⚠️  读取文件失败 {split_file}: {e}")

    return results


def display_results(results: list, verbose: bool = False):
    """显示搜索结果"""
    if not results:
        print("❌ 未找到匹配的API")
        return

    print(f"✅ 找到 {len(results)} 个API端点\n")

    for i, ep in enumerate(results, 1):
        print(f"{i}. {ep['method']} {ep['path']}")
        print(f"   文件: {ep['file']}")
        print(f"   函数: {ep['function']}")
        print(f"   返回: {ep['return_model']}")
        print(f"   数据源: {ep['source_type']}")

        if verbose:
            print(f"   行号: {ep['line_number']}")
            if ep["data_fields"]:
                print(f"   字段: {', '.join(ep['data_fields'][:5])}")
            if ep["db_dependencies"]:
                print(f"   数据库: {', '.join(ep['db_dependencies'])}")
        print()


def show_summary(index_data: dict):
    """显示概览统计"""
    print("📊 API端点统计\n")
    print(f"总API端点数: {index_data['total_endpoints']}")
    print(f"拆分文件数: {len(index_data['split_files'])}\n")

    # 统计HTTP方法
    method_count = defaultdict(int)
    source_count = defaultdict(int)

    for file_info in index_data["split_files"]:
        split_file = Path("docs/reports/api_split") / file_info["file"]
        try:
            with open(split_file, "r", encoding="utf-8") as f:
                split_data = json.load(f)
                for ep in split_data["endpoints"]:
                    method_count[ep["method"]] += 1
                    source_count[ep["source_type"]] += 1
        except:
            pass

    print("按HTTP方法分布:")
    for method, count in sorted(method_count.items()):
        percentage = count / index_data["total_endpoints"] * 100
        print(f"  {method:6s}: {count:3d} ({percentage:5.1f}%)")

    print("\n按数据源分布:")
    for source, count in sorted(source_count.items()):
        percentage = count / index_data["total_endpoints"] * 100
        print(f"  {source:12s}: {count:3d} ({percentage:5.1f}%)")


def list_prefixes(index_data: dict):
    """列出所有路径前缀"""
    print("📁 所有API路径前缀\n")

    print(f"{'前缀':<30} {'文件名':<30} {'端点数'}")
    print("-" * 70)

    for file_info in index_data["split_files"]:
        print(f"{file_info['prefix']:<30} {file_info['file']:<30} {file_info['count']}")


def main():
    parser = argparse.ArgumentParser(description="API快速查询工具")
    parser.add_argument("--path", "-p", help="按路径搜索（如: /stocks, /auth）")
    parser.add_argument("--method", "-m", help="按HTTP方法搜索（GET/POST/PUT/DELETE）")
    parser.add_argument("--file", "-f", help="按后端文件名搜索（如: data.py, auth.py）")
    parser.add_argument("--function", "-u", help="按函数名搜索")
    parser.add_argument("--summary", "-s", action="store_true", help="显示统计概览")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有路径前缀")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")

    args = parser.parse_args()

    # 加载索引
    index_data = load_index()
    if not index_data:
        return

    # 处理命令
    if args.summary:
        show_summary(index_data)
    elif args.list:
        list_prefixes(index_data)
    elif args.path:
        results = search_by_path(args.path, index_data)
        display_results(results, args.verbose)
    elif args.method:
        results = search_by_method(args.method, index_data)
        display_results(results, args.verbose)
    elif args.file:
        results = search_by_file(args.file, index_data)
        display_results(results, args.verbose)
    elif args.function:
        results = search_by_function(args.function, index_data)
        display_results(results, args.verbose)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
