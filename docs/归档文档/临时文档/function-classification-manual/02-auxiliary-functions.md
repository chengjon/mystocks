# 辅助功能

**类别**: auxiliary
**模块数**: 57
**类数**: 70
**函数数**: 500
**代码行数**: 20646

## 概述


辅助功能模块为核心功能提供扩展和支持，主要包括各种数据源适配器、
工厂模式实现、交易策略、回测引擎等可插拔组件。

**关键特性**:
- 外部数据源适配器（AKShare, Baostock, 通达信等）
- 数据源工厂模式
- 量化交易策略实现
- 回测引擎
- 机器学习策略
- 实时数据处理

**设计模式**: Adapter Pattern, Factory Pattern, Strategy Pattern


## 模块列表

### adapters.__init__

**文件**: `adapters/__init__.py`

**说明**:

数据源适配器模块
包含各种数据源的具体实现

---

### adapters.akshare_adapter

**文件**: `adapters/akshare_adapter.py`

**说明**:

# 功能：AkShare数据源适配器，提供A股行情和基本面数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `AkshareDataSource`

Akshare数据源实现

属性:
    api_timeout (int): API请求超时时间(秒)
    max_retries (int): 最大重试次数

**继承**: `IDataSource`

**方法**:

- `__init__(self, api_timeout: int = REQUEST_TIMEOUT, max_retries: int = MAX_RETRIES)` → `None` [adapters/akshare_adapter.py:43]
  - 初始化Akshare数据源
- `_retry_api_call(self, func)` → `None` [adapters/akshare_adapter.py:54]
  - API调用重试装饰器
- `get_stock_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/akshare_adapter.py:70]
  - 获取股票日线数据-Akshare实现
- `get_index_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/akshare_adapter.py:142]
  - 获取指数日线数据-Akshare实现
- `_process_index_data(self, df: pd.DataFrame)` → `pd.DataFrame` [adapters/akshare_adapter.py:224]
  - 处理指数数据统一格式
- `get_stock_basic(self, symbol: str)` → `Dict` [adapters/akshare_adapter.py:229]
  - 获取股票基本信息-Akshare实现
- `get_index_components(self, symbol: str)` → `List[str]` [adapters/akshare_adapter.py:253]
  - 获取指数成分股-Akshare实现
- `get_real_time_data(self, symbol: str)` → `None` [adapters/akshare_adapter.py:276]
  - 获取实时数据-Akshare实现
- `get_market_calendar(self, start_date: str, end_date: str)` → `None` [adapters/akshare_adapter.py:298]
  - 获取交易日历-Akshare实现
- `get_financial_data(self, symbol: str, period: str = "annual")` → `None` [adapters/akshare_adapter.py:321]
  - 获取财务数据-Akshare实现
- `get_news_data(self, symbol: str = None, limit: int = 10)` → `None` [adapters/akshare_adapter.py:337]
  - 获取新闻数据-Akshare实现
- `get_ths_industry_summary(self)` → `pd.DataFrame` [adapters/akshare_adapter.py:359]
  - 获取同花顺行业一览表数据-Akshare实现
- `get_ths_industry_stocks(self, industry_name: str)` → `pd.DataFrame` [adapters/akshare_adapter.py:414]
  - 获取同花顺指定行业的成分股数据-Akshare实现
- `get_ths_industry_names(self)` → `pd.DataFrame` [adapters/akshare_adapter.py:470]
  - 获取同花顺行业名称列表-Akshare实现

---

### adapters.akshare_proxy_adapter

**文件**: `adapters/akshare_proxy_adapter.py`

**说明**:

AkShare通用接口代理适配器

功能：
- 动态调用任何akshare接口，无需提前定义
- 提供统一的错误处理和重试机制
- 支持参数验证和类型转换
- 自动添加时间戳和数据标准化

使用场景：
- 快速接入新的akshare接口
- 测试和验证akshare功能
- 临时数据获取需求

注意：此适配器适合快速原型开发，生产环境建议使用专门的适配器

#### 类

##### `AkshareProxyAdapter`

AkShare通用接口代理适配器

可以动态调用任何akshare接口，提供统一的错误处理和数据标准化

**继承**: `IDataSource`

**方法**:

- `__init__(self, api_timeout: int = REQUEST_TIMEOUT, max_retries: int = MAX_RETRIES)` → `None` [adapters/akshare_proxy_adapter.py:49]
  - 初始化AkShare代理适配器
- `_discover_akshare_functions(self)` → `Dict[(str, callable)]` [adapters/akshare_proxy_adapter.py:62]
  - 发现所有可用的akshare函数
- `_retry_api_call(self, func)` → `None` [adapters/akshare_proxy_adapter.py:77]
  - API调用重试装饰器
- `call_akshare_function(self, function_name: str, **kwargs)` → `Union[(pd.DataFrame, Dict, List, Any)]` [adapters/akshare_proxy_adapter.py:93]
  - 动态调用akshare函数
- `get_function_info(self, function_name: str)` → `Dict` [adapters/akshare_proxy_adapter.py:145]
  - 获取akshare函数的信息
- `search_functions(self, keyword: str)` → `List[str]` [adapters/akshare_proxy_adapter.py:171]
  - 搜索包含关键词的akshare函数
- `list_stock_functions(self)` → `List[str]` [adapters/akshare_proxy_adapter.py:192]
  - 列出所有股票相关的函数
- `list_industry_functions(self)` → `List[str]` [adapters/akshare_proxy_adapter.py:204]
  - 列出所有行业板块相关的函数
- `get_stock_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/akshare_proxy_adapter.py:217]
  - 获取股票日线数据
- `get_index_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/akshare_proxy_adapter.py:228]
  - 获取指数日线数据
- `get_stock_basic(self, symbol: str)` → `Dict` [adapters/akshare_proxy_adapter.py:232]
  - 获取股票基本信息
- `get_index_components(self, symbol: str)` → `List[str]` [adapters/akshare_proxy_adapter.py:239]
  - 获取指数成分股
- `get_real_time_data(self, symbol: str)` → `Dict` [adapters/akshare_proxy_adapter.py:249]
  - 获取实时数据
- `get_market_calendar(self, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/akshare_proxy_adapter.py:258]
  - 获取交易日历
- `get_financial_data(self, symbol: str, period: str = "annual")` → `pd.DataFrame` [adapters/akshare_proxy_adapter.py:265]
  - 获取财务数据
- `get_news_data(self, symbol: str = None, limit: int = 10)` → `List[Dict]` [adapters/akshare_proxy_adapter.py:272]
  - 获取新闻数据

#### 函数

##### `demo_akshare_proxy()` → `None`

**位置**: [adapters/akshare_proxy_adapter.py:284]

演示AkShare代理适配器的使用

---

### adapters.baostock_adapter

**文件**: `adapters/baostock_adapter.py`

**说明**:

# 功能：BaoStock数据源适配器，提供历史行情和财务数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `BaostockDataSource`

Baostock数据源实现

**继承**: `IDataSource`

**方法**:

- `__init__(self)` → `None` [adapters/baostock_adapter.py:31]
- `__del__(self)` → `None` [adapters/baostock_adapter.py:51]
- `get_stock_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/baostock_adapter.py:56]
  - 获取股票日线数据-Baostock实现
- `get_index_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/baostock_adapter.py:93]
  - 获取指数日线数据-Baostock实现
- `get_stock_basic(self, symbol: str)` → `Dict` [adapters/baostock_adapter.py:140]
  - 获取股票基本信息-Baostock实现
- `get_index_components(self, symbol: str)` → `List[str]` [adapters/baostock_adapter.py:170]
  - 获取指数成分股-Baostock实现
- `get_real_time_data(self, symbol: str)` → `None` [adapters/baostock_adapter.py:192]
  - 获取实时数据-Baostock实现
- `get_market_calendar(self, start_date: str, end_date: str)` → `None` [adapters/baostock_adapter.py:220]
  - 获取交易日历-Baostock实现
- `get_financial_data(self, symbol: str, period: str = "annual")` → `None` [adapters/baostock_adapter.py:230]
  - 获取财务数据-Baostock实现
- `get_news_data(self, symbol: str = None, limit: int = 10)` → `None` [adapters/baostock_adapter.py:250]
  - 获取新闻数据-Baostock实现

---

### adapters.byapi.byapi_mapping_optimized

**文件**: `adapters/byapi/byapi_mapping_optimized.py`

**说明**:

API映射配置文件 - 优化版
根据optimized_api_data_v2.json中的接口定义，提供API接口的类型、名称、URL、描述及返回字段映射。

#### 函数

##### `load_api_data_from_json(json_file_path=None)` → `None`

**位置**: [adapters/byapi/byapi_mapping_optimized.py:17]

从JSON文件加载API数据并构建API_MAPPING_TYPE
:param json_file_path: JSON文件路径，如果未提供则使用默认路径
:return: 加载是否成功

##### `generate_column_name_mapping()` → `None`

**位置**: [adapters/byapi/byapi_mapping_optimized.py:91]

生成字段名称映射字典

##### `get_api_types()` → `None`

**位置**: [adapters/byapi/byapi_mapping_optimized.py:108]

获取所有API类型

##### `get_api_names_by_type(api_type)` → `None`

**位置**: [adapters/byapi/byapi_mapping_optimized.py:112]

根据API类型获取该类型下的所有API名称

##### `get_field_mapping(api_name)` → `None`

**位置**: [adapters/byapi/byapi_mapping_optimized.py:118]

根据API名称获取字段映射

##### `get_api_documentation(api_name)` → `None`

**位置**: [adapters/byapi/byapi_mapping_optimized.py:125]

根据API名称获取API文档信息

##### `get_column_name_mapping(api_name)` → `None`

**位置**: [adapters/byapi/byapi_mapping_optimized.py:139]

根据API名称获取列名映射

---

### adapters.byapi.byapi_mapping_updated

**文件**: `adapters/byapi/byapi_mapping_updated.py`

**说明**:

API映射配置文件
根据byapi_info_all.md文档中的接口定义，提供API接口的类型、名称、URL、描述及返回字段映射。

#### 函数

##### `get_api_info(api_type=None, api_name=None, api_url=None)` → `None`

**位置**: [adapters/byapi/byapi_mapping_updated.py:2348]

根据API类型、名称或URL获取API接口信息

参数:
    api_type: API类型
    api_name: API名称
    api_url: API URL
    
返回:
    dict: API接口信息

##### `get_all_api_types()` → `None`

**位置**: [adapters/byapi/byapi_mapping_updated.py:2369]

获取所有API类型

返回:
    list: 所有API类型的列表

##### `get_api_names_by_type(api_type)` → `None`

**位置**: [adapters/byapi/byapi_mapping_updated.py:2379]

获取特定类型的所有API名称

参数:
    api_type: API类型
    
返回:
    list: 特定类型的所有API名称列表

##### `get_field_mapping(api_type, api_name)` → `None`

**位置**: [adapters/byapi/byapi_mapping_updated.py:2394]

获取特定API的字段映射

参数:
    api_type: API类型
    api_name: API名称
    
返回:
    dict: 字段映射字典

##### `get_api_documentation(api_name)` → `None`

**位置**: [adapters/byapi/byapi_mapping_updated.py:2410]

根据API名称获取API文档信息

参数:
    api_name: API中文名称
    
返回:
    dict: 包含API文档信息的字典

---

### adapters.byapi.byapi_new_updated

**文件**: `adapters/byapi/byapi_new_updated.py`

#### 类

##### `ApiInfoReader`

用于读取和解析api_info.json文件的类
提供方法来获取api_links和tables数据，并支持通过api_mapping.json中的键进行访问

**方法**:

- `__init__(self, api_info_path, api_mapping_path=None)` → `None` [adapters/byapi/byapi_new_updated.py:215]
  - 初始化ApiInfoReader类
- `read_api_info_file(self)` → `None` [adapters/byapi/byapi_new_updated.py:230]
  - 读取api_info.json文件内容
- `read_api_mapping_file(self)` → `None` [adapters/byapi/byapi_new_updated.py:259]
  - 读取api_mapping.json文件内容
- `_init_mappings(self)` → `None` [adapters/byapi/byapi_new_updated.py:288]
  - 初始化api_links和tables的映射关系
- `get_api_links(self, key=None)` → `None` [adapters/byapi/byapi_new_updated.py:330]
  - 获取api_links数据，支持通过key参数过滤特定的api_link
- `get_tables(self, key=None, export="json")` → `None` [adapters/byapi/byapi_new_updated.py:359]
  - 获取tables的headers数据，支持通过key参数过滤特定表格的headers，并支持不同的输出格式

##### `ByapiInfo`

BYAPI接口管理类 - 基于新的API映射关系更新

**方法**:

- `__init__(self, licence: str)` → `None` [adapters/byapi/byapi_new_updated.py:431]
  - 初始化API管理器
- `_get_stock_code_without_suffix(self, stock_code: str)` → `str` [adapters/byapi/byapi_new_updated.py:527]
  - 移除股票代码中的市场后缀
- `get_api_links(self, key=None)` → `None` [adapters/byapi/byapi_new_updated.py:540]
  - 获取API链接信息
- `get_tables(self, key=None, export="json")` → `None` [adapters/byapi/byapi_new_updated.py:559]
  - 获取表格定义信息
- `_request(self, url: str)` → `Dict[(Any, Any)]` [adapters/byapi/byapi_new_updated.py:582]
  - 发送HTTP请求并返回JSON数据
- `_to_dataframe(self, json_data: Any, func_name: str, col_name: bool = False)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:623]
  - 将JSON数据转换为DataFrame
- `__call__(self, api_name: str, *args, **kwargs)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:732]
  - 通过中文名称调用API接口
- `stock_list(self, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:760]
  - 获取基础的股票代码和名称，用于后续接口的参数传入
- `new_stock_calendar(self, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:766]
  - 新股日历，按申购日期倒序
- `index_industry_concept_tree(self, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:774]
  - 获取指数、行业、概念（包括基金，债券，美股，外汇，期货，黄金等的代码）
- `stocks_by_index_industry_concept(self, code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:780]
  - 根据"指数、行业、概念树"接口得到的代码作为参数，得到相关的股票
- `index_industry_concept_by_stock(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:786]
  - 根据《股票列表》得到的股票代码作为参数，得到相关的指数、行业、概念
- `limit_up_stocks(self, date: str = "", col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:798]
  - 根据日期获取每天的涨停股票列表，根据封板时间升序
- `limit_down_stocks(self, date: str = "", col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:807]
  - 根据日期获取每天的跌停股票列表，根据封单资金升序
- `strong_stocks(self, date: str = "", col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:816]
  - 根据日期获取每天的强势股票列表，根据涨幅倒序
- `new_stocks(self, date: str = "", col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:825]
  - 根据日期获取每天的次新股票列表，根据开板几日升序
- `broken_limit_stocks(self, date: str = "", col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:834]
  - 根据日期获取每天的炸板股票列表，根据首次封板时间升序
- `company_profile(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:845]
  - 根据股票代码获取上市公司的简介
- `index_membership(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:853]
  - 根据股票代码获取上市公司所属的指数信息
- `executive_history(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:861]
  - 根据股票代码获取上市公司历届高管成员信息
- `board_history(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:869]
  - 根据股票代码获取上市公司历届董事会成员信息
- `supervisory_history(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:877]
  - 根据股票代码获取上市公司历届监事会成员信息
- `recent_dividends(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:885]
  - 根据股票代码获取上市公司近年分红信息
- `recent_seo(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:893]
  - 根据股票代码获取上市公司近年增发信息
- `lifted_shares(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:901]
  - 根据股票代码获取上市公司解禁限售信息
- `quarterly_profits(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:909]
  - 根据股票代码获取上市公司近一年各季度利润信息
- `quarterly_cashflow(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:917]
  - 根据股票代码获取上市公司近一年各季度现金流信息
- `earnings_forecast(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:925]
  - 根据股票代码获取上市公司近年业绩预告信息
- `financial_indicators(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:933]
  - 根据股票代码获取上市公司的财务指标数据
- `top_shareholders(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:941]
  - 根据股票代码获取上市公司的十大股东信息
- `top_float_shareholders(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:949]
  - 根据股票代码获取上市公司的十大流通股东信息
- `shareholder_trend(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:957]
  - 根据股票代码获取上市公司的股东变化趋势信息
- `fund_ownership(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:965]
  - 根据股票代码获取上市公司的基金持股信息
- `realtime_quotes_public(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:975]
  - 获取单个股票的实时交易公开数据（不需要授权）
- `intraday_transactions(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:983]
  - 获取当天的逐笔交易数据
- `realtime_quotes(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:991]
  - 获取单个股票的实时交易数据
- `five_level_quotes(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:999]
  - 获取单个股票的买卖五档盘口数据
- `multi_stock_realtime(self, stock_codes: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1008]
  - 获取多个股票的实时交易数据，股票代码用逗号分隔
- `fund_flow_data(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1014]
  - 获取单个股票的资金流向数据
- `latest_minute_quotes(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1024]
  - 获取单个股票的最新分时交易数据
- `history_minute_quotes(self, stock_code: str, date: str = "", col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1032]
  - 获取单个股票的历史分时交易数据
- `history_limit_prices(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1042]
  - 获取单个股票的历史涨跌停价格数据
- `market_indicators(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1050]
  - 获取单个股票的行情指标数据
- `stock_basic_info(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1060]
  - 获取单个股票的基础信息
- `balance_sheet(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1070]
  - 获取单个股票的资产负债表数据
- `income_statement(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1077]
  - 获取单个股票的利润表数据
- `cash_flow_statement(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1084]
  - 获取单个股票的现金流量表数据
- `financial_ratios(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1092]
  - 获取单个股票的财务主要指标数据
- `capital_structure(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1100]
  - 获取单个股票的公司股本表数据
- `company_top_shareholders(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1108]
  - 获取单个股票的公司十大股东数据
- `company_top_float_holders(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1116]
  - 获取单个股票的公司十大流通股东数据
- `shareholder_count(self, stock_code: str, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1124]
  - 获取单个股票的公司股东数数据
- `history_macd(self, stock_code: str, level: str = "d", adj_type: str = "n", start_time: str = "", end_time: str = "", limit: int = 0, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1134]
  - 获取单个股票的历史分时MACD数据
- `history_ma(self, stock_code: str, level: str = "d", adj_type: str = "n", start_time: str = "", end_time: str = "", limit: int = 0, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1165]
  - 获取单个股票的历史分时MA数据
- `history_boll(self, stock_code: str, level: str = "d", adj_type: str = "n", start_time: str = "", end_time: str = "", limit: int = 0, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1198]
  - 获取单个股票的历史分时BOLL数据
- `history_kdj(self, stock_code: str, level: str = "d", adj_type: str = "n", start_time: str = "", end_time: str = "", limit: int = 0, col_name: bool = True)` → `pd.DataFrame` [adapters/byapi/byapi_new_updated.py:1231]
  - 获取单个股票的历史分时KDJ数据
- `_get_stock_code_without_suffix(self, stock_code: str)` → `str` [adapters/byapi/byapi_new_updated.py:1266]
  - 去除股票代码中的市场后缀
- `get_supported_apis(self)` → `List[Dict[(str, str)]]` [adapters/byapi/byapi_new_updated.py:1272]
  - 获取所有支持的API名称列表，格式为中文名:英文函数名的映射
- `get_api_documentation(self, api_name: str)` → `Dict[(str, Any)]` [adapters/byapi/byapi_new_updated.py:1277]
  - 获取API的文档信息

#### 函数

##### `json_to_dict(json_data)` → `None`

**位置**: [adapters/byapi/byapi_new_updated.py:56]

将JSON格式的headers数据转换为字段信息字典

Args:
    json_data: JSON格式的headers数据，可能是一个列表的字典，也可能是扁平的列表

Returns:
    dict: 转换后的字段信息字典，key为字段名，value为包含字段描述、数据类型等信息的字典

Raises:
    TypeError: 当json_data不是列表时抛出
    Exception: 其他转换错误

##### `dict_to_df(field_dict)` → `None`

**位置**: [adapters/byapi/byapi_new_updated.py:136]

将字段信息字典转换为pandas DataFrame

Args:
    field_dict: 字段信息字典，key为字段名，value为包含字段描述、数据类型等信息的字典

Returns:
    pandas.DataFrame: 转换后的DataFrame，每行代表一个字段的信息

Raises:
    TypeError: 当field_dict不是字典时抛出
    ImportError: 当pandas库不可用时抛出
    Exception: 其他转换错误

---

### adapters.byapi.load_json_1by1

**文件**: `adapters/byapi/load_json_1by1.py`

#### 类

##### `load_json`

**方法**:

- `__init__(self, file_path, api_key=None, item=None)` → `None` [adapters/byapi/load_json_1by1.py:29]
  - 初始化load_json类
- `read_json(self)` → `None` [adapters/byapi/load_json_1by1.py:47]
  - 读取JSON文件并解析数据
- `__getattr__(self, name)` → `None` [adapters/byapi/load_json_1by1.py:81]
  - 允许通过点操作符访问JSON数据中的属性

---

### adapters.byapi_adapter

**文件**: `adapters/byapi_adapter.py`

**说明**:

# 功能：Byapi (biyingapi.com) 数据源适配器，提供A股实时行情、K线和财务数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2024-08-29
# 版本：2.1.0
# 依赖：requests, pandas (详见requirements.txt)
# 注意事项：
#   - API License: 04C01BF1-7F2F-41A3-B470-1F81F14B1FC8
#   - 内置频率控制: 300请求/分钟 (0.2s间隔)
#   - 支持A股市场，实时行情+历史K线+财务报表+涨跌停股池
#   - 辅助文件位于adapters/byapi/目录 (API文档和映射表)
# 版权：MyStocks Project © 2025

#### 类

##### `DataSourceError`

数据源异常

**继承**: `Exception`

##### `IDataSource`

数据源统一接口

**继承**: `ABC`

**方法**:

- `source_name(self)` → `str` [adapters/byapi_adapter.py:33]
  - 数据源名称
- `supported_markets(self)` → `List[str]` [adapters/byapi_adapter.py:39]
  - 支持的市场列表
- `get_kline_data(self, symbol: str, start_date: str, end_date: str, frequency: str = "daily")` → `pd.DataFrame` [adapters/byapi_adapter.py:44]
  - 获取K线数据
- `get_realtime_quotes(self, symbols: List[str])` → `pd.DataFrame` [adapters/byapi_adapter.py:55]
  - 获取实时行情
- `get_fundamental_data(self, symbol: str, report_period: str, data_type: str = "income")` → `pd.DataFrame` [adapters/byapi_adapter.py:60]
  - 获取财务数据
- `get_stock_list(self)` → `pd.DataFrame` [adapters/byapi_adapter.py:70]
  - 获取股票列表

##### `ByapiAdapter`

Byapi (biyingapi.com) 数据源适配器

特点:
- 支持A股市场全量数据
- 提供实时行情和历史K线
- 包含完整的财务报表数据
- 内置频率控制 (300请求/分钟)

Args:
    licence: biyingapi.com API许可证
    base_url: API基础URL (默认: http://api.biyingapi.com)
    min_interval: 最小请求间隔秒数 (默认: 0.2s, 对应300次/分钟)

**继承**: `IDataSource`

**方法**:

- `__init__(self, licence: str = "04C01BF1-7F2F-41A3-B470-1F81F14B1FC8", base_url: str = "http://api.biyingapi.com", min_interval: float = 0.2)` → `None` [adapters/byapi_adapter.py:91]
- `source_name(self)` → `str` [adapters/byapi_adapter.py:124]
- `supported_markets(self)` → `List[str]` [adapters/byapi_adapter.py:128]
- `_standardize_symbol(self, symbol: str)` → `str` [adapters/byapi_adapter.py:131]
  - 标准化股票代码格式
- `_rate_limit(self)` → `None` [adapters/byapi_adapter.py:152]
  - 控制API请求频率
- `_request(self, url: str, timeout: int = 30)` → `Dict[(Any, Any)]` [adapters/byapi_adapter.py:162]
  - 发送HTTP请求并返回JSON数据
- `get_stock_list(self)` → `pd.DataFrame` [adapters/byapi_adapter.py:187]
  - 获取股票列表
- `get_kline_data(self, symbol: str, start_date: str, end_date: str, frequency: str = "daily")` → `pd.DataFrame` [adapters/byapi_adapter.py:235]
  - 获取K线数据
- `get_realtime_quotes(self, symbols: List[str])` → `pd.DataFrame` [adapters/byapi_adapter.py:306]
  - 获取实时行情
- `get_fundamental_data(self, symbol: str, report_period: str, data_type: str = "income")` → `pd.DataFrame` [adapters/byapi_adapter.py:371]
  - 获取财务数据
- `get_limit_up_stocks(self, trade_date: str)` → `pd.DataFrame` [adapters/byapi_adapter.py:433]
  - 获取涨停股池 (byapi特有功能)
- `get_limit_down_stocks(self, trade_date: str)` → `pd.DataFrame` [adapters/byapi_adapter.py:461]
  - 获取跌停股池 (byapi特有功能)
- `get_technical_indicator(self, symbol: str, indicator: str, frequency: str = "daily", start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 100)` → `pd.DataFrame` [adapters/byapi_adapter.py:489]
  - 获取技术指标 (byapi特有功能)

---

### adapters.customer_adapter

**文件**: `adapters/customer_adapter.py`

**说明**:

# 功能：自定义数据源适配器，支持用户扩展数据源
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `CustomerDataSource`

Customer数据源实现（统一管理efinance和easyquotation）

属性:
    efinance_available (bool): efinance库是否可用
    easyquotation_available (bool): easyquotation库是否可用
    use_column_mapping (bool): 是否使用列名映射标准化

**继承**: `IDataSource`

**方法**:

- `__init__(self, use_column_mapping: bool = True)` → `None` [adapters/customer_adapter.py:42]
  - 初始化Customer数据源
- `_standardize_dataframe(self, df: pd.DataFrame, data_type: str = "stock_daily")` → `pd.DataFrame` [adapters/customer_adapter.py:79]
  - 标准化DataFrame列名
- `get_stock_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/customer_adapter.py:93]
  - 获取股票日线数据-Customer实现
- `get_index_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/customer_adapter.py:129]
  - 获取指数日线数据-Customer实现
- `get_stock_basic(self, symbol: str)` → `Dict` [adapters/customer_adapter.py:148]
  - 获取股票基本信息-Customer实现
- `get_index_components(self, symbol: str)` → `List[str]` [adapters/customer_adapter.py:168]
  - 获取指数成分股-Customer实现
- `get_real_time_data(self, symbol: str)` → `Union[(pd.DataFrame, Dict, str)]` [adapters/customer_adapter.py:187]
  - 获取实时数据-Customer实现（重点实现efinance的沪深市场A股最新状况功能）
- `get_market_realtime_quotes(self)` → `pd.DataFrame` [adapters/customer_adapter.py:332]
  - 专门获取沪深市场A股最新状况的方法
- `get_market_calendar(self, start_date: str, end_date: str)` → `Union[(pd.DataFrame, str)]` [adapters/customer_adapter.py:341]
  - 获取交易日历-Customer实现
- `get_financial_data(self, symbol: str, period: str = "annual")` → `Union[(pd.DataFrame, str)]` [adapters/customer_adapter.py:349]
  - 获取财务数据-Customer实现
- `get_news_data(self, symbol: Optional[str] = None, limit: int = 10)` → `Union[(List[Dict], str)]` [adapters/customer_adapter.py:373]
  - 获取新闻数据-Customer实现

---

### adapters.data_source_manager

**文件**: `adapters/data_source_manager.py`

**说明**:

# 功能：数据源管理器，统一管理多个数据源适配器的生命周期
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `DataSourceManager`

数据源管理器

功能:
1. 统一管理多个数据源适配器
2. 数据源优先级和故障转移
3. 数据验证和质量检查
4. 缓存和性能优化

使用示例:
    >>> manager = DataSourceManager()
    >>> manager.register_source('tdx', TdxDataSource())
    >>> manager.register_source('akshare', AkshareDataSource())
    >>>
    >>> # 获取实时行情(优先使用TDX)
    >>> quote = manager.get_real_time_data('600519', source='tdx')
    >>>
    >>> # 获取历史数据(自动故障转移)
    >>> df = manager.get_stock_daily('600519', '2024-01-01', '2024-12-31')

**方法**:

- `__init__(self)` → `None` [adapters/data_source_manager.py:45]
  - 初始化数据源管理器
- `register_source(self, name: str, source: IDataSource)` → `None` [adapters/data_source_manager.py:61]
  - 注册数据源适配器
- `get_source(self, name: str)` → `Optional[IDataSource]` [adapters/data_source_manager.py:75]
  - 获取指定数据源
- `list_sources(self)` → `List[str]` [adapters/data_source_manager.py:87]
  - 获取所有已注册的数据源名称
- `get_real_time_data(self, symbol: str, source: Optional[str] = None)` → `Union[(Dict, str)]` [adapters/data_source_manager.py:93]
  - 获取实时行情数据
- `get_stock_daily(self, symbol: str, start_date: str, end_date: str, source: Optional[str] = None)` → `pd.DataFrame` [adapters/data_source_manager.py:136]
  - 获取股票日线数据
- `get_index_daily(self, symbol: str, start_date: str, end_date: str, source: Optional[str] = None)` → `pd.DataFrame` [adapters/data_source_manager.py:182]
  - 获取指数日线数据
- `get_stock_basic(self, symbol: str, source: Optional[str] = None)` → `Dict` [adapters/data_source_manager.py:230]
  - 获取股票基本信息
- `get_financial_data(self, symbol: str, period: str = "quarter", source: Optional[str] = None)` → `pd.DataFrame` [adapters/data_source_manager.py:249]
  - 获取财务数据
- `get_index_components(self, symbol: str, source: Optional[str] = None)` → `List[str]` [adapters/data_source_manager.py:273]
  - 获取指数成分股
- `set_priority(self, data_type: str, priority_list: List[str])` → `None` [adapters/data_source_manager.py:292]
  - 设置数据源优先级

#### 函数

##### `get_default_manager()` → `DataSourceManager`

**位置**: [adapters/data_source_manager.py:307]

获取默认配置的数据源管理器

自动注册TDX和AKShare数据源

Returns:
    DataSourceManager实例

---

### adapters.financial_adapter

**文件**: `adapters/financial_adapter.py`

**说明**:

# 功能：财务数据适配器，整合多源财务报表和指标数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `FinancialDataSource`

财务数据适配器 - 参考数据/基本面数据统一门户

数据分类: DataClassification.FUNDAMENTAL_METRICS (第2类-参考数据-基本面数据)
存储目标: MySQL/MariaDB
数据特性: 低频、结构化、关系型

多数据源整合:
- 当前实现: efinance(主要) + easyquotation(备用)
- 计划扩展: akshare、tushare、byapi、新浪财经爬虫

核心能力:
- 统一的财务数据获取接口
- 多数据源自动降级切换
- 数据验证和清洗
- 智能缓存机制

**继承**: `IDataSource`

**方法**:

- `__init__(self)` → `None` [adapters/financial_adapter.py:88]
  - 初始化财务数据适配器
- `_get_cache_key(self, symbol: str, data_type: str, **kwargs)` → `str` [adapters/financial_adapter.py:109]
  - 生成缓存键
- `_get_from_cache(self, cache_key: str)` → `None` [adapters/financial_adapter.py:128]
  - 从缓存中获取数据
- `_save_to_cache(self, cache_key: str, data)` → `None` [adapters/financial_adapter.py:149]
  - 保存数据到缓存
- `_init_data_sources(self)` → `None` [adapters/financial_adapter.py:163]
  - 初始化多数据源
- `get_stock_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/financial_adapter.py:196]
  - 获取股票日线数据
- `_rename_columns(self, data: pd.DataFrame)` → `pd.DataFrame` [adapters/financial_adapter.py:339]
  - 重命名列名以匹配预期格式
- `get_index_daily(self, index_code, start_date=None, end_date=None)` → `None` [adapters/financial_adapter.py:365]
  - 获取指数日线数据
- `get_stock_basic(self, symbol: str)` → `Dict` [adapters/financial_adapter.py:451]
  - 获取股票基本信息
- `get_index_components(self, index_code)` → `None` [adapters/financial_adapter.py:539]
  - 获取指数的成分股数据
- `get_real_time_data(self, symbol: str = None)` → `pd.DataFrame` [adapters/financial_adapter.py:587]
  - 获取实时数据（仅支持A股市场）
- `get_financial_data(self, symbol: str, period: str = "annual")` → `pd.DataFrame` [adapters/financial_adapter.py:725]
  - 获取股票财务数据
- `get_market_calendar(self)` → `pd.DataFrame` [adapters/financial_adapter.py:846]
  - 获取交易日历
- `get_news_data(self, symbol: str)` → `pd.DataFrame` [adapters/financial_adapter.py:891]
  - 获取股票新闻数据
- `_validate_and_clean_data(self, data: pd.DataFrame, data_type: str = "stock")` → `pd.DataFrame` [adapters/financial_adapter.py:940]
  - 验证和清洗数据

---

### adapters.financial_adapter_example

**文件**: `adapters/financial_adapter_example.py`

**说明**:

Financial适配器使用示例
展示如何使用FinancialDataSource类获取各种金融数据

#### 函数

##### `main()` → `None`

**位置**: [adapters/financial_adapter_example.py:18]

主函数：演示Financial适配器的使用方法

---

### adapters.tdx_adapter

**文件**: `adapters/tdx_adapter.py`

**说明**:

# 功能：通达信(TDX)数据源适配器，提供实时行情和多周期K线数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `TdxDataSource`

TDX(通达信)数据源适配器

实现IDataSource接口,提供A股市场数据访问:
- 实时行情 (get_real_time_data)
- 历史日线 (get_stock_daily, get_index_daily)
- 财务数据 (get_financial_data - 有限支持)
- 板块信息 (get_index_components - 有限支持)

特点:
- 直连通达信服务器,无API限流
- 使用本地pytdx代码(temp/pytdx/),可二次开发
- 自动重试、连接管理、数据验证
- 完整日志记录

限制:
- 仅支持A股(深交所+上交所),不含期货/期权
- 部分IDataSource方法为stub实现(get_market_calendar, get_news_data)

**继承**: `IDataSource`

**方法**:

- `__init__(self, tdx_host: str = None, tdx_port: int = None, max_retries: int = None, retry_delay: int = None, api_timeout: int = None, use_server_config: bool = True)` → `None` [adapters/tdx_adapter.py:56]
  - 初始化TDX数据源适配器
- `_get_tdx_connection(self)` → `None` [adapters/tdx_adapter.py:107]
  - 获取TDX连接(上下文管理器)
- `_get_market_code(self, symbol: str)` → `int` [adapters/tdx_adapter.py:122]
  - 识别股票代码对应的市场类型
- `_retry_api_call(self, func)` → `None` [adapters/tdx_adapter.py:157]
  - API调用重试装饰器(带指数退避和服务器故障转移)
- `_validate_kline_data(self, df: pd.DataFrame)` → `pd.DataFrame` [adapters/tdx_adapter.py:207]
  - 验证K线数据完整性和合法性
- `get_stock_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/tdx_adapter.py:255]
  - 获取股票日线数据
- `get_index_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/tdx_adapter.py:404]
  - 获取指数日线数据
- `get_stock_basic(self, symbol: str)` → `Dict` [adapters/tdx_adapter.py:556]
  - 获取股票基本信息 - Phase 6实现(有限支持)
- `get_index_components(self, symbol: str)` → `List[str]` [adapters/tdx_adapter.py:561]
  - 获取指数成分股 - Phase 7实现(有限支持)
- `get_real_time_data(self, symbol: str)` → `Union[(Dict, str)]` [adapters/tdx_adapter.py:566]
  - 获取实时行情数据
- `get_market_calendar(self, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/tdx_adapter.py:683]
  - 获取交易日历 - Phase 8 stub实现(TDX不支持)
- `get_financial_data(self, symbol: str, period: str = "quarter")` → `pd.DataFrame` [adapters/tdx_adapter.py:688]
  - 获取财务数据 - Phase 6实现(有限支持)
- `get_news_data(self, symbol: str, limit: int = 20)` → `List[Dict]` [adapters/tdx_adapter.py:693]
  - 获取新闻数据 - Phase 8 stub实现(TDX不支持)
- `get_stock_kline(self, symbol: str, start_date: str, end_date: str, period: str = "1d")` → `pd.DataFrame` [adapters/tdx_adapter.py:700]
  - 获取股票K线数据(支持多种周期)
- `get_index_kline(self, symbol: str, start_date: str, end_date: str, period: str = "1d")` → `pd.DataFrame` [adapters/tdx_adapter.py:841]
  - 获取指数K线数据(支持多种周期)
- `read_day_file(self, file_path: str)` → `pd.DataFrame` [adapters/tdx_adapter.py:955]
  - 读取通达信二进制 .day 文件

---

### adapters.test_customer_adapter

**文件**: `adapters/test_customer_adapter.py`

**说明**:

Customer 数据源适配器测试脚本
测试 efinance 和 easyquotation 数据源的功能

示例用法：
    >>> python test_customer_adapter.py

#### 函数

##### `test_customer_data_source()` → `None`

**位置**: [adapters/test_customer_adapter.py:20]

测试Customer数据源

---

### adapters.test_financial_adapter

**文件**: `adapters/test_financial_adapter.py`

**说明**:

Financial适配器测试文件
用于测试FinancialDataSource类的功能

#### 函数

##### `test_financial_adapter()` → `None`

**位置**: [adapters/test_financial_adapter.py:18]

测试Financial适配器

---

### adapters.test_simple

**文件**: `adapters/test_simple.py`

**说明**:

简化测试脚本，用于检查Customer适配器是否能正常导入和初始化

---

### adapters.tushare_adapter

**文件**: `adapters/tushare_adapter.py`

**说明**:

Tushare 数据源适配器
实现了统一数据接口，提供 Tushare 数据访问

使用前需要：
1. 安装 tushare: pip install tushare
2. 申请 Tushare Token
3. 设置环境变量: TUSHARE_TOKEN=your_token

#### 类

##### `TushareDataSource`

Tushare数据源实现

**继承**: `IDataSource`

**方法**:

- `__init__(self)` → `None` [adapters/tushare_adapter.py:25]
- `get_stock_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/tushare_adapter.py:43]
  - 获取股票日线数据-Tushare实现
- `get_index_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [adapters/tushare_adapter.py:76]
  - 获取指数日线数据-Tushare实现
- `get_stock_basic(self, symbol: str)` → `Dict` [adapters/tushare_adapter.py:108]
  - 获取股票基本信息-Tushare实现
- `get_index_components(self, symbol: str)` → `List[str]` [adapters/tushare_adapter.py:126]
  - 获取指数成分股-Tushare实现
- `get_real_time_data(self, symbol: str)` → `Union[(Dict, str)]` [adapters/tushare_adapter.py:143]
  - 获取实时数据-Tushare实现
- `get_market_calendar(self, start_date: str, end_date: str)` → `Union[(pd.DataFrame, str)]` [adapters/tushare_adapter.py:148]
  - 获取交易日历-Tushare实现
- `get_financial_data(self, symbol: str, period: str = "annual")` → `Union[(pd.DataFrame, str)]` [adapters/tushare_adapter.py:161]
  - 获取财务数据-Tushare实现
- `get_news_data(self, symbol: Optional[str] = None, limit: int = 10)` → `Union[(List[Dict], str)]` [adapters/tushare_adapter.py:177]
  - 获取新闻数据-Tushare实现
- `_format_symbol_for_tushare(self, symbol: str)` → `str` [adapters/tushare_adapter.py:182]
  - 格式化股票代码为Tushare格式
- `_format_index_for_tushare(self, symbol: str)` → `str` [adapters/tushare_adapter.py:192]
  - 格式化指数代码为Tushare格式

---

### automation.__init__

**文件**: `automation/__init__.py`

**说明**:

自动化调度系统 (Automation and Scheduling System)

提供量化交易系统的自动化任务调度功能:
- 定时数据更新
- 策略自动执行
- 交易信号通知
- 任务监控和日志

主要组件:
- TaskScheduler: 任务调度器
- NotificationManager: 通知管理器
- PredefinedTasks: 预定义任务

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

---

### automation.notification_manager

**文件**: `automation/notification_manager.py`

**说明**:

通知管理器 (Notification Manager)

功能说明:
- 多渠道通知发送（邮件、Webhook、日志）
- 通知模板管理
- 通知历史记录
- 通知过滤和频率限制

支持的通知渠道:
- Email: SMTP邮件通知
- Webhook: HTTP POST到指定URL
- Log: 记录到日志文件
- Console: 控制台输出（开发调试）

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `NotificationChannel`

通知渠道

**继承**: `Enum`

##### `NotificationLevel`

通知级别

**继承**: `Enum`

##### `NotificationConfig`

通知配置

##### `Notification`

通知记录

##### `NotificationManager`

通知管理器

功能:
- 多渠道通知发送
- 通知模板
- 频率限制
- 发送历史

**方法**:

- `__init__(self, config: Optional[NotificationConfig] = None)` → `None` [automation/notification_manager.py:114]
  - 初始化通知管理器
- `send_notification(self, title: str, message: str, level: NotificationLevel = ..., context: Optional[Dict] = None, channels: Optional[List[NotificationChannel]] = None)` → `bool` [automation/notification_manager.py:143]
  - 发送通知
- `send_success_notification(self, task_name: str, execution_time: float, result: Any = None)` → `None` [automation/notification_manager.py:218]
  - 发送任务成功通知
- `send_failure_notification(self, task_name: str, error_message: str, retry_count: int = 0)` → `None` [automation/notification_manager.py:236]
  - 发送任务失败通知
- `send_signal_notification(self, strategy_name: str, symbol: str, signal: str, price: float, context: Optional[Dict] = None)` → `None` [automation/notification_manager.py:259]
  - 发送交易信号通知
- `_send_email(self, notification: Notification)` → `None` [automation/notification_manager.py:296]
  - 发送邮件通知
- `_send_webhook(self, notification: Notification)` → `None` [automation/notification_manager.py:329]
  - 发送Webhook通知
- `_send_log(self, notification: Notification)` → `None` [automation/notification_manager.py:358]
  - 发送日志通知
- `_send_console(self, notification: Notification)` → `None` [automation/notification_manager.py:372]
  - 发送控制台通知
- `_format_html_email(self, notification: Notification)` → `str` [automation/notification_manager.py:386]
  - 格式化HTML邮件
- `_is_rate_limited(self, title: str, message: str)` → `bool` [automation/notification_manager.py:422]
  - 检查是否达到频率限制
- `_update_rate_limit(self, title: str, message: str)` → `None` [automation/notification_manager.py:433]
  - 更新频率限制追踪
- `get_notification_history(self, level: Optional[NotificationLevel] = None, limit: int = 100)` → `List[Notification]` [automation/notification_manager.py:438]
  - 获取通知历史
- `get_statistics(self)` → `Dict` [automation/notification_manager.py:458]
  - 获取统计信息
- `clear_history(self, days: int = 30)` → `None` [automation/notification_manager.py:466]
  - 清除旧通知历史

---

### automation.predefined_tasks

**文件**: `automation/predefined_tasks.py`

**说明**:

预定义任务 (Predefined Tasks)

功能说明:
- 常用自动化任务的预定义实现
- 数据更新任务
- 策略执行任务
- 信号生成任务
- 系统维护任务

所有任务都遵循统一接口，可直接用于TaskScheduler调度

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `PredefinedTasks`

预定义任务集合

提供常用的自动化任务函数，可直接用于调度器

**方法**:

- `daily_data_update(market: str = "sh", lookback_days: int = 3, unified_manager=None)` → `Dict` [automation/predefined_tasks.py:39]
  - 每日数据更新任务
- `execute_strategy(strategy_name: str, universe: List[str], strategy_executor=None, notification_manager=None)` → `Dict` [automation/predefined_tasks.py:87]
  - 执行策略任务
- `screen_stocks(screener_config: Dict, universe: Optional[List[str]] = None, unified_manager=None)` → `Dict` [automation/predefined_tasks.py:151]
  - 股票筛选任务
- `database_maintenance(unified_manager=None)` → `Dict` [automation/predefined_tasks.py:199]
  - 数据库维护任务
- `generate_daily_report(date: Optional[date] = None, unified_manager=None, notification_manager=None)` → `Dict` [automation/predefined_tasks.py:243]
  - 生成每日报告任务
- `health_check(services: Optional[List[str]] = None)` → `Dict` [automation/predefined_tasks.py:320]
  - 系统健康检查任务

#### 函数

##### `create_daily_update_task(market: str = "sh", hour: int = 16, minute: int = 0)` → `TaskConfig`

**位置**: [automation/predefined_tasks.py:371]

创建每日数据更新任务配置

参数:
    market: 市场代码
    hour: 执行小时（默认16:00，收盘后）
    minute: 执行分钟

返回:
    TaskConfig: 任务配置

##### `create_strategy_execution_task(strategy_name: str, hour: int = 9, minute: int = 30)` → `TaskConfig`

**位置**: [automation/predefined_tasks.py:399]

创建策略执行任务配置

参数:
    strategy_name: 策略名称
    hour: 执行小时（默认9:30，开盘后）
    minute: 执行分钟

返回:
    TaskConfig: 任务配置

##### `create_health_check_task(interval_minutes: int = 30)` → `TaskConfig`

**位置**: [automation/predefined_tasks.py:428]

创建健康检查任务配置

参数:
    interval_minutes: 检查间隔（分钟）

返回:
    TaskConfig: 任务配置

---

### automation.scheduler

**文件**: `automation/scheduler.py`

**说明**:

自动化调度系统 (Automated Scheduling System)

功能说明:
- 定时数据更新和策略执行
- 多任务调度管理
- 任务监控和日志
- 故障重试和通知

使用APScheduler实现灵活的任务调度，支持:
- Cron表达式定时
- 间隔时间调度
- 一次性任务
- 任务链和依赖

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `TaskStatus`

任务状态

**继承**: `Enum`

##### `TaskPriority`

任务优先级

**继承**: `Enum`

##### `TaskConfig`

任务配置

##### `TaskExecution`

任务执行记录

##### `JobLock`

任务锁 - 防止重叠执行

**方法**:

- `__init__(self)` → `None` [automation/scheduler.py:107]
- `acquire(self, job_id: str, timeout: int = 3600)` → `bool` [automation/scheduler.py:111]
  - 获取任务锁
- `release(self, job_id: str)` → `None` [automation/scheduler.py:140]
  - 释放任务锁
- `is_locked(self, job_id: str)` → `bool` [automation/scheduler.py:146]
  - 检查任务是否已锁定

##### `TaskScheduler`

自动化任务调度器

功能:
- 定时任务调度
- 任务重试逻辑
- 执行监控和日志
- 防止重叠执行

**方法**:

- `__init__(self, notification_manager=None, monitoring_db=None)` → `None` [automation/scheduler.py:162]
  - 初始化调度器
- `add_task(self, task_config: TaskConfig)` → `str` [automation/scheduler.py:203]
  - 添加定时任务
- `_create_trigger(self, trigger_type: str, trigger_args: Dict)` → `None` [automation/scheduler.py:249]
  - 创建触发器
- `_wrap_task_function(self, task_config: TaskConfig)` → `Callable` [automation/scheduler.py:258]
  - 包装任务函数，添加锁、重试、监控逻辑
- `_execute_with_retry(self, func: Callable, kwargs: Dict, max_retries: int, retry_delay: int, execution: TaskExecution)` → `Any` [automation/scheduler.py:344]
  - 执行任务，失败时重试（指数退避）
- `_trigger_next_tasks(self, next_task_names: List[str])` → `None` [automation/scheduler.py:384]
  - 触发后续任务
- `_job_listener(self, event)` → `None` [automation/scheduler.py:399]
  - APScheduler事件监听器
- `_log_to_monitoring(self, execution: TaskExecution)` → `None` [automation/scheduler.py:406]
  - 记录到监控数据库
- `start(self)` → `None` [automation/scheduler.py:423]
  - 启动调度器
- `stop(self)` → `None` [automation/scheduler.py:434]
  - 停止调度器
- `get_task_status(self, task_name: str)` → `Optional[TaskStatus]` [automation/scheduler.py:440]
  - 获取任务状态
- `get_execution_history(self, task_name: Optional[str] = None, limit: int = 100)` → `List[TaskExecution]` [automation/scheduler.py:448]
  - 获取执行历史
- `get_statistics(self)` → `Dict` [automation/scheduler.py:468]
  - 获取调度器统计信息
- `pause_task(self, task_name: str)` → `None` [automation/scheduler.py:477]
  - 暂停任务
- `resume_task(self, task_name: str)` → `None` [automation/scheduler.py:483]
  - 恢复任务
- `remove_task(self, task_name: str)` → `None` [automation/scheduler.py:489]
  - 移除任务
- `list_tasks(self)` → `List[Dict]` [automation/scheduler.py:498]
  - 列出所有任务

---

### backtest.__init__

**文件**: `backtest/__init__.py`

---

### backtest.backtest_engine

**文件**: `backtest/backtest_engine.py`

**说明**:

回测引擎主接口 (Backtest Engine)

功能说明:
- 整合向量化回测器、性能指标、风险指标
- 提供统一的回测接口
- 支持单股票和批量回测
- 自动生成完整的回测报告

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `BacktestEngine`

回测引擎 - 策略回测的统一接口

功能:
- 执行向量化回测
- 计算性能和风险指标
- 生成完整回测报告
- 支持基准比较

**方法**:

- `__init__(self, config: Optional[BacktestConfig] = None, risk_free_rate: float = 0.03)` → `None` [backtest/backtest_engine.py:46]
  - 初始化回测引擎
- `run(self, price_data: pd.DataFrame, signals: pd.DataFrame, benchmark_returns: Optional[pd.Series] = None)` → `Dict` [backtest/backtest_engine.py:71]
  - 执行回测
- `get_trades_df(self)` → `pd.DataFrame` [backtest/backtest_engine.py:142]
  - 获取交易记录DataFrame
- `get_equity_curve(self)` → `pd.DataFrame` [backtest/backtest_engine.py:146]
  - 获取权益曲线
- `get_daily_returns(self)` → `pd.Series` [backtest/backtest_engine.py:152]
  - 获取每日收益率
- `save_result(self, filepath: str)` → `None` [backtest/backtest_engine.py:158]
  - 保存回测结果

---

### backtest.vectorized_backtester

**文件**: `backtest/vectorized_backtester.py`

**说明**:

向量化回测引擎 (Vectorized Backtester)

功能说明:
- 基于预计算信号的向量化回测
- 支持多种仓位管理策略
- 自动计算交易成本（佣金、印花税、滑点）
- 生成详细的交易记录和权益曲线
- 性能优于事件驱动回测（10-100x）

设计原理:
- 使用NumPy向量化操作，避免循环
- 预计算所有买卖点位
- 批量计算收益和成本
- 适合已有信号的策略回测

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `BacktestConfig`

回测配置

##### `Trade`

交易记录

##### `VectorizedBacktester`

向量化回测引擎

特点:
- 基于预计算的买卖信号
- 向量化计算，性能优异
- 支持多种仓位管理模式
- 自动计算交易成本

**方法**:

- `__init__(self, config: Optional[BacktestConfig] = None)` → `None` [backtest/vectorized_backtester.py:76]
  - 初始化回测引擎
- `run(self, price_data: pd.DataFrame, signals: pd.DataFrame)` → `Dict` [backtest/vectorized_backtester.py:94]
  - 执行回测
- `_validate_data(self, price_data: pd.DataFrame, signals: pd.DataFrame)` → `None` [backtest/vectorized_backtester.py:316]
  - 验证输入数据
- `_calculate_summary(self)` → `Dict` [backtest/vectorized_backtester.py:329]
  - 计算汇总统计
- `get_trades_df(self)` → `pd.DataFrame` [backtest/vectorized_backtester.py:373]
  - 获取交易记录DataFrame

---

### core.batch_failure_strategy

**文件**: `core/batch_failure_strategy.py`

**说明**:

批量操作失败策略

定义批量数据操作失败时的三种处理策略:
1. ROLLBACK - 回滚整个批次
2. CONTINUE - 跳过失败记录,继续处理
3. RETRY - 自动重试失败记录

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `BatchFailureStrategy`

批量操作失败策略枚举

- ROLLBACK: 任何记录失败则回滚整个批次 (ACID语义)
- CONTINUE: 跳过失败记录,继续处理剩余记录 (最大努力语义)
- RETRY: 自动重试失败记录,使用指数退避 (最终一致性语义)

**继承**: `str`, `Enum`

##### `BatchOperationResult`

批量操作结果

记录批量操作的详细结果,包括成功/失败统计和错误详情

**方法**:

- `__post_init__(self)` → `None` [core/batch_failure_strategy.py:75]
- `success_rate(self)` → `float` [core/batch_failure_strategy.py:82]
  - 成功率 (0.0-1.0)
- `to_dict(self)` → `Dict[(str, Any)]` [core/batch_failure_strategy.py:88]
  - 转换为字典

##### `BatchFailureHandler`

批量失败处理器

提供三种失败策略的具体实现逻辑

**方法**:

- `__init__(self, strategy: BatchFailureStrategy = ..., max_retries: int = 3, retry_delay_base: float = 1.0, retry_delay_multiplier: float = 2.0)` → `None` [core/batch_failure_strategy.py:111]
  - 初始化失败处理器
- `execute_batch(self, data: pd.DataFrame, operation: Callable[(Any, bool)], operation_name: str = "batch_operation")` → `BatchOperationResult` [core/batch_failure_strategy.py:132]
  - 执行批量操作 (根据策略处理失败)
- `_execute_with_rollback(self, data: pd.DataFrame, operation: Callable[(Any, bool)], operation_name: str)` → `BatchOperationResult` [core/batch_failure_strategy.py:176]
  - ROLLBACK策略: 任何失败都回滚整个批次
- `_execute_with_continue(self, data: pd.DataFrame, operation: Callable[(Any, bool)], operation_name: str)` → `BatchOperationResult` [core/batch_failure_strategy.py:229]
  - CONTINUE策略: 逐条处理,跳过失败记录
- `_execute_with_retry(self, data: pd.DataFrame, operation: Callable[(Any, bool)], operation_name: str)` → `BatchOperationResult` [core/batch_failure_strategy.py:279]
  - RETRY策略: 失败记录自动重试 (指数退避)

---

### core.data_storage_strategy

**文件**: `core/data_storage_strategy.py`

**说明**:

数据存储策略

实现23个数据分类到4种数据库的智能路由映射。
基于数据特征(时序性、访问频率、存储周期)自动选择最优数据库。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `DataStorageStrategy`

数据存储策略

根据数据分类的特征自动选择最优存储数据库:
- 高频时序数据 → TDengine (极致压缩 + 高写入性能)
- 历史分析数据 → PostgreSQL+TimescaleDB (复杂查询 + 自动分区)
- 参考元数据 → MySQL/MariaDB (ACID + 复杂JOIN)
- 实时热数据 → Redis (亚毫秒访问)

**方法**:

- `get_target_database(cls, classification: DataClassification)` → `DatabaseTarget` [core/data_storage_strategy.py:76]
  - 根据数据分类获取目标数据库
- `get_classifications_by_database(cls, database: DatabaseTarget)` → `List[DataClassification]` [core/data_storage_strategy.py:98]
  - 获取指定数据库负责的所有数据分类
- `validate_routing_completeness(cls)` → `bool` [core/data_storage_strategy.py:115]
  - 验证路由映射是否完整 (覆盖所有23个数据分类)
- `get_routing_statistics(cls)` → `Dict[(DatabaseTarget, int)]` [core/data_storage_strategy.py:135]
  - 获取路由分布统计
- `print_routing_map(cls)` → `None` [core/data_storage_strategy.py:150]
  - 打印完整的路由映射表 (用于调试和文档)

##### `DataStorageRules`

数据存储规则

定义各数据库的存储策略、保留周期、压缩策略等

**方法**:

- `get_retention_days(cls, classification: DataClassification)` → `Optional[int]` [core/data_storage_strategy.py:215]
  - 获取数据保留天数
- `get_redis_ttl(cls, classification: DataClassification)` → `Optional[int]` [core/data_storage_strategy.py:233]
  - 获取Redis缓存过期时间

---

### create_realtime_quotes_table

**文件**: `create_realtime_quotes_table.py`

**说明**:

创建实时行情数据表

#### 函数

##### `create_realtime_quotes_table()` → `None`

**位置**: [create_realtime_quotes_table.py:15]

创建实时行情数据表

---

### db_manager.save_realtime_market_data_offline

**文件**: `db_manager/save_realtime_market_data_offline.py`

**说明**:

沪深市场A股实时数据保存系统 - 离线版
完全离线运行，只需要efinance库，数据保存到CSV文件

功能特点：
1. 从efinance获取沪深A股实时数据
2. 保存到CSV文件（带时间戳）
3. 自动创建备份目录
4. 支持强制更新
5. 无需任何数据库依赖

适用场景：
- 快速测试和验证
- 数据收集和备份
- 开发环境测试
- 离线数据分析

作者: MyStocks项目组
日期: 2025-09-21
版本: 离线版 v1.0

#### 类

##### `OfflineRealtimeDataSaver`

离线版实时数据保存器 - 只使用CSV文件

**方法**:

- `__init__(self)` → `None` [db_manager/save_realtime_market_data_offline.py:37]
  - 初始化离线版数据保存器
- `_setup_logging(self)` → `None` [db_manager/save_realtime_market_data_offline.py:53]
  - 配置日志系统
- `_create_backup_directory(self)` → `None` [db_manager/save_realtime_market_data_offline.py:66]
  - 创建备份目录
- `check_dependencies(self)` → `bool` [db_manager/save_realtime_market_data_offline.py:76]
  - 检查依赖库
- `get_realtime_market_data(self, market_symbol: str = None)` → `Optional[pd.DataFrame]` [db_manager/save_realtime_market_data_offline.py:106]
  - 获取实时市场数据
- `_validate_data(self, data: pd.DataFrame)` → `None` [db_manager/save_realtime_market_data_offline.py:152]
  - 验证数据质量
- `save_to_csv(self, data: pd.DataFrame, market_symbol: str = None)` → `str` [db_manager/save_realtime_market_data_offline.py:189]
  - 保存数据到CSV文件
- `save_to_json(self, data: pd.DataFrame, market_symbol: str = None)` → `str` [db_manager/save_realtime_market_data_offline.py:211]
  - 保存数据到JSON文件
- `save_to_excel(self, data: pd.DataFrame, market_symbol: str = None)` → `str` [db_manager/save_realtime_market_data_offline.py:242]
  - 保存数据到Excel文件
- `create_summary_report(self, data: pd.DataFrame, saved_files: list)` → `None` [db_manager/save_realtime_market_data_offline.py:267]
  - 创建汇总报告
- `run(self, market_symbol: str = None, force_update: bool = False)` → `bool` [db_manager/save_realtime_market_data_offline.py:305]
  - 运行完整流程

#### 函数

##### `main()` → `None`

**位置**: [db_manager/save_realtime_market_data_offline.py:376]

主函数

---

### examples.automation_example

**文件**: `examples/automation_example.py`

**说明**:

自动化调度系统完整示例 (Automation System Complete Example)

功能说明:
- 演示如何使用TaskScheduler进行任务调度
- 展示NotificationManager的多渠道通知
- 使用预定义任务进行常见操作
- 监控任务执行和性能

使用场景:
1. 每日自动数据更新
2. 定时策略执行和信号生成
3. 系统健康检查和维护
4. 任务失败通知和重试

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 函数

##### `example_1_basic_scheduling()` → `None`

**位置**: [examples/automation_example.py:47]

示例1: 基本任务调度

##### `example_2_notification_system()` → `None`

**位置**: [examples/automation_example.py:89]

示例2: 通知系统

##### `example_3_predefined_tasks()` → `None`

**位置**: [examples/automation_example.py:150]

示例3: 使用预定义任务

##### `example_4_integrated_system()` → `None`

**位置**: [examples/automation_example.py:192]

示例4: 完整集成系统

##### `example_5_monitoring_and_stats()` → `None`

**位置**: [examples/automation_example.py:273]

示例5: 监控和统计

##### `main()` → `None`

**位置**: [examples/automation_example.py:335]

主函数 - 运行所有示例

---

### factory.__init__

**文件**: `factory/__init__.py`

**说明**:

数据源工厂模块
负责创建具体的数据源对象

---

### factory.data_source_factory

**文件**: `factory/data_source_factory.py`

**说明**:

# 功能：数据源工厂类，负责创建和管理数据源适配器实例
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `DataSourceFactory`

数据源工厂：负责创建具体的数据源对象

**方法**:

- `register_source(cls, source_type: str, source_class: Type[IDataSource])` → `None` [factory/data_source_factory.py:63]
  - 注册新的数据源类型
- `register_multiple_sources(cls, sources: Dict[(str, Type[IDataSource])])` → `None` [factory/data_source_factory.py:75]
  - 批量注册多个数据源
- `get_available_sources(cls)` → `List[str]` [factory/data_source_factory.py:86]
  - 获取所有可用的数据源类型
- `unregister_source(cls, source_type: str)` → `bool` [factory/data_source_factory.py:96]
  - 取消注册数据源
- `create_source(cls, source_type: str)` → `IDataSource` [factory/data_source_factory.py:114]
  - 根据类型创建数据源

---

### interfaces.data_source

**文件**: `interfaces/data_source.py`

**说明**:

# 功能：统一数据源接口定义，所有数据源适配器必须实现此接口
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `IDataSource`

统一数据接口：定义所有数据源必须实现的方法

**继承**: `abc.ABC`

**方法**:

- `get_stock_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [interfaces/data_source.py:22]
  - 获取股票日线数据
- `get_index_daily(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [interfaces/data_source.py:37]
  - 获取指数日线数据
- `get_stock_basic(self, symbol: str)` → `Dict` [interfaces/data_source.py:52]
  - 获取股票基本信息
- `get_index_components(self, symbol: str)` → `List[str]` [interfaces/data_source.py:65]
  - 获取指数成分股
- `get_real_time_data(self, symbol: str)` → `Union[(Dict, str)]` [interfaces/data_source.py:78]
  - 获取实时数据
- `get_market_calendar(self, start_date: str, end_date: str)` → `Union[(pd.DataFrame, str)]` [interfaces/data_source.py:91]
  - 获取交易日历
- `get_financial_data(self, symbol: str, period: str = "annual")` → `Union[(pd.DataFrame, str)]` [interfaces/data_source.py:105]
  - 获取财务数据
- `get_news_data(self, symbol: Optional[str] = None, limit: int = 10)` → `Union[(List[Dict], str)]` [interfaces/data_source.py:119]
  - 获取新闻数据

---

### ml_strategy.__init__

**文件**: `ml_strategy/__init__.py`

**说明**:

Machine Learning Strategy Module for MyStocks

This module provides machine learning capabilities for stock price prediction,
feature engineering, and feature selection.

Modules:
    - feature_engineering: Rolling window feature generation
    - price_predictor: LightGBM-based price prediction
    - feature_selector: Multiple feature selection algorithms

Author: MyStocks Development Team
Created: 2025-10-19

---

### ml_strategy.feature_engineering

**文件**: `ml_strategy/feature_engineering.py`

**说明**:

特征工程模块 - 滚动窗口特征生成

基于 PyProf 项目的特征工程方法，扩展为更完整的特征生成系统。
支持滚动窗口特征、技术指标特征和自定义特征。

作者: MyStocks Development Team
创建日期: 2025-10-19
版本: 1.0.0

#### 类

##### `RollingFeatureGenerator`

滚动窗口特征生成器

生成基于历史数据的滚动窗口特征,用于机器学习预测。

主要功能:
- 滚动窗口特征提取
- 技术指标计算
- 特征矩阵构建

示例:
    >>> generator = RollingFeatureGenerator(window_size=10)
    >>> X, y = generator.prepare_ml_data(df, target_col='close', forecast_horizon=1)

**方法**:

- `__init__(self, window_size: int = 10)` → `None` [ml_strategy/feature_engineering.py:39]
  - 初始化特征生成器
- `generate_features(self, df: pd.DataFrame)` → `pd.DataFrame` [ml_strategy/feature_engineering.py:49]
  - 生成滚动窗口特征
- `_extract_window_features(self, window: pd.DataFrame)` → `Dict[(str, float)]` [ml_strategy/feature_engineering.py:88]
  - 从单个窗口提取特征
- `generate_rolling_raw_features(self, df: pd.DataFrame, feature_cols: List[str] = None)` → `pd.DataFrame` [ml_strategy/feature_engineering.py:155]
  - 生成滚动原始特征（PyProf 原始方法）
- `prepare_ml_data(self, df: pd.DataFrame, target_col: str = "close", forecast_horizon: int = 1, feature_type: str = "aggregate")` → `Tuple[(pd.DataFrame, pd.Series)]` [ml_strategy/feature_engineering.py:215]
  - 准备机器学习数据
- `add_technical_indicators(self, df: pd.DataFrame)` → `pd.DataFrame` [ml_strategy/feature_engineering.py:284]
  - 添加技术指标特征

---

### ml_strategy.ml_strategy

**文件**: `ml_strategy/ml_strategy.py`

**说明**:

机器学习策略 (Machine Learning Strategy)

功能说明:
- 基于机器学习的量化策略
- 自动特征工程
- 多种ML模型支持
- 模型训练和预测

支持的模型:
- Random Forest
- Gradient Boosting
- XGBoost / LightGBM
- Neural Networks

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `FeatureEngineering`

特征工程

自动生成技术指标特征

**方法**:

- `create_features(data: pd.DataFrame)` → `pd.DataFrame` [ml_strategy/ml_strategy.py:63]
  - 创建特征
- `create_target(data: pd.DataFrame, forward_days: int = 1, threshold: float = 0.0)` → `pd.Series` [ml_strategy/ml_strategy.py:120]
  - 创建目标变量（分类）

##### `MLStrategy`

机器学习策略

使用机器学习模型预测股票涨跌

**方法**:

- `__init__(self, model_type: str = "random_forest", forward_days: int = 1, threshold: float = 0.01, **kwargs)` → `None` [ml_strategy/ml_strategy.py:146]
  - 初始化ML策略
- `_create_model(self)` → `None` [ml_strategy/ml_strategy.py:189]
  - 创建ML模型
- `train(self, data: pd.DataFrame, test_size: float = 0.2, cross_validate: bool = True)` → `Dict` [ml_strategy/ml_strategy.py:209]
  - 训练模型
- `predict(self, data: pd.DataFrame)` → `pd.DataFrame` [ml_strategy/ml_strategy.py:326]
  - 预测
- `generate_signals(self, data: pd.DataFrame)` → `pd.DataFrame` [ml_strategy/ml_strategy.py:359]
  - 生成交易信号
- `save_model(self, path: str)` → `None` [ml_strategy/ml_strategy.py:390]
  - 保存模型
- `load_model(self, path: str)` → `None` [ml_strategy/ml_strategy.py:409]
  - 加载模型
- `_calculate_metrics(self, y_true, y_pred)` → `Dict` [ml_strategy/ml_strategy.py:425]
  - 计算评估指标

---

### ml_strategy.price_predictor

**文件**: `ml_strategy/price_predictor.py`

**说明**:

价格预测策略模块 - LightGBM 股票价格预测

基于 PyProf 项目的价格预测模型，扩展为完整的预测策略系统。
使用 LightGBM 梯度提升决策树进行回归预测。

主要功能:
- LightGBM 模型训练
- 价格预测
- 超参数调优
- 模型持久化
- 完整的评估指标

作者: MyStocks Development Team
创建日期: 2025-10-19
版本: 1.0.0

#### 类

##### `PricePredictorStrategy`

股票价格预测策略

基于 LightGBM 的价格回归预测模型。

示例:
    >>> predictor = PricePredictorStrategy()
    >>> metrics = predictor.train(X_train, y_train)
    >>> predictions = predictor.predict(X_test)
    >>> predictor.save_model('models/sh000001.pkl')

**方法**:

- `__init__(self, config: Optional[Dict[(str, Any)]] = None)` → `None` [ml_strategy/price_predictor.py:56]
  - 初始化预测器
- `_default_config()` → `Dict[(str, Any)]` [ml_strategy/price_predictor.py:74]
  - 默认 LightGBM 配置（基于 PyProf 项目的优化参数）
- `train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42, validation_split: bool = True)` → `Dict[(str, float)]` [ml_strategy/price_predictor.py:96]
  - 训练模型
- `predict(self, X: pd.DataFrame)` → `np.ndarray` [ml_strategy/price_predictor.py:181]
  - 预测价格
- `predict_with_confidence(self, X: pd.DataFrame, confidence_level: float = 0.95)` → `Tuple[(np.ndarray, np.ndarray, np.ndarray)]` [ml_strategy/price_predictor.py:208]
  - 预测价格并返回置信区间（简化版本）
- `hyperparameter_tuning(self, X: pd.DataFrame, y: pd.Series, param_grid: Optional[Dict[(str, list)]] = None, cv: int = 5, scoring: str = "neg_mean_squared_error")` → `Dict[(str, Any)]` [ml_strategy/price_predictor.py:238]
  - 超参数调优（网格搜索）
- `evaluate(self, X: pd.DataFrame, y: pd.Series)` → `Dict[(str, float)]` [ml_strategy/price_predictor.py:315]
  - 评估模型性能
- `_calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray)` → `Dict[(str, float)]` [ml_strategy/price_predictor.py:341]
  - 计算评估指标
- `save_model(self, file_path: str)` → `None` [ml_strategy/price_predictor.py:375]
  - 保存模型
- `load_model(self, file_path: str)` → `None` [ml_strategy/price_predictor.py:404]
  - 加载模型
- `get_feature_importance(self, feature_names: Optional[list] = None, top_k: int = 10)` → `pd.DataFrame` [ml_strategy/price_predictor.py:428]
  - 获取特征重要性
- `plot_predictions(self, y_true: np.ndarray, y_pred: np.ndarray, save_path: Optional[str] = None)` → `None` [ml_strategy/price_predictor.py:461]
  - 绘制预测结果对比图

---

### realtime.__init__

**文件**: `realtime/__init__.py`

**说明**:

实时数据模块 (Real-time Data Module)

提供实时行情接收和处理功能:
- Tick数据接收
- WebSocket连接管理
- 数据缓存和分发
- 回调函数处理

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

---

### realtime.tick_receiver

**文件**: `realtime/tick_receiver.py`

**说明**:

实时行情接收器 (Real-time Tick Receiver)

功能说明:
- 接收实时tick数据
- WebSocket连接管理
- 数据缓存和分发
- 支持多数据源

支持的数据源:
- TDX实时行情
- 自定义WebSocket源
- Redis发布/订阅

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `DataSourceType`

数据源类型

**继承**: `Enum`

##### `TickData`

Tick数据

##### `TickReceiver`

实时行情接收器

功能:
- 管理多个数据源连接
- 数据缓存和分发
- 回调函数处理
- 线程安全

**方法**:

- `__init__(self, cache_size: int = 1000, source_type: DataSourceType = ...)` → `None` [realtime/tick_receiver.py:87]
  - 初始化接收器
- `subscribe(self, symbols: List[str])` → `None` [realtime/tick_receiver.py:126]
  - 订阅股票
- `unsubscribe(self, symbols: List[str])` → `None` [realtime/tick_receiver.py:139]
  - 取消订阅
- `register_callback(self, callback: Callable[(Any, None)])` → `None` [realtime/tick_receiver.py:147]
  - 注册回调函数
- `start(self)` → `None` [realtime/tick_receiver.py:157]
  - 启动接收器
- `stop(self)` → `None` [realtime/tick_receiver.py:185]
  - 停止接收器
- `_receiver_loop(self)` → `None` [realtime/tick_receiver.py:197]
  - 接收线程主循环
- `_processor_loop(self)` → `None` [realtime/tick_receiver.py:208]
  - 处理线程主循环
- `_receive_from_tdx(self)` → `None` [realtime/tick_receiver.py:229]
  - 从TDX接收数据
- `_receive_from_websocket(self)` → `None` [realtime/tick_receiver.py:237]
  - 从WebSocket接收数据
- `_receive_from_redis(self)` → `None` [realtime/tick_receiver.py:254]
  - 从Redis订阅数据
- `_receive_mock_data(self)` → `None` [realtime/tick_receiver.py:266]
  - 接收模拟数据（用于测试）
- `_cache_tick(self, tick: TickData)` → `None` [realtime/tick_receiver.py:296]
  - 缓存tick数据
- `_invoke_callbacks(self, tick: TickData)` → `None` [realtime/tick_receiver.py:308]
  - 调用所有回调函数
- `_update_stats(self)` → `None` [realtime/tick_receiver.py:316]
  - 更新统计信息
- `get_latest_tick(self, symbol: str)` → `Optional[TickData]` [realtime/tick_receiver.py:321]
  - 获取最新tick数据
- `get_tick_history(self, symbol: str, limit: int = 100)` → `List[TickData]` [realtime/tick_receiver.py:334]
  - 获取历史tick数据
- `get_statistics(self)` → `Dict` [realtime/tick_receiver.py:348]
  - 获取统计信息

---

### run_realtime_market_saver

**文件**: `run_realtime_market_saver.py`

**说明**:

MyStocks 沪深市场A股实时数据保存系统 - 使用efinance和自动路由
通过customer_adapter统一管理efinance数据获取，按自动路由保存到PostgreSQL

执行说明：
python run_realtime_market_saver.py [--interval 60] [--count 1]

作者: MyStocks项目组
日期: 2025-09-24

#### 函数

##### `setup_logging()` → `None`

**位置**: [run_realtime_market_saver.py:29]

设置日志

##### `get_realtime_market_data_via_adapter()` → `None`

**位置**: [run_realtime_market_saver.py:41]

使用customer_adapter获取沪深A股实时行情数据

##### `save_to_auto_routing(data, manager)` → `None`

**位置**: [run_realtime_market_saver.py:69]

使用自动路由保存数据到合适的数据库

##### `run_single_fetch_and_save()` → `None`

**位置**: [run_realtime_market_saver.py:101]

执行单次数据获取和保存

##### `main()` → `None`

**位置**: [run_realtime_market_saver.py:125]

主启动函数

---

### save_realtime_data

**文件**: `save_realtime_data.py`

**说明**:

将通过customer接口获取的股票实时行情数据保存到本地数据库中
完整的数据库保存工作流程，遵循db_manager的工作原理

#### 类

##### `RealtimeDataSaver`

实时数据保存器 - 完整的数据库保存工作流程

**方法**:

- `__init__(self, database_type=DATABASE_TYPE, database_name=DATABASE_NAME, table_name=TABLE_NAME, update_mode=UPDATE_MODE)` → `None` [save_realtime_data.py:52]
  - 初始化数据保存器
- `_validate_dataframe(self, df: pd.DataFrame)` → `bool` [save_realtime_data.py:66]
  - 验证DataFrame数据的有效性
- `_prepare_dataframe(self, df: pd.DataFrame)` → `pd.DataFrame` [save_realtime_data.py:83]
  - 准备和清理DataFrame数据
- `_generate_table_columns(self, df: pd.DataFrame)` → `List[Dict]` [save_realtime_data.py:101]
  - 根据DataFrame生成表列定义
- `_create_table_if_not_exists(self, df: pd.DataFrame)` → `bool` [save_realtime_data.py:148]
  - 如果表不存在则创建表
- `_table_exists(self)` → `bool` [save_realtime_data.py:179]
  - 检查表是否存在
- `_insert_data_batch(self, df: pd.DataFrame)` → `bool` [save_realtime_data.py:205]
  - 批量插入数据
- `save_realtime_data(self, market_symbol: str = MARKET_SYMBOL)` → `bool` [save_realtime_data.py:239]
  - 完整的实时数据保存流程
- `cleanup(self)` → `None` [save_realtime_data.py:281]
  - 清理资源

#### 函数

##### `save_realtime_data_to_db(market_symbol=MARKET_SYMBOL, database_type=DATABASE_TYPE, database_name=DATABASE_NAME, table_name=TABLE_NAME, update_mode=UPDATE_MODE)` → `None`

**位置**: [save_realtime_data.py:290]

将股票实时行情数据保存到数据库 - 向后兼容的函数接口

##### `save_realtime_data_continuous(market_symbol=MARKET_SYMBOL, interval_minutes=5, database_type=DATABASE_TYPE, database_name=DATABASE_NAME, table_name=TABLE_NAME)` → `None`

**位置**: [save_realtime_data.py:307]

连续保存实时数据 - 定时任务模式

---

### strategy.__init__

**文件**: `strategy/__init__.py`

---

### strategy.base_strategy

**文件**: `strategy/base_strategy.py`

**说明**:

策略基类 (Base Strategy Class)

功能说明:
- 提供策略开发的基础框架
- 定义策略必须实现的接口方法
- 提供常用的工具方法和指标计算
- 集成UnifiedDataManager进行数据访问
- 支持参数验证和回测兼容

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `BaseStrategy`

策略基类 - 所有自定义策略必须继承此类

子类必须实现:
    - generate_signals(): 核心信号生成逻辑

子类可选重写:
    - validate_parameters(): 自定义参数验证
    - on_before_execute(): 执行前回调
    - on_after_execute(): 执行后回调

**继承**: `ABC`

**方法**:

- `__init__(self, name: str, version: str, parameters: Dict, unified_manager=None, description: str = "")` → `None` [strategy/base_strategy.py:49]
  - 初始化策略
- `generate_signals(self, data: pd.DataFrame)` → `pd.DataFrame` [strategy/base_strategy.py:93]
  - 核心信号生成方法 - 子类必须实现
- `validate_parameters(self)` → `bool` [strategy/base_strategy.py:130]
  - 参数验证方法 - 子类可重写以添加自定义验证
- `calculate_code_hash(self)` → `str` [strategy/base_strategy.py:152]
  - 计算策略代码的SHA-256哈希值
- `get_market_data(self, symbol: str, start_date: date, end_date: date, frequency: str = "daily")` → `pd.DataFrame` [strategy/base_strategy.py:169]
  - 获取市场数据
- `execute(self, symbols: List[str], start_date: date, end_date: date, **kwargs)` → `Dict` [strategy/base_strategy.py:208]
  - 执行策略对股票池进行筛选
- `on_before_execute(self, symbols: List[str], start_date: date, end_date: date, **kwargs)` → `None` [strategy/base_strategy.py:319]
  - 执行前回调 - 子类可重写
- `on_after_execute(self, result: Dict)` → `None` [strategy/base_strategy.py:331]
  - 执行后回调 - 子类可重写
- `to_dict(self)` → `Dict` [strategy/base_strategy.py:340]
  - 将策略转换为字典格式 (用于数据库存储)
- `__repr__(self)` → `str` [strategy/base_strategy.py:358]

##### `MomentumStrategy`

动量策略示例 - MA交叉 + RSI过滤

策略逻辑:
    - 买入信号: MA5上穿MA20 且 RSI < 30 (超卖)
    - 卖出信号: MA5下穿MA20 或 RSI > 70 (超买)

**继承**: `BaseStrategy`

**方法**:

- `__init__(self, unified_manager=None)` → `None` [strategy/base_strategy.py:375]
- `generate_signals(self, data: pd.DataFrame)` → `pd.DataFrame` [strategy/base_strategy.py:392]
  - 实现信号生成逻辑

---

### strategy.signal_manager

**文件**: `strategy/signal_manager.py`

**说明**:

信号管理器 (Signal Manager)

功能说明:
- 策略信号的持久化存储和查询
- 批量操作优化
- 与UnifiedDataManager集成
- 支持信号统计和分析

数据库:
- PostgreSQL+TimescaleDB (strategy_signals表)
- 通过UnifiedDataManager进行数据访问

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `SignalManager`

信号管理器 - 负责策略信号的存储、查询和管理

功能:
    - 批量保存策略信号到数据库
    - 按条件查询信号
    - 信号统计分析
    - 信号去重和验证

**方法**:

- `__init__(self, unified_manager=None, batch_size: int = 1000)` → `None` [strategy/signal_manager.py:38]
  - 初始化信号管理器
- `save_signals(self, signals: pd.DataFrame, strategy_id: int, batch_insert: bool = True)` → `Dict` [strategy/signal_manager.py:62]
  - 保存策略信号到数据库
- `_save_to_database(self, signals_df: pd.DataFrame)` → `None` [strategy/signal_manager.py:201]
  - 实际保存信号到数据库 (通过UnifiedDataManager)
- `query_signals(self, strategy_id: Optional[int] = None, symbol: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, signal_type: Optional[str] = None, limit: int = 1000, offset: int = 0)` → `pd.DataFrame` [strategy/signal_manager.py:220]
  - 查询策略信号
- `delete_signals(self, strategy_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None)` → `int` [strategy/signal_manager.py:295]
  - 删除策略信号
- `get_signal_statistics(self, strategy_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None)` → `Dict` [strategy/signal_manager.py:352]
  - 获取信号统计信息
- `validate_signal(self, signal: Dict)` → `Tuple[(bool, Optional[str])]` [strategy/signal_manager.py:409]
  - 验证单个信号的有效性
- `get_latest_signals(self, strategy_id: int, limit: int = 10)` → `pd.DataFrame` [strategy/signal_manager.py:450]
  - 获取最新的N个信号
- `get_manager_stats(self)` → `Dict` [strategy/signal_manager.py:477]
  - 获取管理器统计信息

---

### strategy.stock_screener

**文件**: `strategy/stock_screener.py`

**说明**:

股票筛选器 (Stock Screener)

功能说明:
- 根据多维度条件筛选股票池
- 支持市值、行业、价格、成交量等过滤条件
- 排除ST股票、停牌股票等特殊状态
- 与UnifiedDataManager集成获取股票信息

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `ScreeningCriteria`

筛选条件配置

**方法**:

- `__post_init__(self)` → `None` [strategy/stock_screener.py:56]
  - 初始化后处理

##### `StockScreener`

股票筛选器 - 根据条件过滤股票池

功能:
    - 多维度条件筛选
    - ST股票、停牌股票过滤
    - 行业、板块、市值过滤
    - 自定义过滤函数支持

**方法**:

- `__init__(self, unified_manager=None, criteria: Optional[ScreeningCriteria] = None)` → `None` [strategy/stock_screener.py:83]
  - 初始化股票筛选器
- `screen(self, symbols: Optional[List[str]] = None, as_of_date: Optional[date] = None)` → `List[str]` [strategy/stock_screener.py:114]
  - 执行股票筛选
- `_get_all_symbols(self)` → `List[str]` [strategy/stock_screener.py:202]
  - 获取全市场股票列表
- `_get_stock_info(self, symbols: List[str], as_of_date: date)` → `pd.DataFrame` [strategy/stock_screener.py:220]
  - 获取股票基本信息
- `_filter_st_stocks(self, symbols: Set[str], stock_info: pd.DataFrame)` → `Set[str]` [strategy/stock_screener.py:269]
  - 过滤ST股票
- `_filter_suspended_stocks(self, symbols: Set[str], stock_info: pd.DataFrame)` → `Set[str]` [strategy/stock_screener.py:284]
  - 过滤停牌股票
- `_filter_new_stocks(self, symbols: Set[str], stock_info: pd.DataFrame, as_of_date: date)` → `Set[str]` [strategy/stock_screener.py:300]
  - 过滤次新股
- `_filter_by_price(self, symbols: Set[str], stock_info: pd.DataFrame)` → `Set[str]` [strategy/stock_screener.py:324]
  - 按价格过滤
- `_filter_by_volume(self, symbols: Set[str], stock_info: pd.DataFrame)` → `Set[str]` [strategy/stock_screener.py:352]
  - 按成交量/成交额过滤
- `_filter_by_market_cap(self, symbols: Set[str], stock_info: pd.DataFrame)` → `Set[str]` [strategy/stock_screener.py:377]
  - 按市值过滤
- `_filter_by_industry(self, symbols: Set[str], stock_info: pd.DataFrame)` → `Set[str]` [strategy/stock_screener.py:407]
  - 按行业过滤
- `_filter_by_board(self, symbols: Set[str], stock_info: pd.DataFrame)` → `Set[str]` [strategy/stock_screener.py:434]
  - 按板块过滤
- `_filter_by_exchange(self, symbols: Set[str], stock_info: pd.DataFrame)` → `Set[str]` [strategy/stock_screener.py:460]
  - 按交易所过滤
- `_apply_custom_filters(self, symbols: Set[str], stock_info: pd.DataFrame)` → `Set[str]` [strategy/stock_screener.py:475]
  - 应用自定义过滤函数
- `_print_summary(self)` → `None` [strategy/stock_screener.py:497]
  - 打印筛选摘要

---

### strategy.strategy_executor

**文件**: `strategy/strategy_executor.py`

**说明**:

策略执行引擎 (Strategy Executor)

功能说明:
- 多进程并行执行策略
- 进度跟踪和性能监控
- 异常处理和失败重试
- 自动保存信号到数据库
- 支持快速模式和完整模式

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `ExecutionMode`

执行模式枚举

**继承**: `Enum`

##### `ExecutionConfig`

执行配置

##### `ExecutionProgress`

执行进度

**方法**:

- `get_progress_pct(self)` → `float` [strategy/strategy_executor.py:69]
  - 获取进度百分比

##### `StrategyExecutor`

策略执行引擎 - 负责策略的并行执行和结果管理

功能:
    - 多进程并行执行策略
    - 实时进度跟踪
    - 异常处理和重试
    - 自动保存信号到数据库

**方法**:

- `__init__(self, strategy: BaseStrategy, signal_manager: SignalManager, config: Optional[ExecutionConfig] = None)` → `None` [strategy/strategy_executor.py:87]
  - 初始化策略执行引擎
- `execute(self, stock_pool: List[str], mode: ExecutionMode = ..., start_date: Optional[date] = None, end_date: Optional[date] = None, **kwargs)` → `Dict` [strategy/strategy_executor.py:112]
  - 执行策略对股票池进行筛选
- `_execute_serial(self, stock_pool: List[str], start_date: date, end_date: date, **kwargs)` → `tuple` [strategy/strategy_executor.py:281]
  - 串行执行策略
- `_execute_parallel(self, stock_pool: List[str], start_date: date, end_date: date, **kwargs)` → `tuple` [strategy/strategy_executor.py:318]
  - 并行执行策略
- `_process_batch(self, symbols: List[str], start_date: date, end_date: date, **kwargs)` → `tuple` [strategy/strategy_executor.py:373]
  - 处理一批股票
- `_process_single_stock(self, symbol: str, start_date: date, end_date: date, **kwargs)` → `Optional[pd.DataFrame]` [strategy/strategy_executor.py:399]
  - 处理单只股票
- `get_progress(self)` → `Dict` [strategy/strategy_executor.py:425]
  - 获取当前执行进度

---

### test_customer_realtime_data

**文件**: `test_customer_realtime_data.py`

**说明**:

测试Customer适配器获取实时数据的脚本
用于了解stock.get_realtime_quotes()返回的数据结构

#### 函数

##### `test_realtime_data_structure()` → `None`

**位置**: [test_customer_realtime_data.py:11]

测试获取实时数据的结构

---

### test_financial_adapter

**文件**: `test_financial_adapter.py`

**说明**:

财务数据适配器测试脚本
测试FinancialDataSource的功能

#### 函数

##### `test_financial_adapter()` → `None`

**位置**: [test_financial_adapter.py:16]

测试FinancialDataSource的功能

---

### test_save_realtime_data

**文件**: `test_save_realtime_data.py`

**说明**:

测试和验证 save_realtime_data.py 程序
展示完整的数据库保存工作流程

#### 函数

##### `test_basic_save()` → `None`

**位置**: [test_save_realtime_data.py:20]

测试基本的数据保存功能

##### `test_saver_class()` → `None`

**位置**: [test_save_realtime_data.py:40]

测试 RealtimeDataSaver 类的功能

##### `test_dataframe_preparation()` → `None`

**位置**: [test_save_realtime_data.py:67]

测试数据准备和处理功能

##### `test_different_modes()` → `None`

**位置**: [test_save_realtime_data.py:106]

测试不同的数据更新模式

##### `test_error_handling()` → `None`

**位置**: [test_save_realtime_data.py:132]

测试错误处理机制

##### `run_comprehensive_test()` → `None`

**位置**: [test_save_realtime_data.py:164]

运行综合测试

---

### tests.test_automation

**文件**: `tests/test_automation.py`

**说明**:

自动化系统测试 (Automation System Tests)

测试覆盖:
- TaskScheduler: 任务调度器
- NotificationManager: 通知管理器
- JobLock: 任务锁
- PredefinedTasks: 预定义任务

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `TestJobLock`

任务锁测试

**方法**:

- `test_acquire_lock(self)` → `None` [tests/test_automation.py:53]
  - 测试获取锁
- `test_acquire_locked_job(self)` → `None` [tests/test_automation.py:61]
  - 测试获取已锁定的任务
- `test_release_lock(self)` → `None` [tests/test_automation.py:71]
  - 测试释放锁
- `test_lock_timeout(self)` → `None` [tests/test_automation.py:81]
  - 测试锁超时
- `test_multiple_jobs(self)` → `None` [tests/test_automation.py:95]
  - 测试多个任务的锁

##### `TestNotificationManager`

通知管理器测试

**方法**:

- `test_basic_notification(self)` → `None` [tests/test_automation.py:115]
  - 测试基本通知发送
- `test_multiple_channels(self)` → `None` [tests/test_automation.py:132]
  - 测试多渠道通知
- `test_rate_limiting(self)` → `None` [tests/test_automation.py:149]
  - 测试频率限制
- `test_success_notification(self)` → `None` [tests/test_automation.py:174]
  - 测试成功通知
- `test_failure_notification(self)` → `None` [tests/test_automation.py:188]
  - 测试失败通知
- `test_signal_notification(self)` → `None` [tests/test_automation.py:202]
  - 测试交易信号通知
- `test_notification_history(self)` → `None` [tests/test_automation.py:217]
  - 测试通知历史
- `test_notification_history_filter(self)` → `None` [tests/test_automation.py:233]
  - 测试通知历史过滤
- `test_statistics(self)` → `None` [tests/test_automation.py:248]
  - 测试统计信息

##### `TestTaskScheduler`

任务调度器测试

**方法**:

- `test_create_scheduler(self)` → `None` [tests/test_automation.py:269]
  - 测试创建调度器
- `test_add_task(self)` → `None` [tests/test_automation.py:275]
  - 测试添加任务
- `test_add_disabled_task(self)` → `None` [tests/test_automation.py:293]
  - 测试添加禁用的任务
- `test_list_tasks(self)` → `None` [tests/test_automation.py:311]
  - 测试列出任务
- `test_get_statistics(self)` → `None` [tests/test_automation.py:330]
  - 测试获取统计信息

##### `TestPredefinedTasks`

预定义任务测试

**方法**:

- `test_health_check(self)` → `None` [tests/test_automation.py:357]
  - 测试健康检查
- `test_health_check_specific_services(self)` → `None` [tests/test_automation.py:365]
  - 测试特定服务健康检查
- `test_generate_daily_report(self)` → `None` [tests/test_automation.py:372]
  - 测试生成每日报告
- `test_create_daily_update_task(self)` → `None` [tests/test_automation.py:380]
  - 测试创建每日更新任务配置
- `test_create_strategy_execution_task(self)` → `None` [tests/test_automation.py:389]
  - 测试创建策略执行任务配置
- `test_create_health_check_task(self)` → `None` [tests/test_automation.py:402]
  - 测试创建健康检查任务配置

##### `TestIntegration`

集成测试

**方法**:

- `test_scheduler_with_notification(self)` → `None` [tests/test_automation.py:419]
  - 测试调度器与通知集成
- `test_task_execution_flow(self)` → `None` [tests/test_automation.py:442]
  - 测试任务执行流程
- `test_multiple_tasks_coordination(self)` → `None` [tests/test_automation.py:463]
  - 测试多任务协调

---

### visualization.backtest_visualizer

**文件**: `visualization/backtest_visualizer.py`

**说明**:

回测性能可视化 (Backtest Visualizer)

功能说明:
- 权益曲线图
- 回撤分析图
- 收益分布图
- 月度/年度收益表
- 综合性能仪表盘

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `BacktestVisualizer`

回测性能可视化器

功能:
- 生成权益曲线
- 回撤分析
- 收益分布
- 性能仪表盘

**方法**:

- `__init__(self, figsize: Tuple[(int, int)] = ...)` → `None` [visualization/backtest_visualizer.py:37]
  - 初始化可视化器
- `plot_equity_curve(self, equity_curve: pd.DataFrame, benchmark: Optional[pd.Series] = None, title: str = "权益曲线", show: bool = False, save_path: Optional[str] = None)` → `None` [visualization/backtest_visualizer.py:51]
  - 绘制权益曲线
- `plot_drawdown(self, equity_curve: pd.DataFrame, title: str = "回撤分析", show: bool = False, save_path: Optional[str] = None)` → `None` [visualization/backtest_visualizer.py:112]
  - 绘制回撤分析图
- `plot_returns_distribution(self, daily_returns: pd.Series, title: str = "收益分布", show: bool = False, save_path: Optional[str] = None)` → `None` [visualization/backtest_visualizer.py:178]
  - 绘制收益分布图
- `plot_monthly_returns(self, daily_returns: pd.Series, title: str = "月度收益热力图", show: bool = False, save_path: Optional[str] = None)` → `None` [visualization/backtest_visualizer.py:225]
  - 绘制月度收益热力图
- `plot_dashboard(self, result: Dict, title: str = "回测性能仪表盘", show: bool = False, save_path: Optional[str] = None)` → `None` [visualization/backtest_visualizer.py:303]
  - 绘制综合性能仪表盘

---

### web.backend.app.adapters.__init__

**文件**: `web/backend/app/adapters/__init__.py`

---

### web.backend.app.adapters.akshare_extension

**文件**: `web/backend/app/adapters/akshare_extension.py`

**说明**:

Akshare适配器扩展模块
添加4个新方法支持股票数据扩展功能

数据源: 东方财富网 (通过Akshare)
新增方法:
1. get_etf_spot() - ETF实时行情
2. get_stock_fund_flow() - 个股资金流向
3. get_stock_lhb_detail() - 龙虎榜详细数据
4. get_dividend_data() - 分红配送数据

#### 类

##### `AkshareExtension`

Akshare适配器扩展类

**方法**:

- `get_etf_spot()` → `pd.DataFrame` [web/backend/app/adapters/akshare_extension.py:24]
  - 获取ETF基金实时行情数据 - 东方财富网
- `get_stock_fund_flow(symbol: str, timeframe: str = "1")` → `Dict` [web/backend/app/adapters/akshare_extension.py:62]
  - 获取个股资金流向数据 - 东方财富网
- `get_stock_lhb_detail(date: str)` → `pd.DataFrame` [web/backend/app/adapters/akshare_extension.py:123]
  - 获取指定日期龙虎榜详细数据 - 东方财富网
- `get_dividend_data(symbol: str)` → `pd.DataFrame` [web/backend/app/adapters/akshare_extension.py:174]
  - 获取股票分红配送数据 - 东方财富网
- `get_sector_fund_flow(date: Optional[str] = None)` → `pd.DataFrame` [web/backend/app/adapters/akshare_extension.py:218]
  - 获取行业/概念板块资金流向 - 东方财富网

#### 函数

##### `get_akshare_extension()` → `AkshareExtension`

**位置**: [web/backend/app/adapters/akshare_extension.py:257]

获取Akshare扩展单例

---

### web.backend.app.adapters.tqlex_adapter

**文件**: `web/backend/app/adapters/tqlex_adapter.py`

**说明**:

通达信TQLEX数据源适配器
实现竞价抢筹数据获取接口

数据分类: DataClassification.TRADING_ANALYSIS (衍生数据-交易分析)
存储目标: PostgreSQL+TimescaleDB

#### 类

##### `TqlexDataSource`

通达信TQLEX数据源实现

**方法**:

- `__init__(self, token: Optional[str] = None)` → `None` [web/backend/app/adapters/tqlex_adapter.py:27]
  - 初始化TQLEX数据源
- `_retry_api_call(self, func)` → `None` [web/backend/app/adapters/tqlex_adapter.py:53]
  - API调用重试装饰器 (复用akshare_adapter的模式)
- `get_chip_race_open(self, date: Optional[str] = None)` → `pd.DataFrame` [web/backend/app/adapters/tqlex_adapter.py:69]
  - 获取早盘抢筹数据
- `get_chip_race_end(self, date: Optional[str] = None)` → `pd.DataFrame` [web/backend/app/adapters/tqlex_adapter.py:127]
  - 获取尾盘抢筹数据
- `get_chip_race_combined(self, date: Optional[str] = None)` → `pd.DataFrame` [web/backend/app/adapters/tqlex_adapter.py:182]
  - 获取完整的竞价抢筹数据(早盘+尾盘)

#### 函数

##### `get_tqlex_adapter()` → `TqlexDataSource`

**位置**: [web/backend/app/adapters/tqlex_adapter.py:213]

获取TQLEX适配器单例

---

### web.backend.app.adapters.wencai_adapter

**文件**: `web/backend/app/adapters/wencai_adapter.py`

**说明**:

问财数据源适配器

功能:
  1. 调用问财(iwencai.com) Web API获取股票筛选数据
  2. 数据解析和清理
  3. 错误处理和重试机制
  4. 实现IDataSource接口（如果需要）

作者: MyStocks Backend Team
创建日期: 2025-10-17

#### 类

##### `WencaiDataSource`

问财数据源适配器

负责与问财API交互，获取股票筛选数据

**方法**:

- `__init__(self, timeout: int = DEFAULT_TIMEOUT, retry_count: int = DEFAULT_RETRY_COUNT)` → `None` [web/backend/app/adapters/wencai_adapter.py:44]
  - 初始化问财数据源
- `_create_session(self)` → `requests.Session` [web/backend/app/adapters/wencai_adapter.py:65]
  - 创建带重试机制的HTTP会话
- `fetch_data(self, query: str, pages: int = DEFAULT_PAGES)` → `pd.DataFrame` [web/backend/app/adapters/wencai_adapter.py:88]
  - 从问财获取数据
- `_fetch_single_page(self, query: str, page: int)` → `pd.DataFrame` [web/backend/app/adapters/wencai_adapter.py:139]
  - 获取单页数据
- `clean_data(self, data: pd.DataFrame)` → `pd.DataFrame` [web/backend/app/adapters/wencai_adapter.py:222]
  - 清理数据：处理列名和数据格式
- `_handle_duplicate_columns(df: pd.DataFrame)` → `pd.DataFrame` [web/backend/app/adapters/wencai_adapter.py:273]
  - 处理重复的列名
- `validate_query(self, query: str)` → `bool` [web/backend/app/adapters/wencai_adapter.py:297]
  - 验证查询语句是否有效
- `close(self)` → `None` [web/backend/app/adapters/wencai_adapter.py:319]
  - 关闭HTTP会话

#### 函数

##### `get_query_text(query_name: str)` → `Optional[str]`

**位置**: [web/backend/app/adapters/wencai_adapter.py:340]

根据查询名称获取查询文本

Args:
    query_name: 查询名称（如'qs_1'）

Returns:
    查询文本，如果不存在返回None

##### `get_all_queries()` → `Dict[(str, str)]`

**位置**: [web/backend/app/adapters/wencai_adapter.py:353]

获取所有预定义查询

Returns:
    查询名称到查询文本的映射

---

### web.backend.app.services.backtest_engine

**文件**: `web/backend/app/services/backtest_engine.py`

**说明**:

回测引擎 - 支持策略回测和性能评估

复用现有组件:
- DataService: 获取历史OHLCV数据
- StrategyRegistry: 获取策略实例

#### 类

##### `BacktestConfig`

回测配置

##### `BacktestResult`

回测结果

##### `BacktestEngine`

回测引擎

**方法**:

- `__init__(self, config: BacktestConfig = None)` → `None` [web/backend/app/services/backtest_engine.py:47]
- `run_backtest(self, strategy_id: str, symbol: str, start_date: str, end_date: str, strategy_params: Dict[(str, Any)] = None)` → `BacktestResult` [web/backend/app/services/backtest_engine.py:50]
  - 运行单策略回测
- `_simulate_trades(self, signals_df: pd.DataFrame)` → `pd.DataFrame` [web/backend/app/services/backtest_engine.py:109]
  - 模拟交易执行
- `_calculate_metrics(self, backtest_id: str, strategy_id: str, symbol: str, trades_df: pd.DataFrame, signals_df: pd.DataFrame)` → `BacktestResult` [web/backend/app/services/backtest_engine.py:160]
  - 计算回测指标
- `_calculate_equity_curve(self, signals_df: pd.DataFrame, trades_df: pd.DataFrame)` → `pd.DataFrame` [web/backend/app/services/backtest_engine.py:228]
  - 计算权益曲线
- `_calculate_max_drawdown(self, equity_curve: pd.DataFrame)` → `float` [web/backend/app/services/backtest_engine.py:248]
  - 计算最大回撤
- `_empty_result(self, strategy_id: str, symbol: str, backtest_id: str = "unknown")` → `BacktestResult` [web/backend/app/services/backtest_engine.py:258]
  - 返回空回测结果

#### 函数

##### `get_backtest_engine()` → `BacktestEngine`

**位置**: [web/backend/app/services/backtest_engine.py:285]

获取回测引擎单例

---

### web.backend.app.strategies.strategy_base

**文件**: `web/backend/app/strategies/strategy_base.py`

**说明**:

策略基类和策略注册表

复用现有组件:
- indicator_calculator (161个TA-Lib指标) - EXISTING
- data_service (OHLCV数据加载) - EXISTING

#### 类

##### `StrategyCategory`

策略分类

**继承**: `Enum`

##### `StrategyBase`

策略基类

所有策略必须继承此类并实现execute()方法

**继承**: `ABC`

**方法**:

- `__init__(self, strategy_id: str, name: str, description: str, category: StrategyCategory)` → `None` [web/backend/app/strategies/strategy_base.py:34]
- `execute(self, symbol: str, start_date: str, end_date: str, parameters: Dict[(str, Any)])` → `pd.DataFrame` [web/backend/app/strategies/strategy_base.py:41]
  - 执行策略生成交易信号
- `get_default_parameters(self)` → `Dict[(str, Any)]` [web/backend/app/strategies/strategy_base.py:64]
  - 获取默认参数

##### `StrategyRegistry`

策略注册表 (单例模式)

**方法**:

- `__new__(cls)` → `None` [web/backend/app/strategies/strategy_base.py:75]
- `register_strategy(self, strategy_class: type[StrategyBase])` → `None` [web/backend/app/strategies/strategy_base.py:80]
  - 注册策略
- `get_strategy(self, strategy_id: str)` → `Optional[StrategyBase]` [web/backend/app/strategies/strategy_base.py:89]
  - 获取策略实例
- `list_strategies(self)` → `List[Dict[(str, Any)]]` [web/backend/app/strategies/strategy_base.py:95]
  - 列出所有策略

#### 函数

##### `get_strategy_registry()` → `StrategyRegistry`

**位置**: [web/backend/app/strategies/strategy_base.py:114]

获取策略注册表单例

---
