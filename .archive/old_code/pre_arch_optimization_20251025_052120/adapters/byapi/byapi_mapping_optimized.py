"""
API映射配置文件 - 优化版
根据optimized_api_data_v2.json中的接口定义，提供API接口的类型、名称、URL、描述及返回字段映射。
"""

import json
import os

# API映射配置 - 按接口类型分类
# 注意：这个变量现在会在加载JSON文件后动态生成
API_MAPPING_TYPE = {}

# 为每个API创建column_name_mapping字典
# key为fields中的field_name，value为fields中的name
COLUMN_NAME_MAPPING = {}

def load_api_data_from_json(json_file_path=None):
    """
    从JSON文件加载API数据并构建API_MAPPING_TYPE
    :param json_file_path: JSON文件路径，如果未提供则使用默认路径
    :return: 加载是否成功
    """
    global API_MAPPING_TYPE
    
    # 如果未提供文件路径，使用默认路径
    if json_file_path is None:
        # 构建相对于当前脚本的文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, '..', '2网页抓取直出数据表', 'optimized_api_data_v2.json')
    
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            api_data = json.load(f)
        
        # 构建API_MAPPING_TYPE结构
        # 首先需要确定API的类型分类
        # 这里我们根据API名称和URL特征进行分类
        api_types = {
            '股票列表': ['股票列表', '新股日历'],
            '指数行业概念': ['指数、行业、概念树', '根据指数、行业、概念找相关股票', '根据股票找相关指数、行业、概念'],
            '涨跌股池': ['涨停股池', '跌停股池', '强势股池', '次新股池', '炸板股池'],
            '上市公司详情': ['公司简介', '所属指数', '历届高管/董事会/监事会成员', '近年分红', '近年增发', '解禁限售'],
            '实时交易': ['实时交易(公开数据)', '当天逐笔交易', '实时交易数据', '买卖五档盘口', '实时交易数据（多股）', '资金流向数据'],
            '财务数据': ['近一年各季度利润', '近一年各季度现金流', '近年业绩预告', '财务指标', '十大股东', '十大流通股东', '股东变化趋势', '基金持股']
        }
        
        # 初始化API_MAPPING_TYPE
        API_MAPPING_TYPE = {}
        
        # 遍历所有API
        for api_name, api_info in api_data.items():
            # 确定API类型
            api_type = '其他'
            for type_name, api_list in api_types.items():
                if api_name in api_list:
                    api_type = type_name
                    break
            
            # 初始化该类型的字典
            if api_type not in API_MAPPING_TYPE:
                API_MAPPING_TYPE[api_type] = {}
            
            # 处理fields，从列表转换为字典格式
            fields_dict = {}
            if 'fields' in api_info and isinstance(api_info['fields'], list):
                for field in api_info['fields']:
                    if 'field_name' in field:
                        field_name = field['field_name']
                        fields_dict[field_name] = {
                            'data_type': field.get('data_type', ''),
                            'name': field.get('name', field_name),
                            'description': field.get('description', '')
                        }
            
            # 添加到API_MAPPING_TYPE
            API_MAPPING_TYPE[api_type][api_name] = {
                'api_url': api_info.get('api_url', ''),
                'description': api_info.get('description', api_info.get('api_description', '')),
                'fields': fields_dict
            }
        
        # 生成列名映射
        generate_column_name_mapping()
        return True
    except Exception as e:
        print(f"加载API数据失败: {str(e)}")
        return False

# 遍历API_MAPPING_TYPE生成COLUMN_NAME_MAPPING
def generate_column_name_mapping():
    """生成字段名称映射字典"""
    global COLUMN_NAME_MAPPING
    COLUMN_NAME_MAPPING = {}
    
    for api_type, apis in API_MAPPING_TYPE.items():
        for api_name, api_info in apis.items():
            column_mapping = {}
            for field_name, field_info in api_info.get('fields', {}).items():
                column_mapping[field_name] = field_info.get('name', field_name)
            COLUMN_NAME_MAPPING[api_name] = column_mapping
    
    return COLUMN_NAME_MAPPING

# 初始化加载API数据和生成列名映射
load_api_data_from_json()

def get_api_types():
    """获取所有API类型"""
    return list(API_MAPPING_TYPE.keys())

def get_api_names_by_type(api_type):
    """根据API类型获取该类型下的所有API名称"""
    if api_type in API_MAPPING_TYPE:
        return list(API_MAPPING_TYPE[api_type].keys())
    return []

def get_field_mapping(api_name):
    """根据API名称获取字段映射"""
    for api_type, apis in API_MAPPING_TYPE.items():
        if api_name in apis:
            return apis[api_name].get('fields', {})
    return {}

def get_api_documentation(api_name):
    """根据API名称获取API文档信息"""
    for api_type, apis in API_MAPPING_TYPE.items():
        if api_name in apis:
            api_info = apis[api_name]
            return {
                "name": api_name,
                "type": api_type,
                "description": api_info.get('description', ''),
                "api_url": api_info.get('api_url', ''),
                "fields": api_info.get('fields', {})
            }
    return None

def get_column_name_mapping(api_name):
    """根据API名称获取列名映射"""
    return COLUMN_NAME_MAPPING.get(api_name, {})

if __name__ == "__main__":
    # 示例用法
    print("所有API类型：")
    for api_type in get_api_types():
        print(f"- {api_type}")
        
    print("\n股票列表类型下的API名称：")
    for api_name in get_api_names_by_type("股票列表"):
        print(f"- {api_name}")
        
    print("\n股票列表API的字段映射：")
    for field_name, field_info in get_field_mapping("股票列表").items():
        print(f"  {field_name}: {field_info['name']}")
        
    print("\n股票列表API的列名映射：")
    for field_name, column_name in get_column_name_mapping("股票列表").items():
        print(f"  {field_name}: {column_name}")
        
    print("\n股票列表API的文档信息：")
    doc = get_api_documentation("股票列表")
    if doc:
        print(f"类型: {doc['type']}")
        print(f"描述: {doc['description']}")
        print(f"URL: {doc['api_url']}")
        print(f"字段数量: {len(doc['fields'])}")
        
    # 测试从不同路径加载数据
    # load_api_data_from_json("/path/to/your/custom/optimized_api_data_v2.json")