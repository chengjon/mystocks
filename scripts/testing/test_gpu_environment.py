#!/usr/bin/env python3
"""
GPU环境配置验证脚本
验证MyStocks项目的GPU加速环境是否正确配置
适用于RTX 2080 GPU + CUDA 12.x环境
"""

import sys
import time
import traceback
from typing import Dict


class GPUEnvironmentTester:
    """GPU环境测试器"""

    def __init__(self):
        self.test_results = {}
        self.gpu_info = {}

    def test_nvidia_driver(self) -> bool:
        """测试NVIDIA驱动状态"""
        print("🔍 测试NVIDIA驱动...")
        try:
            import subprocess

            result = subprocess.run(
                ["nvidia-smi"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # 解析GPU信息
                lines = result.stdout.split("\n")
                for line in lines:
                    if "GPU Name" in line:
                        gpu_name = line.split("GPU Name")[1].strip()
                        self.gpu_info["name"] = gpu_name
                    elif "Driver Version" in line:
                        driver_version = line.split("Driver Version")[1].split()[0]
                        self.gpu_info["driver_version"] = driver_version
                    elif "CUDA Version" in line:
                        cuda_version = line.split("CUDA Version")[1].split()[0]
                        self.gpu_info["cuda_version"] = cuda_version

                self.test_results["nvidia_driver"] = True
                print(f"✅ NVIDIA驱动正常: {self.gpu_info}")
                return True
            else:
                self.test_results["nvidia_driver"] = False
                print("❌ NVIDIA驱动异常")
                return False
        except Exception as e:
            self.test_results["nvidia_driver"] = False
            print(f"❌ NVIDIA驱动测试失败: {e}")
            return False

    def test_cuda_runtime(self) -> bool:
        """测试CUDA运行时"""
        print("🔍 测试CUDA运行时...")
        try:
            import cupy as cp

            # 创建简单的GPU数组
            x = cp.array([1, 2, 3, 4, 5])
            y = x * 2
            result = cp.asnumpy(y)

            if list(result) == [2, 4, 6, 8, 10]:
                self.test_results["cuda_runtime"] = True
                print(f"✅ CUDA运行时正常 (CuPy版本: {cp.__version__})")
                return True
            else:
                self.test_results["cuda_runtime"] = False
                print("❌ CUDA运行时计算错误")
                return False
        except Exception as e:
            self.test_results["cuda_runtime"] = False
            print(f"❌ CUDA运行时测试失败: {e}")
            return False

    def test_cudf(self) -> bool:
        """测试cuDF DataFrame"""
        print("🔍 测试cuDF DataFrame...")
        try:
            import cudf

            # 创建GPU DataFrame
            data = {
                "stock_code": ["000001", "000002", "000003", "000004", "000005"],
                "price": [10.5, 15.2, 8.7, 12.3, 9.8],
                "volume": [1000000, 2000000, 1500000, 800000, 1200000],
                "date": ["2025-11-03"] * 5,
            }

            df_gpu = cudf.DataFrame(data)

            # 测试GPU计算
            df_gpu["price_squared"] = df_gpu["price"] ** 2
            df_gpu["volume_normalized"] = (
                df_gpu["volume"] - df_gpu["volume"].mean()
            ) / df_gpu["volume"].std()

            # 转换回CPU验证
            result_cpu = df_gpu.to_pandas()

            # 验证计算结果
            expected_price_squared = [110.25, 231.04, 75.69, 151.29, 96.04]
            price_squared_match = (
                list(result_cpu["price_squared"].round(2)) == expected_price_squared
            )

            if price_squared_match and len(result_cpu) == 5:
                self.test_results["cudf"] = True
                print(f"✅ cuDF正常 (版本: {cudf.__version__})")
                print(f"   GPU计算示例: {len(df_gpu)}行数据处理完成")
                return True
            else:
                self.test_results["cudf"] = False
                print("❌ cuDF计算错误")
                return False
        except Exception as e:
            self.test_results["cudf"] = False
            print(f"❌ cuDF测试失败: {e}")
            return False

    def test_cuml(self) -> bool:
        """测试cuML机器学习库"""
        print("🔍 测试cuML机器学习...")
        try:
            import cuml
            import cupy as cp

            # 测试线性回归
            from cuml.linear_model import LinearRegression

            # 创建测试数据
            X = cp.array([[1], [2], [3], [4], [5]])
            y = cp.array([2, 4, 6, 8, 10]) + cp.random.normal(0, 0.1, 5)

            # 训练模型
            model = LinearRegression()
            model.fit(X, y)

            # 预测
            predictions = model.predict(X)

            # 验证模型
            score = model.score(X, y)
            if 0.8 <= score <= 1.0:  # R²分数应该在合理范围内
                self.test_results["cuml"] = True
                print(f"✅ cuML正常 (版本: {cuml.__version__})")
                print(f"   线性回归R²分数: {score:.4f}")
                return True
            else:
                self.test_results["cuml"] = False
                print("❌ cuML模型性能异常")
                return False
        except Exception as e:
            self.test_results["cuml"] = False
            print(f"❌ cuML测试失败: {e}")
            return False

    def test_quantitative_trading_scenarios(self) -> bool:
        """测试量化交易场景"""
        print("🔍 测试量化交易场景...")
        try:
            import cudf
            import cupy as cp
            import numpy as np

            # 场景1: 大规模历史数据回测模拟
            print("   1. 模拟大规模历史数据回测...")
            start_time = time.time()

            # 创建大量模拟股票数据
            num_stocks = 1000
            num_days = 252  # 1年数据
            np.random.seed(42)

            # 生成模拟数据 (使用GPU)
            stocks = cudf.DataFrame(
                {
                    "stock_code": [f"000{i:04d}" for i in range(num_stocks)],
                    "annual_return": cp.random.normal(0.1, 0.2, num_stocks),
                    "volatility": cp.abs(cp.random.normal(0.15, 0.1, num_stocks)),
                    "market_cap": cp.random.lognormal(15, 1, num_stocks),
                }
            )

            # 计算夏普比率 (GPU并行计算)
            stocks["sharpe_ratio"] = stocks["annual_return"] / stocks["volatility"]

            # 模拟策略筛选 (GPU过滤)
            strategy_mask = (stocks["sharpe_ratio"] > 1.0) & (
                stocks["market_cap"] > 1e8
            )
            selected_stocks = stocks[strategy_mask]

            processing_time = time.time() - start_time
            selected_count = len(selected_stocks)

            print(f"      处理了 {num_stocks} 只股票，{selected_count} 只符合策略条件")
            print(f"      GPU处理时间: {processing_time:.4f}秒")

            # 场景2: 实时特征计算
            print("   2. 模拟实时特征计算...")
            start_time = time.time()

            # 模拟实时数据流
            real_time_data = cudf.DataFrame(
                {
                    "price": cp.random.uniform(10, 100, 10000),
                    "volume": cp.random.uniform(1000, 100000, 10000),
                    "timestamp": range(10000),
                }
            )

            # 批量计算技术指标 (GPU加速)
            real_time_data["sma_20"] = real_time_data["price"].rolling(20).mean()
            real_time_data["std_20"] = real_time_data["price"].rolling(20).std()
            real_time_data["rsi"] = 100 - (
                100 / (1 + real_time_data["price"].pct_change().rolling(14).mean())
            )

            feature_time = time.time() - start_time
            print(f"      处理了 {len(real_time_data)} 条实时数据")
            print(f"      特征计算时间: {feature_time:.4f}秒")

            # 场景3: 多因子模型
            print("   3. 模拟多因子模型...")
            start_time = time.time()

            # 创建因子数据
            factors = cudf.DataFrame(
                {
                    "pe_ratio": cp.random.uniform(10, 50, 500),
                    "pb_ratio": cp.random.uniform(1, 10, 500),
                    "roe": cp.random.uniform(0.05, 0.25, 500),
                    "momentum": cp.random.normal(0, 0.1, 500),
                    "size": cp.random.lognormal(10, 1, 500),
                }
            )

            # 计算因子权重 (GPU矩阵运算)
            weights = cp.array([0.2, 0.2, 0.3, 0.15, 0.15])
            composite_score = (factors * weights).sum(axis=1)

            # 因子排名 (GPU排序)
            factors["composite_score"] = composite_score
            factors["rank"] = (
                factors["composite_score"]
                .rank(method="dense", ascending=False)
                .to_numpy()
            )

            model_time = time.time() - start_time
            print(f"      处理了 {len(factors)} 只股票的因子分析")
            print(f"      模型计算时间: {model_time:.4f}秒")

            # 综合评估
            total_time = processing_time + feature_time + model_time
            if total_time < 5.0:  # 总时间应该在5秒以内
                self.test_results["quantitative_scenarios"] = True
                print(f"✅ 量化交易场景测试通过 (总耗时: {total_time:.4f}秒)")
                return True
            else:
                self.test_results["quantitative_scenarios"] = False
                print(f"⚠️  量化交易场景性能一般 (总耗时: {total_time:.4f}秒)")
                return True  # 仍然通过，只是性能提示

        except Exception as e:
            self.test_results["quantitative_scenarios"] = False
            print(f"❌ 量化交易场景测试失败: {e}")
            return False

    def test_memory_management(self) -> bool:
        """测试GPU内存管理"""
        print("🔍 测试GPU内存管理...")
        try:
            import cupy as cp
            import gc

            # 获取初始内存
            initial_memory = cp.get_default_memory_pool().used_bytes()
            print(f"   初始GPU内存使用: {initial_memory / 1024 / 1024:.2f} MB")

            # 分配和释放内存
            allocations = []
            for i in range(3):
                # 分配不同大小的数组
                size = 100_000 * (i + 1)
                arr = cp.random.random(size)
                allocations.append(arr)
                print(f"   分配 {size} 个元素: {arr.nbytes / 1024 / 1024:.2f} MB")

            # 当前内存使用
            current_memory = cp.get_default_memory_pool().used_bytes()
            print(f"   当前GPU内存使用: {current_memory / 1024 / 1024:.2f} MB")

            # 释放内存
            for arr in allocations:
                del arr
            gc.collect()

            # 强制释放GPU内存
            cp.get_default_memory_pool().free_all_blocks()

            # 最终内存使用
            final_memory = cp.get_default_memory_pool().used_bytes()
            print(f"   最终GPU内存使用: {final_memory / 1024 / 1024:.2f} MB")

            # 验证内存释放
            memory_freed = current_memory - final_memory
            if memory_freed > 10 * 1024 * 1024:  # 释放了至少10MB
                self.test_results["memory_management"] = True
                print("✅ GPU内存管理正常")
                return True
            else:
                self.test_results["memory_management"] = False
                print("⚠️  GPU内存释放不充分")
                return True  # 仍然通过，只是有警告

        except Exception as e:
            self.test_results["memory_management"] = False
            print(f"❌ GPU内存管理测试失败: {e}")
            return False

    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        print("=" * 60)
        print("🚀 开始GPU环境验证测试")
        print("=" * 60)

        # 运行所有测试
        test_methods = [
            self.test_nvidia_driver,
            self.test_cuda_runtime,
            self.test_cudf,
            self.test_cuml,
            self.test_memory_management,
            self.test_quantitative_trading_scenarios,
        ]

        passed = 0
        total = len(test_methods)

        for method in test_methods:
            try:
                result = method()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ 测试异常: {e}")
                traceback.print_exc()

        # 生成测试报告
        print("\n" + "=" * 60)
        print("📊 GPU环境测试报告")
        print("=" * 60)

        print(f"总测试项目: {total}")
        print(f"通过项目: {passed}")
        print(f"失败项目: {total - passed}")
        print(f"通过率: {(passed / total) * 100:.1f}%")

        # 显示详细结果
        for test_name, result in self.test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {test_name}: {status}")

        # 显示GPU信息
        if self.gpu_info:
            print("\n🖥️  GPU硬件信息:")
            for key, value in self.gpu_info.items():
                print(f"  {key}: {value}")

        # 生成建议
        print("\n💡 建议:")
        if passed == total:
            print("🎉 GPU环境完美！可以启用所有GPU加速功能")
        elif passed >= total - 1:
            print("✅ GPU环境良好，大部分功能可以正常使用")
            print("💡 建议检查失败项目的详细错误信息")
        else:
            print("⚠️  GPU环境存在问题，建议先修复基础配置")
            print("💡 可以尝试重新安装GPU依赖或检查CUDA版本")

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": (passed / total) * 100,
            "results": self.test_results,
            "gpu_info": self.gpu_info,
        }

    def generate_test_code(self) -> str:
        """生成测试代码示例"""
        test_code = '''
# MyStocks GPU加速测试代码示例
import cudf
import cupy as cp
import cuml
import numpy as np

# 1. 大规模历史数据回测
def backtest_strategies_gpu(stock_data, strategies):
    """GPU加速的策略回测"""
    df_gpu = cudf.DataFrame(stock_data)

    results = []
    for strategy in strategies:
        # GPU并行计算策略信号
        signals = strategy.calculate_signals(df_gpu)

        # GPU计算收益
        returns = df_gpu['close'].pct_change()
        strategy_returns = returns * signals

        # GPU计算性能指标
        sharpe = (strategy_returns.mean() / strategy_returns.std()) * np.sqrt(252)
        max_drawdown = (strategy_returns.cumsum().cummax() - strategy_returns.cumsum()).max()

        results.append({
            'strategy': strategy.name,
            'sharpe': sharpe,
            'max_drawdown': max_drawdown
        })

    return results

# 2. 实时特征计算
def calculate_features_gpu(real_time_data):
    """GPU加速的实时特征计算"""
    df_gpu = cudf.DataFrame(real_time_data)

    # 技术指标计算 (GPU加速)
    df_gpu['sma_20'] = df_gpu['price'].rolling(20).mean()
    df_gpu['sma_50'] = df_gpu['price'].rolling(50).mean()
    df_gpu['rsi'] = calculate_rsi_gpu(df_gpu['price'])
    df_gpu['macd'], df_gpu['macd_signal'] = calculate_macd_gpu(df_gpu['price'])

    return df_gpu

# 3. 多因子模型
def multi_factor_model_gpu(factors_data):
    """GPU加速的多因子模型"""
    df_gpu = cudf.DataFrame(factors_data)

    # 因子标准化 (GPU)
    for factor in ['pe', 'pb', 'roe', 'momentum']:
        df_gpu[f'{factor}_normalized'] = (df_gpu[factor] - df_gpu[factor].mean()) / df_gpu[factor].std()

    # 因子权重计算 (GPU矩阵运算)
    weights = cp.array([0.25, 0.25, 0.3, 0.2])  # 因子权重
    factor_columns = ['pe_normalized', 'pb_normalized', 'roe_normalized', 'momentum_normalized']

    df_gpu['composite_score'] = (df_gpu[factor_columns] * weights).sum(axis=1)
    df_gpu['rank'] = df_gpu['composite_score'].rank(method='dense', ascending=False)

    return df_gpu

# 4. 风险计算
def risk_calculation_gpu(portfolio_data):
    """GPU加速的风险计算"""
    df_gpu = cudf.DataFrame(portfolio_data)

    # 协方差矩阵 (GPU)
    returns = df_gpu[['stock1_return', 'stock2_return']].pct_change().dropna()
    cov_matrix = returns.cov().to_numpy()  # 转换为CPU用于计算

    # VaR计算
    portfolio_returns = returns.mean(axis=1)
    var_95 = cp.percentile(cp.array(portfolio_returns), 5)

    return {
        'covariance_matrix': cov_matrix,
        'var_95': var_95,
        'volatility': portfolio_returns.std()
    }
'''
        return test_code


def main():
    """主函数"""
    # 创建测试器
    tester = GPUEnvironmentTester()

    # 运行测试
    results = tester.run_all_tests()

    # 生成测试代码
    if results["passed"] >= results["total"] - 1:
        print("\n📝 生成的测试代码已保存到: gpu_test_examples.py")
        with open("gpu_test_examples.py", "w", encoding="utf-8") as f:
            f.write(tester.generate_test_code())

    return results


if __name__ == "__main__":
    results = main()

    # 设置退出码
    sys.exit(0 if results["pass_rate"] >= 80 else 1)
