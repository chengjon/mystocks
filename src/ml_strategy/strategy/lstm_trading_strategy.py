"""
LSTM交易策略
LSTM Trading Strategy

使用长短期记忆网络进行时间序列预测和交易信号生成。
Uses Long Short-Term Memory networks for time series prediction and trading signal generation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from sklearn.preprocessing import StandardScaler
    from torch.utils.data import DataLoader, Dataset

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available, LSTM strategy will use fallback implementation")

from src.ml_strategy.strategy.ml_strategy_base import MLTradingStrategy

logger = logging.getLogger(__name__)


class LSTMModel(nn.Module):
    """LSTM神经网络模型"""

    def __init__(
        self, input_size: int, hidden_size: int = 64, num_layers: int = 2, output_size: int = 1, dropout: float = 0.2
    ):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
        )

        self.fc = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # 初始化隐藏状态
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

        # LSTM前向传播
        out, _ = self.lstm(x, (h0, c0))

        # 只使用最后一个时间步的输出
        out = self.dropout(out[:, -1, :])
        out = self.fc(out)
        return out


class TimeSeriesDataset(Dataset):
    """时间序列数据集"""

    def __init__(self, data: np.ndarray, targets: np.ndarray, sequence_length: int = 60):
        self.data = data
        self.targets = targets
        self.sequence_length = sequence_length

    def __len__(self):
        return len(self.data) - self.sequence_length

    def __getitem__(self, idx):
        x = self.data[idx : idx + self.sequence_length]
        y = self.targets[idx + self.sequence_length]
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)


class LSTMTradingStrategy(MLTradingStrategy):
    """
    LSTM交易策略

    使用LSTM神经网络分析价格时间序列，预测未来价格走势并生成交易信号。
    Uses LSTM neural networks to analyze price time series, predict future price movements, and generate trading signals.
    """

    def __init__(
        self,
        strategy_name: str = "LSTM_Predictor",
        sequence_length: int = 60,
        prediction_horizon: int = 5,
        hidden_size: int = 64,
        num_layers: int = 2,
        learning_rate: float = 0.001,
        epochs: int = 50,
        batch_size: int = 32,
    ):
        # 初始化基础策略
        config = {
            "algorithm_type": "lstm",
            "sequence_length": sequence_length,
            "prediction_horizon": prediction_horizon,
            "hidden_size": hidden_size,
            "num_layers": num_layers,
            "learning_rate": learning_rate,
            "epochs": epochs,
            "batch_size": batch_size,
        }

        super().__init__(strategy_name, "lstm", config=config)

        # LSTM特定参数
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.hidden_size = hidden_size
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

        logger.info("初始化LSTM交易策略: %(strategy_name)s")

    async def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        准备LSTM特征

        为LSTM模型准备时间序列特征，包括技术指标和价格数据。
        """
        try:
            # 基础价格特征
            features = data.copy()

            # 添加技术指标
            features["returns"] = features["close"].pct_change()
            features["log_returns"] = np.log(features["close"] / features["close"].shift(1))

            # 移动平均线
            for period in [5, 10, 20, 30]:
                features[f"ma_{period}"] = features["close"].rolling(window=period).mean()
                features[f"ma_{period}_slope"] = features[f"ma_{period}"].pct_change()

            # 波动率指标
            features["volatility_5"] = features["returns"].rolling(window=5).std()
            features["volatility_10"] = features["returns"].rolling(window=10).std()
            features["volatility_20"] = features["returns"].rolling(window=20).std()

            # 相对强弱指标 (RSI)
            def calculate_rsi(price, period=14):
                delta = price.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                return 100 - (100 / (1 + rs))

            features["rsi_14"] = calculate_rsi(features["close"], 14)

            # MACD指标
            ema_12 = features["close"].ewm(span=12).mean()
            ema_26 = features["close"].ewm(span=26).mean()
            features["macd"] = ema_12 - ema_26
            features["macd_signal"] = features["macd"].ewm(span=9).mean()
            features["macd_hist"] = features["macd"] - features["macd_signal"]

            # 布林带
            sma_20 = features["close"].rolling(window=20).mean()
            std_20 = features["close"].rolling(window=20).std()
            features["bb_upper"] = sma_20 + (std_20 * 2)
            features["bb_lower"] = sma_20 - (std_20 * 2)
            features["bb_position"] = (features["close"] - features["bb_lower"]) / (
                features["bb_upper"] - features["bb_lower"]
            )

            # 填充NaN值
            features = features.fillna(method="bfill").fillna(method="ffill").fillna(0)

            # 选择特征列
            feature_columns = [
                "close",
                "volume",
                "returns",
                "log_returns",
                "ma_5",
                "ma_10",
                "ma_20",
                "ma_30",
                "ma_5_slope",
                "ma_10_slope",
                "ma_20_slope",
                "ma_30_slope",
                "volatility_5",
                "volatility_10",
                "volatility_20",
                "rsi_14",
                "macd",
                "macd_signal",
                "macd_hist",
                "bb_upper",
                "bb_lower",
                "bb_position",
            ]

            # 确保所有特征列都存在
            available_features = [col for col in feature_columns if col in features.columns]
            features = features[available_features]

            logger.info("LSTM特征准备完成: {len(available_features)} 个特征")
            return features

        except Exception:
            logger.error("LSTM特征准备失败: %(e)s")
            # 返回基础特征作为fallback
            return data[["close", "volume"]].fillna(0)

    async def train_ml_model(self, data: pd.DataFrame) -> str:
        """
        训练LSTM模型

        使用历史数据训练LSTM模型进行价格预测。
        """
        try:
            if not TORCH_AVAILABLE:
                logger.warning("PyTorch不可用，使用简化实现")
                return "lstm_fallback_model"

            # 准备特征
            features = await self.prepare_features(data)

            # 创建目标变量 (未来N期的收益率)
            target = data["close"].shift(-self.prediction_horizon) / data["close"] - 1
            target = target.fillna(0)  # 处理NaN值

            # 移除NaN行
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
            self.model = LSTMModel(input_size=input_size, hidden_size=self.hidden_size, num_layers=self.num_layers).to(
                self.device
            )

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
                if epoch % 10 == 0:
                    logger.info("Epoch {epoch + 1}/{self.epochs}, Loss: %(avg_loss)s")

            # 保存模型
            model_key = f"lstm_{self.strategy_name}_{int(datetime.now().timestamp())}"
            self.trained_model_key = model_key

            # 重置预测统计
            self.total_predictions = 0
            self.correct_predictions = 0
            self.prediction_accuracy = 0.0

            logger.info("LSTM模型训练完成: %(model_key)s")
            return model_key

        except Exception:
            logger.error("LSTM模型训练失败: %(e)s")
            return "training_failed"

    async def get_ml_prediction(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        获取LSTM预测

        使用训练好的LSTM模型进行价格预测。
        """
        try:
            if not TORCH_AVAILABLE or self.model is None:
                # Fallback实现：使用简单趋势预测
                return self._fallback_prediction(data)

            # 准备特征
            features = await self.prepare_features(data)
            feature_array = self.scaler.transform(features.values)

            # 创建预测序列
            if len(feature_array) < self.sequence_length:
                logger.warning("数据长度不足以进行预测")
                return []

            # 使用最新的序列数据进行预测
            input_sequence = feature_array[-self.sequence_length :].reshape(1, self.sequence_length, -1)
            input_tensor = torch.tensor(input_sequence, dtype=torch.float32).to(self.device)

            # 模型预测
            self.model.eval()
            with torch.no_grad():
                prediction = self.model(input_tensor).cpu().numpy()[0][0]

            # 转换为交易信号
            current_price = data["close"].iloc[-1]
            predicted_return = prediction

            # 生成预测结果
            predictions = [
                {
                    "timestamp": data.index[-1] if hasattr(data.index[-1], "isoformat") else datetime.now(),
                    "predicted_return": float(predicted_return),
                    "predicted_price": float(current_price * (1 + predicted_return)),
                    "current_price": float(current_price),
                    # 基于预测幅度计算置信度
                    "confidence": min(0.9, max(0.1, 1.0 - abs(predicted_return))),
                    "model_key": self.trained_model_key or "lstm_model",
                }
            ]

            # 更新预测统计
            self.total_predictions += 1

            logger.info("LSTM预测完成: 预测收益率 %(predicted_return)s")
            return predictions

        except Exception:
            logger.error("LSTM预测失败: %(e)s")
            return self._fallback_prediction(data)

    def _fallback_prediction(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Fallback预测实现（当PyTorch不可用时使用）"""
        try:
            if len(data) < 10:
                return []

            # 简单的趋势预测：基于最近5期的平均收益率
            recent_returns = data["close"].pct_change().tail(5).mean()
            current_price = data["close"].iloc[-1]

            prediction = {
                "timestamp": datetime.now(),
                "predicted_return": float(recent_returns),
                "predicted_price": float(current_price * (1 + recent_returns)),
                "current_price": float(current_price),
                "confidence": 0.5,  # 中等置信度
                "model_key": "lstm_fallback",
            }

            return [prediction]

        except Exception:
            logger.error("Fallback预测失败: %(e)s")
            return []

    async def interpret_ml_signals(self, predictions: List[Dict[str, Any]], data: pd.DataFrame) -> pd.DataFrame:
        """
        解释LSTM信号为交易信号

        将LSTM的预测结果转换为具体的买卖信号。
        """
        try:
            signals = []

            for prediction in predictions:
                predicted_return = prediction["predicted_return"]
                confidence = prediction["confidence"]

                # 信号生成逻辑
                if predicted_return > 0.02 and confidence > 0.6:  # 预测上涨2%以上且置信度高
                    signal = 1  # 买入信号
                    signal_strength = min(1.0, predicted_return * 10)  # 基于预测幅度计算信号强度
                elif predicted_return < -0.02 and confidence > 0.6:  # 预测下跌2%以上且置信度高
                    signal = -1  # 卖出信号
                    signal_strength = min(1.0, abs(predicted_return) * 10)
                else:
                    signal = 0  # 无信号
                    signal_strength = 0.1

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

            # 创建信号DataFrame
            signals_df = pd.DataFrame(signals)

            # 添加技术指标确认
            if len(data) > 0:
                # 检查是否与技术指标一致
                latest_rsi = data["rsi_14"].iloc[-1] if "rsi_14" in data.columns else 50
                latest_macd = data["macd"].iloc[-1] if "macd" in data.columns else 0

                # RSI过滤：超买时避免买入，超卖时避免卖出
                if len(signals_df) > 0:
                    for idx, row in signals_df.iterrows():
                        if row["signal"] == 1 and latest_rsi > 70:  # RSI超买
                            signals_df.loc[idx, "signal"] = 0
                            signals_df.loc[idx, "confidence"] *= 0.5
                        elif row["signal"] == -1 and latest_rsi < 30:  # RSI超卖
                            signals_df.loc[idx, "signal"] = 0
                            signals_df.loc[idx, "confidence"] *= 0.5

            logger.info("LSTM信号解释完成: 生成 {len(signals_df)} 个信号")
            return signals_df

        except Exception:
            logger.error("LSTM信号解释失败: %(e)s")
            return pd.DataFrame(columns=["signal", "confidence", "predicted_return", "signal_strength"])

    def get_strategy_info(self) -> Dict[str, Any]:
        """获取策略信息"""
        base_info = super().get_strategy_info()
        base_info.update(
            {
                "model_type": "LSTM",
                "sequence_length": self.sequence_length,
                "prediction_horizon": self.prediction_horizon,
                "hidden_size": self.hidden_size,
                "num_layers": self.num_layers,
                "trained_model_key": self.trained_model_key,
                "prediction_accuracy": self.prediction_accuracy,
                "total_predictions": self.total_predictions,
                "torch_available": TORCH_AVAILABLE,
                "device": str(self.device) if TORCH_AVAILABLE else "N/A",
            }
        )
        return base_info
