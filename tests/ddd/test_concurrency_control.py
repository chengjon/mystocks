"""
Concurrency Control Verification Test
验证乐观锁 (Versioning) 是否能防止数据覆盖冲突
"""

import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import StaleDataError

# 确保项目根目录在 path 中
sys.path.append(os.getcwd())

from src.storage.database.database_manager import Base
from src.infrastructure.persistence.models import PortfolioModel
from src.infrastructure.persistence.repository_impl import PortfolioRepositoryImpl, ConcurrencyException
from src.domain.portfolio.model.portfolio import Portfolio


def test_optimistic_locking():
    # 1. 准备 DB
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # 2. 初始化数据
    session1 = Session()
    repo1 = PortfolioRepositoryImpl(session1)
    p = Portfolio.create(name="Concurrency Test", initial_capital=100000.0)
    repo1.save(p)
    # session1.commit() # save 内部已经 commit 了

    portfolio_id = p.id

    # 3. 模拟两个并发 Session 获取同一个对象
    session_a = Session()
    session_b = Session()

    repo_a = PortfolioRepositoryImpl(session_a)
    repo_b = PortfolioRepositoryImpl(session_b)

    p_a = repo_a.get_by_id(portfolio_id)
    p_b = repo_b.get_by_id(portfolio_id)

    # 验证版本号初始一致
    model_a = session_a.query(PortfolioModel).get(portfolio_id)
    model_b = session_b.query(PortfolioModel).get(portfolio_id)
    assert model_a.version == model_b.version
    initial_version = model_a.version

    # 4. A 尝试更新并成功
    p_a.cash -= 1000
    repo_a.save(p_a)

    # 验证 A 更新后版本号增加了
    session_a.expire_all()
    model_a_updated = session_a.query(PortfolioModel).get(portfolio_id)
    assert model_a_updated.version > initial_version

    # 5. B 尝试更新（由于它持有的是旧版本号，应当失败）
    p_b.cash += 5000

    print("\nAttempting concurrent update from Session B...")
    with pytest.raises(ConcurrencyException) as excinfo:
        repo_b.save(p_b)

    print(f"✅ Success: Caught expected concurrency exception: {excinfo.value}")


if __name__ == "__main__":
    test_optimistic_locking()
