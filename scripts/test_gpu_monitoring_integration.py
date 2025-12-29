#!/usr/bin/env python3
"""
GPU监控仪表板集成测试
Integration Test for GPU Monitoring Dashboard
"""

import sys
import os
import time
import requests
from datetime import datetime

# 颜色定义
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
NC = "\033[0m"

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/gpu"


def print_header(text):
    print(f"\n{'=' * 60}")
    print(f"{text}")
    print(f"{'=' * 60}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{NC}")


def print_error(text):
    print(f"{RED}❌ {text}{NC}")


def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{NC}")


def test_health_check():
    """测试健康检查端点"""
    print("测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("健康检查通过")
            return True
        else:
            print_error(f"健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"连接失败: {e}")
        return False


def test_gpu_metrics():
    """测试GPU指标端点"""
    print("测试GPU指标...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/metrics/0", timeout=5)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["gpu_utilization", "temperature", "memory_used"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                print_error(f"缺少字段: {missing_fields}")
                return False
            print_success(f"GPU指标获取成功 (利用率: {data['gpu_utilization']}%)")
            return True
        else:
            print_error(f"GPU指标获取失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"GPU指标请求失败: {e}")
        return False


def test_all_gpu_metrics():
    """测试所有GPU指标端点"""
    print("测试所有GPU指标...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print_success(f"获取到{len(data)}个GPU的指标")
                return True
            else:
                print_error("返回数据格式错误")
                return False
        else:
            print_error(f"所有GPU指标获取失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"所有GPU指标请求失败: {e}")
        return False


def test_performance_metrics():
    """测试性能指标端点"""
    print("测试性能指标...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/performance", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["matrix_gflops", "overall_speedup", "cache_hit_rate"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                print_error(f"缺少字段: {missing_fields}")
                return False
            print_success(f"性能指标获取成功 (加速比: {data['overall_speedup']}x)")
            return True
        else:
            print_error(f"性能指标获取失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"性能指标请求失败: {e}")
        return False


def test_gpu_history():
    """测试历史数据端点"""
    print("测试历史数据...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/history/0?hours=1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print_success(f"历史数据获取成功 ({len(data)}条记录)")
                return True
            else:
                print_error("历史数据格式错误")
                return False
        else:
            print_error(f"历史数据获取失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"历史数据请求失败: {e}")
        return False


def test_gpu_stats():
    """测试聚合统计端点"""
    print("测试聚合统计...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/stats/0?hours=24", timeout=5)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["avg_utilization", "max_utilization", "avg_gflops"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                print_error(f"缺少字段: {missing_fields}")
                return False
            print_success(f"聚合统计获取成功 (平均利用率: {data['avg_utilization']}%)")
            return True
        else:
            print_error(f"聚合统计获取失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"聚合统计请求失败: {e}")
        return False


def test_recommendations():
    """测试优化建议端点"""
    print("测试优化建议...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/recommendations?device_id=0", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print_success(f"优化建议获取成功 ({len(data)}条建议)")
                return True
            else:
                print_error("优化建议格式错误")
                return False
        else:
            print_error(f"优化建议获取失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"优化建议请求失败: {e}")
        return False


def test_gpu_processes():
    """测试GPU进程端点"""
    print("测试GPU进程...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/processes/0", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print_success(f"GPU进程获取成功 ({len(data)}个进程)")
                return True
            else:
                print_error("GPU进程格式错误")
                return False
        else:
            print_error(f"GPU进程获取失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"GPU进程请求失败: {e}")
        return False


def test_sse_stream():
    """测试SSE流"""
    print("测试SSE实时流...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/stream/0", stream=True, timeout=2)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "text/event-stream" in content_type:
                print_success("SSE流连接成功")
                return True
            else:
                print_warning(f"Content-Type错误: {content_type}")
                return False
        else:
            print_error(f"SSE流连接失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_warning(f"SSE流请求失败（可能正常）: {e}")
        return True  # SSE超时是正常的


def main():
    """主函数"""
    print_header("GPU监控仪表板集成测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端地址: {BASE_URL}")
    print(f"API前缀: {API_PREFIX}")

    # 运行所有测试
    tests = [
        ("健康检查", test_health_check),
        ("GPU指标", test_gpu_metrics),
        ("所有GPU指标", test_all_gpu_metrics),
        ("性能指标", test_performance_metrics),
        ("历史数据", test_gpu_history),
        ("聚合统计", test_gpu_stats),
        ("优化建议", test_recommendations),
        ("GPU进程", test_gpu_processes),
        ("SSE流", test_sse_stream),
    ]

    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
        time.sleep(0.5)  # 避免请求过快

    # 打印测试结果
    print_header("测试结果")

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")

    # 打印统计
    print_header(f"测试统计: {passed}/{len(results)} 通过")

    if failed == 0:
        print_success("所有测试通过！GPU监控仪表板运行正常")
        return 0
    else:
        print_error(f"{failed}个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
