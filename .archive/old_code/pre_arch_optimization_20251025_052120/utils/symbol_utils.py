"""
股票代码处理工具
提供股票代码格式化和转换功能
"""
from typing import Optional, Tuple, Union


def normalize_stock_code(code: Union[str, int, float]) -> str:
    """
    标准化股票代码格式
    支持格式: 
    - 基本格式: 000001, 600000
    - 后缀格式: 000001.SZ, 600000.SH 
    - 前缀格式: sz000001, SH600000
    - 点分隔格式: sz.000001, sh.600000
    - Baostock格式: sh.600000, sz.000001
    - AKShare格式: 600000
    
    返回格式: 6位纯数字代码
    
    参数:
        code: 输入的股票代码(可以是字符串、整数或浮点数)
        
    返回:
        标准化后的6位数字股票代码
        
    异常:
        ValueError: 当输入为空或无法识别的格式时抛出
    """
    # 输入验证
    if code is None:
        raise ValueError("股票代码不能为None")
    
    # 转换为字符串并处理
    code_str = str(code).strip()
    if not code_str:
        raise ValueError("股票代码不能为空或空白字符串")
    
    # 统一转为大写
    code_str = code_str.upper()
    
    # 1. 处理带点分隔符的格式 (sz.000001 或 000001.SZ)
    if '.' in code_str:
        parts = [p.strip() for p in code_str.split('.') if p.strip()]
        if len(parts) == 2:
            # 确定哪部分是市场代码，哪部分是数字代码
            market_candidate = parts[0] if len(parts[0]) == 2 else parts[1]
            num_candidate = parts[1] if len(parts[0]) == 2 else parts[0]
            
            if market_candidate in ['SH', 'SZ', 'BJ'] and num_candidate.isdigit() and len(num_candidate) == 6:
                return num_candidate
    
    # 2. 处理无分隔符的格式 (sz000001)
    if len(code_str) >= 8:
        market_part = code_str[:2]
        num_part = code_str[2:]
        if market_part in ['SH', 'SZ', 'BJ'] and num_part.isdigit() and len(num_part) == 6:
            return num_part
    
    # 3. 处理纯数字格式 (600000)
    if code_str.isdigit():
        if len(code_str) == 6:
            return code_str
        elif len(code_str) > 6:
            return code_str[-6:]  # 取最后6位
    
    # 4. 处理特殊情况 (如指数代码)
    if code_str.startswith(('SH', 'SZ')) and len(code_str) == 8 and code_str[2:].isdigit():
        return code_str[2:]
    
    # 尝试提取纯数字部分
    digits = ''.join(c for c in code_str if c.isdigit())
    if len(digits) == 6:
        return digits
    
    raise ValueError(
        f"无法识别的股票代码格式: '{code_str}'\n"
        "支持的格式示例:\n"
        "- 基本格式: '600000', '000001'\n"
        "- 后缀格式: '000001.SZ', '600000.SH'\n"
        "- 前缀格式: 'sz000001', 'SH600000'\n"
        "- 点分隔格式: 'sz.000001', 'sh.600000'"
    )


def get_stock_exchange(code: Union[str, int, float]) -> str:
    """
    根据股票代码获取交易所代码
    
    参数:
        code: 股票代码(可以是任何支持的格式)
        
    返回:
        str: 交易所代码 (SH/SZ/BJ)
    """
    try:
        std_code = normalize_stock_code(code)
    except ValueError:
        return 'SH'  # 默认返回上海
    
    # 根据首位判断交易所
    first_char = std_code[0]
    if first_char in ['6', '9']:
        return 'SH'  # 上海证券交易所
    elif first_char in ['0', '1', '2', '3']:
        return 'SZ'  # 深圳证券交易所
    elif first_char in ['4', '8']:
        return 'BJ'  # 北京证券交易所
    else:
        return 'SH'  # 默认


def format_stock_code_for_source(
    code: Union[str, int, float], 
    source_type: str = 'akshare'
) -> str:
    """
    根据数据源类型格式化股票代码
    
    参数:
        code: 股票代码(可以是任何支持的格式)
        source_type: 数据源类型
            - 'akshare': AKShare格式 (600000) - 6位纯数字
            - 'baostock': Baostock格式 (sh.600000) - 交易所.代码
            
    返回:
        str: 适合指定数据源的股票代码格式
        
    异常:
        ValueError: 当数据源类型无效时抛出
    """
    std_code = normalize_stock_code(code)
    exchange = get_stock_exchange(std_code)
    
    source_type = source_type.lower()
    if source_type == 'akshare':
        # AKShare使用6位纯数字格式
        return std_code
    elif source_type == 'baostock':
        # Baostock使用"交易所.代码"格式
        return f"{exchange.lower()}.{std_code}"
    else:
        raise ValueError(f"不支持的数据源类型: {source_type}")


def format_stock_code(
    code: Union[str, int, float], 
    format_type: str = 'numeric'
) -> str:
    """
    根据指定格式格式化股票代码（保持向后兼容）
    
    参数:
        code: 股票代码(可以是任何支持的格式)
        format_type: 格式类型
            - 'numeric': 纯数字格式 (600001)
            - 'prefix': 前缀格式 (sh600001)
            - 'suffix': 后缀格式 (600001.SH)
            - 'baostock': Baostock格式 (sh.600000)
            - 'akshare': AKShare格式 (600000)
            
    返回:
        str: 格式化后的股票代码
        
    异常:
        ValueError: 当格式类型无效时抛出
    """
    std_code = normalize_stock_code(code)
    exchange = get_stock_exchange(std_code)
    
    format_type = format_type.lower()
    if format_type == 'numeric':
        return std_code
    elif format_type == 'prefix':
        return f"{exchange.lower()}{std_code}"
    elif format_type == 'suffix':
        return f"{std_code}.{exchange}"
    elif format_type == 'baostock':
        return f"{exchange.lower()}.{std_code}"
    elif format_type == 'akshare':
        return std_code
    else:
        raise ValueError(f"不支持的格式类型: {format_type}")


def is_valid_stock_code(code: Union[str, int, float]) -> bool:
    """
    检查股票代码是否有效
    
    参数:
        code: 股票代码
        
    返回:
        bool: 股票代码是否有效
    """
    try:
        normalize_stock_code(code)
        return True
    except ValueError:
        return False


def format_index_code_for_source(
    code: Union[str, int, float], 
    source_type: str = 'akshare'
) -> str:
    """
    根据数据源类型格式化指数代码
    
    参数:
        code: 指数代码(可以是任何支持的格式)
        source_type: 数据源类型
            - 'akshare': AKShare格式 (通常是 sh000001, sz399001 或 000001, 399001)
            - 'baostock': Baostock格式 (sh.000001, sz.399001)
            
    返回:
        str: 适合指定数据源的指数代码格式
        
    异常:
        ValueError: 当数据源类型无效时抛出
    """
    std_code = normalize_index_code(code)
    
    # 根据指数代码判断交易所
    if std_code.startswith('000'):
        exchange = 'sh'  # 上证指数
    elif std_code.startswith('399'):
        exchange = 'sz'  # 深证指数
    else:
        exchange = 'sh'  # 默认上海
    
    source_type = source_type.lower()
    if source_type == 'akshare':
        # AKShare对于指数可以使用多种格式，但通常使用前缀格式
        return f"{exchange}{std_code}"
    elif source_type == 'baostock':
        # Baostock使用"交易所.代码"格式
        return f"{exchange}.{std_code}"
    else:
        raise ValueError(f"不支持的数据源类型: {source_type}")


def normalize_index_code(code: Union[str, int, float]) -> str:
    """
    标准化指数代码格式
    支持格式: 
    - 基本格式: 000001, 399001
    - 后缀格式: 000001.SH, 399001.SZ 
    - 前缀格式: sh000001, SZ399001
    - 点分隔格式: sh.000001, sz.399001
    
    返回格式: 6位纯数字代码
    
    参数:
        code: 输入的指数代码(可以是字符串、整数或浮点数)
        
    返回:
        标准化后的6位数字指数代码
        
    异常:
        ValueError: 当输入为空或无法识别的格式时抛出
    """
    # 输入验证
    if code is None:
        raise ValueError("指数代码不能为None")
    
    # 转换为字符串并处理
    code_str = str(code).strip()
    if not code_str:
        raise ValueError("指数代码不能为空或空白字符串")
    
    # 统一转为大写
    code_str = code_str.upper()
    
    # 1. 处理带点分隔符的格式 (sh.000001 或 000001.SH)
    if '.' in code_str:
        parts = [p.strip() for p in code_str.split('.') if p.strip()]
        if len(parts) == 2:
            # 确定哪部分是市场代码，哪部分是数字代码
            market_candidate = parts[0] if len(parts[0]) == 2 else parts[1]
            num_candidate = parts[1] if len(parts[0]) == 2 else parts[0]
            
            if market_candidate in ['SH', 'SZ'] and num_candidate.isdigit() and len(num_candidate) == 6:
                return num_candidate
    
    # 2. 处理无分隔符的格式 (sh000001)
    if len(code_str) >= 8:
        market_part = code_str[:2]
        num_part = code_str[2:]
        if market_part in ['SH', 'SZ'] and num_part.isdigit() and len(num_part) == 6:
            return num_part
    
    # 3. 处理纯数字格式 (000001)
    if code_str.isdigit():
        if len(code_str) == 6:
            return code_str
        elif len(code_str) > 6:
            return code_str[-6:]  # 取最后6位
    
    # 尝试提取纯数字部分
    digits = ''.join(c for c in code_str if c.isdigit())
    if len(digits) == 6:
        return digits
    
    error_msg = """无法识别的指数代码格式: '{}'
支持的格式示例:
- 基本格式: '000001', '399001'
- 后缀格式: '000001.SH', '399001.SZ'
- 前缀格式: 'sh000001', 'SZ399001'
- 点分隔格式: 'sh.000001', 'sz.399001'""".format(code_str)
    raise ValueError(error_msg)


# 测试代码
if __name__ == '__main__':
    print("=== 基础格式化测试 ===")
    test_cases = [
        '600000', '000001', 'sh600000', 'SZ000001',
        '600000.SH', '000001.SZ', 'sz.000001', 'sh.600000',
        '123456789', 'abc123', ''
    ]
    
    for case in test_cases:
        try:
            print(f"输入: {case:<15} => 标准化: {normalize_stock_code(case)}")
        except ValueError as e:
            print(f"输入: {case:<15} => 错误: {str(e)}")
    
    print("\n=== 数据源格式化测试 ===")
    test_stocks = ['600000', '000001', '600000.SH', 'sz.000001']
    
    for stock in test_stocks:
        try:
            print(f"原始代码: {stock}")
            print(f"  -> AKShare格式: {format_stock_code_for_source(stock, 'akshare')}")
            print(f"  -> Baostock格式: {format_stock_code_for_source(stock, 'baostock')}")
            print()
        except ValueError as e:
            print(f"  -> 错误: {str(e)}")
    
    print("=== 指数代码格式化测试 ===")
    test_indices = ['000001', '399001', 'sh000001', 'sz.399001']
    
    for index in test_indices:
        try:
            print(f"原始指数: {index}")
            print(f"  -> AKShare格式: {format_index_code_for_source(index, 'akshare')}")
            print(f"  -> Baostock格式: {format_index_code_for_source(index, 'baostock')}")
            print()
        except ValueError as e:
            print(f"  -> 错误: {str(e)}")