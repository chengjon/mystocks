"""
端到端 (E2E) 用户工作流测试

测试覆盖关键用户场景:
1. 用户登录 → 搜索股票 → 添加到自选
2. 策略配置 → 回测 → 查看结果
3. 下单 → 确认 → 持仓更新
"""

from ._test_e2e_user_workflows_login import TestUserWorkflowLoginSearchWatchlist, client
from ._test_e2e_user_workflows_orders import (
    TestUserWorkflowErrorRecovery,
    TestUserWorkflowOrderPlacement,
    TestUserWorkflowPerformance,
)
from ._test_e2e_user_workflows_real_data import TestRealDataIntegration
from ._test_e2e_user_workflows_strategy import TestUserWorkflowStrategyBacktest
from ._test_e2e_user_workflows_support import RealDataValidationMixin, _install_fake_api_modules

__all__ = [
    "RealDataValidationMixin",
    "TestRealDataIntegration",
    "TestUserWorkflowErrorRecovery",
    "TestUserWorkflowLoginSearchWatchlist",
    "TestUserWorkflowOrderPlacement",
    "TestUserWorkflowPerformance",
    "TestUserWorkflowStrategyBacktest",
    "_install_fake_api_modules",
    "client",
]


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v", "--tb=short"])
