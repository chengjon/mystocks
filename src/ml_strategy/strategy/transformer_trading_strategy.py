"""
Transformer交易策略
Transformer Trading Strategy

使用Transformer架构进行多头注意力机制的时间序列分析和交易信号生成。
Uses Transformer architecture with multi-head attention for time series analysis and trading signal generation.
"""

from src.ml_strategy.strategy.lstm_trading_strategy import TimeSeriesDataset
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import math

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    from sklearn.preprocessing import StandardScaler

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available, Transformer strategy will use fallback implementation")

from src.ml_strategy.strategy.ml_strategy_base import MLTradingStrategy


logger = logging.getLogger(__name__)


class PositionalEncoding(nn.Module):
    """位置编码"""


def __init__(self, d_model: int, max_len: int = 5000):
    super(PositionalEncoding, self).__init__()

    pe = torch.zeros(max_len, d_model)
    position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
    div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))

    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)

    pe = pe.unsqueeze(0).transpose(0, 1)
    self.register_buffer("pe", pe)


def forward(self, x):
    return x + self.pe[: x.size(0), :]


class TransformerModel(nn.Module):
    """Transformer模型"""


def __init__(
    self,
    input_size: int,
    d_model: int = 64,
    nhead: int = 8,
    num_layers: int = 3,
    output_size: int = 1,
    dropout: float = 0.1,
):
    super(TransformerModel, self).__init__()

    self.input_projection = nn.Linear(input_size, d_model)
    self.pos_encoder = PositionalEncoding(d_model)

    encoder_layer = nn.TransformerEncoderLayer(
        d_model=d_model, nhead=nhead, dim_feedforward=d_model * 4, dropout=dropout, batch_first=True
    )

    self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
    self.decoder = nn.Linear(d_model, output_size)
    self.dropout = nn.Dropout(dropout)


def forward(self, src):
    # 输入投影
    src = self.input_projection(src)

    # 添加位置编码
    src = self.pos_encoder(src)

    # Transformer编码器
    output = self.transformer_encoder(src)

    # 全局平均池化
    output = torch.mean(output, dim=1)

    # 解码器
    output = self.dropout(output)
    output = self.decoder(output)
    return output


class TransformerTradingStrategy(MLTradingStrategy):
    """
    Transformer交易策略

    使用Transformer架构的多头注意力机制分析市场时间序列，捕捉复杂的模式依赖关系。
    Uses Transformer architecture with multi-head attention to analyze market time series and capture complex pattern dependencies.
    """


def __init__(
    self,
    strategy_name: str = "Transformer_Predictor",
    sequence_length: int = 60,
    prediction_horizon: int = 5,
    d_model: int = 64,
    nhead: int = 8,
    num_layers: int = 3,
    learning_rate: float = 0.001,
    epochs: int = 30,
    batch_size: int = 32,
):
    # 初始化基础策略
    config = {
        "algorithm_type": "transformer",
        "sequence_length": sequence_length,
        "prediction_horizon": prediction_horizon,
        "d_model": d_model,
        "nhead": nhead,
        "num_layers": num_layers,
        "learning_rate": learning_rate,
        "epochs": epochs,
        "batch_size": batch_size,
    }

    super().__init__(strategy_name, "transformer", config=config)

    # Transformer特定参数
    self.sequence_length = sequence_length
    self.prediction_horizon = prediction_horizon
    self.d_model = d_model
    self.nhead = nhead
    self.num_layers = num_layers
    self.learning_rate = learning_rate
    self.epochs = epochs
    self.batch_size = batch_size

    # 模型和训练组件
    self.model = None
    self.scaler = StandardScaler()
    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 性能跟踪
    self.prediction_accuracy = 0.0
    self.total_predictions = 0
    self.correct_predictions = 0

    logger.info(f"初始化Transformer交易策略: {strategy_name}")


async def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
    """准备Transformer特征"""
    # 使用与LSTM相同的特征工程
    from src.ml_strategy.strategy.lstm_trading_strategy import LSTMTradingStrategy

    lstm_strategy = LSTMTradingStrategy()
    return await lstm_strategy.prepare_features(data)


async def train_ml_model(self, data: pd.DataFrame) -> str:
    """
    训练Transformer模型
    """
    try:
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch不可用，使用简化实现")
            return "transformer_fallback_model"

        # 准备特征
        features = await self.prepare_features(data)

        # 创建目标变量
        target = data["close"].shift(-self.prediction_horizon) / data["close"] - 1
        target = target.fillna(0)

        # 清理数据
        valid_indices = ~(features.isna().any(axis=1) | target.isna())
        features_clean = features[valid_indices]
        target_clean = target[valid_indices]

        if len(features_clean) < self.sequence_length + 10:
            logger.warning("训练数据不足")
            return "insufficient_data"

        # 标准化特征
        feature_array = self.scaler.fit_transform(features_clean.values)
        target_array = target_clean.values.reshape(-1, 1)

        # 创建数据集
        dataset = TimeSeriesDataset(feature_array, target_array, self.sequence_length)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        # 初始化模型
        input_size = feature_array.shape[1]
        self.model = TransformerModel(
            input_size=input_size, d_model=self.d_model, nhead=self.nhead, num_layers=self.num_layers
        ).to(self.device)

        # 损失函数和优化器
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)

        # 训练循环
        self.model.train()
        for epoch in range(self.epochs):
            total_loss = 0
            for batch_x, batch_y in dataloader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)

                # 前向传播
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)

                # 反向传播
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(dataloader)
            if epoch % 5 == 0:
                logger.info(f"Epoch {epoch + 1}/{self.epochs}, Loss: {avg_loss:.6f}")

        # 保存模型
        model_key = f"transformer_{self.strategy_name}_{
            int(datetime.now().timestamp())}"
        self.trained_model_key = model_key

        # 重置预测统计
        self.total_predictions = 0
        self.correct_predictions = 0
        self.prediction_accuracy = 0.0

        logger.info(f"Transformer模型训练完成: {model_key}")
        return model_key

    except Exception as e:
        logger.error(f"Transformer模型训练失败: {e}")
        return "training_failed"


async def get_ml_prediction(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    获取Transformer预测
    """
    try:
        if not TORCH_AVAILABLE or self.model is None:
            # 使用与LSTM相同的fallback
            from src.ml_strategy.strategy.lstm_trading_strategy import LSTMTradingStrategy

            lstm_strategy = LSTMTradingStrategy()
            return await lstm_strategy.get_ml_prediction(data)

        # 准备特征
        features = await self.prepare_features(data)
        feature_array = self.scaler.transform(features.values)

        if len(feature_array) < self.sequence_length:
            logger.warning("数据长度不足以进行预测")
            return []

        # 预测
        input_sequence = feature_array[-self.sequence_length :].reshape(1, self.sequence_length, -1)
        input_tensor = torch.tensor(input_sequence, dtype=torch.float32).to(self.device)

        self.model.eval()
        with torch.no_grad():
            prediction = self.model(input_tensor).cpu().numpy()[0][0]

        # 转换为交易信号
        current_price = data["close"].iloc[-1]
        predicted_return = prediction

        predictions = [
            {
                "timestamp": datetime.now(),
                "predicted_return": float(predicted_return),
                "predicted_price": float(current_price * (1 + predicted_return)),
                "current_price": float(current_price),
                # Transformer通常有更高置信度
                "confidence": min(0.95, max(0.1, 1.0 - abs(predicted_return))),
                "model_key": self.trained_model_key or "transformer_model",
            }
        ]

        self.total_predictions += 1

        logger.info(f"Transformer预测完成: 预测收益率 {predicted_return:.4f}")
        return predictions

    except Exception as e:
        logger.error(f"Transformer预测失败: {e}")
        # Fallback到简单预测
        from src.ml_strategy.strategy.lstm_trading_strategy import LSTMTradingStrategy

        lstm_strategy = LSTMTradingStrategy()
        return await lstm_strategy._fallback_prediction(data)


async def interpret_ml_signals(self, predictions: List[Dict[str, Any]], data: pd.DataFrame) -> pd.DataFrame:
    """
    解释Transformer信号为交易信号
    """
    try:
        signals = []

        for prediction in predictions:
            predicted_return = prediction["predicted_return"]
            confidence = prediction["confidence"]

            # Transformer信号逻辑（更激进的阈值）
            if predicted_return > 0.015 and confidence > 0.7:  # 预测上涨1.5%以上且置信度高
                signal = 1
                signal_strength = min(1.0, predicted_return * 15)
            elif predicted_return < -0.015 and confidence > 0.7:  # 预测下跌1.5%以上且置信度高
                signal = -1
                signal_strength = min(1.0, abs(predicted_return) * 15)
            else:
                signal = 0
                signal_strength = 0.05

            signals.append(
                {
                    "signal": signal,
                    "confidence": confidence,
                    "predicted_return": predicted_return,
                    "signal_strength": signal_strength,
                    "timestamp": prediction["timestamp"],
                    "model_key": prediction["model_key"],
                }
            )

        signals_df = pd.DataFrame(signals)

        # Transformer特定的过滤逻辑
        if len(data) > 0 and len(signals_df) > 0:
            # 检查波动率 - 高波动期Transformer信号更可靠
            volatility = data["returns"].rolling(window=20).std().iloc[-1] if "returns" in data.columns else 0.02

            # 高波动期降低阈值
            if volatility > 0.03:  # 高波动
                for idx, row in signals_df.iterrows():
                    if row["signal"] != 0:
                        signals_df.loc[idx, "confidence"] *= 1.1  # 提高置信度

        logger.info(f"Transformer信号解释完成: 生成 {len(signals_df)} 个信号")
        return signals_df

    except Exception as e:
        logger.error(f"Transformer信号解释失败: {e}")
        return pd.DataFrame(columns=["signal", "confidence", "predicted_return", "signal_strength"])


def get_strategy_info(self) -> Dict[str, Any]:
    """获取策略信息"""
    base_info = super().get_strategy_info()
    base_info.update(
        {
            "model_type": "Transformer",
            "sequence_length": self.sequence_length,
            "prediction_horizon": self.prediction_horizon,
            "d_model": self.d_model,
            "nhead": self.nhead,
            "num_layers": self.num_layers,
            "trained_model_key": self.trained_model_key,
            "prediction_accuracy": self.prediction_accuracy,
            "total_predictions": self.total_predictions,
            "torch_available": TORCH_AVAILABLE,
            "device": str(self.device) if TORCH_AVAILABLE else "N/A",
        }
    )
    return base_info


# 导入TimeSeriesDataset以供Transformer使用
