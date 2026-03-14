from src.gpu.accelerated.data_processor_gpu_fixed import GPUDataProcessorFixed


def test_gpu_data_processor_imports_without_cudf_runtime():
    processor = GPUDataProcessorFixed(gpu_enabled=False)
    assert processor.gpu_enabled is False
