import sys
import os
sys.path.insert(0, os.getcwd())

print(f"PYTHONPATH: {sys.path[0]}")

modules_to_test = [
    "src.gpu.api_system.main_server",
    "src.gpu.api_system.services.integrated_backtest_service",
    "src.gpu.api_system.services.integrated_realtime_service",
    "src.gpu.api_system.services.integrated_ml_service",
    "src.gpu.api_system.utils.gpu_utils",
    "src.gpu.api_system.utils.redis_utils",
    "src.gpu.api_system.utils.monitoring",
    "src.gpu.api_system.utils.cache_optimization",
    "src.gpu.api_system.utils.cache_optimization_enhanced",
    "src.gpu.api_system.utils.gpu_acceleration_engine",
]

for module_name in modules_to_test:
    try:
        __import__(module_name)
        print(f"Import {module_name}: SUCCESS")
    except ImportError as e:
        print(f"Import {module_name}: FAILED - {e}")
    except Exception as e:
        print(f"Import {module_name}: ERROR - {e}")

print("\nVerifying GPUAPIServer class...")
try:
    from src.gpu.api_system.main_server import GPUAPIServer
    from src.gpu.api_system.config.system_config import SystemConfig
    config = SystemConfig()
    server = GPUAPIServer(config)
    print("GPUAPIServer instantiation: SUCCESS")
except Exception as e:
    print(f"GPUAPIServer instantiation: FAILED - {e}")
    import traceback
    traceback.print_exc()
