"""
风险设置模块

提供风险参数配置、风险模型选择、风险阈值设置、用户风险管理配置功能
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .risk_base import RiskProfile, RiskMetrics
from .risk_base import RiskLevel

logger = __import__("logging").getLogger(__name__)


class ModelType(Enum):
    """风险模型类型"""

    VAR = "variance"
    CVAR = "cvar"
    HISTORICAL_VAR = "historical_var"
    MONTE_CARLO = "monte_carlo"
    NORMAL_VAR = "normal_var"


class TimeHorizon(Enum):
    """时间周期"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class OptimizationObjective(Enum):
    """优化目标"""

    MINIMIZE_RISK = "minimize_risk"
    MAXIMIZE_RETURN = "maximize_return"
    BALANCE = "balance"


@dataclass
class RiskSettings:
    """风险设置数据类"""

    settings_id: str = ""
    user_id: str = ""
    profile_id: str = ""

    model_type: ModelType = ModelType.VAR
    time_horizon: TimeHorizon = TimeHorizon.DAILY
    optimization_objective: OptimizationObjective = OptimizationObjective.BALANCE

    var_95_threshold: float = 0.0
    var_99_threshold: float = 0.0
    sharpe_threshold: float = 0.0
    max_drawdown_threshold: float = 0.0

    confidence_level: float = 0.95
    lookback_days: int = 252
    rebalance_threshold: float = 0.10

    is_enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "settings_id": self.settings_id,
            "user_id": self.user_id,
            "profile_id": self.profile_id,
            "model_type": self.model_type.value,
            "time_horizon": self.time_horizon.value,
            "optimization_objective": self.optimization_objective.value,
            "var_95_threshold": self.var_95_threshold,
            "var_99_threshold": self.var_99_threshold,
            "sharpe_threshold": self.sharpe_threshold,
            "max_drawdown_threshold": self.max_drawdown_threshold,
            "confidence_level": f"{self.confidence_level:.0%}",
            "lookback_days": self.lookback_days,
            "rebalance_threshold": f"{self.rebalance_threshold:.0%}",
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RiskSettingsManager:
    """风险设置管理器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.default_settings = self._get_default_settings()
        self.user_settings = {}  # user_id -> RiskSettings
        self.profile_settings = {}  # profile_id -> RiskSettings

        logger.info("风险设置管理器初始化")

    def _get_default_settings(self) -> RiskSettings:
        """获取默认风险设置"""
        return RiskSettings(
            settings_id="default",
            user_id="system",
            profile_id="default",
            model_type=ModelType.CVAR,
            time_horizon=TimeHorizon.DAILY,
            optimization_objective=OptimizationObjective.BALANCE,
            var_95_threshold=0.025,
            var_99_threshold=0.010,
            sharpe_threshold=1.0,
            max_drawdown_threshold=0.15,
            confidence_level=0.95,
            lookback_days=252,
            rebalance_threshold=0.10,
            is_enabled=True,
        )

    async def create_settings(self, user_id: str, profile_id: str, settings_data: Dict) -> RiskSettings:
        """
        创建风险设置

        Args:
            user_id: 用户ID
            profile_id: 风险配置文件ID
            settings_data: 设置数据

        Returns:
            RiskSettings: 创建的设置
        """
        try:
            import uuid

            settings_id = f"settings_{uuid.uuid4()}"

            settings = RiskSettings(
                settings_id=settings_id,
                user_id=user_id,
                profile_id=profile_id,
                model_type=ModelType(settings_data.get("model_type", "variance")),
                time_horizon=TimeHorizon(settings_data.get("time_horizon", "daily")),
                optimization_objective=OptimizationObjective(settings_data.get("objective", "balance")),
                var_95_threshold=settings_data.get("var_95_threshold", 0.025),
                var_99_threshold=settings_data.get("var_99_threshold", 0.010),
                sharpe_threshold=settings_data.get("sharpe_threshold", 1.0),
                max_drawdown_threshold=settings_data.get("max_drawdown_threshold", 0.15),
                confidence_level=settings_data.get("confidence_level", 0.95),
                lookback_days=settings_data.get("lookback_days", 252),
                rebalance_threshold=settings_data.get("rebalance_threshold", 0.10),
                is_enabled=True,
                created_at=datetime.now(),
            )

            self.user_settings[settings_id] = settings
            self.profile_settings[profile_id] = settings

            self.logger.info(f"创建风险设置: {settings_id}")

            return settings

        except Exception as e:
            self.logger.error(f"创建风险设置失败: {e}")
            raise

    async def get_settings(self, user_id: str) -> Optional[RiskSettings]:
        """获取用户风险设置"""
        try:
            if user_id in self.user_settings:
                return list(self.user_settings[user_id].values())[0]

            return self.default_settings

        except Exception as e:
            self.logger.error(f"获取风险设置失败: {e}")
            return None

    async def update_settings(self, settings_id: str, update_data: Dict) -> bool:
        """更新风险设置"""
        try:
            settings = self.user_settings.get(settings_id)
            if not settings:
                return False

            for key, value in update_data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)

            settings.updated_at = datetime.now()

            self.logger.info(f"更新风险设置: {settings_id}")
            return True

        except Exception as e:
            self.logger.error(f"更新风险设置失败: {e}")
            return False

    async def delete_settings(self, settings_id: str) -> bool:
        """删除风险设置"""
        try:
            if settings_id in self.user_settings:
                del self.user_settings[settings_id]
                self.logger.info(f"删除风险设置: {settings_id}")
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"删除风险设置失败: {e}")
            return False

    def get_default_settings(self) -> RiskSettings:
        """获取默认设置"""
        return self.default_settings

    def get_available_models(self) -> List[str]:
        """获取可用的风险模型"""
        return [model.value for model in ModelType]

    def get_available_time_horizons(self) -> List[str]:
        """获取可用的时间周期"""
        return [horizon.value for horizon in TimeHorizon]

    def get_available_objectives(self) -> List[str]:
        """获取可用的优化目标"""
        return [obj.value for obj in OptimizationObjective]

    async def reset_user_settings(self, user_id: str) -> bool:
        """重置用户风险设置为默认"""
        try:
            user_settings = list(self.user_settings.get(user_id, {}).values())

            for settings in user_settings:
                if settings in self.user_settings.get(user_id, {}).values():
                    del self.user_settings[user_id][settings.settings_id]

            self.logger.info(f"重置用户{user_id}的风险设置")
            return True

        except Exception as e:
            self.logger.error(f"重置风险设置失败: {e}")
            return False

    async def export_settings(self, user_id: str, format: str = "json") -> str:
        """导出风险设置"""
        try:
            user_settings = self.user_settings.get(user_id, {})

            if format == "json":
                import json

                return json.dumps([s.to_dict() for s in user_settings.values()], indent=2)
            elif format == "csv":
                import csv
                import io

                output = io.StringIO()
                writer = csv.DictWriter(
                    output,
                    fieldnames=[
                        "settings_id",
                        "model_type",
                        "time_horizon",
                        "var_95_threshold",
                        "var_99_threshold",
                        "sharpe_threshold",
                        "max_drawdown_threshold",
                        "confidence_level",
                        "lookback_days",
                        "rebalance_threshold",
                        "is_enabled",
                    ],
                )

                for settings in user_settings.values():
                    writer.writerow(
                        {
                            "settings_id": settings.settings_id,
                            "model_type": settings.model_type.value,
                            "time_horizon": settings.time_horizon.value,
                            "var_95_threshold": settings.var_95_threshold,
                            "var_99_threshold": settings.var_99_threshold,
                            "sharpe_threshold": settings.sharpe_threshold,
                            "max_drawdown_threshold": settings.max_drawdown_threshold,
                            "confidence_level": f"{settings.confidence_level:.0%}",
                            "lookback_days": settings.lookback_days,
                            "rebalance_threshold": f"{settings.rebalance_threshold:.0%}",
                            "is_enabled": settings.is_enabled,
                        }
                    )

                output.seek(0)
                return output.getvalue()

            return ""

        except Exception as e:
            self.logger.error(f"导出风险设置失败: {e}")
            return ""

    async def import_settings(self, user_id: str, import_data: str, format: str = "json") -> bool:
        """导入风险设置"""
        try:
            settings_list = []

            if format == "json":
                import json

                data = json.loads(import_data)
                settings_list = data.get("settings", [])

            elif format == "csv":
                import csv
                import io

                csv_reader = csv.DictReader(io.StringIO(import_data))
                for row in csv_reader:
                    settings = RiskSettings(
                        settings_id=row.get("settings_id", ""),
                        user_id=user_id,
                        profile_id=row.get("profile_id", ""),
                        model_type=ModelType(row.get("model_type", "variance")),
                        time_horizon=TimeHorizon(row.get("time_horizon", "daily")),
                        optimization_objective=OptimizationObjective(row.get("objective", "balance")),
                        var_95_threshold=float(row.get("var_95_threshold", 0.025)),
                        var_99_threshold=float(row.get("var_99_threshold", 0.010)),
                        sharpe_threshold=float(row.get("sharpe_threshold", 1.0)),
                        max_drawdown_threshold=float(row.get("max_drawdown_threshold", 0.15)),
                        confidence_level=float(row.get("confidence_level", 0.95)),
                        lookback_days=int(row.get("lookback_days", 252)),
                        rebalance_threshold=float(row.get("rebalance_threshold", 0.10)),
                    )
                    settings_list.append(settings)

            for settings in settings_list:
                self.user_settings[settings.settings_id] = settings
                self.profile_settings[settings.profile_id] = settings

            self.logger.info(f"导入{len(settings_list)}个风险设置")
            return True

        except Exception as e:
            self.logger.error(f"导入风险设置失败: {e}")
            return False
