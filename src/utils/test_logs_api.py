#!/usr/bin/env python3
"""
测试系统运行日志API端点
验证日志查询和筛选功能
"""

import requests
from datetime import datetime

# Backend API基础URL
BASE_URL = "http://localhost:8000"


def print_separator():
    """打印分隔线"""
    print("\n" + "=" * 80 + "\n")


def test_get_all_logs():
    """测试1: 获取所有日志"""
    print("测试1: 获取所有日志")
    print("-" * 80)

    url = f"{BASE_URL}/api/system/logs"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态码: {response.status_code}")
            print(f"✅ 成功: {data.get('success')}")
            print(f"✅ 总日志数: {data.get('total')}")
            print(f"✅ 返回日志数: {data.get('filtered')}")
            print("\n前3条日志:")
            for log in data.get("data", [])[:3]:
                print(f"  - [{log['level']}] {log['timestamp']}: {log['message']}")
            return True
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败: 无法连接到 {BASE_URL}")
        print("   请确保Backend服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def test_filter_errors_only():
    """测试2: 只获取有问题的日志"""
    print("测试2: 只获取有问题的日志 (filter_errors=true)")
    print("-" * 80)

    url = f"{BASE_URL}/api/system/logs?filter_errors=true"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态码: {response.status_code}")
            print(f"✅ 成功: {data.get('success')}")
            print(f"✅ 总日志数: {data.get('total')}")
            print(f"✅ 问题日志数: {data.get('filtered')}")

            # 验证所有日志都是WARNING/ERROR/CRITICAL级别
            error_logs = data.get("data", [])
            all_errors = all(log["level"] in ["WARNING", "ERROR", "CRITICAL"] for log in error_logs)

            if all_errors:
                print("✅ 验证通过: 所有日志都是问题日志")
            else:
                print("⚠️  警告: 存在非问题日志")

            print("\n问题日志详情:")
            for log in error_logs[:5]:
                print(f"  - [{log['level']}] {log['category']}: {log['message']}")

            return all_errors
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def test_filter_by_level():
    """测试3: 按日志级别筛选"""
    print("测试3: 按日志级别筛选 (level=ERROR)")
    print("-" * 80)

    url = f"{BASE_URL}/api/system/logs?level=ERROR"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态码: {response.status_code}")
            print(f"✅ ERROR级别日志数: {data.get('filtered')}")

            error_logs = data.get("data", [])
            all_error_level = all(log["level"] == "ERROR" for log in error_logs)

            if all_error_level:
                print("✅ 验证通过: 所有日志都是ERROR级别")
            else:
                print("⚠️  警告: 存在其他级别日志")

            for log in error_logs[:3]:
                print(f"  - [{log['level']}] {log['message']}")

            return all_error_level
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def test_filter_by_category():
    """测试4: 按分类筛选"""
    print("测试4: 按分类筛选 (category=database)")
    print("-" * 80)

    url = f"{BASE_URL}/api/system/logs?category=database"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态码: {response.status_code}")
            print(f"✅ database分类日志数: {data.get('filtered')}")

            db_logs = data.get("data", [])
            all_database = all(log["category"] == "database" for log in db_logs)

            if all_database:
                print("✅ 验证通过: 所有日志都是database分类")
            else:
                print("⚠️  警告: 存在其他分类日志")

            for log in db_logs[:3]:
                print(f"  - [{log['category']}] {log['message']}")

            return all_database
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def test_pagination():
    """测试5: 分页功能"""
    print("测试5: 分页功能 (limit=5, offset=0)")
    print("-" * 80)

    url = f"{BASE_URL}/api/system/logs?limit=5&offset=0"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态码: {response.status_code}")
            print(f"✅ 总数: {data.get('total')}")
            print(f"✅ 返回数: {data.get('filtered')}")

            logs = data.get("data", [])
            if len(logs) <= 5:
                print("✅ 验证通过: 返回日志数 <= limit (5)")
            else:
                print("❌ 验证失败: 返回日志数 > limit")

            return len(logs) <= 5
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def test_logs_summary():
    """测试6: 日志统计摘要"""
    print("测试6: 日志统计摘要")
    print("-" * 80)

    url = f"{BASE_URL}/api/system/logs/summary"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})

            print(f"✅ 状态码: {response.status_code}")
            print(f"✅ 成功: {result.get('success')}")
            print("\n日志统计:")
            print(f"  - 总日志数: {data.get('total_logs')}")
            print(f"  - 最近错误数: {data.get('recent_errors_1h')}")
            print("\n各级别统计:")
            level_counts = data.get("level_counts", {})
            for level, count in level_counts.items():
                print(f"  - {level}: {count}")
            print("\n各分类统计:")
            category_counts = data.get("category_counts", {})
            for category, count in category_counts.items():
                print(f"  - {category}: {count}")

            return True
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("系统运行日志API测试")
    print("=" * 80)
    print(f"Backend URL: {BASE_URL}")
    print(f"测试时间: {datetime.now().isoformat()}")
    print("=" * 80)

    # 运行所有测试
    tests = [
        ("获取所有日志", test_get_all_logs),
        ("筛选问题日志", test_filter_errors_only),
        ("按级别筛选", test_filter_by_level),
        ("按分类筛选", test_filter_by_category),
        ("分页功能", test_pagination),
        ("日志统计摘要", test_logs_summary),
    ]

    results = []
    for test_name, test_func in tests:
        print_separator()
        result = test_func()
        results.append((test_name, result))
        print_separator()

    # 打印测试总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")

    print("-" * 80)
    print(f"总计: {passed}/{total} 通过 ({passed / total * 100:.1f}%)")
    print("=" * 80)

    # API使用示例
    print("\nAPI使用示例:")
    print("-" * 80)
    print("1. 获取所有日志:")
    print(f"   GET {BASE_URL}/api/system/logs")
    print("\n2. 只获取有问题的日志:")
    print(f"   GET {BASE_URL}/api/system/logs?filter_errors=true")
    print("\n3. 按级别筛选:")
    print(f"   GET {BASE_URL}/api/system/logs?level=ERROR")
    print("\n4. 按分类筛选:")
    print(f"   GET {BASE_URL}/api/system/logs?category=database")
    print("\n5. 分页查询:")
    print(f"   GET {BASE_URL}/api/system/logs?limit=10&offset=0")
    print("\n6. 日志统计:")
    print(f"   GET {BASE_URL}/api/system/logs/summary")
    print("=" * 80)

    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
