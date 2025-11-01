# 工具功能

**类别**: utility
**模块数**: 22
**类数**: 46
**函数数**: 158
**代码行数**: 6698

## 概述


工具功能模块提供各种通用辅助功能，包括日期处理、股票代码转换、
列名映射、重试装饰器等。这些工具被其他模块广泛使用。

**关键特性**:
- 日期和时间处理工具
- 股票代码格式转换
- 列名映射和标准化
- 重试和错误处理装饰器
- 数据验证工具

**设计模式**: Decorator Pattern, Utility Pattern


## 模块列表

### indicators.talib_wrapper

**文件**: `indicators/talib_wrapper.py`

**说明**:

TA-Lib 技术指标包装器

功能说明:
- 封装TA-Lib库的常用技术指标函数
- 提供统一的错误处理和参数验证
- 支持pandas Series和numpy array输入
- 自动处理NaN值和数据长度校验

依赖:
- TA-Lib 0.6.7+ (使用binary wheels安装)

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `TALibIndicators`

TA-Lib技术指标包装类

提供常用技术指标的便捷访问接口，自动处理输入数据格式和异常情况

**方法**:

- `_to_numpy(data: Union[(np.ndarray, pd.Series)])` → `np.ndarray` [indicators/talib_wrapper.py:32]
  - 将输入数据转换为numpy array
- `_validate_length(data: np.ndarray, min_length: int, name: str = "数据")` → `None` [indicators/talib_wrapper.py:47]
  - 验证数据长度
- `calculate_sma(cls, close: Union[(np.ndarray, pd.Series)], period: int = 20)` → `np.ndarray` [indicators/talib_wrapper.py:69]
  - 简单移动平均 (Simple Moving Average)
- `calculate_ema(cls, close: Union[(np.ndarray, pd.Series)], period: int = 20)` → `np.ndarray` [indicators/talib_wrapper.py:86]
  - 指数移动平均 (Exponential Moving Average)
- `calculate_wma(cls, close: Union[(np.ndarray, pd.Series)], period: int = 20)` → `np.ndarray` [indicators/talib_wrapper.py:103]
  - 加权移动平均 (Weighted Moving Average)
- `calculate_macd(cls, close: Union[(np.ndarray, pd.Series)], fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9)` → `Tuple[(np.ndarray, np.ndarray, np.ndarray)]` [indicators/talib_wrapper.py:120]
  - MACD指标 (Moving Average Convergence Divergence)
- `calculate_rsi(cls, close: Union[(np.ndarray, pd.Series)], period: int = 14)` → `np.ndarray` [indicators/talib_wrapper.py:151]
  - 相对强弱指标 (Relative Strength Index)
- `calculate_stoch(cls, high: Union[(np.ndarray, pd.Series)], low: Union[(np.ndarray, pd.Series)], close: Union[(np.ndarray, pd.Series)], fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3)` → `Tuple[(np.ndarray, np.ndarray)]` [indicators/talib_wrapper.py:168]
  - 随机指标 (Stochastic Oscillator)
- `calculate_cci(cls, high: Union[(np.ndarray, pd.Series)], low: Union[(np.ndarray, pd.Series)], close: Union[(np.ndarray, pd.Series)], period: int = 14)` → `np.ndarray` [indicators/talib_wrapper.py:206]
  - 顺势指标 (Commodity Channel Index)
- `calculate_mom(cls, close: Union[(np.ndarray, pd.Series)], period: int = 10)` → `np.ndarray` [indicators/talib_wrapper.py:230]
  - 动量指标 (Momentum)
- `calculate_bbands(cls, close: Union[(np.ndarray, pd.Series)], period: int = 20, nbdevup: float = 2.0, nbdevdn: float = 2.0)` → `Tuple[(np.ndarray, np.ndarray, np.ndarray)]` [indicators/talib_wrapper.py:251]
  - 布林带 (Bollinger Bands)
- `calculate_atr(cls, high: Union[(np.ndarray, pd.Series)], low: Union[(np.ndarray, pd.Series)], close: Union[(np.ndarray, pd.Series)], period: int = 14)` → `np.ndarray` [indicators/talib_wrapper.py:280]
  - 平均真实波幅 (Average True Range)
- `calculate_obv(cls, close: Union[(np.ndarray, pd.Series)], volume: Union[(np.ndarray, pd.Series)])` → `np.ndarray` [indicators/talib_wrapper.py:308]
  - 能量潮 (On Balance Volume)
- `calculate_ad(cls, high: Union[(np.ndarray, pd.Series)], low: Union[(np.ndarray, pd.Series)], close: Union[(np.ndarray, pd.Series)], volume: Union[(np.ndarray, pd.Series)])` → `np.ndarray` [indicators/talib_wrapper.py:327]
  - 累积/派发线 (Accumulation/Distribution Line)
- `detect_doji(cls, open_: Union[(np.ndarray, pd.Series)], high: Union[(np.ndarray, pd.Series)], low: Union[(np.ndarray, pd.Series)], close: Union[(np.ndarray, pd.Series)])` → `np.ndarray` [indicators/talib_wrapper.py:356]
  - 十字星形态识别 (Doji)
- `detect_hammer(cls, open_: Union[(np.ndarray, pd.Series)], high: Union[(np.ndarray, pd.Series)], low: Union[(np.ndarray, pd.Series)], close: Union[(np.ndarray, pd.Series)])` → `np.ndarray` [indicators/talib_wrapper.py:380]
  - 锤子线形态识别 (Hammer)
- `detect_engulfing(cls, open_: Union[(np.ndarray, pd.Series)], high: Union[(np.ndarray, pd.Series)], low: Union[(np.ndarray, pd.Series)], close: Union[(np.ndarray, pd.Series)])` → `np.ndarray` [indicators/talib_wrapper.py:404]
  - 吞没形态识别 (Engulfing)
- `calculate_all_indicators(cls, df: pd.DataFrame)` → `Dict[(str, np.ndarray)]` [indicators/talib_wrapper.py:432]
  - 批量计算所有常用指标

---

### scripts.analysis.utils.__init__

**文件**: `scripts/analysis/utils/__init__.py`

**说明**:

代码分析工具模块

---

### scripts.analysis.utils.ast_parser

**文件**: `scripts/analysis/utils/ast_parser.py`

**说明**:

AST 解析器 - 提取 Python 代码的结构化元数据

使用 Python 的 ast 模块解析代码文件，提取类、函数、参数等信息。

作者: MyStocks Team
日期: 2025-10-19

#### 类

##### `ASTParser`

AST 解析器类

**方法**:

- `__init__(self, project_root: str)` → `None` [scripts/analysis/utils/ast_parser.py:29]
  - 初始化 AST 解析器
- `parse_file(self, file_path: Path)` → `Optional[ModuleMetadata]` [scripts/analysis/utils/ast_parser.py:38]
  - 解析单个 Python 文件
- `_get_module_name(self, file_path: Path)` → `str` [scripts/analysis/utils/ast_parser.py:102]
  - 获取模块名称
- `_parse_class(self, node: ast.ClassDef)` → `ClassMetadata` [scripts/analysis/utils/ast_parser.py:108]
  - 解析类定义
- `_parse_function(self, node: Any)` → `FunctionMetadata` [scripts/analysis/utils/ast_parser.py:147]
  - 解析函数定义
- `_parse_parameters(self, args: ast.arguments)` → `List[ParameterMetadata]` [scripts/analysis/utils/ast_parser.py:190]
  - 解析函数参数
- `_get_type_annotation(self, annotation)` → `str` [scripts/analysis/utils/ast_parser.py:233]
  - 提取类型注解字符串
- `_get_default_value(self, default)` → `str` [scripts/analysis/utils/ast_parser.py:256]
  - 提取默认值字符串
- `_get_decorator_name(self, decorator)` → `str` [scripts/analysis/utils/ast_parser.py:274]
  - 提取装饰器名称
- `scan_directory(self, directory: Path, exclude_patterns: List[str] = None)` → `List[ModuleMetadata]` [scripts/analysis/utils/ast_parser.py:287]
  - 扫描目录下的所有 Python 文件

#### 函数

##### `extract_code_block(file_path: str, start_line: int, end_line: int)` → `str`

**位置**: [scripts/analysis/utils/ast_parser.py:326]

从文件中提取代码块

Args:
    file_path: 文件路径
    start_line: 起始行号（从 1 开始）
    end_line: 结束行号

Returns:
    代码块字符串

##### `tokenize_code(code: str)` → `List[str]`

**位置**: [scripts/analysis/utils/ast_parser.py:348]

将代码分词为 token 列表

Args:
    code: 代码字符串

Returns:
    token 列表

---

### scripts.analysis.utils.markdown_writer

**文件**: `scripts/analysis/utils/markdown_writer.py`

**说明**:

Markdown 文档生成器 - 生成手册文档

生成格式良好的 Markdown 文档，包括：
- 模块分类文档
- 重复分析报告
- 优化路线图
- 合并指南
- 数据流图

作者: MyStocks Team
日期: 2025-10-19

#### 类

##### `MarkdownWriter`

Markdown 文档生成器

**方法**:

- `__init__(self, output_dir: str)` → `None` [scripts/analysis/utils/markdown_writer.py:33]
  - 初始化文档生成器
- `generate_category_document(self, category: CategoryEnum, modules: List[ModuleMetadata], category_name_cn: str, category_description: str)` → `str` [scripts/analysis/utils/markdown_writer.py:43]
  - 生成功能类别文档
- `generate_duplication_analysis(self, duplication_index: DuplicationIndex)` → `str` [scripts/analysis/utils/markdown_writer.py:161]
  - 生成重复分析文档
- `generate_optimization_roadmap(self, roadmap: OptimizationRoadmap)` → `str` [scripts/analysis/utils/markdown_writer.py:222]
  - 生成优化路线图文档
- `generate_consolidation_guide(self, guide: ConsolidationGuide)` → `str` [scripts/analysis/utils/markdown_writer.py:273]
  - 生成合并指南文档
- `generate_data_flow_maps(self, data_flows: List[DataFlow])` → `str` [scripts/analysis/utils/markdown_writer.py:315]
  - 生成数据流图文档
- `_format_parameters(self, parameters: List)` → `str` [scripts/analysis/utils/markdown_writer.py:404]
  - 格式化参数列表
- `_format_duplication(self, dup: DuplicationCase)` → `List[str]` [scripts/analysis/utils/markdown_writer.py:425]
  - 格式化重复案例
- `_format_optimization(self, opp: OptimizationOpportunity)` → `List[str]` [scripts/analysis/utils/markdown_writer.py:445]
  - 格式化优化机会
- `_format_merge_recommendation(self, rec: MergeRecommendation)` → `List[str]` [scripts/analysis/utils/markdown_writer.py:476]
  - 格式化合并建议

---

### scripts.analysis.utils.similarity

**文件**: `scripts/analysis/utils/similarity.py`

**说明**:

代码相似性检测 - 识别重复和相似代码

使用混合方法：token-based 相似度 + AST 结构相似度

作者: MyStocks Team
日期: 2025-10-19

#### 类

##### `SimilarityDetector`

代码相似性检测器

**方法**:

- `__init__(self, min_token_similarity: float = 0.4, min_ast_similarity: float = 0.3)` → `None` [scripts/analysis/utils/similarity.py:29]
  - 初始化相似性检测器
- `calculate_token_similarity(self, code1: str, code2: str)` → `float` [scripts/analysis/utils/similarity.py:40]
  - 计算两段代码的 token 相似度
- `calculate_ast_similarity(self, code1: str, code2: str)` → `float` [scripts/analysis/utils/similarity.py:61]
  - 计算两段代码的 AST 结构相似度
- `_ast_structure_hash(self, tree: ast.AST)` → `str` [scripts/analysis/utils/similarity.py:97]
  - 计算 AST 结构哈希（忽略标识符名称）
- `_extract_node_sequence(self, tree: ast.AST)` → `List[str]` [scripts/analysis/utils/similarity.py:128]
  - 提取 AST 节点类型序列
- `compare_functions(self, func1: FunctionMetadata, func2: FunctionMetadata, file1_path: str, file2_path: str)` → `Optional[Tuple[(float, float)]]` [scripts/analysis/utils/similarity.py:145]
  - 比较两个函数的相似度
- `create_duplication_case(self, blocks: List[Tuple[(str, int, int, str)]], token_similarity: float, ast_similarity: float, description: str = "")` → `DuplicationCase` [scripts/analysis/utils/similarity.py:189]
  - 创建重复案例
- `_generate_merge_suggestion(self, severity: SeverityEnum, blocks: List[CodeBlock])` → `str` [scripts/analysis/utils/similarity.py:252]
  - 生成合并建议
- `find_similar_code_blocks(self, code_blocks: List[Tuple[(str, int, int, str)]])` → `List[DuplicationCase]` [scripts/analysis/utils/similarity.py:287]
  - 在代码块列表中查找相似项

#### 函数

##### `normalize_code(code: str)` → `str`

**位置**: [scripts/analysis/utils/similarity.py:349]

标准化代码以便更好地比较

Args:
    code: 原始代码

Returns:
    标准化后的代码

---

### utils.__init__

**文件**: `utils/__init__.py`

**说明**:

工具类包
包含各种辅助函数和工具

---

### utils.add_doc_metadata

**文件**: `utils/add_doc_metadata.py`

**说明**:

批量为MD文档添加元数据标记

用法:
    python utils/add_doc_metadata.py --doc README.md --creator "JohnC & Claude" --version "2.1.0"

#### 函数

##### `add_metadata(file_path: str, creator: str, version: str, approved_date: str = None, revision_notes: str = "添加文档元数据标记")` → `None`

**位置**: [utils/add_doc_metadata.py:25]

为MD文档添加元数据

Args:
    file_path: 文档路径
    creator: 创建人
    version: 版本号
    approved_date: 批准日期 (可选，默认今天)
    revision_notes: 修订内容描述

##### `batch_add_metadata()` → `None`

**位置**: [utils/add_doc_metadata.py:84]

批量为核心文档添加元数据

##### `main()` → `None`

**位置**: [utils/add_doc_metadata.py:139]

---

### utils.add_python_headers

**文件**: `utils/add_python_headers.py`

**说明**:

# 功能：批量为Python核心文件添加规范化头注释
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：1.0.0
# 依赖：无外部依赖
# 注意事项：
#   - 自动检测已有头注释，避免重复添加
#   - 支持7组件Python头注释标准
#   - 备份原文件到.backup
# 版权：MyStocks Project © 2025

#### 类

##### `PythonHeaderAdder`

批量添加Python头注释的工具类

**方法**:

- `__init__(self)` → `None` [utils/add_python_headers.py:38]
- `has_standard_header(self, content: str)` → `bool` [utils/add_python_headers.py:43]
  - 检查文件是否已有标准头注释
- `extract_shebang_and_encoding(self, content: str)` → `Tuple[(str, str)]` [utils/add_python_headers.py:58]
  - 提取文件的shebang和编码声明
- `add_header_to_file(self, file_path: str, description: str, author: str = "JohnC (ninjas@sina.com) & Claude", created_date: str = "2025-10-16", version: str = "2.1.0", dependencies: str = "详见requirements.txt或导入部分", notes: str = "本文件是MyStocks v2.1核心组件", copyright: str = "MyStocks Project © 2025")` → `bool` [utils/add_python_headers.py:80]
  - 为单个Python文件添加头注释
- `_remove_simple_docstring(self, content: str)` → `str` [utils/add_python_headers.py:149]
  - 移除简单的docstring，保留复杂的类/函数说明

#### 函数

##### `batch_add_headers()` → `None`

**位置**: [utils/add_python_headers.py:179]

批量为核心文件添加头注释

---

### utils.check_api_health

**文件**: `utils/check_api_health.py`

**说明**:

Web API健康检查脚本

验证10个关键页面的数据接口可用性

#### 函数

##### `check_backend_running()` → `bool`

**位置**: [utils/check_api_health.py:111]

检查Backend服务是否运行

##### `get_auth_token()` → `Optional[str]`

**位置**: [utils/check_api_health.py:120]

获取认证Token

##### `test_api_endpoint(endpoint: Dict, token: Optional[str])` → `Tuple[(bool, str, Optional[int])]`

**位置**: [utils/check_api_health.py:135]

测试单个API端点

Returns:
    (成功, 错误消息, 状态码)

##### `main()` → `None`

**位置**: [utils/check_api_health.py:181]

主函数

---

### utils.check_api_health_v2

**文件**: `utils/check_api_health_v2.py`

**说明**:

# 功能：Web API健康检查工具 v2.0 - 验证短期优化改进后的API端点
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.0.0
# 依赖：requests
# 注意事项：
#   - 测试10个关键API端点（包含6个新增端点）
#   - 自动获取JWT token进行认证测试
#   - 生成详细的测试报告
# 版权：MyStocks Project © 2025

#### 类

##### `Colors`

终端颜色

##### `APIHealthChecker`

API健康检查器

**方法**:

- `__init__(self)` → `None` [utils/check_api_health_v2.py:38]
- `print_header(self, text: str)` → `None` [utils/check_api_health_v2.py:42]
  - 打印标题
- `print_result(self, name: str, status: str, detail: str = "")` → `None` [utils/check_api_health_v2.py:48]
  - 打印测试结果
- `check_backend_running(self)` → `bool` [utils/check_api_health_v2.py:61]
  - 检查Backend服务是否运行
- `get_jwt_token(self)` → `Tuple[(bool, str)]` [utils/check_api_health_v2.py:69]
  - 获取JWT token
- `test_endpoint(self, name: str, method: str, url: str, priority: str, need_auth: bool = False, params: Dict = None, data: Dict = None)` → `Dict` [utils/check_api_health_v2.py:91]
  - 测试单个API端点
- `run_tests(self)` → `None` [utils/check_api_health_v2.py:173]
  - 运行所有API测试
- `generate_report(self)` → `None` [utils/check_api_health_v2.py:309]
  - 生成测试报告

#### 函数

##### `main()` → `None`

**位置**: [utils/check_api_health_v2.py:375]

主函数

---

### utils.check_db_health

**文件**: `utils/check_db_health.py`

**说明**:

数据库健康检查脚本

验证4个数据库的连接状态，为修复Web页面问题做准备

#### 函数

##### `check_mysql_connection()` → `None`

**位置**: [utils/check_db_health.py:14]

验证MySQL连接

##### `check_postgresql_connection()` → `None`

**位置**: [utils/check_db_health.py:57]

验证PostgreSQL连接

##### `check_tdengine_connection()` → `None`

**位置**: [utils/check_db_health.py:131]

验证TDengine连接

##### `check_redis_connection()` → `None`

**位置**: [utils/check_db_health.py:194]

验证Redis连接

##### `main()` → `None`

**位置**: [utils/check_db_health.py:229]

主函数

---

### utils.column_mapper

**文件**: `utils/column_mapper.py`

**说明**:

统一列名管理器
提供DataFrame列名的标准化映射功能

作用：
- 统一不同数据源的列名格式
- 支持中英文列名转换
- 提供标准的列名映射规则
- 简化数据源适配器的列名处理逻辑

功能：
- 标准化DataFrame列名
- 中英文列名互转
- 自动识别和映射常见列名
- 支持自定义列名映射规则

#### 类

##### `ColumnMapper`

统一列名管理器

**方法**:

- `standardize_columns(cls, df: pd.DataFrame, target_lang: str = "en", custom_mapping: Optional[Dict[(str, str)]] = None)` → `pd.DataFrame` [utils/column_mapper.py:134]
  - 标准化DataFrame列名
- `to_english(cls, df: pd.DataFrame, custom_mapping: Optional[Dict[(str, str)]] = None)` → `pd.DataFrame` [utils/column_mapper.py:190]
  - 将DataFrame列名转换为英文
- `to_chinese(cls, df: pd.DataFrame, custom_mapping: Optional[Dict[(str, str)]] = None)` → `pd.DataFrame` [utils/column_mapper.py:205]
  - 将DataFrame列名转换为中文
- `get_standard_columns(cls, data_type: str = "stock_daily", lang: str = "en")` → `list` [utils/column_mapper.py:220]
  - 获取特定数据类型的标准列名
- `validate_columns(cls, df: pd.DataFrame, required_columns: list, strict: bool = False)` → `tuple` [utils/column_mapper.py:249]
  - 验证DataFrame是否包含必需的列
- `add_custom_mapping(cls, custom_mapping: Dict[(str, str)], target_lang: str = "en")` → `None` [utils/column_mapper.py:274]
  - 添加自定义映射规则到默认映射表

#### 函数

##### `standardize_dataframe(df: pd.DataFrame, target_lang: str = "en", custom_mapping: Optional[Dict[(str, str)]] = None)` → `pd.DataFrame`

**位置**: [utils/column_mapper.py:293]

便捷函数：标准化DataFrame列名

Args:
    df: 输入的DataFrame
    target_lang: 目标语言，"en"或"cn"
    custom_mapping: 自定义映射规则
    
Returns:
    pd.DataFrame: 标准化后的DataFrame

##### `to_english_columns(df: pd.DataFrame)` → `pd.DataFrame`

**位置**: [utils/column_mapper.py:310]

便捷函数：转换为英文列名

##### `to_chinese_columns(df: pd.DataFrame)` → `pd.DataFrame`

**位置**: [utils/column_mapper.py:315]

便捷函数：转换为中文列名

---

### utils.date_utils

**文件**: `utils/date_utils.py`

**说明**:

日期处理工具
提供日期格式化和转换功能

#### 函数

##### `normalize_date(date_str: Union[(str, datetime.date, datetime.datetime)])` → `str`

**位置**: [utils/date_utils.py:9]

将各种格式的日期转换为标准格式 YYYY-MM-DD

支持的输入格式:
- YYYY-MM-DD (标准格式)
- YYYYMMDD (紧凑格式)
- YYYY/MM/DD (斜杠分隔)
- datetime.date 对象
- datetime.datetime 对象

Args:
    date_str: 需要格式化的日期字符串或日期对象
    
Returns:
    str: 格式化后的日期字符串 (YYYY-MM-DD)
    
Raises:
    ValueError: 如果日期格式无法识别

##### `get_date_range(start_date: Union[(str, datetime.date)], end_date: Optional[Union[(str, datetime.date)]] = None, days: Optional[Union[(int, str)]] = None)` → `tuple`

**位置**: [utils/date_utils.py:78]

获取标准化的日期范围

Args:
    start_date: 开始日期
    end_date: 结束日期 (如果提供了days参数，则忽略此参数)
    days: 从开始日期算起的天数 (可选)，可以是整数或字符串
    
Returns:
    tuple: (标准化开始日期, 标准化结束日期)

##### `is_valid_date(date_str: str)` → `bool`

**位置**: [utils/date_utils.py:113]

检查日期字符串是否有效

Args:
    date_str: 日期字符串
    
Returns:
    bool: 日期是否有效

---

### utils.failure_recovery_queue

**文件**: `utils/failure_recovery_queue.py`

**说明**:

# 功能：故障恢复队列，数据库不可用时缓存操作并自动重试
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `FailureRecoveryQueue`

故障恢复队列

当目标数据库不可用时,将数据持久化到本地SQLite队列,
待数据库恢复后自动重试。

**方法**:

- `__init__(self, db_path: str = "/tmp/mystocks_recovery_queue.db")` → `None` [utils/failure_recovery_queue.py:27]
  - 初始化队列
- `_init_db(self)` → `None` [utils/failure_recovery_queue.py:39]
  - 初始化SQLite数据库表
- `enqueue(self, classification: str, target_database: str, data: Dict[(str, Any)])` → `None` [utils/failure_recovery_queue.py:59]
  - 将失败的数据操作加入队列
- `get_pending_items(self, limit: int = 100)` → `None` [utils/failure_recovery_queue.py:79]
  - 获取待重试的队列项
- `mark_item_processed(self, item_id: int)` → `None` [utils/failure_recovery_queue.py:105]
  - 标记队列项为已处理
- `mark_item_failed(self, item_id: int, error_message: str = "")` → `None` [utils/failure_recovery_queue.py:124]
  - 标记队列项为失败并增加重试次数
- `retry_failed_items(self, max_retries: int = 3)` → `None` [utils/failure_recovery_queue.py:147]
  - 重试失败的队列项
- `cleanup_old_items(self, days_old: int = 30)` → `None` [utils/failure_recovery_queue.py:172]
  - 清理旧的已处理项
- `get_queue_stats(self)` → `Dict[(str, Any)]` [utils/failure_recovery_queue.py:197]
  - 获取队列统计信息
- `get_failed_items_with_high_retry_count(self, min_retries: int = 5)` → `list` [utils/failure_recovery_queue.py:235]
  - 获取重试次数过多的失败项

---

### utils.symbol_utils

**文件**: `utils/symbol_utils.py`

**说明**:

股票代码处理工具
提供股票代码格式化和转换功能

#### 函数

##### `normalize_stock_code(code: Union[(str, int, float)])` → `str`

**位置**: [utils/symbol_utils.py:8]

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

##### `get_stock_exchange(code: Union[(str, int, float)])` → `str`

**位置**: [utils/symbol_utils.py:86]

根据股票代码获取交易所代码

参数:
    code: 股票代码(可以是任何支持的格式)
    
返回:
    str: 交易所代码 (SH/SZ/BJ)

##### `format_stock_code_for_source(code: Union[(str, int, float)], source_type: str = "akshare")` → `str`

**位置**: [utils/symbol_utils.py:113]

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

##### `format_stock_code(code: Union[(str, int, float)], format_type: str = "numeric")` → `str`

**位置**: [utils/symbol_utils.py:146]

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

##### `is_valid_stock_code(code: Union[(str, int, float)])` → `bool`

**位置**: [utils/symbol_utils.py:186]

检查股票代码是否有效

参数:
    code: 股票代码
    
返回:
    bool: 股票代码是否有效

##### `format_index_code_for_source(code: Union[(str, int, float)], source_type: str = "akshare")` → `str`

**位置**: [utils/symbol_utils.py:203]

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

##### `normalize_index_code(code: Union[(str, int, float)])` → `str`

**位置**: [utils/symbol_utils.py:243]

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

---

### utils.test_logs_api

**文件**: `utils/test_logs_api.py`

**说明**:

测试系统运行日志API端点
验证日志查询和筛选功能

#### 函数

##### `print_separator()` → `None`

**位置**: [utils/test_logs_api.py:16]

打印分隔线

##### `test_get_all_logs()` → `None`

**位置**: [utils/test_logs_api.py:21]

测试1: 获取所有日志

##### `test_filter_errors_only()` → `None`

**位置**: [utils/test_logs_api.py:55]

测试2: 只获取有问题的日志

##### `test_filter_by_level()` → `None`

**位置**: [utils/test_logs_api.py:95]

测试3: 按日志级别筛选

##### `test_filter_by_category()` → `None`

**位置**: [utils/test_logs_api.py:131]

测试4: 按分类筛选

##### `test_pagination()` → `None`

**位置**: [utils/test_logs_api.py:167]

测试5: 分页功能

##### `test_logs_summary()` → `None`

**位置**: [utils/test_logs_api.py:199]

测试6: 日志统计摘要

##### `main()` → `None`

**位置**: [utils/test_logs_api.py:237]

主函数

---

### utils.validate_gitignore

**文件**: `utils/validate_gitignore.py`

**说明**:

# 功能：验证.gitignore配置是否正确排除应忽略的文件
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：1.0.0
# 依赖：无外部依赖
# 注意事项：
#   - 检查git status中不应出现的文件类型
#   - 验证.env.example等例外文件可见
#   - 提供清理建议
# 版权：MyStocks Project © 2025

#### 类

##### `GitIgnoreValidator`

Git忽略规则验证器

**方法**:

- `__init__(self, root_dir: str = ".")` → `None` [utils/validate_gitignore.py:26]
- `run_git_command(self, args: List[str])` → `str` [utils/validate_gitignore.py:55]
  - 执行git命令
- `get_untracked_files(self)` → `List[str]` [utils/validate_gitignore.py:69]
  - 获取未跟踪的文件列表
- `check_ignored_patterns(self)` → `None` [utils/validate_gitignore.py:81]
  - 检查应该被忽略的文件模式
- `check_exception_files(self)` → `None` [utils/validate_gitignore.py:102]
  - 检查排除规则文件是否可见
- `check_gitignore_exists(self)` → `bool` [utils/validate_gitignore.py:123]
  - 检查.gitignore文件是否存在
- `generate_cleanup_commands(self)` → `List[str]` [utils/validate_gitignore.py:144]
  - 生成清理命令
- `generate_report(self)` → `str` [utils/validate_gitignore.py:165]
  - 生成验证报告

#### 函数

##### `main()` → `None`

**位置**: [utils/validate_gitignore.py:259]

主函数

---

### utils.validate_test_naming

**文件**: `utils/validate_test_naming.py`

**说明**:

# 功能：验证测试文件命名规范是否符合pytest约定
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：1.0.0
# 依赖：无外部依赖
# 注意事项：
#   - 检查所有测试文件是否以test_开头
#   - 统计符合/不符合pytest规范的文件
#   - 提供修复建议
# 版权：MyStocks Project © 2025

#### 类

##### `TestNamingValidator`

测试文件命名规范验证器

**方法**:

- `__init__(self, root_dir: str = ".")` → `None` [utils/validate_test_naming.py:25]
- `find_all_test_files(self)` → `List[Path]` [utils/validate_test_naming.py:34]
  - 查找所有测试文件（包含'test'关键字的.py文件）
- `validate_file_naming(self, file_path: Path)` → `bool` [utils/validate_test_naming.py:60]
  - 验证单个文件是否符合pytest命名规范
- `validate_all(self)` → `Dict` [utils/validate_test_naming.py:71]
  - 验证所有测试文件
- `suggest_rename(self, file_path: Path)` → `str` [utils/validate_test_naming.py:88]
  - 为不符合规范的文件建议新名称
- `generate_report(self)` → `str` [utils/validate_test_naming.py:114]
  - 生成验证报告

#### 函数

##### `main()` → `None`

**位置**: [utils/validate_test_naming.py:180]

主函数

---

### web.backend.app.schemas.market_schemas

**文件**: `web/backend/app/schemas/market_schemas.py`

**说明**:

市场数据API Schemas (Pydantic模型)

用于FastAPI请求验证和响应序列化:
- FundFlow: 个股资金流向
- ETFData: ETF基金数据
- ChipRace: 竞价抢筹数据
- LongHuBang: 龙虎榜数据

#### 类

##### `FundFlowRequest`

资金流向查询请求

**继承**: `BaseModel`

**方法**:

- `validate_timeframe(cls, v)` → `None` [web/backend/app/schemas/market_schemas.py:27]

##### `FundFlowResponse`

资金流向响应

**继承**: `BaseModel`

##### `ETFDataRequest`

ETF数据查询请求

**继承**: `BaseModel`

**方法**:

- `validate_symbol(cls, v)` → `None` [web/backend/app/schemas/market_schemas.py:61]

##### `ETFDataResponse`

ETF数据响应

**继承**: `BaseModel`

##### `ChipRaceRequest`

竞价抢筹查询请求

**继承**: `BaseModel`

**方法**:

- `validate_race_type(cls, v)` → `None` [web/backend/app/schemas/market_schemas.py:102]

##### `ChipRaceResponse`

竞价抢筹响应

**继承**: `BaseModel`

##### `LongHuBangRequest`

龙虎榜查询请求

**继承**: `BaseModel`

##### `LongHuBangResponse`

龙虎榜响应

**继承**: `BaseModel`

##### `PaginatedResponse`

分页响应

**继承**: `BaseModel`

##### `MessageResponse`

通用消息响应

**继承**: `BaseModel`

---

### web.backend.app.schemas.wencai_schemas

**文件**: `web/backend/app/schemas/wencai_schemas.py`

**说明**:

问财API请求/响应Schema

定义问财功能的Pydantic数据模型，用于API请求验证和响应序列化

作者: MyStocks Backend Team
创建日期: 2025-10-17

#### 类

##### `WencaiQueryRequest`

执行问财查询请求

用于POST /api/market/wencai/query

**继承**: `BaseModel`

**方法**:

- `validate_query_name(cls, v)` → `None` [web/backend/app/schemas/wencai_schemas.py:44]
  - 验证查询名称格式 - 只允许 qs_1 到 qs_9

##### `WencaiCustomQueryRequest`

自定义查询请求

用于POST /api/market/wencai/custom-query

**继承**: `BaseModel`

##### `WencaiRefreshRequest`

刷新查询数据请求（可选参数）

用于POST /api/market/wencai/refresh/{query_name}

**继承**: `BaseModel`

##### `WencaiQueryInfo`

查询信息

用于GET /api/market/wencai/queries

**继承**: `BaseModel`

##### `WencaiQueryListResponse`

查询列表响应

用于GET /api/market/wencai/queries

**继承**: `BaseModel`

##### `WencaiQueryResponse`

查询执行响应

用于POST /api/market/wencai/query

**继承**: `BaseModel`

##### `WencaiCustomQueryResponse`

自定义查询响应

用于POST /api/market/wencai/custom-query

**继承**: `BaseModel`

##### `WencaiResultItem`

单条查询结果

注意：由于不同查询返回的字段不同，这里使用动态字典

**继承**: `BaseModel`

##### `WencaiResultsResponse`

查询结果列表响应

用于GET /api/market/wencai/results/{query_name}

**继承**: `BaseModel`

##### `WencaiRefreshResponse`

刷新任务响应

用于POST /api/market/wencai/refresh/{query_name}

**继承**: `BaseModel`

##### `WencaiHistoryItem`

历史数据项

**继承**: `BaseModel`

##### `WencaiHistoryResponse`

历史数据响应

用于GET /api/market/wencai/history/{query_name}

**继承**: `BaseModel`

##### `WencaiErrorResponse`

错误响应

统一的错误格式

**继承**: `BaseModel`

##### `WencaiStatsResponse`

统计信息响应（可选，用于监控面板）

**继承**: `BaseModel`

---

### web.backend.app.services.indicator_registry

**文件**: `web/backend/app/services/indicator_registry.py`

**说明**:

Indicator Registry Service
管理所有161个TA-Lib技术指标的元数据注册表

#### 类

##### `IndicatorCategory`

指标分类

**继承**: `str`, `Enum`

##### `PanelType`

显示面板类型

**继承**: `str`, `Enum`

##### `IndicatorRegistry`

指标注册表

在应用启动时加载所有161个TA-Lib指标的元数据
提供指标查询、验证和元数据访问功能

**方法**:

- `__init__(self)` → `None` [web/backend/app/services/indicator_registry.py:33]
  - 初始化注册表并加载所有指标元数据
- `_load_indicators(self)` → `None` [web/backend/app/services/indicator_registry.py:38]
  - 从TA-Lib加载所有161个指标的元数据
- `get_indicator(self, abbreviation: str)` → `Optional[Dict[(str, Any)]]` [web/backend/app/services/indicator_registry.py:375]
  - 获取指定指标的元数据
- `get_all_indicators(self)` → `Dict[(str, Dict[(str, Any)])]` [web/backend/app/services/indicator_registry.py:387]
  - 获取所有指标的元数据
- `get_indicators_by_category(self, category: IndicatorCategory)` → `Dict[(str, Dict[(str, Any)])]` [web/backend/app/services/indicator_registry.py:391]
  - 按分类获取指标
- `validate_indicator(self, abbreviation: str, parameters: Dict[(str, Any)])` → `tuple[(bool, Optional[str])]` [web/backend/app/services/indicator_registry.py:407]
  - 验证指标及其参数
- `get_min_data_points(self, abbreviation: str, parameters: Dict[(str, Any)])` → `int` [web/backend/app/services/indicator_registry.py:446]
  - 计算指标所需的最小数据点数

#### 函数

##### `get_indicator_registry()` → `IndicatorRegistry`

**位置**: [web/backend/app/services/indicator_registry.py:469]

获取指标注册表单例

---

### web.backend.tests.test_indicators

**文件**: `web/backend/tests/test_indicators.py`

**说明**:

Unit and Integration Tests for Indicator Calculation
测试技术指标计算功能

#### 类

##### `TestMACalculation`

测试MA指标计算 (T016)

**方法**:

- `test_calculate_ma(self)` → `None` [web/backend/tests/test_indicators.py:24]
  - T016: Unit test for MA calculation

##### `TestMultipleMACalculation`

测试批量MA计算 (T017)

**方法**:

- `test_calculate_multiple_mas(self)` → `None` [web/backend/tests/test_indicators.py:69]
  - T017: Unit test for multiple MAs

##### `TestInsufficientDataHandling`

测试数据点不足处理 (T018)

**方法**:

- `test_insufficient_data_error(self)` → `None` [web/backend/tests/test_indicators.py:120]
  - T018: Unit test for insufficient data handling
- `test_minimum_data_points_edge_case(self)` → `None` [web/backend/tests/test_indicators.py:150]
  - 测试临界情况: 刚好满足最小数据点要求

##### `TestRegistryEndpoint`

测试注册表API端点 (T019)

**方法**:

- `test_get_registry(self)` → `None` [web/backend/tests/test_indicators.py:178]
  - T019: Integration test for registry endpoint
- `test_get_indicators_by_category(self)` → `None` [web/backend/tests/test_indicators.py:217]
  - 测试按分类获取指标
- `test_get_invalid_category(self)` → `None` [web/backend/tests/test_indicators.py:235]
  - 测试无效的分类

##### `TestCalculateEndpoint`

测试指标计算API端点 (T020)

**方法**:

- `test_calculate_indicators_endpoint(self)` → `None` [web/backend/tests/test_indicators.py:246]
  - T020: Integration test for calculate endpoint
- `test_calculate_with_invalid_symbol(self)` → `None` [web/backend/tests/test_indicators.py:294]
  - 测试无效的股票代码
- `test_calculate_with_invalid_date_range(self)` → `None` [web/backend/tests/test_indicators.py:310]
  - 测试无效的日期范围
- `test_calculate_with_future_date(self)` → `None` [web/backend/tests/test_indicators.py:326]
  - 测试未来日期
- `test_calculate_with_unknown_indicator(self)` → `None` [web/backend/tests/test_indicators.py:342]
  - 测试未知指标

##### `TestDataQualityValidation`

测试数据质量验证

**方法**:

- `test_validate_ohlc_relationships(self)` → `None` [web/backend/tests/test_indicators.py:362]
  - 测试OHLC关系验证
- `test_validate_negative_volume(self)` → `None` [web/backend/tests/test_indicators.py:379]
  - 测试负成交量验证

##### `TestMACDCalculation`

测试MACD指标计算

**方法**:

- `test_calculate_macd(self)` → `None` [web/backend/tests/test_indicators.py:400]
  - 验证MACD计算返回三个输出 (macd, signal, hist)

##### `TestRSICalculation`

测试RSI指标计算

**方法**:

- `test_calculate_rsi(self)` → `None` [web/backend/tests/test_indicators.py:439]
  - 验证RSI计算结果在0-100范围内

---
