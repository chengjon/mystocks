"""
Service Factory - Centralized singleton service management
Task 1.4: Remove Duplicate Code - Phase 1

Consolidates the repeated singleton pattern used in 8+ service files:

BEFORE (in each service):
```python
_service = None

def get_service():
    global _service
    if _service is None:
        _service = MarketDataService()
    return _service
```

AFTER (use factory):
```python
service = ServiceFactory.get_service(MarketDataService)
```

Estimated Duplication Reduced: 80+ lines
"""

from typing import Dict, Type, TypeVar, Generic
import structlog

logger = structlog.get_logger()

T = TypeVar("T")


class ServiceFactory(Generic[T]):
    """
    Generic factory for managing singleton service instances

    Consolidates the repeated singleton pattern across all services.
    Each service no longer needs to implement its own singleton.

    Usage:
        ```python
        # Define service
        class MyService:
            def __init__(self):
                self.data = []

        # Get singleton instance
        service = ServiceFactory.get_instance(MyService)
        service.data.append("item")

        # Same instance returned on subsequent calls
        service2 = ServiceFactory.get_instance(MyService)
        assert service is service2  # True
        ```
    """

    _instances: Dict[Type, any] = {}

    @staticmethod
    def get_instance(service_class: Type[T], *args, **kwargs) -> T:
        """
        Get or create singleton instance of a service

        Args:
            service_class: Service class to instantiate
            *args: Arguments to pass to service constructor (first call only)
            **kwargs: Keyword arguments to pass to service constructor (first call only)

        Returns:
            Singleton instance of the service

        PERFORMANCE: Service instantiated only once, then reused
        """
        if service_class not in ServiceFactory._instances:
            logger.info(
                f"✅ Creating singleton instance of {service_class.__name__}"
            )
            ServiceFactory._instances[service_class] = service_class(
                *args, **kwargs
            )

        return ServiceFactory._instances[service_class]

    @staticmethod
    def get_service(service_class: Type[T]) -> T:
        """Alias for get_instance for backwards compatibility"""
        return ServiceFactory.get_instance(service_class)

    @staticmethod
    def reset_instance(service_class: Type[T]) -> None:
        """
        Reset/clear a service instance

        Useful for testing or when you need to recreate a service.

        Args:
            service_class: Service class to reset
        """
        if service_class in ServiceFactory._instances:
            logger.info(
                f"🔄 Resetting singleton instance of {service_class.__name__}"
            )
            del ServiceFactory._instances[service_class]

    @staticmethod
    def reset_all() -> None:
        """Reset all service instances (useful for testing)"""
        logger.info(
            f"🔄 Resetting all {len(ServiceFactory._instances)} service instances"
        )
        ServiceFactory._instances.clear()

    @staticmethod
    def get_all_instances() -> Dict[Type, any]:
        """Get dictionary of all instantiated services"""
        return ServiceFactory._instances.copy()

    @staticmethod
    def instance_count() -> int:
        """Get count of currently instantiated services"""
        return len(ServiceFactory._instances)
