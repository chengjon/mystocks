#!/usr/bin/env python3
"""
WSL2 GPU环境初始化脚本
解决RAPIDS在WSL2环境下的GPU访问问题
"""

import os
import sys


def initialize_wsl2_gpu():
    """初始化WSL2 GPU环境"""

    print("=" * 70)
    print("WSL2 GPU��境初始化")
    print("=" * 70)

    # 1. 检查CUDA是否可用
    print("\n1. 检查CUDA环境...")
    try:
        import cupy as cp
        device_count = cp.cuda.runtime.getDeviceCount()
        print(f"   ✓ 检测到 {device_count} 个CUDA设备")

        device_props = cp.cuda.runtime.getDeviceProperties(0)
        print(f"   ✓ GPU: {device_props['name'].decode()}")
        print(f"   ✓ 显存: {device_props['totalGlobalMem'] / 1024**3:.2f} GB")
    except Exception as e:
        print(f"   ✗ CUDA检测失败: {e}")
        return False

    # 2. 初始化RMM
    print("\n2. 初始化RAPIDS Memory Manager...")
    try:
        import rmm

        # 关键：在WSL2下需要显式初始化RMM
        rmm.reinitialize(
            pool_allocator=False,  # 不使用内存池，更稳定
            devices=0,              # 使用GPU 0
            managed_memory=False    # 不使用统一内存
        )
        print("   ✓ RMM初始化成功")

    except Exception as e:
        print(f"   ✗ RMM初始化失败: {e}")
        return False

    # 3. 测试cuDF
    print("\n3. 测试cuDF...")
    try:
        import cudf

        # 创建测试DataFrame
        df = cudf.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        result = df['a'].sum()

        print(f"   ✓ cuDF工作正常")
        print(f"   ✓ 测试计算: sum([1,2,3]) = {result}")

    except Exception as e:
        print(f"   ✗ cuDF测试失败: {e}")
        return False

    # 4. 测试cuML
    print("\n4. 测试cuML...")
    try:
        import cuml
        import numpy as np

        # 简单的KMeans测试
        from cuml.cluster import KMeans

        X = cudf.DataFrame({
            'x': [1.0, 2.0, 3.0, 8.0, 9.0, 10.0],
            'y': [1.0, 2.0, 3.0, 8.0, 9.0, 10.0]
        })

        kmeans = KMeans(n_clusters=2, random_state=0)
        kmeans.fit(X)

        print(f"   ✓ cuML工作正常")
        print(f"   ✓ KMeans聚类完成")

    except Exception as e:
        print(f"   ✗ cuML测试失败: {e}")
        return False

    # 5. 性能测试
    print("\n5. GPU性能测试...")
    try:
        import time

        # CPU vs GPU性能对比
        n = 1000000

        # CPU
        import pandas as pd
        cpu_data = pd.DataFrame({'x': range(n)})
        start = time.time()
        cpu_result = cpu_data['x'].sum()
        cpu_time = time.time() - start

        # GPU
        gpu_data = cudf.DataFrame({'x': range(n)})
        start = time.time()
        gpu_result = gpu_data['x'].sum()
        gpu_time = time.time() - start

        speedup = cpu_time / gpu_time

        print(f"   ✓ 数据量: {n:,} 行")
        print(f"   ✓ CPU时间: {cpu_time:.4f}秒")
        print(f"   ✓ GPU时间: {gpu_time:.4f}秒")
        print(f"   ✓ 加速比: {speedup:.2f}x")

    except Exception as e:
        print(f"   ⚠ 性能测试失败: {e}")

    print("\n" + "=" * 70)
    print("✅ WSL2 GPU环境初始化成功！")
    print("=" * 70)

    return True


def setup_environment_variables():
    """设置必要的环境变量"""

    env_vars = {
        'CUDA_VISIBLE_DEVICES': '0',
        'CUDF_SPILL': '1',
        'CUDF_SPILL_ON_DEMAND': '1',
        'RAPIDS_NO_INITIALIZE': '0',
    }

    print("\n设置环境变量:")
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  {key}={value}")


if __name__ == '__main__':
    print("开始WSL2 GPU环境配置...\n")

    # 设置环境变量
    setup_environment_variables()

    # 初始化GPU
    success = initialize_wsl2_gpu()

    if success:
        print("\n下一步:")
        print("  1. 在Python代码开始处导入此模块:")
        print("     from wsl2_gpu_init import initialize_wsl2_gpu")
        print("     initialize_wsl2_gpu()")
        print()
        print("  2. 或者在测试前运行:")
        print("     python wsl2_gpu_init.py")
        sys.exit(0)
    else:
        print("\n❌ GPU初始化失败，请检查错误信息")
        sys.exit(1)
