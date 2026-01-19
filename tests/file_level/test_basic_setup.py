"""
Simple test to verify file-level testing framework setup
"""


def test_framework_import():
    """Test that the framework can be imported"""
    try:
        from tests.file_level.core import FileLevelTestRunner
        from tests.file_level.fixtures import TestDataFactory

        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"


def test_config_loading():
    """Test that configuration can be loaded"""
    try:
        from tests.file_level.fixtures import TestConfig

        config = TestConfig()
        assert config.get("api.base_url") is not None
    except Exception as e:
        assert False, f"Config loading failed: {e}"


def test_data_factory():
    """Test that test data factory works"""
    try:
        from tests.file_level.fixtures import TestDataFactory

        factory = TestDataFactory()
        data = factory.create_market_data()
        assert "symbol" in data
        assert "price" in data
    except Exception as e:
        assert False, f"Data factory failed: {e}"
