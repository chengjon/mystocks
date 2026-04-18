from src.core import DataManager
from src.core.data_manager import DataManager as DirectDataManager


def test_src_core_re_exports_data_manager():
    assert DataManager is DirectDataManager
