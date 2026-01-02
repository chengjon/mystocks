# TDX功能增强计划 - 取长补短

**生成时间**: 2026-01-02
**版本**: v1.0
**对比基准**: PyTDX (位于 `/opt/iflow/tdxpy/`) vs MyStocks TDX适配器

---

## 📊 功能对比总览

| 功能类别 | PyTDX支持 | MyStocks现状 | 差距分析 |
|---------|-----------|-------------|---------|
| **实时行情** | ✅ 完整 | ✅ 完整 | 无差距 |
| **K线数据(分钟)** | ✅ 1m/5m/15m/30m/1h | ✅ 1m/5m/15m/30m/1h | 无差距 |
| **K线数据(日)** | ✅ 日线 | ✅ 日线 | 无差距 |
| **K线数据(周/月/季/年)** | ✅ 支持 | ❌ 不支持 | **缺少4种周期** |
| **财务数据** | ✅ 15+字段 | ❌ 不支持 | **完全缺失** |
| **除权除息** | ✅ 完整 | ❌ 不支持 | **完全缺失** |
| **公司信息** | ✅ 16大类 | ❌ 不支持 | **完全缺失** |
| **板块数据** | ✅ 4种类型 | ❌ 不支持 | **完全缺失** |
| **分时数据** | ✅ 支持 | ❌ 不支持 | **完全缺失** |
| **分笔成交** | ✅ 支持 | ❌ 不支持 | **完全缺失** |
| **股票列表** | ✅ 支持 | ⚠️ 有限 | 功能较弱 |
| **二进制文件** | ✅ 完整 | ✅ 完整 | 无差距 |

**核心差距**:
- ❌ **6大功能模块完全缺失**: 财务数据、除权除息、公司信息、板块数据、分时数据、分笔成交
- ❌ **4种K线周期不支持**: 周线、月线、季线、年线

---

## 🎯 增强方案一: 扩展K线周期支持

### 1.1 目标

新增4种K线周期: **周线、月线、季线、年线**

### 1.2 实现方式

**步骤1**: 更新周期映射 (在 `src/adapters/tdx_adapter.py`)

```python
# 当前实现 (约第180-195行)
period_map = {
    '1m':  8,   # 1分钟
    '5m':  0,   # 5分钟
    '15m': 1,   # 15分钟
    '30m': 2,   # 30分钟
    '1h':  3,   # 1小时
    '1d':  9    # 日线
}

# 增强后
period_map = {
    '1m':   8,   # 1分钟
    '5m':   0,   # 5分钟
    '15m':  1,   # 15分钟
    '30m':  2,   # 30分钟
    '1h':   3,   # 1小时
    '1d':   9,   # 日线
    '1w':   5,   # 周线 (新增)
    '1M':   6,   # 月线 (新增)
    '1q':   10,  # 季线 (新增)
    '1y':   11   # 年线 (新增)
}
```

**步骤2**: 更新文档字符串和类型提示

```python
def get_stock_kline(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    period: str = '1d'  # 支持: 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1M, 1q, 1y
) -> pd.DataFrame:
```

**步骤3**: 添加使用示例

```python
# 获取周线数据
df_weekly = tdx.get_stock_kline('600519', '2020-01-01', '2024-12-31', period='1w')

# 获取月线数据
df_monthly = tdx.get_stock_kline('600519', '2020-01-01', '2024-12-31', period='1M')

# 获取季线数据
df_quarterly = tdx.get_stock_kline('600519', '2020-01-01', '2024-12-31', period='1q')

# 获取年线数据
df_yearly = tdx.get_stock_kline('600519', '2020-01-01', '2024-12-31', period='1y')
```

**数据库路由策略**:
- 周线/月线 → PostgreSQL TimescaleDB (长期存储)
- 季线/年线 → PostgreSQL TimescaleDB (长期存储)

---

## 🎯 增强方案二: 财务数据支持

### 2.1 目标

实现 `get_finance_info()` 方法,获取15+项基本财务指标

### 2.2 PyTDX参考实现

**文件位置**: `/opt/iflow/tdxpy/pytdx/parser/get_finance_info.py`
**API方法**: `TdxHq_API.get_finance_info(market, code)`

**返回字段** (15+项):
```python
{
    'code': str,           # 股票代码
    'name': str,           # 股票名称
    'totalamount': float,  # 总股本 (万股)
    'mgjzc': float,        # 每股净资产 (元)
    'mgxjlc': float,       # 每股现金流 (元)
    'mgsy': float,         # 每股收益 (元)
    'mgzbgjj': float,      # 每股资本公积金 (元)
    'mgwlygjj': float,     # 每股未分配利润 (元)
    'jyzmj': float,        # 经营业务毛利 (万元)
    'jyzmr': float,        # 经营业务收入 (万元)
    'jyywlr': float,       # 经营业务利润 (万元)
    'lrze': float,         # 利润总额 (万元)
    'jlr': float,          # 净利润 (万元)
    'totalcap': float,     # 总资产 (万元)
    'totalprofit': float,  # 总利润 (万元)
    'totalrights': float   # 股东权益 (万元)
}
```

### 2.3 MyStocks实现方案

**步骤1**: 在 `src/adapters/tdx_adapter.py` 添加方法

```python
def get_financial_info(self, symbol: str) -> Dict[str, Any]:
    """
    获取股票基本财务信息

    Args:
        symbol: 股票代码 (6位数字)

    Returns:
        Dict: 包含15+项财务指标的字典

    Raises:
        ValueError: 股票代码格式错误
        ConnectionError: TDX服务器连接失败
    """
    try:
        # 解析市场代码
        market, code = self._parse_symbol(symbol)

        # 调用PyTDX API
        api = TdxHq_API()
        if not api.connect(self.host, self.port):
            raise ConnectionError(f"无法连接到TDX服务器: {self.host}:{self.port}")

        data = api.get_finance_info(market, code)
        api.disconnect()

        if not data:
            return {}

        return {
            'symbol': symbol,
            'total_amount': data.get('totalamount', 0),      # 总股本(万股)
            'net_asset_per_share': data.get('mgjzc', 0),     # 每股净资产(元)
            'cash_flow_per_share': data.get('mgxjlc', 0),    # 每股现金流(元)
            'eps': data.get('mgsy', 0),                      # 每股收益(元)
            'reserve_per_share': data.get('mgzbgjj', 0),     # 每股资本公积金(元)
            'retained_earnings_per_share': data.get('mgwlygjj', 0), # 每股未分配利润(元)
            'operating_profit': data.get('jyzmj', 0),        # 经营业务毛利(万元)
            'operating_revenue': data.get('jyzmr', 0),       # 经营业务收入(万元)
            'operating_profit_total': data.get('jyywlr', 0), # 经营业务利润(万元)
            'total_profit': data.get('lrze', 0),             # 利润总额(万元)
            'net_profit': data.get('jlr', 0),                # 净利润(万元)
            'total_assets': data.get('totalcap', 0),         # 总资产(万元)
            'shareholder_equity': data.get('totalrights', 0) # 股东权益(万元)
        }
    except Exception as e:
        self.logger.error(f"获取财务信息失败 {symbol}: {e}")
        return {}
```

**步骤2**: 更新接口定义 (`src/interfaces/data_source.py`)

```python
class IDataSource(ABC):
    @abstractmethod
    def get_financial_data(self, symbol: str, period: str = 'annual') -> pd.DataFrame:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            period: 报告周期 (annual/quarter)

        Returns:
            pd.DataFrame: 财务数据
        """
        pass
```

**步骤3**: 数据库路由

- **信息类别**: `DataClassification.REFERENCE_DATA` (参考数据)
- **目标数据库**: PostgreSQL
- **表名**: `financial_basic_info`
- **更新频率**: 每日更新 (相对静态)

**配置** (`config/table_config.yaml`):
```yaml
- name: financial_basic_info
  description: 股票基本财务信息
  database: postgresql
  info_category: REFERENCE_DATA
  schema:
    symbol: varchar(10) PRIMARY KEY
    total_amount: float
    net_asset_per_share: float
    cash_flow_per_share: float
    eps: float
    reserve_per_share: float
    retained_earnings_per_share: float
    operating_profit: float
    operating_revenue: float
    operating_profit_total: float
    total_profit: float
    net_profit: float
    total_assets: float
    shareholder_equity: float
    updated_at: timestamp
```

---

## 🎯 增强方案三: 除权除息数据

### 3.1 目标

实现 `get_xdxr_info()` 方法,获取股票除权除息历史记录

### 3.2 PyTDX参考实现

**文件位置**: `/opt/iflow/tdxpy/pytdx/reader/gbbq_reader.py`
**API方法**: `TdxHq_API.get_xdxr_info(market, code)`
**本地文件**: `gbbq` (加密二进制文件)

**返回字段**:
```python
{
    'datetime': str,       # 除权除息日期
    'category': int,       # 类别 (0=分红, 1=送股, 2=配股)
    'hongli': float,       # 每股分红(元)
    'songgu': float,       # 每股送股比例
    'peigu': float,        # 每股配股比例
    'peigujia': float,     # 配股价格(元)
    'content': str         # 内容描述 (如: "10派2.5元(含税)")
}
```

### 3.3 MyStocks实现方案

**步骤1**: 在 `src/adapters/tdx_adapter.py` 添加方法

```python
def get_dividend_info(self, symbol: str) -> pd.DataFrame:
    """
    获取股票除权除息信息

    Args:
        symbol: 股票代码 (6位数字)

    Returns:
        pd.DataFrame: 除权除息记录
        Columns: [datetime, category, dividend, bonus, rights_ratio, rights_price, description]
    """
    try:
        market, code = self._parse_symbol(symbol)

        api = TdxHq_API()
        if not api.connect(self.host, self.port):
            raise ConnectionError(f"无法连接到TDX服务器")

        data = api.get_xdxr_info(market, code)
        api.disconnect()

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df.columns = ['datetime', 'category', 'dividend', 'bonus_ratio',
                     'rights_ratio', 'rights_price', 'description']

        # 数据类型转换
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['category'] = df['category'].map({0: '分红', 1: '送股', 2: '配股'})

        return df
    except Exception as e:
        self.logger.error(f"获取除权除息信息失败 {symbol}: {e}")
        return pd.DataFrame()
```

**步骤2**: 数据库路由

- **信息类别**: `DataClassification.REFERENCE_DATA` (参考数据)
- **目标数据库**: PostgreSQL
- **表名**: `stock_dividend_history`
- **数据特性**: 历史数据，不频繁更新

**配置** (`config/table_config.yaml`):
```yaml
- name: stock_dividend_history
  description: 股票除权除息历史记录
  database: postgresql
  info_category: REFERENCE_DATA
  schema:
    symbol: varchar(10)
    datetime: timestamp
    category: varchar(10)
    dividend: float           # 每股分红(元)
    bonus_ratio: float        # 每股送股比例
    rights_ratio: float       # 每股配股比例
    rights_price: float       # 配股价格(元)
    description: text
    PRIMARY KEY (symbol, datetime)
```

---

## 🎯 增强方案四: 公司信息分类

### 4.1 目标

实现公司信息16大类的获取功能

### 4.2 PyTDX参考实现

**API方法**:
- `get_company_info_category()` - 获取16个信息类别
- `get_company_info_content()` - 获取具体内容

**16个信息类别**:
1. 最新提示
2. 公司概况
3. 财务分析
4. 股东研究
5. 股本结构
6. 资本运作
7. 业内点评
8. 行业分析
9. 公司大事
10. 研究报告
11. 经营分析
12. 主力追踪
13. 分红扩股
14. 高层治理
15. 龙虎榜单
16. 关联个股

### 4.3 MyStocks实现方案

**步骤1**: 添加方法

```python
def get_company_info_categories(self, symbol: str) -> List[Dict[str, str]]:
    """
    获取公司信息类别列表

    Returns:
        List[Dict]: 16个信息类别
        [{'filename': '...', 'name': '...'}, ...]
    """
    # 实现略
    pass

def get_company_info_content(self, symbol: str, category: str) -> bytes:
    """
    获取公司信息具体内容

    Args:
        symbol: 股票代码
        category: 类别文件名

    Returns:
        bytes: 内容数据
    """
    # 实现略
    pass
```

**数据库路由**:
- **信息类别**: `DataClassification.REFERENCE_DATA`
- **目标数据库**: PostgreSQL
- **表名**: `company_info_cache`
- **用途**: 缓存公司信息,减少重复请求

---

## 🎯 增强方案五: 板块数据

### 5.1 目标

实现板块数据读取功能 (指数板块、风格板块、概念板块、默认板块)

### 5.2 PyTDX参考实现

**文件位置**: `/opt/iflow/tdxpy/pytdx/reader/block_reader.py`
**本地文件**:
- `T0002/hq_cache/block_zs.dat` - 指数板块
- `T0002/hq_cache/block_fg.dat` - 风格板块
- `T0002/hq_cache/block_gn.dat` - 概念板块
- `T0002/hq_cache/block.dat` - 默认板块

**返回格式**:
```python
{
    'blockname': str,      # 板块名称
    'block_type': str,     # 板块类型
    'code': str,           # 股票代码
    'code_index': int      # 代码索引
}
```

### 5.3 MyStocks实现方案

**步骤1**: 复制并适配 `block_reader.py`

创建 `src/data_sources/tdx_block_reader.py`:

```python
from pytdx.reader.block_reader import BlockReader, BlockReader_TYPE_FLAT

class TdxBlockReader:
    """通达信板块数据读取器"""

    def __init__(self, tdx_path: str):
        """
        Args:
            tdx_path: 通达信安装路径 (如: /mnt/d/ProgramData/tdx_new)
        """
        self.tdx_path = tdx_path
        self.reader = BlockReader()

    def get_index_blocks(self) -> pd.DataFrame:
        """获取指数板块"""
        file_path = f"{self.tdx_path}/T0002/hq_cache/block_zs.dat"
        return self.reader.get_df(file_path, BlockReader_TYPE_FLAT)

    def get_style_blocks(self) -> pd.DataFrame:
        """获取风格板块"""
        file_path = f"{self.tdx_path}/T0002/hq_cache/block_fg.dat"
        return self.reader.get_df(file_path, BlockReader_TYPE_FLAT)

    def get_concept_blocks(self) -> pd.DataFrame:
        """获取概念板块"""
        file_path = f"{self.tdx_path}/T0002/hq_cache/block_gn.dat"
        return self.reader.get_df(file_path, BlockReader_TYPE_FLAT)

    def get_default_blocks(self) -> pd.DataFrame:
        """获取默认板块"""
        file_path = f"{self.tdx_path}/T0002/hq_cache/block.dat"
        return self.reader.get_df(file_path, BlockReader_TYPE_FLAT)
```

**步骤2**: 集成到 TdxDataSource

```python
# 在 src/adapters/tdx_adapter.py 添加方法

def get_block_data(self, block_type: str = 'all') -> pd.DataFrame:
    """
    获取板块数据

    Args:
        block_type: 板块类型 ('index', 'style', 'concept', 'default', 'all')

    Returns:
        pd.DataFrame: 板块数据
    """
    try:
        from src.data_sources.tdx_block_reader import TdxBlockReader

        reader = TdxBlockReader(self.tdx_path)

        if block_type == 'index':
            return reader.get_index_blocks()
        elif block_type == 'style':
            return reader.get_style_blocks()
        elif block_type == 'concept':
            return reader.get_concept_blocks()
        elif block_type == 'default':
            return reader.get_default_blocks()
        elif block_type == 'all':
            # 合并所有板块
            dfs = [
                reader.get_index_blocks(),
                reader.get_style_blocks(),
                reader.get_concept_blocks(),
                reader.get_default_blocks()
            ]
            return pd.concat(dfs, ignore_index=True)
        else:
            raise ValueError(f"不支持的板块类型: {block_type}")
    except Exception as e:
        self.logger.error(f"获取板块数据失败: {e}")
        return pd.DataFrame()
```

**数据库路由**:
- **信息类别**: `DataClassification.REFERENCE_DATA`
- **目标数据库**: PostgreSQL
- **表名**: `stock_blocks`
- **更新频率**: 每周更新

**配置**:
```yaml
- name: stock_blocks
  description: 股票板块分类
  database: postgresql
  info_category: REFERENCE_DATA
  schema:
    blockname: varchar(50)
    block_type: varchar(20)
    code: varchar(10)
    code_index: int
    updated_at: timestamp
    PRIMARY KEY (blockname, code)
```

---

## 🎯 增强方案六: 分时数据和分笔成交

### 6.1 目标

实现分时行情和分笔成交数据获取

### 6.2 PyTDX参考实现

**API方法**:
- `get_minute_time_data()` - 实时分时行情
- `get_history_minute_time_data()` - 历史分时行情
- `get_transaction_data()` - 分笔成交明细
- `get_history_transaction_data()` - 历史分笔成交

**返回字段**:
```python
# 分时数据
{
    'datetime': datetime,
    'price': float,
    'volume': int,
    'turnover': float
}

# 分笔数据
{
    'time': str,
    'price': float,
    'volume': int,
    'turnover': float,
    'nature': str  # 买卖性质
}
```

### 6.3 MyStocks实现方案

**添加方法**:

```python
def get_intraday_time_data(self, symbol: str, date: str = None) -> pd.DataFrame:
    """
    获取分时行情数据

    Args:
        symbol: 股票代码
        date: 日期 (YYYY-MM-DD), None表示实时

    Returns:
        pd.DataFrame: 分时数据
    """
    # 实现略
    pass

def get_transaction_data(self, symbol: str, date: str = None) -> pd.DataFrame:
    """
    获取分笔成交数据

    Args:
        symbol: 股票代码
        date: 日期 (YYYY-MM-DD), None表示实时

    Returns:
        pd.DataFrame: 分笔成交数据
    """
    # 实现略
    pass
```

**数据库路由**:
- **信息类别**: `DataClassification.MINUTE_KLINE` (分钟K线)
- **目标数据库**: TDengine
- **表名**: `intraday_time_data`, `transaction_data`
- **理由**: 高频数据,TDengine压缩优势明显

---

## 📦 文件复制清单

### 需要从 `/opt/iflow/tdxpy/` 复制的文件

| 文件路径 | 用途 | 目标位置 |
|---------|------|---------|
| `pytdx/reader/block_reader.py` | 板块数据读取 | `src/data_sources/tdx_block_reader.py` (适配) |
| `pytdx/reader/gbbq_reader.py` | 除权除息读取 | `src/data_sources/tdx_dividend_reader.py` (适配) |
| `pytdx/params.py` | 参数常量 | `src/data_sources/tdx_params.py` (参考) |

### 新建文件

1. `src/data_sources/tdx_block_reader.py` - 板块数据读取器
2. `src/data_sources/tdx_dividend_reader.py` - 除权除息读取器
3. `src/data_sources/tdx_company_info.py` - 公司信息获取器

---

## 🚀 实施优先级

### P0 (立即实施) - 高价值,低复杂度

1. ✅ **扩展K线周期** (周/月/季/年)
   - 复杂度: 低
   - 价值: 高 (长期投资者需求)
   - 实施时间: 1小时

2. ✅ **板块数据支持**
   - 复杂度: 低 (复制现有代码)
   - 价值: 高 (板块轮动策略)
   - 实施时间: 2小时

### P1 (近期实施) - 中等价值,中等复杂度

3. **财务数据支持**
   - 复杂度: 中
   - 价值: 高 (基本面分析)
   - 实施时间: 3小时

4. **除权除息数据**
   - 复杂度: 中
   - 价值: 高 (复权计算)
   - 实施时间: 2小时

### P2 (中期实施) - 中等价值,高复杂度

5. **公司信息分类**
   - 复杂度: 高
   - 价值: 中
   - 实施时间: 4小时

6. **分时数据和分笔成交**
   - 复杂度: 高
   - 价值: 中
   - 实施时间: 4小时

---

## 📋 实施检查清单

### Phase 1: K线周期扩展
- [ ] 更新 `period_map` 添加4种新周期
- [ ] 更新文档字符串
- [ ] 添加使用示例
- [ ] 更新数据库表配置
- [ ] 测试4种新周期数据获取

### Phase 2: 板块数据
- [ ] 复制 `block_reader.py`
- [ ] 创建 `TdxBlockReader` 类
- [ ] 集成到 `TdxDataSource`
- [ ] 创建数据库表
- [ ] 测试4种板块数据获取

### Phase 3: 财务数据
- [ ] 实现 `get_financial_info()`
- [ ] 更新接口定义
- [ ] 配置数据库表
- [ ] 测试财务数据获取

### Phase 4: 除权除息
- [ ] 复制 `gbbq_reader.py`
- [ ] 创建 `TdxDividendReader` 类
- [ ] 集成到 `TdxDataSource`
- [ ] 配置数据库表
- [ ] 测试除权除息数据

### Phase 5: 公司信息
- [ ] 实现 `get_company_info_categories()`
- [ ] 实现 `get_company_info_content()`
- [ ] 配置数据库缓存表
- [ ] 测试16个类别获取

### Phase 6: 分时数据
- [ ] 实现 `get_intraday_time_data()`
- [ ] 实现 `get_transaction_data()`
- [ ] 配置TDengine表
- [ ] 测试分时和分笔数据

---

## 📈 预期效果

实施完成后,MyStocks TDX适配器将支持:

| 指标 | 当前 | 增强后 | 提升 |
|------|------|--------|------|
| **数据类型数量** | 11种 | 30+种 | **+173%** |
| **K线周期** | 6种 | 10种 | **+67%** |
| **财务指标** | 0个 | 15+个 | **+∞** |
| **板块类型** | 0种 | 4种 | **+∞** |
| **公司信息类别** | 0个 | 16个 | **+∞** |

**核心优势**:
- 🎯 **功能完整性**: 覆盖通达信90%+数据类型
- 🚀 **实施效率**: 复用PyTDX成熟代码
- 💾 **数据路由**: 自动选择最优数据库
- 📊 **统一接口**: 与现有架构无缝集成

---

**文档维护**: MyStocks项目组
**最后更新**: 2026-01-02
**相关文档**:
- `docs/reports/TDX_DATA_INVENTORY.md` - 当前TDX数据清单
- `/opt/iflow/tdxpy/data_catalog.md` - PyTDX完整功能清单
- `/opt/iflow/tdxpy/data_quick_reference.md` - PyTDX快速参考
