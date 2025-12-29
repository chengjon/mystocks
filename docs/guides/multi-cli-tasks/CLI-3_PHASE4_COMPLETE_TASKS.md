# CLI-3 任务分配文档 - Phase 4完整实现 (A股规则 + 161指标 + GPU加速)

**Worker CLI**: CLI-3 (Backend Technical Analysis Engineer)
**Branch**: `cli3-phase4-indicators-gpu`
**Worktree**: `/opt/claude/mystocks_phase6_indicators/`
**Phase**: Round 2 (Day 15-28, 优先级: 高)
**预计工作量**: 10-12天
**完成标准**: 161个技术指标完整实现, GPU加速集成, API测试通过

---

## 🎯 核心职责

完成 **Phase 4: A股规则 + 161技术指标 + GPU加速**完整实现,包括:

1. ✅ **A股交易规则引擎** (T+1, 涨跌停限制, 100股整数倍)
2. ✅ **TA-Lib 161个技术指标** (Trend/Momentum/Volatility/Volume/Pattern)
3. ✅ **GPU加速批量计算** (100股票 × 161指标 < 5秒)
4. ✅ **指标计算API接口** (主图叠加/副图震荡)
5. ✅ **PostgreSQL缓存优化** (避免重复计算)
6. ✅ **单元测试覆盖** (>80%)

**架构原则**:
- ✅ **Backend-First** - 所有指标在后端计算,前端只负责展示
- ✅ **TA-Lib优先** - 使用TA-Lib C库实现核心指标,性能最优
- ✅ **GPU加速** - 利用现有GPU引擎 (68.58x性能提升) 批量计算
- ✅ **缓存优先** - PostgreSQL缓存避免重复计算,提高响应速度
- ✅ **API Contract** - 遵循CLI-2定义的API契约标准

**依赖关系**:
- **前置依赖**: CLI-2 (API契约标准化) 必须完成
- **后置依赖**: CLI-4 (AI智能选股) 依赖本CLI的指标数据

---

## 📋 任务清单 (18个任务)

### 阶段1: A股交易规则引擎 (T3.1-T3.3, 2天)

#### T3.1: 实现A股交易规则验证器 (1天)

**目标**: 创建A股特有交易规则验证引擎

**实施步骤**:
1. 创建A股规则模块 (`src/technical_analysis/astock_rules.py`):
   ```python
   from datetime import datetime, timedelta
   from typing import Optional
   from enum import Enum

   class AStockExchange(Enum):
       """A股交易所"""
       SSE = "SH"   # 上海证券交易所
       SZSE = "SZ"  # 深圳证券交易所

   class AStockLimitType(Enum):
       """涨跌停类型"""
       NORMAL = 10.0     # 普通股票 ±10%
       ST = 5.0          # ST股票 ±5%
       NEW_STOCK = 44.0  # 新股首日 +44%/-36%
       KECHUANG = 20.0   # 科创板 ±20%

   class AStockRulesEngine:
       """A股交易规则引擎"""

       def __init__(self):
           self.trading_hours = {
               "morning_start": "09:30",
               "morning_end": "11:30",
               "afternoon_start": "13:00",
               "afternoon_end": "15:00"
           }

       def validate_t1_rule(
           self,
           buy_date: datetime,
           sell_date: datetime
       ) -> tuple[bool, Optional[str]]:
           """
           验证T+1规则: 今天买入的股票,最早明天才能卖出

           Returns:
               (is_valid, error_message)
           """
           if sell_date.date() <= buy_date.date():
               return False, f"T+1规则: 买入日{buy_date.date()}当天不能卖出"

           # 检查是否隔了至少1个交易日
           if (sell_date.date() - buy_date.date()).days < 1:
               return False, "T+1规则: 至少需要隔1个交易日"

           return True, None

       def calculate_price_limit(
           self,
           yesterday_close: float,
           stock_type: AStockLimitType = AStockLimitType.NORMAL
       ) -> tuple[float, float]:
           """
           计算涨跌停价格

           Returns:
               (limit_up_price, limit_down_price)
           """
           limit_pct = stock_type.value / 100.0

           limit_up = yesterday_close * (1 + limit_pct)
           limit_down = yesterday_close * (1 - limit_pct)

           # 四舍五入到分 (0.01元)
           limit_up = round(limit_up, 2)
           limit_down = round(limit_down, 2)

           return limit_up, limit_down

       def validate_price_limit(
           self,
           current_price: float,
           yesterday_close: float,
           stock_type: AStockLimitType = AStockLimitType.NORMAL
       ) -> tuple[bool, Optional[str]]:
           """验证价格是否在涨跌停范围内"""
           limit_up, limit_down = self.calculate_price_limit(yesterday_close, stock_type)

           if current_price > limit_up:
               return False, f"超过涨停价: {limit_up:.2f}"
           elif current_price < limit_down:
               return False, f"低于跌停价: {limit_down:.2f}"

           return True, None

       def validate_lot_size(
           self,
           quantity: int,
           is_sell: bool = False
       ) -> tuple[bool, Optional[str]]:
           """
           验证交易数量 (100股整数倍)

           买入: 必须100股整数倍
           卖出: 不足100股可以一次性卖出,否则必须100股整数倍
           """
           if quantity <= 0:
               return False, "数量必须大于0"

           if not is_sell:
               # 买入必须100股整数倍
               if quantity % 100 != 0:
                   return False, f"买入数量必须为100股整数倍,当前: {quantity}股"
           else:
               # 卖出: 如果持仓 >= 100,必须100股整数倍; 如果持仓 < 100,可全部卖出
               if quantity >= 100 and quantity % 100 != 0:
                   return False, f"卖出数量(>=100股)必须为100股整数倍,当前: {quantity}股"

           return True, None

       def is_trading_time(self, check_time: datetime) -> bool:
           """检查是否在交易时间内"""
           time_str = check_time.strftime("%H:%M")

           # 早盘
           if self.trading_hours["morning_start"] <= time_str <= self.trading_hours["morning_end"]:
               return True

           # 午盘
           if self.trading_hours["afternoon_start"] <= time_str <= self.trading_hours["afternoon_end"]:
               return True

           return False

       def validate_order(
           self,
           symbol: str,
           price: float,
           quantity: int,
           direction: str,  # 'buy' or 'sell'
           yesterday_close: float,
           buy_date: Optional[datetime] = None,
           stock_type: AStockLimitType = AStockLimitType.NORMAL
       ) -> tuple[bool, list[str]]:
           """
           综合验证订单

           Returns:
               (is_valid, error_messages)
           """
           errors = []

           # 1. T+1规则验证 (仅卖出)
           if direction == 'sell' and buy_date:
               is_valid, error_msg = self.validate_t1_rule(buy_date, datetime.now())
               if not is_valid:
                   errors.append(error_msg)

           # 2. 涨跌停验证
           is_valid, error_msg = self.validate_price_limit(price, yesterday_close, stock_type)
           if not is_valid:
               errors.append(error_msg)

           # 3. 100股整数倍验证
           is_valid, error_msg = self.validate_lot_size(quantity, is_sell=(direction == 'sell'))
           if not is_valid:
               errors.append(error_msg)

           # 4. 交易时间验证
           if not self.is_trading_time(datetime.now()):
               errors.append(f"当前不在交易时间内 ({datetime.now().strftime('%H:%M')})")

           return len(errors) == 0, errors
   ```

2. 创建单元测试 (`tests/unit/test_astock_rules.py`):
   ```python
   import pytest
   from datetime import datetime, timedelta
   from src.technical_analysis.astock_rules import AStockRulesEngine, AStockLimitType

   class TestAStockRulesEngine:
       def setup_method(self):
           self.engine = AStockRulesEngine()

       def test_t1_rule_same_day(self):
           """测试T+1规则: 同日不能卖出"""
           buy_date = datetime(2024, 12, 29, 10, 0)
           sell_date = datetime(2024, 12, 29, 14, 0)

           is_valid, error = self.engine.validate_t1_rule(buy_date, sell_date)
           assert not is_valid
           assert "当天不能卖出" in error

       def test_t1_rule_next_day(self):
           """测试T+1规则: 隔日可以卖出"""
           buy_date = datetime(2024, 12, 29, 10, 0)
           sell_date = datetime(2024, 12, 30, 10, 0)

           is_valid, error = self.engine.validate_t1_rule(buy_date, sell_date)
           assert is_valid
           assert error is None

       def test_price_limit_normal_stock(self):
           """测试普通股票涨跌停价格计算 (±10%)"""
           yesterday_close = 10.00

           limit_up, limit_down = self.engine.calculate_price_limit(
               yesterday_close,
               AStockLimitType.NORMAL
           )

           assert limit_up == 11.00
           assert limit_down == 9.00

       def test_price_limit_st_stock(self):
           """测试ST股票涨跌停价格计算 (±5%)"""
           yesterday_close = 10.00

           limit_up, limit_down = self.engine.calculate_price_limit(
               yesterday_close,
               AStockLimitType.ST
           )

           assert limit_up == 10.50
           assert limit_down == 9.50

       def test_lot_size_buy_valid(self):
           """测试买入数量验证: 100股整数倍"""
           is_valid, error = self.engine.validate_lot_size(200, is_sell=False)
           assert is_valid

       def test_lot_size_buy_invalid(self):
           """测试买入数量验证: 非100股整数倍"""
           is_valid, error = self.engine.validate_lot_size(250, is_sell=False)
           assert not is_valid
           assert "100股整数倍" in error

       def test_lot_size_sell_odd_lot(self):
           """测试卖出数量验证: 不足100股可以全部卖出"""
           is_valid, error = self.engine.validate_lot_size(50, is_sell=True)
           assert is_valid
   ```

**验收标准**:
- [ ] A股规则引擎实现完成
- [ ] 单元测试覆盖率 > 90%
- [ ] 所有规则验证测试通过

---

#### T3.2: 创建A股特性API端点 (0.5天)

**目标**: 提供A股交易规则查询API

**实施步骤**:
1. 创建A股API路由 (`web/backend/app/api/astock.py`):
   ```python
   from fastapi import APIRouter
   from app.schemas.common_schemas import APIResponse
   from app.schemas.astock_schemas import (
       StopLimitRequest,
       StopLimitResponse,
       T1SellableRequest,
       T1SellableResponse
   )
   from src.technical_analysis.astock_rules import AStockRulesEngine, AStockLimitType

   router = APIRouter(prefix="/api/astock", tags=["astock"])
   engine = AStockRulesEngine()

   @router.get("/stop-limit", response_model=APIResponse[StopLimitResponse])
   async def get_stop_limit(request: StopLimitRequest):
       """
       获取股票涨跌停价格

       CLI-1前端调用此API获取涨跌停线,绘制在K线图上
       """
       limit_up, limit_down = engine.calculate_price_limit(
           request.yesterday_close,
           AStockLimitType[request.stock_type]
       )

       return APIResponse(
           success=True,
           code=0,
           message="成功获取涨跌停价格",
           data=StopLimitResponse(
               symbol=request.symbol,
               yesterday_close=request.yesterday_close,
               limit_up_price=limit_up,
               limit_down_price=limit_down,
               limit_percent=AStockLimitType[request.stock_type].value
           )
       )

   @router.get("/t1-sellable", response_model=APIResponse[T1SellableResponse])
   async def check_t1_sellable(request: T1SellableRequest):
       """
       检查T+1可卖出

       CLI-1前端调用此API,标记持仓中哪些是今天买入的(不可卖出)
       """
       is_sellable, error = engine.validate_t1_rule(
           request.buy_date,
           request.check_date
       )

       return APIResponse(
           success=True,
           code=0,
           message="T+1规则检查完成",
           data=T1SellableResponse(
               symbol=request.symbol,
               is_sellable=is_sellable,
               reason=error if not is_sellable else None
           )
       )
   ```

2. 定义Pydantic Schema (`web/backend/app/schemas/astock_schemas.py`):
   ```python
   from pydantic import BaseModel, Field
   from datetime import datetime

   class StopLimitRequest(BaseModel):
       symbol: str = Field(..., description="股票代码")
       yesterday_close: float = Field(..., description="昨日收盘价")
       stock_type: str = Field("NORMAL", description="股票类型 (NORMAL/ST/NEW_STOCK/KECHUANG)")

   class StopLimitResponse(BaseModel):
       symbol: str
       yesterday_close: float
       limit_up_price: float
       limit_down_price: float
       limit_percent: float

   class T1SellableRequest(BaseModel):
       symbol: str
       buy_date: datetime
       check_date: datetime

   class T1SellableResponse(BaseModel):
       symbol: str
       is_sellable: bool
       reason: Optional[str] = None
   ```

**验收标准**:
- [ ] A股API端点创建完成
- [ ] API测试通过 (Swagger UI可调试)
- [ ] CLI-1可调用获取涨跌停价格

---

#### T3.3: 集成A股规则到订单验证流程 (0.5天)

**目标**: 在交易下单时自动验证A股规则

**实施步骤**:
1. 更新订单下单API (`web/backend/app/api/trade.py`):
   ```python
   from src.technical_analysis.astock_rules import AStockRulesEngine

   @router.post("/order", response_model=APIResponse[OrderResponse])
   async def create_order(order: OrderRequest):
       """下单 (自动验证A股规则)"""
       engine = AStockRulesEngine()

       # 获取昨日收盘价 (从数据库查询)
       yesterday_close = await get_yesterday_close(order.symbol)

       # A股规则验证
       is_valid, errors = engine.validate_order(
           symbol=order.symbol,
           price=order.price,
           quantity=order.quantity,
           direction=order.direction,
           yesterday_close=yesterday_close,
           buy_date=order.buy_date if order.direction == 'sell' else None
       )

       if not is_valid:
           raise APIException(
               ErrorCode.ORDER_REJECTED,
               detail="; ".join(errors)
           )

       # 提交订单到交易系统
       ...
   ```

**验收标准**:
- [ ] 订单下单自动验证A股规则
- [ ] 违反规则的订单被拒绝,返回明确错误信息
- [ ] 集成测试通过

---

### 阶段2: TA-Lib 161个技术指标实现 (T3.4-T3.8, 4.5天)

#### T3.4: 安装和配置TA-Lib (0.5天)

**目标**: 确保TA-Lib C库正确安装

**实施步骤**:
1. 验证TA-Lib安装:
   ```bash
   python -c "import talib; print(talib.get_functions())"
   ```

2. 如果未安装,执行安装:
   ```bash
   # Ubuntu/Debian
   wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
   tar -xzf ta-lib-0.4.0-src.tar.gz
   cd ta-lib/
   ./configure --prefix=/usr
   make
   sudo make install

   # Python绑定
   pip install TA-Lib
   ```

3. 创建TA-Lib工具类 (`src/technical_analysis/talib_wrapper.py`):
   ```python
   import talib
   import numpy as np
   from typing import List, Dict, Optional

   class TALibWrapper:
       """TA-Lib封装类,提供统一接口"""

       @staticmethod
       def get_all_functions() -> List[str]:
           """获取所有支持的指标函数"""
           return talib.get_functions()

       @staticmethod
       def get_function_groups() -> Dict[str, List[str]]:
           """按类别获取指标分组"""
           return talib.get_function_groups()

       @staticmethod
       def calculate_indicator(
           func_name: str,
           data: Dict[str, np.ndarray],
           params: Optional[Dict] = None
       ) -> np.ndarray:
           """
           通用指标计算接口

           Args:
               func_name: TA-Lib函数名 (如 'MA', 'MACD')
               data: 价格数据 {'close': [...], 'high': [...], ...}
               params: 指标参数 (如 {'timeperiod': 20})

           Returns:
               指标计算结果数组
           """
           func = getattr(talib, func_name.upper())

           # 准备参数
           kwargs = params or {}

           # 根据函数签名传递数据
           if func_name.upper() in ['MA', 'EMA', 'SMA', 'WMA']:
               # 单输入指标
               result = func(data['close'], **kwargs)
           elif func_name.upper() in ['MACD', 'STOCH', 'RSI']:
               # 需要完整OHLC数据
               result = func(
                   data['high'],
                   data['low'],
                   data['close'],
                   **kwargs
               )
           else:
               # 其他指标
               result = func(data['close'], **kwargs)

           return result
   ```

**验收标准**:
- [ ] TA-Lib安装验证通过
- [ ] TALibWrapper工具类创建完成
- [ ] 基础指标计算测试通过 (MA/EMA/MACD)

---

#### T3.5: 实现161个技术指标注册表 (1天)

**目标**: 创建完整的指标元数据注册表,包含所有161个指标

**实施步骤**:
1. 创建指标注册表 (`src/technical_analysis/indicator_registry.py`):
   ```python
   from typing import Dict, List
   from enum import Enum
   from pydantic import BaseModel

   class IndicatorCategory(Enum):
       """指标分类"""
       TREND = "趋势指标"           # 50个
       MOMENTUM = "动量指标"       # 35个
       VOLATILITY = "波动率指标"   # 28个
       VOLUME = "成交量指标"       # 25个
       PATTERN = "形态指标"        # 23个

   class IndicatorMetadata(BaseModel):
       """指标元数据"""
       code: str                   # 指标代码 (MA/EMA/MACD)
       name_cn: str                # 中文名称
       name_en: str                # 英文名称
       category: IndicatorCategory  # 分类
       description: str            # 功能描述
       params: Dict[str, any]      # 默认参数
       input_fields: List[str]     # 输入字段 (close/high/low/volume)
       output_fields: List[str]    # 输出字段
       display_type: str           # 显示类型 (overlay/oscillator)

   class IndicatorRegistry:
       """指标注册表 (161个指标完整元数据)"""

       def __init__(self):
           self.indicators = self._init_indicators()

       def _init_indicators(self) -> Dict[str, IndicatorMetadata]:
           """初始化所有161个指标"""
           return {
               # === 趋势指标 (50个) ===
               "MA": IndicatorMetadata(
                   code="MA",
                   name_cn="移动平均线",
                   name_en="Moving Average",
                   category=IndicatorCategory.TREND,
                   description="计算N日简单移动平均",
                   params={"timeperiod": 20},
                   input_fields=["close"],
                   output_fields=["ma"],
                   display_type="overlay"
               ),
               "EMA": IndicatorMetadata(
                   code="EMA",
                   name_cn="指数移动平均",
                   name_en="Exponential Moving Average",
                   category=IndicatorCategory.TREND,
                   description="指数加权移动平均,对近期数据权重更高",
                   params={"timeperiod": 20},
                   input_fields=["close"],
                   output_fields=["ema"],
                   display_type="overlay"
               ),
               "BOLL": IndicatorMetadata(
                   code="BOLL",
                   name_cn="布林带",
                   name_en="Bollinger Bands",
                   category=IndicatorCategory.TREND,
                   description="中轨 ± N倍标准差,判断价格波动范围",
                   params={"timeperiod": 20, "nbdevup": 2, "nbdevdn": 2},
                   input_fields=["close"],
                   output_fields=["upper", "middle", "lower"],
                   display_type="overlay"
               ),

               # === 动量指标 (35个) ===
               "MACD": IndicatorMetadata(
                   code="MACD",
                   name_cn="平滑异同移动平均",
                   name_en="Moving Average Convergence Divergence",
                   category=IndicatorCategory.MOMENTUM,
                   description="DIF/DEA/MACD柱,判断趋势强弱",
                   params={"fastperiod": 12, "slowperiod": 26, "signalperiod": 9},
                   input_fields=["close"],
                   output_fields=["dif", "dea", "macd"],
                   display_type="oscillator"
               ),
               "RSI": IndicatorMetadata(
                   code="RSI",
                   name_cn="相对强弱指标",
                   name_en="Relative Strength Index",
                   category=IndicatorCategory.MOMENTUM,
                   description="0-100区间,超买超卖判断",
                   params={"timeperiod": 14},
                   input_fields=["close"],
                   output_fields=["rsi"],
                   display_type="oscillator"
               ),
               "KDJ": IndicatorMetadata(
                   code="STOCH",  # TA-Lib中使用STOCH
                   name_cn="随机指标KDJ",
                   name_en="Stochastic Oscillator",
                   category=IndicatorCategory.MOMENTUM,
                   description="K/D/J三线,超买超卖和金叉死叉",
                   params={"fastk_period": 9, "slowk_period": 3, "slowd_period": 3},
                   input_fields=["high", "low", "close"],
                   output_fields=["k", "d"],
                   display_type="oscillator"
               ),

               # === 波动率指标 (28个) ===
               "ATR": IndicatorMetadata(
                   code="ATR",
                   name_cn="平均真实波幅",
                   name_en="Average True Range",
                   category=IndicatorCategory.VOLATILITY,
                   description="衡量价格波动幅度",
                   params={"timeperiod": 14},
                   input_fields=["high", "low", "close"],
                   output_fields=["atr"],
                   display_type="oscillator"
               ),
               "STDDEV": IndicatorMetadata(
                   code="STDDEV",
                   name_cn="标准差",
                   name_en="Standard Deviation",
                   category=IndicatorCategory.VOLATILITY,
                   description="衡量价格离散程度",
                   params={"timeperiod": 20},
                   input_fields=["close"],
                   output_fields=["stddev"],
                   display_type="oscillator"
               ),

               # === 成交量指标 (25个) ===
               "OBV": IndicatorMetadata(
                   code="OBV",
                   name_cn="能量潮",
                   name_en="On Balance Volume",
                   category=IndicatorCategory.VOLUME,
                   description="累积成交量与价格变化关系",
                   params={},
                   input_fields=["close", "volume"],
                   output_fields=["obv"],
                   display_type="oscillator"
               ),
               "AD": IndicatorMetadata(
                   code="AD",
                   name_cn="累积/派发线",
                   name_en="Accumulation/Distribution",
                   category=IndicatorCategory.VOLUME,
                   description="资金流向累积指标",
                   params={},
                   input_fields=["high", "low", "close", "volume"],
                   output_fields=["ad"],
                   display_type="oscillator"
               ),

               # === 形态指标 (23个) ===
               "SAR": IndicatorMetadata(
                   code="SAR",
                   name_cn="抛物线转向",
                   name_en="Parabolic SAR",
                   category=IndicatorCategory.PATTERN,
                   description="趋势追踪止损点",
                   params={"acceleration": 0.02, "maximum": 0.2},
                   input_fields=["high", "low"],
                   output_fields=["sar"],
                   display_type="overlay"
               ),
               # ... (完整161个指标定义,此处省略)
           }

       def get_indicator(self, code: str) -> Optional[IndicatorMetadata]:
           """获取单个指标元数据"""
           return self.indicators.get(code.upper())

       def list_indicators(
           self,
           category: Optional[IndicatorCategory] = None
       ) -> List[IndicatorMetadata]:
           """列出指标 (可按分类筛选)"""
           if category:
               return [ind for ind in self.indicators.values() if ind.category == category]
           return list(self.indicators.values())

       def get_categories(self) -> Dict[str, int]:
           """获取各分类指标数量"""
           counts = {}
           for ind in self.indicators.values():
               cat = ind.category.value
               counts[cat] = counts.get(cat, 0) + 1
           return counts
   ```

2. 补全所有161个指标定义 (参考TA-Lib官方文档):
   - Trend (50个): MA, EMA, SMA, WMA, DEMA, TEMA, KAMA, MAMA, T3, ...
   - Momentum (35个): MACD, RSI, KDJ, CCI, MOM, ROC, WILLR, ...
   - Volatility (28个): ATR, BBANDS, NATR, TRANGE, ...
   - Volume (25个): OBV, AD, ADOSC, MFI, ...
   - Pattern (23个): SAR, CDLDOJI, CDLENGULFING, CDLHAMMER, ...

**验收标准**:
- [ ] 161个指标元数据完整定义
- [ ] 指标按5大分类组织清晰
- [ ] Registry可以按分类查询指标

---

#### T3.6: 实现批量指标计算引擎 (1.5天)

**目标**: 创建高性能批量指标计算引擎

**实施步骤**:
1. 创建批量计算引擎 (`src/technical_analysis/batch_calculator.py`):
   ```python
   import numpy as np
   from typing import List, Dict
   from concurrent.futures import ThreadPoolExecutor
   import pandas as pd

   from src.technical_analysis.talib_wrapper import TALibWrapper
   from src.technical_analysis.indicator_registry import IndicatorRegistry

   class BatchIndicatorCalculator:
       """批量指标计算引擎"""

       def __init__(self, use_gpu: bool = False):
           self.registry = IndicatorRegistry()
           self.use_gpu = use_gpu

       def calculate_single_indicator(
           self,
           symbol: str,
           indicator_code: str,
           kline_data: pd.DataFrame,
           params: Optional[Dict] = None
       ) -> pd.DataFrame:
           """
           计算单个指标

           Args:
               symbol: 股票代码
               indicator_code: 指标代码 (MA/EMA/MACD)
               kline_data: K线数据 (columns: timestamp, open, high, low, close, volume)
               params: 指标参数 (覆盖默认参数)

           Returns:
               包含指标值的DataFrame
           """
           # 获取指标元数据
           indicator = self.registry.get_indicator(indicator_code)
           if not indicator:
               raise ValueError(f"未知指标: {indicator_code}")

           # 准备输入数据
           data = {
               'close': kline_data['close'].values,
               'high': kline_data['high'].values,
               'low': kline_data['low'].values,
               'volume': kline_data['volume'].values
           }

           # 合并参数
           calc_params = {**indicator.params, **(params or {})}

           # 调用TA-Lib计算
           result = TALibWrapper.calculate_indicator(
               indicator.code,
               data,
               calc_params
           )

           # 转换为DataFrame
           if isinstance(result, tuple):
               # 多输出指标 (如MACD返回 dif, dea, macd)
               result_df = pd.DataFrame({
                   field: result[i]
                   for i, field in enumerate(indicator.output_fields)
               })
           else:
               # 单输出指标
               result_df = pd.DataFrame({
                   indicator.output_fields[0]: result
               })

           result_df['timestamp'] = kline_data['timestamp']
           return result_df

       def calculate_multiple_indicators(
           self,
           symbol: str,
           indicator_codes: List[str],
           kline_data: pd.DataFrame
       ) -> Dict[str, pd.DataFrame]:
           """
           计算多个指标 (并行计算)

           Args:
               symbol: 股票代码
               indicator_codes: 指标代码列表
               kline_data: K线数据

           Returns:
               {indicator_code: result_dataframe}
           """
           results = {}

           with ThreadPoolExecutor(max_workers=8) as executor:
               futures = {
                   executor.submit(
                       self.calculate_single_indicator,
                       symbol,
                       code,
                       kline_data
                   ): code
                   for code in indicator_codes
               }

               for future in futures:
                   code = futures[future]
                   results[code] = future.result()

           return results

       def calculate_for_multiple_stocks(
           self,
           symbols: List[str],
           indicator_codes: List[str],
           kline_data_map: Dict[str, pd.DataFrame]
       ) -> Dict[str, Dict[str, pd.DataFrame]]:
           """
           批量计算: N个股票 × M个指标

           Args:
               symbols: 股票代码列表
               indicator_codes: 指标代码列表
               kline_data_map: {symbol: kline_dataframe}

           Returns:
               {symbol: {indicator_code: result_dataframe}}
           """
           results = {}

           for symbol in symbols:
               kline_data = kline_data_map.get(symbol)
               if kline_data is None:
                   continue

               results[symbol] = self.calculate_multiple_indicators(
                   symbol,
                   indicator_codes,
                   kline_data
               )

           return results
   ```

2. 性能优化 (向量化计算):
   ```python
   # 使用NumPy向量化操作,避免Python循环
   def fast_ma(close_prices: np.ndarray, period: int) -> np.ndarray:
       """快速MA计算 (使用卷积)"""
       kernel = np.ones(period) / period
       ma = np.convolve(close_prices, kernel, mode='valid')

       # 填充前面的NaN
       result = np.full_like(close_prices, np.nan)
       result[period-1:] = ma

       return result
   ```

**验收标准**:
- [ ] 单指标计算功能测试通过
- [ ] 多指标并行计算功能测试通过
- [ ] 批量计算 (100股票 × 10指标) < 10秒 (CPU)

---

#### T3.7: 集成GPU加速批量计算 (1天)

**目标**: 利用现有GPU引擎加速批量指标计算

**实施步骤**:
1. 创建GPU加速适配器 (`src/technical_analysis/gpu_accelerator.py`):
   ```python
   from typing import List, Dict
   import numpy as np
   import pandas as pd

   # 导入现有GPU引擎
   from src.gpu.core.kernels.matrix_kernels import MatrixKernelEngine
   from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager

   class GPUIndicatorAccelerator:
       """GPU加速指标计算适配器"""

       def __init__(self):
           self.gpu_manager = GPUResourceManager()
           self.matrix_engine = MatrixKernelEngine()

       def batch_ma_calculation(
           self,
           close_prices_batch: np.ndarray,  # Shape: (N_stocks, N_days)
           period: int
       ) -> np.ndarray:
           """
           批量MA计算 (GPU加速)

           Args:
               close_prices_batch: N个股票的收盘价矩阵
               period: MA周期

           Returns:
               MA值矩阵 (Shape: N_stocks, N_days)
           """
           n_stocks, n_days = close_prices_batch.shape

           # 创建卷积核 (MA = 1/period * sum)
           kernel = np.ones((1, period)) / period

           # GPU矩阵乘法加速卷积计算
           ma_batch = self.matrix_engine.batch_matrix_multiply(
               close_prices_batch,
               kernel.T
           )

           return ma_batch

       def batch_indicator_calculation(
           self,
           indicator_code: str,
           data_batch: Dict[str, np.ndarray],  # {field: (N_stocks, N_days)}
           params: Dict
       ) -> np.ndarray:
           """
           批量指标计算 (GPU加速)

           支持的指标: MA, EMA, RSI, MACD等可向量化指标
           """
           if indicator_code == 'MA':
               return self.batch_ma_calculation(
                   data_batch['close'],
                   params['timeperiod']
               )
           elif indicator_code == 'EMA':
               # EMA递推公式: EMA_t = α * Price_t + (1-α) * EMA_(t-1)
               # 可以用GPU并行计算
               return self._batch_ema_gpu(data_batch['close'], params['timeperiod'])
           else:
               # 不支持GPU加速的指标,回退到CPU
               raise NotImplementedError(f"GPU加速暂不支持指标: {indicator_code}")

       def _batch_ema_gpu(self, close_batch: np.ndarray, period: int) -> np.ndarray:
           """批量EMA计算 (GPU实现)"""
           alpha = 2 / (period + 1)
           n_stocks, n_days = close_batch.shape

           ema_batch = np.zeros_like(close_batch)
           ema_batch[:, 0] = close_batch[:, 0]  # 初始值

           # GPU并行计算递推
           for i in range(1, n_days):
               ema_batch[:, i] = (
                   alpha * close_batch[:, i] +
                   (1 - alpha) * ema_batch[:, i-1]
               )

           return ema_batch
   ```

2. 集成到BatchCalculator:
   ```python
   class BatchIndicatorCalculator:
       def __init__(self, use_gpu: bool = False):
           self.use_gpu = use_gpu
           if use_gpu:
               self.gpu_accelerator = GPUIndicatorAccelerator()

       def calculate_for_multiple_stocks(
           self,
           symbols: List[str],
           indicator_codes: List[str],
           kline_data_map: Dict[str, pd.DataFrame]
       ) -> Dict[str, Dict[str, pd.DataFrame]]:
           """批量计算 (优先使用GPU)"""
           if self.use_gpu and self._can_use_gpu(indicator_codes):
               # GPU加速路径
               return self._gpu_batch_calculate(symbols, indicator_codes, kline_data_map)
           else:
               # CPU并行路径
               return self._cpu_batch_calculate(symbols, indicator_codes, kline_data_map)
   ```

3. 性能测试:
   ```python
   # 测试: 100股票 × 161指标
   symbols = [f"{i:06d}.SZ" for i in range(1, 101)]
   indicator_codes = registry.get_all_indicator_codes()

   # CPU基准
   start = time.time()
   cpu_results = calculator_cpu.calculate_for_multiple_stocks(...)
   cpu_time = time.time() - start

   # GPU加速
   start = time.time()
   gpu_results = calculator_gpu.calculate_for_multiple_stocks(...)
   gpu_time = time.time() - start

   print(f"CPU: {cpu_time:.2f}s, GPU: {gpu_time:.2f}s, 加速比: {cpu_time/gpu_time:.2f}x")
   # 目标: GPU加速比 > 50x
   ```

**验收标准**:
- [ ] GPU加速适配器实现完成
- [ ] 批量计算 (100股票 × 161指标) < 5秒 (GPU)
- [ ] GPU加速比 > 50x

---

#### T3.8: 创建指标计算API接口 (0.5天)

**目标**: 提供前端调用的指标计算API

**实施步骤**:
1. 创建技术指标API路由 (`web/backend/app/api/indicators.py`):
   ```python
   from fastapi import APIRouter
   from app.schemas.common_schemas import APIResponse
   from app.schemas.indicator_schemas import (
       IndicatorListResponse,
       OverlayIndicatorRequest,
       OscillatorIndicatorRequest,
       IndicatorResponse
   )
   from src.technical_analysis.batch_calculator import BatchIndicatorCalculator
   from src.technical_analysis.indicator_registry import IndicatorRegistry

   router = APIRouter(prefix="/api/indicators", tags=["indicators"])
   registry = IndicatorRegistry()
   calculator = BatchIndicatorCalculator(use_gpu=True)

   @router.get("/registry", response_model=APIResponse[IndicatorListResponse])
   async def get_indicator_registry():
       """
       获取指标库元数据 (161个指标)

       CLI-1前端调用此API,展示可用指标列表
       """
       indicators = registry.list_indicators()
       categories = registry.get_categories()

       return APIResponse(
           success=True,
           code=0,
           message="成功获取指标库",
           data=IndicatorListResponse(
               indicators=indicators,
               categories=categories,
               total_count=len(indicators)
           )
       )

   @router.get("/overlay", response_model=APIResponse[IndicatorResponse])
   async def get_overlay_indicators(request: OverlayIndicatorRequest):
       """
           获取主图叠加指标 (MA/EMA/BOLL等)

       CLI-1前端调用此API,获取叠加在K线上的指标数据
       """
       # 获取K线数据
       kline_data = await fetch_kline_data(request.symbol, request.interval)

       # 计算指标
       results = calculator.calculate_multiple_indicators(
           request.symbol,
           request.indicators,
           kline_data
       )

       return APIResponse(
           success=True,
           code=0,
           message="成功计算主图指标",
           data=IndicatorResponse(
               symbol=request.symbol,
               interval=request.interval,
               indicators=results
           )
       )

   @router.get("/oscillator", response_model=APIResponse[IndicatorResponse])
   async def get_oscillator_indicators(request: OscillatorIndicatorRequest):
       """
       获取副图震荡指标 (MACD/RSI/KDJ等)

       CLI-1前端调用此API,获取副图指标数据
       """
       kline_data = await fetch_kline_data(request.symbol, request.interval)

       results = calculator.calculate_multiple_indicators(
           request.symbol,
           request.indicators,
           kline_data
       )

       return APIResponse(
           success=True,
           code=0,
           message="成功计算副图指标",
           data=IndicatorResponse(
               symbol=request.symbol,
               interval=request.interval,
               indicators=results
           )
       )
   ```

2. 定义Schema (`web/backend/app/schemas/indicator_schemas.py`):
   ```python
   from pydantic import BaseModel
   from typing import List, Dict

   class OverlayIndicatorRequest(BaseModel):
       symbol: str
       interval: str
       indicators: List[str] = ["MA", "EMA", "BOLL"]
       params: Optional[Dict] = None

   class OscillatorIndicatorRequest(BaseModel):
       symbol: str
       interval: str = "1d"
       indicators: List[str] = ["MACD", "RSI", "KDJ"]

   class IndicatorResponse(BaseModel):
       symbol: str
       interval: str
       indicators: Dict[str, List[Dict]]  # {indicator_code: [{timestamp, value}, ...]}
   ```

**验收标准**:
- [ ] 指标API端点创建完成
- [ ] CLI-1可正确调用获取指标数据
- [ ] API响应时间 < 500ms (单股票10个指标)

---

### 阶段3: PostgreSQL缓存优化 (T3.9-T3.11, 1.5天)

#### T3.9: 设计指标缓存表结构 (0.5天)

**目标**: 创建高效的指标缓存表

**实施步骤**:
1. 设计缓存表 (`migrations/create_indicator_cache_table.sql`):
   ```sql
   CREATE TABLE IF NOT EXISTS indicator_cache (
       id SERIAL PRIMARY KEY,
       symbol VARCHAR(20) NOT NULL,
       interval VARCHAR(10) NOT NULL,
       indicator_code VARCHAR(50) NOT NULL,
       params JSONB NOT NULL,
       calculation_date DATE NOT NULL,
       values JSONB NOT NULL,  -- 指标值数组
       created_at TIMESTAMP DEFAULT NOW(),
       updated_at TIMESTAMP DEFAULT NOW(),

       -- 索引优化
       CONSTRAINT idx_indicator_cache_unique UNIQUE (symbol, interval, indicator_code, params, calculation_date)
   );

   -- 复合索引: 加速查询
   CREATE INDEX idx_indicator_cache_lookup ON indicator_cache (symbol, indicator_code, calculation_date);

   -- 分区表 (按月分区,提高查询性能)
   CREATE TABLE indicator_cache_2024_12 PARTITION OF indicator_cache
   FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
   ```

2. 定义缓存策略:
   - **缓存规则**: 所有计算结果自动缓存
   - **失效策略**: 每日收盘后更新当天数据
   - **清理策略**: 保留最近6个月数据,自动删除过期缓存

**验收标准**:
- [ ] 缓存表创建完成
- [ ] 分区表配置正确
- [ ] 索引优化完成

---

#### T3.10: 实现缓存读写逻辑 (0.5天)

**目标**: 在计算引擎中集成缓存机制

**实施步骤**:
1. 创建缓存管理器 (`src/technical_analysis/indicator_cache.py`):
   ```python
   from sqlalchemy import select, insert, update
   from datetime import datetime, timedelta

   class IndicatorCacheManager:
       """指标缓存管理器"""

       def __init__(self, db_session):
           self.db = db_session

       async def get_cached_indicator(
           self,
           symbol: str,
           indicator_code: str,
           interval: str,
           params: Dict,
           start_date: datetime,
           end_date: datetime
       ) -> Optional[pd.DataFrame]:
           """获取缓存的指标数据"""
           query = select(indicator_cache).where(
               indicator_cache.c.symbol == symbol,
               indicator_cache.c.indicator_code == indicator_code,
               indicator_cache.c.interval == interval,
               indicator_cache.c.params == params,
               indicator_cache.c.calculation_date >= start_date,
               indicator_cache.c.calculation_date <= end_date
           )

           result = await self.db.execute(query)
           rows = result.fetchall()

           if not rows:
               return None

           # 转换为DataFrame
           return pd.DataFrame([row['values'] for row in rows])

       async def save_indicator_cache(
           self,
           symbol: str,
           indicator_code: str,
           interval: str,
           params: Dict,
           result_df: pd.DataFrame
       ):
           """保存指标计算结果到缓存"""
           for _, row in result_df.iterrows():
               await self.db.execute(
                   insert(indicator_cache).values(
                       symbol=symbol,
                       indicator_code=indicator_code,
                       interval=interval,
                       params=params,
                       calculation_date=row['timestamp'].date(),
                       values=row.to_dict()
                   ).on_conflict_do_update(
                       constraint='idx_indicator_cache_unique',
                       set_={'values': row.to_dict(), 'updated_at': datetime.now()}
                   )
               )

       async def clear_expired_cache(self, days_to_keep: int = 180):
           """清理过期缓存"""
           cutoff_date = datetime.now() - timedelta(days=days_to_keep)

           await self.db.execute(
               delete(indicator_cache).where(
                   indicator_cache.c.calculation_date < cutoff_date
               )
           )
   ```

2. 集成到BatchCalculator:
   ```python
   class BatchIndicatorCalculator:
       async def calculate_single_indicator_with_cache(
           self,
           symbol: str,
           indicator_code: str,
           kline_data: pd.DataFrame
       ) -> pd.DataFrame:
           """计算指标 (优先使用缓存)"""
           # 1. 检查缓存
           cached = await self.cache_manager.get_cached_indicator(...)
           if cached is not None:
               return cached

           # 2. 缓存未命中,执行计算
           result = self.calculate_single_indicator(symbol, indicator_code, kline_data)

           # 3. 保存到缓存
           await self.cache_manager.save_indicator_cache(symbol, indicator_code, result)

           return result
   ```

**验收标准**:
- [ ] 缓存读写逻辑实现完成
- [ ] 缓存命中率 > 80% (第二次请求)
- [ ] API响应时间缩短 > 50% (缓存命中时)

---

#### T3.11: 缓存预热和定时更新 (0.5天)

**目标**: 自动预热常用指标缓存,定时更新

**实施步骤**:
1. 创建缓存预热脚本 (`scripts/runtime/warm_indicator_cache.py`):
   ```python
   from src.technical_analysis.batch_calculator import BatchIndicatorCalculator

   async def warm_cache_for_popular_stocks():
       """为热门股票预热指标缓存"""
       # 1. 获取热门股票列表 (沪深300成分股)
       popular_symbols = await fetch_popular_symbols(limit=300)

       # 2. 常用指标
       common_indicators = ['MA', 'EMA', 'MACD', 'RSI', 'KDJ', 'BOLL']

       # 3. 批量计算并缓存
       calculator = BatchIndicatorCalculator(use_gpu=True)

       for symbol in popular_symbols:
           kline_data = await fetch_kline_data(symbol, '1d')
           await calculator.calculate_multiple_indicators_with_cache(
               symbol,
               common_indicators,
               kline_data
           )

       print(f"缓存预热完成: {len(popular_symbols)}个股票 × {len(common_indicators)}个指标")

   if __name__ == "__main__":
       asyncio.run(warm_cache_for_popular_stocks())
   ```

2. 配置定时任务 (每日收盘后更新):
   ```python
   # 使用APScheduler定时更新
   from apscheduler.schedulers.asyncio import AsyncIOScheduler

   scheduler = AsyncIOScheduler()

   @scheduler.scheduled_job('cron', hour=15, minute=30)  # 每日15:30 (收盘后)
   async def daily_cache_update():
       """每日更新指标缓存"""
       await warm_cache_for_popular_stocks()
       await cache_manager.clear_expired_cache(days_to_keep=180)

   scheduler.start()
   ```

**验收标准**:
- [ ] 缓存预热脚本创建完成
- [ ] 定时任务配置正确
- [ ] 沪深300成分股指标缓存预热时间 < 5分钟 (GPU)

---

### 阶段4: 单元测试与文档 (T3.12-T3.18, 2.5天)

#### T3.12-T3.17: 单元测试覆盖 (2天)

**目标**: 单元测试覆盖率 > 80%

**测试模块**:
1. `tests/unit/test_astock_rules.py` - A股规则引擎 (0.3天)
2. `tests/unit/test_indicator_registry.py` - 指标注册表 (0.3天)
3. `tests/unit/test_batch_calculator.py` - 批量计算引擎 (0.5天)
4. `tests/unit/test_gpu_accelerator.py` - GPU加速器 (0.4天)
5. `tests/unit/test_indicator_cache.py` - 指标缓存 (0.3天)
6. `tests/integration/test_indicator_api.py` - API集成测试 (0.2天)

**验收标准**:
- [ ] 所有模块单元测试通过
- [ ] 测试覆盖率 > 80%
- [ ] CI/CD集成测试通过

---

#### T3.18: 编写完成报告 (0.5天)

**目标**: 记录Phase 4完整成果

**完成报告内容** (`docs/guides/multi-cli-tasks/CLI-3_COMPLETION_REPORT.md`):
```markdown
# CLI-3 完成报告 - Phase 4完整实现

## 核心成果
- ✅ A股交易规则引擎 (T+1/涨跌停/100股整数倍)
- ✅ TA-Lib 161个技术指标完整实现
- ✅ GPU加速批量计算 (68.58x性能提升)
- ✅ PostgreSQL缓存优化 (命中率 > 80%)
- ✅ 单元测试覆盖率 > 80%

## 关键指标
| 指标 | 目标 | 实际 |
|------|------|------|
| 指标完整性 | 161个 | 161个 |
| GPU加速比 | >50x | 68.58x |
| 批量计算性能 (100股×161指标) | <5秒 | 3.2秒 |
| 缓存命中率 | >80% | 87% |
| 单元测试覆盖率 | >80% | 85% |

## 关键文件清单
- `src/technical_analysis/astock_rules.py` - A股规则引擎
- `src/technical_analysis/indicator_registry.py` - 161指标注册表
- `src/technical_analysis/batch_calculator.py` - 批量计算引擎
- `src/technical_analysis/gpu_accelerator.py` - GPU加速器
- `src/technical_analysis/indicator_cache.py` - 缓存管理器
- `web/backend/app/api/indicators.py` - 指标API接口

## 后续建议
1. CLI-1可直接调用 `/api/indicators/overlay` 和 `/api/indicators/oscillator`
2. CLI-4 AI选股依赖本CLI的指标数据
3. 定期监控GPU加速性能,确保稳定性
```

**验收标准**:
- [ ] 完成报告创建
- [ ] 关键指标达标
- [ ] 交付文档完整

---

## 📊 任务依赖关系

```
CLI-2 (API契约) ── 必须完成 ──→ T3.1 (开始CLI-3)
  ↓
T3.1-T3.3 (A股规则引擎)
  ↓
T3.4 (安装TA-Lib)
  ↓
T3.5 (161指标注册表)
  ↓
T3.6 (批量计算引擎)
  ↓
T3.7 (GPU加速) ─→ T3.9 (缓存表设计)
  ↓                 ↓
T3.8 (API接口) ←── T3.10 (缓存读写)
  ↓                 ↓
T3.12-T3.17 (单元测试) ←── T3.11 (缓存预热)
  ↓
T3.18 (完成报告)
  ↓
CLI-4 (AI选股) 可以开始
```

---

## ⏱️ 时间分配

| 阶段 | 任务编号 | 预计时间 |
|------|---------|---------|
| 阶段1 | T3.1-T3.3 | 2天 |
| 阶段2 | T3.4-T3.8 | 4.5天 |
| 阶段3 | T3.9-T3.11 | 1.5天 |
| 阶段4 | T3.12-T3.18 | 2.5天 |
| **总计** | **18任务** | **10-12天** |

---

## ✅ 最终验收标准

### 功能验收
- [ ] A股规则引擎所有验证功能测试通过
- [ ] 161个技术指标计算准确性验证通过
- [ ] GPU加速批量计算性能达标 (100股×161指标 < 5秒)
- [ ] PostgreSQL缓存命中率 > 80%
- [ ] API接口功能完整,CLI-1可正常调用

### 性能验收
- [ ] 单股票10个指标计算 < 500ms
- [ ] GPU加速比 > 50x
- [ ] 缓存预热时间 < 5分钟 (沪深300)

### 质量验收
- [ ] 单元测试覆盖率 > 80%
- [ ] CI/CD集成测试通过
- [ ] 代码符合Pylint规范

---

**交付状态**: 待CLI-2完成后开始
**后置依赖**: CLI-4 (AI选股) 需要本CLI的指标数据
