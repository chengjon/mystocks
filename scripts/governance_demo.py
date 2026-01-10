import asyncio
import pandas as pd
import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from src.governance.core.fetcher_bridge import GovernanceDataFetcher, RoutePolicy
from src.governance.engine.gpu_validator import GPUValidator

async def main():
    print("=== 数据治理与架构演进 Demo (V3.0) ===")
    
    # 1. 获取数据 (Mock 演示)
    # fetcher = GovernanceDataFetcher()
    # 在实际场景中: data = await fetcher.fetch_batch_kline(...)
    
    print("\n[Step 1] 获取数据 (模拟)...")
    # 构造包含异常的数据
    data = pd.DataFrame({
        'symbol': ['000001', '000001', '000001'],
        'trade_date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'open': [10.0, 10.0, 10.0],
        'close': [11.0, 11.0, 11.0],
        'high': [12.0, 9.0, 12.0],   # Row 1: High(9) < Open(10) -> Error
        'low':  [9.0,  9.0, 12.0],   # Row 2: Low(12) > Close(11) -> Error
        'volume': [100, 100, 100]
    })
    print(f"原始数据:\n{data}")
    
    # 2. 校验数据
    print("\n[Step 2] 初始化 GPU 验证器...")
    validator = GPUValidator()
    print(f"验证器状态: {'GPU模式' if validator.use_gpu else 'CPU模式 (Fallback)'}")
    
    print("\n[Step 3] 执行 OHLC 规则校验...")
    results = validator.validate(data, rules=['ohlc'])
    
    if 'ohlc' in results:
        invalid = results['ohlc']
        # 统一转换为 pandas 显示
        if hasattr(invalid, 'to_pandas'):
            invalid = invalid.to_pandas()
            
        print(f"验证完成! 发现 {len(invalid)} 条异常数据:")
        print(invalid)
    else:
        print("未发现异常。")

if __name__ == "__main__":
    asyncio.run(main())
