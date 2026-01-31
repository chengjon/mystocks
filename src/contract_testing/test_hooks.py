"""
Test Hooks Manager for Contract Testing

Implements before/after hooks for test setup and cleanup.
Similar to Dredd's hook system.

Task 12.2 Implementation: Test hooks for data preparation and cleanup
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


class HookType(str, Enum):
    """Hook types supported by contract testing"""

    BEFORE_ALL = "beforeAll"
    AFTER_ALL = "afterAll"
    BEFORE_EACH = "beforeEach"
    AFTER_EACH = "afterEach"
    BEFORE_TRANSACTION = "beforeTransaction"
    AFTER_TRANSACTION = "afterTransaction"


@dataclass
class HookContext:
    """Context passed to hook functions"""

    test_id: str
    endpoint_method: str
    endpoint_path: str
    timestamp: datetime = field(default_factory=datetime.now)
    request_data: Dict = field(default_factory=dict)
    response_data: Dict = field(default_factory=dict)
    test_state: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "test_id": self.test_id,
            "endpoint_method": self.endpoint_method,
            "endpoint_path": self.endpoint_path,
            "timestamp": self.timestamp.isoformat(),
            "request_data": self.request_data,
            "response_data": self.response_data,
            "test_state": self.test_state,
            "metadata": self.metadata,
        }


@dataclass
class Hook:
    """Hook definition"""

    type: HookType
    name: str
    handler: Callable
    description: str = ""
    priority: int = 0  # Higher priority runs first

    def execute(self, context: HookContext) -> None:
        """Execute hook"""
        try:
            self.handler(context)
            logger.debug("✅ Hook executed: %s (%s)", self.name, self.type.value)
        except Exception as e:
            logger.error("❌ Hook failed: %s (%s): %s", self.name, self.type.value, e)
            raise


class TestHooksManager:
    """
    Manages test hooks for contract testing.

    Provides setup and teardown hooks for data preparation and cleanup.
    Similar to Dredd's hook system.
    """

    def __init__(self):
        """Initialize hooks manager"""
        self.hooks: Dict[str, List[Hook]] = {}
        self.hook_execution_log: List[Dict] = []

        # Initialize hook type containers
        for hook_type in HookType:
            self.hooks[hook_type.value] = []

    def register_hook(
        self,
        hook_type: HookType,
        handler: Callable,
        name: str = "",
        description: str = "",
        priority: int = 0,
    ) -> None:
        """
        Register a hook

        Args:
            hook_type: Type of hook
            handler: Callable to execute
            name: Hook name (auto-generated if not provided)
            description: Hook description
            priority: Execution priority (higher = earlier)
        """
        if not name:
            name = f"{hook_type.value}_{len(self.hooks[hook_type.value]) + 1}"

        hook = Hook(
            type=hook_type,
            name=name,
            handler=handler,
            description=description,
            priority=priority,
        )

        self.hooks[hook_type.value].append(hook)

        # Sort by priority (descending)
        self.hooks[hook_type.value].sort(key=lambda h: h.priority, reverse=True)

        logger.info("✅ Registered hook: %s (%s)", name, hook_type.value)

    def before_all(self, handler: Callable, name: str = "", description: str = "") -> None:
        """Register beforeAll hook"""
        self.register_hook(HookType.BEFORE_ALL, handler, name, description, priority=100)

    def after_all(self, handler: Callable, name: str = "", description: str = "") -> None:
        """Register afterAll hook"""
        self.register_hook(HookType.AFTER_ALL, handler, name, description, priority=100)

    def before_each(self, handler: Callable, name: str = "", description: str = "") -> None:
        """Register beforeEach hook"""
        self.register_hook(HookType.BEFORE_EACH, handler, name, description, priority=50)

    def after_each(self, handler: Callable, name: str = "", description: str = "") -> None:
        """Register afterEach hook"""
        self.register_hook(HookType.AFTER_EACH, handler, name, description, priority=50)

    def before_transaction(self, handler: Callable, name: str = "", description: str = "") -> None:
        """Register beforeTransaction hook"""
        self.register_hook(HookType.BEFORE_TRANSACTION, handler, name, description, priority=10)

    def after_transaction(self, handler: Callable, name: str = "", description: str = "") -> None:
        """Register afterTransaction hook"""
        self.register_hook(HookType.AFTER_TRANSACTION, handler, name, description, priority=10)

    def execute_hooks(self, hook_type: HookType, context: HookContext) -> None:
        """
        Execute all hooks of a given type

        Args:
            hook_type: Type of hooks to execute
            context: Hook context
        """
        hooks = self.hooks.get(hook_type.value, [])
        logger.debug("⚙️  Executing %s hooks of type %s", len(hooks), hook_type.value)

        for hook in hooks:
            try:
                hook.execute(context)
                self._log_hook_execution(hook, context, success=True)
            except Exception as e:
                self._log_hook_execution(hook, context, success=False, error=str(e))
                raise

    def _log_hook_execution(
        self,
        hook: Hook,
        context: HookContext,
        success: bool = True,
        error: str = "",
    ) -> None:
        """Log hook execution"""
        log_entry = {
            "hook_name": hook.name,
            "hook_type": hook.type.value,
            "test_id": context.test_id,
            "timestamp": context.timestamp.isoformat(),
            "success": success,
            "error": error,
        }
        self.hook_execution_log.append(log_entry)

    def get_execution_log(self) -> List[Dict]:
        """Get hook execution log"""
        return self.hook_execution_log

    def get_hooks_by_type(self, hook_type: HookType) -> List[Hook]:
        """Get all hooks of a given type"""
        return self.hooks.get(hook_type.value, [])

    def get_all_hooks(self) -> Dict[str, List[Hook]]:
        """Get all registered hooks"""
        return self.hooks

    def clear_hooks(self) -> None:
        """Clear all registered hooks"""
        for hook_type in HookType:
            self.hooks[hook_type.value] = []
        logger.info("✅ Cleared all hooks")

    def export_log(self, output_path: str) -> None:
        """Export execution log to JSON"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.hook_execution_log, f, ensure_ascii=False, indent=2)
        logger.info("✅ Exported hook execution log to %s", output_path)


# Common hook implementations for data setup/cleanup


def create_test_user_hook(context: HookContext) -> None:
    """Create test user for API testing"""
    context.test_state["test_user_id"] = "test_user_123"
    context.test_state["test_token"] = "test_token_abc"
    logger.debug("✅ Created test user for %s", context.test_id)


def cleanup_test_data_hook(context: HookContext) -> None:
    """Clean up test data after test"""
    # This would typically delete test data from database
    test_user_id = context.test_state.get("test_user_id")
    if test_user_id:
        logger.debug("✅ Cleaned up test data for user %s", test_user_id)


def add_auth_headers_hook(context: HookContext) -> None:
    """Add authentication headers to request"""
    if "request_data" not in context.metadata:
        context.metadata["request_data"] = {}

    test_token = context.test_state.get("test_token", "default_test_token")
    context.metadata["headers"] = {
        "Authorization": f"Bearer {test_token}",
        "Content-Type": "application/json",
    }
    logger.debug("✅ Added auth headers to %s %s", context.endpoint_method, context.endpoint_path)


def validate_response_structure_hook(context: HookContext) -> None:
    """Validate response structure matches specification"""
    if not context.response_data:
        raise ValueError(f"Empty response for {context.endpoint_method} {context.endpoint_path}")
    logger.debug("✅ Validated response structure for %s", context.test_id)
