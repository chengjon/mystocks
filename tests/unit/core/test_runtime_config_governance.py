from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_redis_connection_kwargs_prefers_role_specific_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('REDIS_HOST', 'redis-host')
    monkeypatch.setenv('REDIS_PORT', '6380')
    monkeypatch.setenv('REDIS_PASSWORD', '')
    monkeypatch.setenv('REDIS_DB', '9')
    monkeypatch.setenv('REDIS_APP_CACHE_DB', '3')

    from src.utils.redis_runtime_config import get_redis_connection_kwargs

    kwargs = get_redis_connection_kwargs('app_cache', decode_responses=True)

    assert kwargs == {
        'host': 'redis-host',
        'port': 6380,
        'db': 3,
        'password': None,
        'decode_responses': True,
    }


def test_redis_connection_kwargs_falls_back_to_legacy_then_role_default(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ['REDIS_HOST', 'REDIS_PORT', 'REDIS_PASSWORD', 'REDIS_DB', 'REDIS_MONITORING_DB']:
        monkeypatch.delenv(key, raising=False)

    from src.utils.redis_runtime_config import get_redis_connection_kwargs

    kwargs_default = get_redis_connection_kwargs('monitoring_events', decode_responses=False)
    assert kwargs_default['host'] == 'localhost'
    assert kwargs_default['port'] == 6379
    assert kwargs_default['db'] == 0
    assert kwargs_default['password'] is None
    assert kwargs_default['decode_responses'] is False

    monkeypatch.setenv('REDIS_DB', '7')
    kwargs_legacy = get_redis_connection_kwargs('monitoring_events')
    assert kwargs_legacy['db'] == 7


def test_mongo_connection_kwargs_prefers_standard_env_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('MONGODB_HOST', 'mongo-host')
    monkeypatch.setenv('MONGODB_PORT', '27019')
    monkeypatch.setenv('MONGODB_ROOT_USERNAME', 'root-user')
    monkeypatch.setenv('MONGODB_ROOT_PASSWORD', 'root-pass')
    monkeypatch.setenv('MONGODB_DATABASE', 'mystocks_docs')
    monkeypatch.setenv('MONGODB_AUTH_SOURCE', 'admin')
    monkeypatch.setenv('MONGODB_IP', 'legacy-host:27017')
    monkeypatch.setenv('USERNAME', 'legacy-user')
    monkeypatch.setenv('PASSWORD', 'legacy-pass')

    from src.utils.mongo_runtime_config import get_mongo_connection_kwargs

    kwargs = get_mongo_connection_kwargs(server_selection_timeout_ms=5000)

    assert kwargs == {
        'host': 'mongo-host',
        'port': 27019,
        'username': 'root-user',
        'password': 'root-pass',
        'authSource': 'admin',
        'serverSelectionTimeoutMS': 5000,
    }


def test_mongo_connection_kwargs_falls_back_to_legacy_aliases(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in [
        'MONGODB_HOST', 'MONGODB_PORT', 'MONGODB_ROOT_USERNAME', 'MONGODB_ROOT_PASSWORD', 'MONGODB_AUTH_SOURCE'
    ]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv('MONGODB_IP', 'localhost:27017')
    monkeypatch.setenv('USERNAME', 'mongo')
    monkeypatch.setenv('PASSWORD', 'secret')

    from src.utils.mongo_runtime_config import get_mongo_connection_kwargs

    kwargs = get_mongo_connection_kwargs()

    assert kwargs['host'] == 'localhost'
    assert kwargs['port'] == 27017
    assert kwargs['username'] == 'mongo'
    assert kwargs['password'] == 'secret'
    assert kwargs['authSource'] == 'admin'


def test_database_connection_manager_uses_role_aware_redis_kwargs() -> None:
    with patch('dotenv.load_dotenv', return_value=True):
        module = importlib.import_module('src.storage.database.connection_manager')
        module = importlib.reload(module)

    fake_pool = MagicMock()
    fake_conn = MagicMock()
    fake_redis_module = MagicMock()
    fake_redis_module.ConnectionPool.return_value = fake_pool
    fake_redis_module.Redis.return_value = fake_conn

    with patch.object(module.DatabaseConnectionManager, '_validate_env_variables', return_value=None), patch.object(
        module, 'redis', fake_redis_module
    ), patch.object(
        module,
        'get_redis_connection_kwargs',
        return_value={
            'host': 'redis-host',
            'port': 6380,
            'db': 3,
            'password': None,
            'decode_responses': True,
        },
        create=True,
    ) as mock_kwargs:
        manager = module.DatabaseConnectionManager()
        conn = manager.get_redis_connection()

    mock_kwargs.assert_called_once_with('app_cache', decode_responses=True)
    fake_redis_module.ConnectionPool.assert_called_once_with(
        host='redis-host',
        port=6380,
        db=3,
        password=None,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        max_connections=10,
    )
    fake_conn.ping.assert_called_once_with()
    assert conn is fake_conn




def test_redis_manager_uses_role_aware_redis_kwargs() -> None:
    module_name = 'test_web_backend_redis_client_module'
    module_path = Path('/opt/claude/mystocks_spec/web/backend/app/core/redis_client.py')

    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None

    fake_settings = type(
        'FakeSettings',
        (),
        {
            'redis_max_connections': 50,
            'redis_socket_timeout': 5,
            'redis_socket_connect_timeout': 5,
            'redis_decode_responses': True,
        },
    )()

    fake_redis_client = MagicMock()
    fake_redis_module = MagicMock()
    fake_redis_module.Redis.return_value = fake_redis_client
    fake_redis_module.ConnectionError = Exception
    fake_redis_module.TimeoutError = TimeoutError

    fake_app_core_config = MagicMock(settings=fake_settings)

    with patch.dict(
        sys.modules,
        {
            'app': MagicMock(),
            'app.core': MagicMock(),
            'app.core.config': fake_app_core_config,
            'redis': fake_redis_module,
        },
    ), patch('src.utils.redis_runtime_config.get_redis_connection_kwargs', return_value={
        'host': 'redis-host',
        'port': 6380,
        'db': 1,
        'password': None,
        'decode_responses': True,
    }) as mock_kwargs:
        sys.modules.pop(module_name, None)
        spec.loader.exec_module(module)
        manager = module.RedisManager()
        manager._initialize_client()

    mock_kwargs.assert_called_with('app_cache', decode_responses=True)
    fake_redis_module.Redis.assert_called_with(
        host='redis-host',
        port=6380,
        db=1,
        password=None,
        max_connections=50,
        socket_timeout=5,
        socket_connect_timeout=5,
        decode_responses=True,
        health_check_interval=30,
        retry_on_timeout=True,
        retry_on_error=[fake_redis_module.ConnectionError, fake_redis_module.TimeoutError],
    )
    fake_redis_client.ping.assert_called()



def test_app_container_uses_role_aware_redis_kwargs() -> None:
    module_name = 'test_src_application_bootstrap_module'
    module_path = Path('/opt/claude/mystocks_spec/src/application/bootstrap.py')

    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None

    fake_redis_client = MagicMock()
    fake_redis_module = MagicMock()
    fake_redis_module.Redis.return_value = fake_redis_client

    fake_event_bus = MagicMock()
    fake_redis_event_bus_cls = MagicMock(return_value=fake_event_bus)
    fake_local_event_bus_cls = MagicMock(return_value=MagicMock())
    fake_lock_cls = MagicMock(return_value=MagicMock())

    fake_repo_cls = MagicMock(return_value=MagicMock())
    fake_market_data_repo = MagicMock()
    fake_gpu_calc = MagicMock()
    fake_signal_service = MagicMock(return_value=MagicMock())
    fake_backtest_service = MagicMock(return_value=MagicMock())
    fake_order_service = MagicMock(return_value=MagicMock())
    fake_order_filled_event = type('OrderFilledEvent', (), {})

    with patch.dict(
        sys.modules,
        {
            'redis': fake_redis_module,
            'sqlalchemy': MagicMock(),
            'sqlalchemy.orm': MagicMock(Session=object),
            'src.application.strategy.backtest_service': MagicMock(BacktestApplicationService=fake_backtest_service),
            'src.application.trading.order_mgmt_service': MagicMock(OrderManagementService=fake_order_service),
            'src.domain.strategy.service': MagicMock(SignalGenerationService=fake_signal_service),
            'src.domain.trading.events': MagicMock(OrderFilledEvent=fake_order_filled_event),
            'src.infrastructure.cache.redis_lock': MagicMock(RedisDistributedLock=fake_lock_cls),
            'src.infrastructure.calculation.gpu_calculator': MagicMock(GPUIndicatorCalculator=MagicMock(return_value=fake_gpu_calc)),
            'src.infrastructure.market_data.adapter': MagicMock(DataSourceV2Adapter=MagicMock(return_value=fake_market_data_repo)),
            'src.infrastructure.messaging.local_event_bus': MagicMock(LocalEventBus=fake_local_event_bus_cls),
            'src.infrastructure.messaging.redis_event_bus': MagicMock(RedisEventBus=fake_redis_event_bus_cls),
            'src.infrastructure.persistence.repository_impl': MagicMock(
                OrderRepositoryImpl=fake_repo_cls,
                PortfolioRepositoryImpl=fake_repo_cls,
                StrategyRepositoryImpl=fake_repo_cls,
                TradingPositionRepositoryImpl=fake_repo_cls,
            ),
        },
    ), patch('src.utils.redis_runtime_config.get_redis_connection_kwargs', return_value={
        'host': 'redis-host',
        'port': 6380,
        'db': 0,
        'password': None,
        'decode_responses': True,
    }) as mock_kwargs, patch.dict('os.environ', {'EVENT_BUS_TYPE': 'REDIS'}):
        sys.modules.pop(module_name, None)
        spec.loader.exec_module(module)
        container = module.AppContainer(MagicMock())

    mock_kwargs.assert_called_once_with('monitoring_events', decode_responses=True)
    fake_redis_module.Redis.assert_called_once_with(
        host='redis-host',
        port=6380,
        db=0,
        password=None,
        decode_responses=True,
    )
    fake_redis_event_bus_cls.assert_called_once_with(redis_client=fake_redis_client)
    fake_lock_cls.assert_called_once_with(fake_redis_client)
    assert container.redis_client is fake_redis_client


def test_initialize_realtime_mtm_uses_role_aware_redis_kwargs() -> None:
    module_name = 'test_web_backend_realtime_mtm_init_module'
    module_path = Path('/opt/claude/mystocks_spec/web/backend/app/api/realtime_mtm_init.py')

    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None

    fake_event_bus = MagicMock()
    fake_redis_event_bus_cls = MagicMock(return_value=fake_event_bus)
    fake_adapter = MagicMock()
    fake_initialize_adapter = MagicMock(return_value=fake_adapter)

    with patch.dict(
        sys.modules,
        {
            'structlog': MagicMock(get_logger=MagicMock(return_value=MagicMock())),
            'sqlalchemy': MagicMock(create_engine=MagicMock()),
            'sqlalchemy.orm': MagicMock(Session=object, sessionmaker=MagicMock()),
            'web.backend.app.core.config': MagicMock(settings=MagicMock(DATABASE_URL='postgresql://u:p@h:5432/db')),
            'src.infrastructure.messaging.redis_event_bus': MagicMock(RedisEventBus=fake_redis_event_bus_cls),
            'web.backend.app.api.realtime_mtm_adapter': MagicMock(initialize_adapter=fake_initialize_adapter),
        },
    ), patch('src.utils.redis_runtime_config.get_redis_connection_kwargs', return_value={
        'host': 'redis-host',
        'port': 6380,
        'db': 0,
        'password': None,
        'decode_responses': True,
    }) as mock_kwargs:
        sys.modules.pop(module_name, None)
        spec.loader.exec_module(module)
        module.get_database_session = MagicMock(return_value=MagicMock())
        adapter = module.initialize_realtime_mtm()

    mock_kwargs.assert_called_once_with('monitoring_events', decode_responses=True)
    fake_redis_event_bus_cls.assert_called_once_with(host='redis-host', port=6380, db=0, password=None)
    fake_initialize_adapter.assert_called_once()
    assert adapter is fake_adapter



def test_redis_event_bus_defaults_to_monitoring_role_kwargs() -> None:
    module_name = 'test_src_infra_redis_event_bus_module'
    module_path = Path('/opt/claude/mystocks_spec/src/infrastructure/messaging/redis_event_bus.py')

    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None

    fake_redis_client = MagicMock()
    fake_redis_module = MagicMock(Redis=MagicMock(return_value=fake_redis_client))

    with patch.dict(
        sys.modules,
        {
            'redis': fake_redis_module,
            'src.domain.shared.event': MagicMock(DomainEvent=object),
            'src.domain.shared.event_bus': MagicMock(IEventBus=object),
        },
    ), patch('src.utils.redis_runtime_config.get_redis_connection_kwargs', return_value={
        'host': 'redis-host',
        'port': 6380,
        'db': 0,
        'password': None,
        'decode_responses': True,
    }) as mock_kwargs:
        sys.modules.pop(module_name, None)
        spec.loader.exec_module(module)
        bus = module.RedisEventBus()

    mock_kwargs.assert_called_once_with('monitoring_events', decode_responses=True)
    fake_redis_module.Redis.assert_called_once_with(host='redis-host', port=6380, db=0, password=None, decode_responses=True)
    assert bus.redis_client is fake_redis_client


def test_redis_event_bus_preserves_explicit_db_argument() -> None:
    module_name = 'test_src_infra_redis_event_bus_module_explicit'
    module_path = Path('/opt/claude/mystocks_spec/src/infrastructure/messaging/redis_event_bus.py')

    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None

    fake_redis_client = MagicMock()
    fake_redis_module = MagicMock(Redis=MagicMock(return_value=fake_redis_client))

    with patch.dict(
        sys.modules,
        {
            'redis': fake_redis_module,
            'src.domain.shared.event': MagicMock(DomainEvent=object),
            'src.domain.shared.event_bus': MagicMock(IEventBus=object),
        },
    ), patch('src.utils.redis_runtime_config.get_redis_connection_kwargs') as mock_kwargs:
        sys.modules.pop(module_name, None)
        spec.loader.exec_module(module)
        bus = module.RedisEventBus(host='explicit-host', port=6390, db=6, password='secret')

    mock_kwargs.assert_not_called()
    fake_redis_module.Redis.assert_called_once_with(host='explicit-host', port=6390, db=6, password='secret', decode_responses=True)
    assert bus.redis_client is fake_redis_client
