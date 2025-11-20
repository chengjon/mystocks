"""
数据源格式兼容性校验工具
用于批量校验Mock数据源和真实数据源的输出格式是否一致
"""

from typing import Dict, List, Any, Tuple
import pandas as pd
from src.interfaces.data_source_interface import DataSourceInterface
from src.factories.data_source_factory import MockDataSource, RealDataSource


def compare_data_structure(mock_result: Any, real_result: Any, field_path: str = "") -> List[str]:
    """
    比较两个数据结构是否一致
    
    Args:
        mock_result: Mock数据结果
        real_result: 真实数据结果
        field_path: 当前字段路径，用于错误定位
        
    Returns:
        List[str]: 不一致的字段列表
    """
    errors = []
    
    # 检查类型是否一致
    if type(mock_result) != type(real_result):
        errors.append(f"类型不一致: {field_path} - Mock: {type(mock_result)}, Real: {type(real_result)}")
        return errors
    
    # 如果是字典类型
    if isinstance(mock_result, dict):
        mock_keys = set(mock_result.keys())
        real_keys = set(real_result.keys())
        
        # 检查键是否一致
        missing_in_real = mock_keys - real_keys
        missing_in_mock = real_keys - mock_keys
        
        if missing_in_real:
            errors.append(f"真实数据缺少字段: {field_path} - {list(missing_in_real)}")
        
        if missing_in_mock:
            errors.append(f"Mock数据缺少字段: {field_path} - {list(missing_in_mock)}")
        
        # 递归检查共同字段
        common_keys = mock_keys & real_keys
        for key in common_keys:
            sub_errors = compare_data_structure(
                mock_result[key], 
                real_result[key], 
                f"{field_path}.{key}" if field_path else key
            )
            errors.extend(sub_errors)
    
    # 如果是列表类型
    elif isinstance(mock_result, list):
        if len(mock_result) != len(real_result):
            errors.append(f"列表长度不一致: {field_path} - Mock: {len(mock_result)}, Real: {len(real_result)}")
        
        # 检查列表中的元素
        min_len = min(len(mock_result), len(real_result))
        for i in range(min_len):
            sub_errors = compare_data_structure(
                mock_result[i], 
                real_result[i], 
                f"{field_path}[{i}]"
            )
            errors.extend(sub_errors)
    
    # 如果是pandas DataFrame
    elif isinstance(mock_result, pd.DataFrame):
        if not isinstance(real_result, pd.DataFrame):
            errors.append(f"类型不一致: {field_path} - Mock: DataFrame, Real: {type(real_result)}")
        else:
            mock_cols = set(mock_result.columns)
            real_cols = set(real_result.columns)
            
            missing_in_real = mock_cols - real_cols
            missing_in_mock = real_cols - mock_cols
            
            if missing_in_real:
                errors.append(f"真实DataFrame缺少列: {field_path} - {list(missing_in_real)}")
            
            if missing_in_mock:
                errors.append(f"Mock DataFrame缺少列: {field_path} - {list(missing_in_mock)}")
    
    return errors


def validate_data_source_compatibility(mock_source: DataSourceInterface, real_source: DataSourceInterface, 
                                     test_stock: str = "600519") -> Dict[str, Any]:
    """
    验证数据源兼容性
    
    Args:
        mock_source: Mock数据源
        real_source: 真实数据源
        test_stock: 测试股票代码
        
    Returns:
        Dict[str, Any]: 校验结果
    """
    results = {
        "overall_status": "success",
        "details": {},
        "errors": []
    }
    
    # 定义要测试的方法和参数
    test_methods = [
        ("get_stock_detail", (test_stock,)),
        ("get_real_time_quote", (test_stock,)),
        ("get_all_indicators", (test_stock,)),
        ("get_trend_indicators", (test_stock,)),
        ("get_momentum_indicators", (test_stock,)),
        ("get_volatility_indicators", (test_stock,)),
        ("get_volume_indicators", (test_stock,)),
        ("get_trading_signals", (test_stock,)),
        ("get_kline_data", (test_stock,)),
        ("get_pattern_recognition", (test_stock,)),
        ("get_monitoring_summary", ()),
        ("get_monitoring_status", ())
    ]
    
    # 添加需要参数的方法
    test_methods_with_params = [
        ("get_stock_list", ({"limit": 5},)),
        ("get_realtime_alerts", ({"limit": 5},))
    ]
    
    all_methods = test_methods + test_methods_with_params
    
    for method_name, args in all_methods:
        try:
            print(f"正在校验方法: {method_name}")
            # 调用Mock和真实数据源的相同方法
            mock_result = getattr(mock_source, method_name)(*args)
            real_result = getattr(real_source, method_name)(*args)
            
            # 比较数据结构
            errors = compare_data_structure(mock_result, real_result, method_name)
            
            if errors:
                results["details"][method_name] = {
                    "status": "failed",
                    "errors": errors
                }
                results["errors"].extend([f"{method_name}: {error}" for error in errors])
                results["overall_status"] = "failed"
            else:
                results["details"][method_name] = {
                    "status": "success",
                    "message": "格式一致"
                }
                
        except Exception as e:
            error_msg = f"方法 {method_name} 执行失败: {str(e)}"
            results["details"][method_name] = {
                "status": "error",
                "error": str(e)
            }
            results["errors"].append(error_msg)
            results["overall_status"] = "failed"
            print(f"校验方法 {method_name} 时出错: {e}")
    
    return results


def run_compatibility_check() -> Dict[str, Any]:
    """
    运行完整的兼容性检查
    
    Returns:
        Dict[str, Any]: 检查结果
    """
    print("开始运行数据源格式兼容性检查...")
    
    # 创建数据源实例
    mock_source = MockDataSource()
    real_source = RealDataSource()
    
    # 执行校验
    results = validate_data_source_compatibility(mock_source, real_source)
    
    # 输出结果
    print("\n兼容性检查结果:")
    print("="*50)
    print(f"总体状态: {results['overall_status']}")
    print(f"错误数量: {len(results['errors'])}")
    
    if results['errors']:
        print("\n错误详情:")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("\n各方法校验详情:")
    for method, detail in results['details'].items():
        status = detail['status']
        print(f"  {method}: {status}")
        if status != 'success':
            print(f"    详情: {detail.get('error', detail.get('errors', ['Unknown']))}")
    
    print("="*50)
    
    return results


if __name__ == "__main__":
    # 运行兼容性检查
    check_results = run_compatibility_check()
    
    # 根据结果决定退出码
    import sys
    if check_results['overall_status'] == 'failed':
        print("\n兼容性检查失败，需要修复格式不一致问题")
        sys.exit(1)
    else:
        print("\n兼容性检查通过！")
        sys.exit(0)
