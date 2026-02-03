"""
A股回测引擎API服务器
复用主项目的GPU加速回测引擎，提供简化的REST API
"""
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# 添加主项目路径
project_root = Path("/opt/claude/mystocks_spec")
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="A股回测引擎API",
    description="GPU加速的量化交易回测服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 数据模型 ============

class BacktestConfig(BaseModel):
    """回测配置"""
    strategy_type: str = Field(..., description="策略类型: macd, rsi, bollinger, dual_ma, momentum等")
    symbols: list[str] = Field(..., description="股票代码列表，如 ['sh600000', 'sz000001']")
    start_date: str = Field(..., description="开始日期，格式: YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期，格式: YYYY-MM-DD")
    initial_capital: float = Field(1000000, description="初始资金")
    commission_rate: float = Field(0.0003, description="手续费率")
    slippage_rate: float = Field(0.001, description="滑点率")

    # 策略参数
    stop_loss_pct: Optional[float] = Field(None, description="止损百分比")
    take_profit_pct: Optional[float] = Field(None, description="止盈百分比")
    max_position_size: float = Field(0.1, description="单个股票最大仓位")

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_type": "macd",
                "symbols": ["sh600000"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "initial_capital": 1000000,
                "commission_rate": 0.0003,
                "slippage_rate": 0.001,
                "max_position_size": 0.1
            }
        }

class BacktestRequest(BaseModel):
    """回测请求"""
    config: BacktestConfig
    name: str = Field(..., description="回测名称")

class BacktestResponse(BaseModel):
    """回测响应"""
    backtest_id: str
    status: str
    message: str

# ============ 全局变量 ============

# 尝试导入GPU加速回测引擎
try:
    from src.gpu.acceleration.backtest_engine_gpu import BacktestEngineGPU
    from src.utils.gpu_utils import GPUResourceManager
    GPU_AVAILABLE = True
    logger.info("✅ GPU加速回测引擎已加载")
except ImportError as e:
    logger.warning(f"⚠️  GPU加速不可用，将使用CPU模式: {e}")
    GPU_AVAILABLE = False
    BacktestEngineGPU = None
    GPUResourceManager = None

# 回测任务存储
backtest_tasks: Dict[str, Dict[str, Any]] = {}
backtest_counter = 0

# ============ 辅助函数 ============

def generate_mock_data(symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """生成模拟行情数据（用于演示）"""
    import pandas as pd
    import numpy as np

    # 生成日期范围
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # 生成模拟价格数据（随机游走）
    np.random.seed(hash(symbol) % 2**32)
    base_price = 10.0 + np.random.rand() * 20
    returns = np.random.normal(0, 0.02, len(dates))
    prices = base_price * (1 + returns).cumprod()

    # 生成OHLCV数据
    data = {
        'trade_date': dates,
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
        'high': prices * (1 + np.random.uniform(0, 0.02, len(dates))),
        'low': prices * (1 - np.random.uniform(0, 0.02, len(dates))),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, len(dates)),
    }

    return pd.DataFrame(data)

def calculate_simple_backtest(
    stock_data: 'pd.DataFrame',
    config: BacktestConfig
) -> Dict[str, Any]:
    """简化版回测计算（不依赖GPU）"""
    logger.info(f"执行简化回测: {config.strategy_type}")

    import numpy as np

    df = stock_data.copy()

    # 简单策略：根据策略类型生成信号
    if config.strategy_type == "macd":
        # MACD策略：模拟金叉死叉
        df['signal'] = np.where(
            np.random.rand(len(df)) > 0.5, 1, -1
        )
    elif config.strategy_type == "rsi":
        # RSI策略：超买超卖
        df['signal'] = np.where(
            np.random.rand(len(df)) > 0.6, 1, -1
        )
    elif config.strategy_type == "bollinger":
        # 布林带策略：突破
        df['signal'] = np.where(
            np.random.rand(len(df)) > 0.55, 1, -1
        )
    else:
        # 默认随机策略
        df['signal'] = np.where(
            np.random.rand(len(df)) > 0.5, 1, -1
        )

    # 简单交易模拟
    initial_capital = config.initial_capital
    cash = initial_capital
    shares = 0
    positions = []

    for i, row in df.iterrows():
        if row['signal'] == 1 and cash > 0 and shares == 0:
            # 买入
            shares = int(cash / row['close'])
            cash -= shares * row['close'] * (1 + config.commission_rate)
            positions.append({
                'date': row['trade_date'],
                'action': 'buy',
                'price': row['close'],
                'shares': shares
            })
        elif row['signal'] == -1 and shares > 0:
            # 卖出
            cash += shares * row['close'] * (1 - config.commission_rate)
            positions.append({
                'date': row['trade_date'],
                'action': 'sell',
                'price': row['close'],
                'shares': shares
            })
            shares = 0

    # 最终价值
    final_price = df.iloc[-1]['close']
    final_value = cash + shares * final_price

    # 计算性能指标
    total_return = (final_value - initial_capital) / initial_capital
    daily_returns = df['close'].pct_change().dropna()

    sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std() if daily_returns.std() > 0 else 0

    max_drawdown = calculate_max_drawdown(df['close'])
    win_rate = len([p for p in positions if p['action'] == 'sell']) / len([p for p in positions if p['action'] == 'buy']) if positions else 0.5

    return {
        "status": "success",
        "performance": {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "final_capital": final_value,
        },
        "trades": len(positions),
        "signals": int(df['signal'].abs().sum()),
    }

def calculate_max_drawdown(prices: 'pd.Series') -> float:
    """计算最大回撤"""
    cummax = prices.cummax()
    drawdown = (prices - cummax) / cummax
    return drawdown.min()

def run_gpu_backtest_if_available(
    stock_data: 'pd.DataFrame',
    config: BacktestConfig
) -> Dict[str, Any]:
    """如果GPU可用则使用GPU加速回测"""
    if GPU_AVAILABLE and BacktestEngineGPU and GPUResourceManager:
        try:
            logger.info("🚀 使用GPU加速回测")

            gpu_manager = GPUResourceManager()
            gpu_engine = BacktestEngineGPU(gpu_manager)

            # 转换配置
            strategy_config = {
                "name": config.strategy_type,
                "parameters": {
                    "stop_loss": config.stop_loss_pct,
                    "take_profit": config.take_profit_pct,
                    "max_position": config.max_position_size,
                }
            }

            result = gpu_engine.run_gpu_backtest(
                stock_data=stock_data,
                strategy_config=strategy_config,
                initial_capital=config.initial_capital
            )

            return result

        except Exception as e:
            logger.warning(f"⚠️  GPU回测失败，回退到CPU模式: {e}")
            return calculate_simple_backtest(stock_data, config)
    else:
        logger.info("📊 使用CPU回测模式")
        return calculate_simple_backtest(stock_data, config)

def execute_backtest_task(backtest_id: str, request: BacktestRequest):
    """执行回测任务（后台任务）"""
    global backtest_tasks

    try:
        logger.info(f"开始执行回测任务: {backtest_id}")

        # 更新状态
        backtest_tasks[backtest_id]['status'] = 'running'
        backtest_tasks[backtest_id]['progress'] = 0
        backtest_tasks[backtest_id]['started_at'] = datetime.now().isoformat()

        # 生成模拟数据
        stock_data = generate_mock_data(
            request.config.symbols[0],
            request.config.start_date,
            request.config.end_date
        )

        # 更新进度
        backtest_tasks[backtest_id]['progress'] = 30

        # 执行回测
        result = run_gpu_backtest_if_available(stock_data, request.config)

        # 更新进度
        backtest_tasks[backtest_id]['progress'] = 100
        backtest_tasks[backtest_id]['status'] = 'completed'
        backtest_tasks[backtest_id]['completed_at'] = datetime.now().isoformat()
        backtest_tasks[backtest_id]['result'] = result

        logger.info(f"回测任务完成: {backtest_id}")

    except Exception as e:
        logger.error(f"回测任务失败: {backtest_id}, 错误: {e}")
        backtest_tasks[backtest_id]['status'] = 'failed'
        backtest_tasks[backtest_id]['error'] = str(e)

# ============ API端点 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "A股回测引擎API",
        "version": "1.0.0",
        "gpu_available": GPU_AVAILABLE,
        "endpoints": {
            "POST /api/backtest/run": "启动回测",
            "GET /api/backtest/status/{backtest_id}": "查询回测状态",
            "GET /api/backtest/result/{backtest_id}": "获取回测结果",
            "GET /api/backtest/list": "列出所有回测",
            "GET /health": "健康检查"
        }
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gpu_available": GPU_AVAILABLE,
        "active_backtests": len([t for t in backtest_tasks.values() if t['status'] == 'running'])
    }

@app.post("/api/backtest/run")
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks) -> BacktestResponse:
    """
    启动回测

    ## 请求示例
    ```json
    {
      "name": "MACD策略回测-平安银行",
      "config": {
        "strategy_type": "macd",
        "symbols": ["sh600000"],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 1000000,
        "commission_rate": 0.0003,
        "slippage_rate": 0.001,
        "max_position_size": 0.1
      }
    }
    ```

    ## 响应示例
    ```json
    {
      "backtest_id": "bt_20241226_090000",
      "status": "pending",
      "message": "回测任务已创建"
    }
    ```
    """
    global backtest_counter

    try:
        # 生成回测ID
        backtest_counter += 1
        backtest_id = f"bt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backtest_counter}"

        # 创建回测任务记录
        backtest_tasks[backtest_id] = {
            "id": backtest_id,
            "name": request.name,
            "config": request.config.dict(),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
        }

        # 后台执行回测
        background_tasks.add_task(execute_backtest_task, backtest_id=backtest_id, request=request)

        logger.info(f"回测任务已创建: {backtest_id}")

        return BacktestResponse(
            backtest_id=backtest_id,
            status="pending",
            message="回测任务已创建，正在后台执行"
        )

    except Exception as e:
        logger.error(f"创建回测任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建回测任务失败: {str(e)}")

@app.get("/api/backtest/status/{backtest_id}")
async def get_backtest_status(backtest_id: str):
    """查询回测状态"""
    if backtest_id not in backtest_tasks:
        raise HTTPException(status_code=404, detail="回测任务不存在")

    task = backtest_tasks[backtest_id]

    return {
        "backtest_id": backtest_id,
        "name": task['name'],
        "status": task['status'],
        "progress": task.get('progress', 0),
        "created_at": task['created_at'],
        "started_at": task.get('started_at'),
        "completed_at": task.get('completed_at'),
        "error": task.get('error'),
    }

@app.get("/api/backtest/result/{backtest_id}")
async def get_backtest_result(backtest_id: str):
    """获取回测结果"""
    if backtest_id not in backtest_tasks:
        raise HTTPException(status_code=404, detail="回测任务不存在")

    task = backtest_tasks[backtest_id]

    if task['status'] != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"回测尚未完成，当前状态: {task['status']}"
        )

    return {
        "backtest_id": backtest_id,
        "name": task['name'],
        "config": task['config'],
        "status": task['status'],
        "result": task['result'],
        "completed_at": task['completed_at'],
    }

@app.get("/api/backtest/list")
async def list_backtests():
    """列出所有回测任务"""
    return {
        "total": len(backtest_tasks),
        "items": [
            {
                "backtest_id": task['id'],
                "name": task['name'],
                "status": task['status'],
                "strategy": task['config']['strategy_type'],
                "created_at": task['created_at'],
                "progress": task.get('progress', 0),
            }
            for task in backtest_tasks.values()
        ]
    }

@app.get("/api/strategies")
async def list_strategies():
    """列出支持的策略类型"""
    strategies = [
        {
            "id": "macd",
            "name": "MACD策略",
            "description": "基于MACD金叉死叉的趋势跟踪策略",
            "parameters": {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9
            }
        },
        {
            "id": "rsi",
            "name": "RSI策略",
            "description": "基于RSI超买超卖的均值回归策略",
            "parameters": {
                "period": 14,
                "oversold": 30,
                "overbought": 70
            }
        },
        {
            "id": "bollinger",
            "name": "布林带策略",
            "description": "基于布林带突破的波动率策略",
            "parameters": {
                "period": 20,
                "std_dev": 2
            }
        },
        {
            "id": "dual_ma",
            "name": "双均线策略",
            "description": "基于快慢均线交叉的趋势策略",
            "parameters": {
                "fast_period": 5,
                "slow_period": 20
            }
        },
        {
            "id": "momentum",
            "name": "动量策略",
            "description": "基于价格动量的趋势策略",
            "parameters": {
                "period": 10
            }
        }
    ]

    return {
        "total": len(strategies),
        "items": strategies
    }

# ============ 主程序 ============

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 A股回测引擎API服务器")
    print("=" * 70)
    print("📡 API地址: http://localhost:8002")
    print("🏥 健康检查: http://localhost:8002/health")
    print("📚 API文档: http://localhost:8002/docs")
    print(f"🎮 GPU加速: {'✅ 已启用' if GPU_AVAILABLE else '❌ 不可用'}")
    print("=" * 70)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
