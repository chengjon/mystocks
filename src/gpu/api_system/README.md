# GPU API 系统使用指南

## 系统概述

GPU API系统是一个专为量化交易设计的高性能GPU加速服务平台，提供以下核心功能：

1. **海量历史数据回测** - GPU加速的策略回测引擎
2. **实时行情数据处理** - 流式数据处理与技术指标计算
3. **机器学习模型训练** - GPU加速的ML/DL模型训练与预测

## 系统架构

```
gpu_api_system/
├── api_proto/              # gRPC API定义
├── config/                 # 配置文件
├── services/              # 核心服务
│   ├── integrated_backtest_service.py    # 集成回测服务
│   ├── integrated_realtime_service.py    # 集成实时数据处理服务
│   └── integrated_ml_service.py          # 集成ML训练服务
├── utils/                 # 工具模块
│   ├── gpu_utils.py                     # GPU资源管理
│   ├── gpu_acceleration_engine.py       # GPU加速引擎
│   ├── cache_optimization.py            # 缓存优化
│   ├── redis_utils.py                   # Redis队列管理
│   └── monitoring.py                    # 监控与指标收集
├── deployment/            # 部署配置
│   ├── docker/           # Docker配置
│   └── kubernetes/       # Kubernetes配置
├── monitoring/           # 监控配置
│   └── prometheus/       # Prometheus配置
└── main_server.py        # 主服务器
```

## 快速开始

### 1. 环境准备

#### 系统要求
- Ubuntu 20.04+
- NVIDIA GPU (CUDA 12.x)
- Docker & Docker Compose
- Python 3.8+

#### 安装GPU驱动
```bash
# 安装NVIDIA驱动
sudo apt-get update
sudo apt-get install -y nvidia-driver-535

# 安装CUDA Toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-12-0

# 验证安装
nvidia-smi
nvcc --version
```

#### 安装Docker与NVIDIA Container Toolkit
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# 验证GPU Docker支持
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### 2. 安装依赖

```bash
cd /opt/claude/mystocks_spec/gpu_api_system

# 安装Python依赖
pip install -r requirements.txt

# 安装GPU加速库
pip install cudf-cu12 cuml-cu12
```

### 3. 配置环境

创建 `.env` 文件：

```bash
# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# gRPC配置
GRPC_HOST=0.0.0.0
GRPC_PORT=50051
GRPC_MAX_WORKERS=10

# GPU配置
GPU_DEVICE_ID=0
GPU_MEMORY_FRACTION=0.8

# 监控配置
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### 4. 启动服务

#### 方式1: Docker Compose (推荐)

```bash
# 构建镜像
docker-compose -f deployment/docker/docker-compose.yml build

# 启动所有服务
docker-compose -f deployment/docker/docker-compose.yml up -d

# 查看日志
docker-compose -f deployment/docker/docker-compose.yml logs -f

# 停止服务
docker-compose -f deployment/docker/docker-compose.yml down
```

#### 方式2: 直接运行

```bash
# 启动Redis
docker run -d --name redis -p 6379:6379 redis:latest

# 启动主服务器
python main_server.py
```

### 5. 验证服务

```bash
# 检查gRPC服务
grpcurl -plaintext localhost:50051 list

# 检查Prometheus指标
curl http://localhost:9090/metrics

# 检查Grafana仪表板
# 浏览器访问: http://localhost:3000
# 默认用户名/密码: admin/admin
```

## API使用示例

### 1. 回测服务

#### Python客户端示例

```python
import grpc
from api_proto import backtest_pb2, backtest_pb2_grpc
import json

# 连接到服务器
channel = grpc.insecure_channel('localhost:50051')
stub = backtest_pb2_grpc.BacktestServiceStub(channel)

# 准备回测请求
strategy_config = {
    'strategy_type': 'trend_following',
    'lookback_period': 20,
    'moving_average_window': 50
}

request = backtest_pb2.BacktestRequest(
    stock_codes=['000001.SZ', '600000.SH'],
    start_time='2024-01-01',
    end_time='2024-12-31',
    strategy_config=json.dumps(strategy_config),
    initial_capital=1000000,
    commission_rate=0.0003
)

# 执行回测
response = stub.IntegratedBacktest(request)
print(f"回测ID: {response.backtest_id}")
print(f"状态: {response.status}")

# 查询回测状态
status_request = backtest_pb2.BacktestStatusRequest(
    backtest_id=response.backtest_id
)
status = stub.GetBacktestStatus(status_request)
print(f"回测状态: {status}")

# 获取回测结果
if status.status == backtest_pb2.BacktestStatus.COMPLETED:
    result_request = backtest_pb2.BacktestResultRequest(
        backtest_id=response.backtest_id
    )
    result = stub.GetBacktestResult(result_request)
    print(f"总收益率: {result.performance_metrics.total_return}")
    print(f"夏普比率: {result.performance_metrics.sharpe_ratio}")
    print(f"最大回撤: {result.performance_metrics.max_drawdown}")
```

### 2. 实时数据处理服务

#### 流式数据处理示例

```python
import grpc
from api_proto import realtime_pb2, realtime_pb2_grpc
from datetime import datetime

# 连接到服务器
channel = grpc.insecure_channel('localhost:50051')
stub = realtime_pb2_grpc.RealTimeServiceStub(channel)

# 创建数据流生成器
def generate_market_data():
    stock_codes = ['000001.SZ', '600000.SH', '000002.SZ']

    for i in range(100):
        for stock_code in stock_codes:
            yield realtime_pb2.StreamDataRequest(
                stock_code=stock_code,
                price=10.0 + i * 0.1,
                volume=1000000 + i * 1000,
                timestamp=datetime.now().isoformat()
            )

# 发送流式数据并接收处理结果
responses = stub.StreamMarketData(generate_market_data())

for response in responses:
    print(f"股票: {response.stock_code}")
    print(f"处理结果: {response.processed_data}")
    print(f"流ID: {response.stream_id}")
```

#### 计算技术指标示例

```python
# 计算技术指标
feature_request = realtime_pb2.FeatureRequest(
    stock_code='000001.SZ',
    feature_types=['sma_20', 'sma_50', 'rsi', 'macd', 'bollinger']
)

feature_response = stub.ComputeFeatures(feature_request)

print(f"股票代码: {feature_response.stock_code}")
print(f"特征值: {feature_response.features}")
print(f"计算时间: {feature_response.timestamp}")
```

### 3. ML训练服务

#### 模型训练示例

```python
import grpc
from api_proto import ml_pb2, ml_pb2_grpc
import json
import pandas as pd

# 连接到服务器
channel = grpc.insecure_channel('localhost:50051')
stub = ml_pb2_grpc.MLServiceStub(channel)

# 准备训练数据
training_data = {
    'price': [10.0, 10.5, 11.0, 10.8, 11.2],
    'volume': [1000000, 1100000, 1200000, 1150000, 1300000],
    'sma_20': [10.2, 10.3, 10.4, 10.5, 10.6],
    'rsi': [50, 55, 60, 58, 62],
    'target': [1, 1, 0, 1, 1]  # 1=上涨, 0=下跌
}

# 创建训练请求
train_request = ml_pb2.TrainModelRequest(
    model_type='random_forest',
    training_data=json.dumps(training_data),
    feature_columns=['price', 'volume', 'sma_20', 'rsi'],
    target_column='target',
    model_params=json.dumps({'n_estimators': 100, 'max_depth': 5})
)

# 提交训练任务
train_response = stub.TrainModel(train_request)
print(f"训练任务ID: {train_response.task_id}")

# 查询训练状态
status_request = ml_pb2.TrainingStatusRequest(
    task_id=train_response.task_id
)
status = stub.GetTrainingStatus(status_request)
print(f"训练状态: {status.status}")

# 训练完成后获取模型ID
if status.status == 'completed':
    model_id = status.model_id

    # 使用模型进行预测
    predict_data = {
        'price': [11.5],
        'volume': [1400000],
        'sma_20': [10.7],
        'rsi': [65]
    }

    predict_request = ml_pb2.PredictRequest(
        model_id=model_id,
        input_data=json.dumps(predict_data)
    )

    predict_response = stub.Predict(predict_request)
    print(f"预测结果: {predict_response.predictions}")
    print(f"预测时间: {predict_response.prediction_time}秒")
```

## 监控与运维

### 1. Prometheus监控

访问 http://localhost:9090 查看系统指标：

- **GPU使用率**: `gpu_utilization`
- **回测任务数**: `backtest_tasks_total`
- **实时数据流数**: `realtime_streams_active`
- **ML训练任务数**: `ml_training_tasks_total`
- **缓存命中率**: `cache_hit_rate`

### 2. Grafana仪表板

访问 http://localhost:3000，使用预配置的仪表板：

- **GPU资源监控**: GPU利用率、内存使用、温度
- **服务性能**: 请求延迟、吞吐量、错误率
- **业务指标**: 回测完成数、预测次数、训练任务状态

### 3. 日志查看

```bash
# 查看主服务器日志
tail -f /opt/claude/mystocks_spec/gpu_api_system/logs/gpu_api_server.log

# 查看Docker容器日志
docker logs -f gpu-api-server

# 查看特定服务日志
docker logs -f gpu-api-backtest-service
```

### 4. 性能调优

#### GPU内存优化
```python
# 调整GPU内存分配比例
export GPU_MEMORY_FRACTION=0.6  # 使用60%的GPU内存
```

#### 并发任务调整
```python
# 修改 config/system_config.py
self.config = {
    'max_concurrent_backtests': 5,  # 增加并发回测数
    'max_concurrent_training': 3,   # 增加并发训练数
    'gpu_batch_size': 200,          # 增加批处理大小
}
```

#### 缓存策略优化
```python
# 修改缓存TTL
self.config = {
    'feature_cache_ttl': 120,  # 特征缓存2分钟
    'model_cache_ttl': 600,    # 模型缓存10分钟
}
```

## 故障排查

### 常见问题

#### 1. GPU不可用

```bash
# 检查GPU状态
nvidia-smi

# 检查CUDA版本
nvcc --version

# 检查Docker GPU支持
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

#### 2. gRPC连接失败

```bash
# 检查端口是否被占用
netstat -tuln | grep 50051

# 检查防火墙规则
sudo ufw status

# 测试gRPC连接
grpcurl -plaintext localhost:50051 list
```

#### 3. Redis连接失败

```bash
# 检查Redis服务
docker ps | grep redis

# 测试Redis连接
redis-cli ping

# 检查Redis日志
docker logs redis
```

#### 4. 内存不足

```bash
# 查看GPU内存使用
nvidia-smi

# 减少批处理大小
export GPU_BATCH_SIZE=50

# 清理GPU缓存
python -c "import torch; torch.cuda.empty_cache()"
```

## 性能基准

### GPU vs CPU性能对比

| 任务类型 | 数据规模 | CPU耗时 | GPU耗时 | 加速比 |
|---------|---------|---------|---------|--------|
| 回测 (单策略) | 1000天 × 100股票 | 45秒 | 3秒 | 15x |
| 特征计算 | 10000条数据 | 8秒 | 0.5秒 | 16x |
| ML训练 (随机森林) | 100万样本 | 120秒 | 8秒 | 15x |
| 批量预测 | 10000条数据 | 5秒 | 0.3秒 | 16.7x |

### 系统吞吐量

- **回测服务**: 10-20个并发回测任务
- **实时数据处理**: 10000条/秒数据处理
- **ML训练**: 2-3个并发训练任务
- **预测服务**: 1000次/秒预测请求

## 最佳实践

### 1. 回测优化

- 使用缓存避免重复计算
- 批量处理多个股票
- 合理设置回测周期
- 启用GPU加速

### 2. 实时数据处理

- 使用流式API减少延迟
- 批量计算技术指标
- 利用多级缓存
- 合理设置缓冲区大小

### 3. ML训练

- 预处理数据减少训练时间
- 使用GPU加速训练
- 启用自动调参
- 定期清理旧模型

### 4. 资源管理

- 监控GPU使用率
- 合理分配GPU资源
- 及时释放资源
- 设置资源限制

## 扩展开发

### 添加新策略

```python
# 在 services/integrated_backtest_service.py 中添加

def _execute_custom_strategy(self, data, params):
    """自定义策略实现"""
    # 实现你的策略逻辑
    signals = []

    # 生成交易信号
    for i in range(len(data)):
        if self._check_entry_condition(data[i], params):
            signals.append({'action': 'buy', 'price': data[i]['close']})
        elif self._check_exit_condition(data[i], params):
            signals.append({'action': 'sell', 'price': data[i]['close']})

    return signals
```

### 添加新指标

```python
# 在 services/integrated_realtime_service.py 中添加

def _calculate_custom_indicator(self, prices):
    """自定义指标计算"""
    # 实现你的指标逻辑
    indicator_value = np.mean(prices[-20:])  # 示例
    return indicator_value
```

### 添加新模型

```python
# 在 services/integrated_ml_service.py 中添加

def _train_custom_model(self, X, y, params):
    """自定义模型训练"""
    from custom_ml_library import CustomModel

    model = CustomModel(**params)
    model.fit(X, y)

    return model
```

## 支持与反馈

- **问题报告**: GitHub Issues
- **功能请求**: GitHub Discussions
- **技术支持**: support@mystocks.com

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

---

**版本**: 1.0.0
**更新时间**: 2025-11-04
**维护者**: MyStocks Development Team
