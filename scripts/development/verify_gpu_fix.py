import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from src.gpu.api_system.main_server import GPUAPIServer
    print("GPUAPIServer import: SUCCESS")
except ImportError as e:
    print(f"GPUAPIServer import: FAILED - {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"GPUAPIServer error: {e}")
    import traceback
    traceback.print_exc()

try:
    from src.gpu.api_system.utils.cache_optimization_enhanced import EnhancedCacheManager
    print("EnhancedCacheManager import: SUCCESS")
except ImportError as e:
    print(f"EnhancedCacheManager import: FAILED - {e}")
    import traceback
    traceback.print_exc()
