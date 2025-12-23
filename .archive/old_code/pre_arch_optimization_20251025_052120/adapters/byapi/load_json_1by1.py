import json
import pandas as pd
import os

"""load_json_1by1.py

功能简要：
- 提供load_json类，用于读取和解析JSON格式的API数据配置文件
- 支持通过指定的KEY值（如'历史分时KDJ'）快速访问对应的API信息
- 提供属性访问功能，支持直接获取API名称、URL、描述等信息
- 支持链式调用格式，如load_json(file, '历史分时KDJ').api_name
- 自动将fields数据转换为pandas DataFrame格式，方便数据处理和分析
- 内置错误处理和文件验证机制

用法：
load_json(file_path, '资产负债表').api_name
load_json(file_path, '资产负债表').api_url
load_json(file_path, '资产负债表').api_description
load_json(file_path, '资产负债表').fields
load_json(file_path, '资产负债表').fields['name']

主要用途：
- 加载和解析optimized_api_data_v2.json格式的API配置文件
- 快速获取特定API的详细信息和字段定义
- 为后续API调用和数据处理提供基础支持
"""


class load_json:
    def __init__(self, file_path, api_key=None, item=None):
        """初始化load_json类

        Args:
            file_path (str): JSON文件路径
            api_key (str, optional): api_mapping.json中的KEY值
            item (str, optional): 指定的items中的参数值
        """
        self.file_path = file_path
        self.api_key = api_key
        self.item = item
        self.json_data = None
        self.api_mapping_data = None
        self.api_info = None

        # 初始化时自动读取JSON文件
        self.read_json()

    def read_json(self):
        """读取JSON文件并解析数据"""
        # 检查文件是否存在
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"文件不存在: {self.file_path}")

        # 读取主JSON文件
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.json_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON文件解析错误: {e}")

        # 尝试读取api_mapping.json文件以验证api_key
        api_mapping_path = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/2网页抓取直出数据表/api_mapping.json"
        if os.path.exists(api_mapping_path):
            try:
                with open(api_mapping_path, "r", encoding="utf-8") as f:
                    self.api_mapping_data = json.load(f)
            except Exception as e:
                print(f"警告: 加载api_mapping.json时出错: {e}")

        # 如果提供了api_key，验证并获取对应的数据
        if self.api_key:
            # 验证api_key是否在api_mapping.json中
            if self.api_mapping_data and self.api_key not in self.api_mapping_data:
                print(f"警告: '{self.api_key}' 不在api_mapping.json的指定范围内")

            # 从主JSON数据中获取对应的API信息
            if self.json_data and self.api_key in self.json_data:
                self.api_info = self.json_data[self.api_key]
            else:
                print(f"警告: 在提供的JSON文件中未找到'{self.api_key}'")

    def __getattr__(self, name):
        """允许通过点操作符访问JSON数据中的属性"""
        # 特殊处理fields，确保返回DataFrame
        if name == "fields":
            try:
                if self.api_info and "fields" in self.api_info:
                    return pd.DataFrame(self.api_info["fields"])
                elif (
                    self.item
                    and hasattr(self, "json_data")
                    and self.json_data
                    and self.item in self.json_data
                ):
                    item_data = self.json_data[self.item]
                    if "fields" in item_data:
                        return pd.DataFrame(item_data["fields"])
            except Exception as e:
                print(f"警告: 转换fields为DataFrame时出错: {e}")
                # 返回空的DataFrame作为后备
                return pd.DataFrame()
            # 如果没有找到fields，返回空的DataFrame
            return pd.DataFrame()

        # 首先检查是否是API信息中的直接属性
        if self.api_info and name in self.api_info:
            return self.api_info[name]

        # 如果指定了item，尝试获取items中的参数值
        if self.item and hasattr(self, "json_data") and self.json_data:
            if self.item in self.json_data:
                item_data = self.json_data[self.item]
                if name in item_data:
                    return item_data[name]

        # 抛出属性错误
        raise AttributeError(f"'{self.__class__.__name__}' 对象没有属性 '{name}'")


# 示例用法
if __name__ == "__main__":
    try:
        # 测试基本功能
        file_path = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/2网页抓取直出数据表/optimized_api_data_v2.json"

        # 测试用例1: 加载特定API并访问其属性
        api_loader = load_json(file_path, "历史分时KDJ")
        print(f"API名称: {api_loader.api_name}")
        print(f"API URL: {api_loader.api_url}")
        print(f"API描述: {api_loader.api_description}")

        # 测试用例2: 获取fields数据
        fields_df = api_loader.fields
        print("\nFields数据:")
        print(fields_df)

        # 测试用例3: 获取中文字段名
        if not fields_df.empty:
            cols_cn = fields_df["name"]
            print("\n中文字段名:")
            print(cols_cn.tolist())

        # 测试用例4: 直接链式调用
        # 如用户要求的: load_json(file, '历史分时KDJ').api_name
        direct_api_name = load_json(file_path, "历史分时KDJ").api_name
        print(f"\n直接链式调用获取的API名称: {direct_api_name}")

    except Exception as e:
        print(f"发生错误: {e}")
