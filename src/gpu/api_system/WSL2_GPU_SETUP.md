# WSL2 GPU Setup Guide

## 概述

本指南说明如何在 WSL2 环境下配置和使用 NVIDIA GPU 加速，专门针对 RAPIDS (cuDF/cuML) 库的特殊初始化需求。

## 问题背景

在 WSL2 环境下，虽然 `nvidia-smi` 可以正常检测到 GPU，但 RAPIDS 库 (cuDF/cuML) 可能无法访问 GPU，出现以下错误：

```
rmm._cuda.gpu.CUDARuntimeError: cudaErrorNoDevice: no CUDA-capable device is detected
```

**根本原因**: RAPIDS Memory Manager (RMM) 在 WSL2 环境下不会自动初始化，需要显式配置。

## 解决方案

### 方案 1: 使用初始化脚本 (推荐)

项目提供了 `wsl2_gpu_init.py` 脚本，可自动检测并初始化 WSL2 GPU 环境。

#### 直接运行测试初始化

```bash
python wsl2_gpu_init.py
```

**预期输出**:
```
======================================================================
WSL2 GPU环境初始化
======================================================================

1. 检查CUDA环境...
   ✓ 检测到 1 个CUDA设备
   ✓ GPU: NVIDIA GeForce RTX 2080
   ✓ 显存: 8.00 GB

2. 初始化RAPIDS Memory Manager...
   ✓ RMM初始化成功

3. 测试cuDF...
   ✓ cuDF工作正常
   ✓ 测试计算: sum([1,2,3]) = 6

4. 测试cuML...
   ✓ cuML工作正常
   ✓ KMeans聚类完成

5. GPU性能测试...
   ✓ 数据量: 1,000,000 行
   ✓ CPU时间: 0.0008秒
   ✓ GPU时间: 0.0022秒
   ✓ 加速比: 0.34x

======================================================================
✅ WSL2 GPU环境初始化成功！
======================================================================
```

#### 在代码中使用

在你的 Python 代码开头添加:

```python
# 方式 1: 在 WSL2 环境下自动初始化
import platform
if 'microsoft' in platform.uname().release.lower():
    from wsl2_gpu_init import initialize_wsl2_gpu
    initialize_wsl2_gpu()

# 现在可以安全使用 cuDF/cuML
import cudf
import cuml
```

或简化为:

```python
# 方式 2: 直接调用
from wsl2_gpu_init import initialize_wsl2_gpu
initialize_wsl2_gpu()

import cudf
import cuml
```

### 方案 2: 手动初始化 RMM

如果你想在自己的代码中手动初始化，使用以下代码:

```python
import rmm

# 关键配置：针对 WSL2 环境
rmm.reinitialize(
    pool_allocator=False,  # 不使用内存池，更稳定
    devices=0,              # 使用 GPU 0
    managed_memory=False    # 不使用统一内存
)

# 现在可以使用 cuDF/cuML
import cudf
df = cudf.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
print(df['a'].sum())  # 应该输出 6
```

## 环境变量配置

`wsl2_gpu_init.py` 会自动设置以下环境变量:

```bash
export CUDA_VISIBLE_DEVICES=0
export CUDF_SPILL=1
export CUDF_SPILL_ON_DEMAND=1
export RAPIDS_NO_INITIALIZE=0
```

你也可以在 shell 配置文件 (如 `~/.bashrc`) 中手动添加这些变量。

## pytest 集成

项目的 pytest 配置 (`tests/conftest.py`) 已经自动集成了 WSL2 GPU 初始化:

```python
@pytest.fixture(scope="session")
def gpu_available():
    """检查GPU是否可用，并在WSL2环境下初始化GPU"""
    try:
        # 检测WSL2环境并初始化GPU
        import platform
        if 'microsoft' in platform.uname().release.lower():
            from wsl2_gpu_init import initialize_wsl2_gpu
            initialize_wsl2_gpu()

        import cudf
        import cuml
        df = cudf.DataFrame({'a': [1, 2, 3]})
        return True
    except Exception as e:
        print(f"GPU initialization failed: {e}")
        return False
```

这意味着你可以直接运行 GPU 测试，无需额外配置:

```bash
# 运行真实 GPU 测试
python tests/test_real_gpu.py

# 或使用 pytest 标记
pytest -m gpu -v tests/
```

## 真实 GPU 测试结果

项目包含完整的真实 GPU 性能测试 (`tests/test_real_gpu.py`):

| 测试项 | 状态 | 性能表现 |
|--------|------|----------|
| DataFrame操作 | ✅ | 1.5x 加速 |
| ML训练 (RandomForest) | ✅ | **44.76x 加速** |
| GPU内存使用 | ✅ | 成功分配 38MB |
| 回测性能 | ✅ | 0.84x (小数据集开销) |

### 运行完整测试

```bash
# 运行所有真实 GPU 测试
python tests/test_real_gpu.py

# 预期输出示例
4 passed in 45.80s

# 关键测试结果
真实GPU ML训练测试结果:
  样本数: 100,000
  特征数: 20
  CPU训练时间: 41.2247秒
  GPU训练时间: 0.9209秒
  加速比: 44.76x  ✅
```

## 验证 GPU 访问

### 方法 1: 检查 NVIDIA 驱动

```bash
nvidia-smi
```

应显示 GPU 信息 (例如: NVIDIA GeForce RTX 2080, 8GB)

### 方法 2: 测试 CUDA

```bash
python -c "import cupy as cp; print(cp.cuda.Device(0).compute_capability)"
```

应输出 GPU 的 compute capability (例如: `(7, 5)` 表示 Compute Capability 7.5)

### 方法 3: 测试 cuDF

```bash
python wsl2_gpu_init.py
```

检查所有 5 个测试步骤是否通过。

### 方法 4: 完整性能测试

```bash
python tests/test_real_gpu.py
```

应显示 `4 passed`，包括 ML 训练的 40x+ 加速比。

## 故障排查

### 问题 1: `nvidia-smi` 正常但 cuDF 报错 "no CUDA-capable device"

**解决方案**: 使用 `wsl2_gpu_init.py` 显式初始化 RMM

```bash
python wsl2_gpu_init.py
```

如果初始化成功，将该脚本集成到你的代码中。

### 问题 2: `ModuleNotFoundError: No module named 'cudf'`

**解决方案**: 安装 RAPIDS

```bash
conda install -c rapidsai -c conda-forge -c nvidia \
    cudf=24.12 cuml=24.12 python=3.12 cudatoolkit=12.0
```

### 问题 3: 性能加速比不明显

**原因**: 小数据集下 GPU 初始化开销大于计算收益

**建议**:
- 增加数据集规模 (推荐 100,000+ 行)
- 使用批处理提高 GPU 利用率
- 参考 `tests/test_real_gpu.py` 中的性能测试用例

### 问题 4: 测试时 GPU 内存不足

**解决方案**: 减小测试数据规模或清理 GPU 内存

```python
import cupy as cp
cp.get_default_memory_pool().free_all_blocks()
```

## 技术细节

### RMM 配置参数说明

```python
rmm.reinitialize(
    pool_allocator=False,  # False: 直接分配，更稳定；True: 使用内存池，更快但可能不稳定
    devices=0,              # GPU 设备 ID (0 表示第一个 GPU)
    managed_memory=False    # False: 禁用统一内存；True: 启用 (WSL2 下可能不稳定)
)
```

### WSL2 特性

- WSL2 使用虚拟化技术访问 GPU，与原生 Linux 有细微差异
- 需�� Windows 11 或 Windows 10 版本 21H2 以上
- 需要安装 NVIDIA Game Ready 或 Studio 驱动 (版本 ≥ 510.60.02)

## 参考资源

- [NVIDIA CUDA on WSL User Guide](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)
- [RAPIDS Installation Guide](https://docs.rapids.ai/install)
- [RMM Documentation](https://github.com/rapidsai/rmm)
- 项目文件:
  - `wsl2_gpu_init.py` - WSL2 GPU 初始化脚本
  - `tests/test_real_gpu.py` - 真实 GPU 性能测试
  - `tests/conftest.py` - pytest GPU fixtures

## 总结

✅ WSL2 环境下 GPU 加速已完全解决并验证
✅ 提供自动化初始化脚本 (`wsl2_gpu_init.py`)
✅ pytest 测试框架已集成 WSL2 支持
✅ 真实性能测试显示 ML 训练可达 **44.76x 加速比**
✅ 所有测试用例 (4/4) 100% 通过

---

**维护者**: MyStocks Development Team
**最后更新**: 2025-11-04
**文档版本**: v1.0
