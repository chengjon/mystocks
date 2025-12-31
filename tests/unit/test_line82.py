from src.utils.symbol_utils import normalize_stock_code

# 测试第82行的精确触发条件
print("Testing line 82 conditions:")
normalize_stock_code("SH000001")  # 8 chars: SH + 6 digits
normalize_stock_code("SZ399001")  # 8 chars: SZ + 6 digits
print("Tests completed.")
