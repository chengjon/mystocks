"""
GPUDataProcessor 的批处理与基准测试绑定。
"""

import logging
import time
from typing import Dict, List

import dask.dataframe as dd
import pandas as pd
from dask.distributed import Client


def create_batch_processing_bindings(gpu_data_processor_cls):
    """构建批处理器与 benchmark 绑定。"""

    class BatchDataProcessor:
        """批量数据处理器"""

        def __init__(self, gpu_enabled: bool = True, max_workers: int = 4):
            self.gpu_enabled = gpu_enabled
            self.max_workers = max_workers
            self.base_processor = gpu_data_processor_cls(gpu_enabled, max_workers)
            self.logger = logging.getLogger(__name__)

        def process_large_dataset(self, data_path: str, output_path: str, chunk_size: int = 100000) -> Dict:
            start_time = time.time()
            reader = pd.read_csv(data_path, chunksize=chunk_size)
            processed_chunks = []

            for index, chunk in enumerate(reader):
                print(f"处理第 {index + 1} 块数据...")
                result = self.base_processor.load_and_preprocess(chunk)
                processed_chunks.append(result.processed_data)
                chunk_path = f"{output_path}_chunk_{index}.csv"
                result.processed_data.to_csv(chunk_path, index=False)

            final_result = pd.concat(processed_chunks, ignore_index=True)
            final_path = f"{output_path}_final.csv"
            final_result.to_csv(final_path, index=False)

            return {
                "total_time": time.time() - start_time,
                "total_chunks": len(processed_chunks),
                "final_records": len(final_result),
                "output_path": final_path,
            }

        def distributed_processing(self, data_paths: List[str], output_path: str) -> Dict:
            start_time = time.time()
            try:
                client = Client(n_workers=self.max_workers)
                dataframes = [dd.read_csv(path) for path in data_paths]
                combined_df = dd.concat(dataframes)

                processed_dfs = []
                for _ in range(len(dataframes)):
                    processed_dfs.append(
                        combined_df.map_partitions(
                            lambda df: self.base_processor.load_and_preprocess(df).processed_data,
                            meta=combined_df._meta,
                        )
                    )

                final_df = dd.concat(processed_dfs)
                final_df.to_csv(output_path, index=False, single_file=True)
                client.close()

                return {
                    "total_time": time.time() - start_time,
                    "input_files": len(data_paths),
                    "output_path": output_path,
                }
            except Exception as error:
                self.logger.error("分布式处理失败: %s", error)
                return {"error": str(error)}

    def benchmark_data_processing(data: pd.DataFrame, gpu_enabled: bool = True):
        """数据处理性能基准测试"""
        print("🔬 开始数据处理性能测试...")

        gpu_processor = gpu_data_processor_cls(gpu_enabled=True)
        gpu_start = time.time()
        gpu_result = gpu_processor.load_and_preprocess(data)
        gpu_time = time.time() - gpu_start

        cpu_processor = gpu_data_processor_cls(gpu_enabled=False)
        cpu_start = time.time()
        cpu_result = cpu_processor.load_and_preprocess(data)
        cpu_time = time.time() - cpu_start

        print("\n📊 数据处理性能对比:")
        print(f"GPU处理时间: {gpu_time:.2f}秒")
        print(f"CPU处理时间: {cpu_time:.2f}秒")
        print(f"加速比: {cpu_time / gpu_time:.2f}x")
        print(f"GPU压缩比: {gpu_result.memory_usage['compression_ratio']:.2f}x")
        print(f"CPU压缩比: {cpu_result.memory_usage['compression_ratio']:.2f}x")
        print(f"GPU处理记录数: {gpu_result.data_shape[0]}")
        print(f"CPU处理记录数: {cpu_result.data_shape[0]}")

        return {
            "gpu_time": gpu_time,
            "cpu_time": cpu_time,
            "speedup": cpu_time / gpu_time,
            "gpu_result": gpu_result,
            "cpu_result": cpu_result,
        }

    return BatchDataProcessor, benchmark_data_processing
