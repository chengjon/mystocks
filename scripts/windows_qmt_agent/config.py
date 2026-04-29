from __future__ import annotations

import os
from dataclasses import dataclass

from src.utils.trading_runtime_config import (
    DEFAULT_TRADING_QMT_BRIDGE_CONTRACT_VERSION,
    get_trading_qmt_bridge_contract_version,
    get_trading_qmt_bridge_token,
)

PROVIDER_MODE_MOCK = "mock"
PROVIDER_MODE_MINIQMT_SDK = "miniqmt_sdk"
SUPPORTED_PROVIDER_MODES = frozenset({PROVIDER_MODE_MOCK, PROVIDER_MODE_MINIQMT_SDK})


@dataclass(slots=True)
class WindowsQmtAgentSettings:
    node_name: str
    bridge_token: str | None
    bridge_contract_version: str
    provider_mode: str
    source_name: str
    host: str
    port: int
    default_account_scope: str
    default_pending_delay_seconds: float
    miniqmt_sdk_enabled: bool

    def __post_init__(self) -> None:
        normalized_mode = self.provider_mode.strip().lower()
        if normalized_mode not in SUPPORTED_PROVIDER_MODES:
            raise ValueError(
                f"Unsupported Windows qmt provider mode '{self.provider_mode}'. "
                f"Expected one of {sorted(SUPPORTED_PROVIDER_MODES)}."
            )
        self.provider_mode = normalized_mode


def load_settings_from_env() -> WindowsQmtAgentSettings:
    provider_mode = os.getenv("WINDOWS_QMT_AGENT_PROVIDER_MODE", PROVIDER_MODE_MOCK).strip().lower()
    return WindowsQmtAgentSettings(
        node_name=os.getenv("WINDOWS_QMT_AGENT_NODE_NAME", "WIN-QMT-REF-01").strip() or "WIN-QMT-REF-01",
        bridge_token=get_trading_qmt_bridge_token(),
        bridge_contract_version=get_trading_qmt_bridge_contract_version(
            DEFAULT_TRADING_QMT_BRIDGE_CONTRACT_VERSION
        ),
        provider_mode=provider_mode or PROVIDER_MODE_MOCK,
        source_name=(
            os.getenv("WINDOWS_QMT_AGENT_SOURCE_NAME", "qmt/windows_reference_service").strip()
            or "qmt/windows_reference_service"
        ),
        host=os.getenv("WINDOWS_QMT_AGENT_HOST", "0.0.0.0").strip() or "0.0.0.0",
        port=int(os.getenv("WINDOWS_QMT_AGENT_PORT", "8001")),
        default_account_scope=(
            os.getenv("WINDOWS_QMT_AGENT_DEFAULT_ACCOUNT_SCOPE", "wsl-ubuntu-paper-account").strip()
            or "wsl-ubuntu-paper-account"
        ),
        default_pending_delay_seconds=float(os.getenv("WINDOWS_QMT_AGENT_DEFAULT_PENDING_DELAY_SECONDS", "0")),
        miniqmt_sdk_enabled=_env_flag("WINDOWS_QMT_AGENT_MINIQMT_SDK_ENABLED"),
    )


def _env_flag(name: str) -> bool:
    value = os.getenv(name)
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}
