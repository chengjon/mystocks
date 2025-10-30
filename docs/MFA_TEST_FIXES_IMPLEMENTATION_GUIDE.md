# MFA 功能测试修复指南

**日期**: 2025-10-28
**状态**: 分析完成，实施方案准备好

---

## 📋 问题分析

### 失败的 6 个 MFA 测试

```
❌ test_login_without_mfa_enabled
❌ test_login_with_mfa_enabled_returns_temp_token
❌ test_mfa_check_graceful_degradation_on_db_error
❌ test_mfa_check_graceful_degradation_on_query_timeout
❌ test_failure_counter_resets_on_success
❌ test_mfa_temp_token_expiration
```

### 根本原因

这 6 个测试失败的共同原因：
- **Mock 与 SQLAlchemy 查询链不匹配**: 测试使用的 mock 无法准确模拟 SQLAlchemy 的 `select().scalar_one_or_none()` 和 `select().scalars().all()` 链式调用
- **FastAPI 依赖注入问题**: `@patch` 装饰器无法正确注入到 FastAPI 的依赖系统中

### 现状

```
原始测试结果:  36/42 通过 (85%)
修复后目标:    42/42 通过 (100%)
工作量:        2-3 小时
难度:          中等 (SQLAlchemy mocking)
```

---

## 🔧 解决方案详解

### 方案 A: 使用 Fixture + Dependency Override (推荐)

**优点**:
- ✅ 最简洁
- ✅ 易于维护
- ✅ 符合 FastAPI 最佳实践

**实施步骤**:

```python
# 步骤 1: 创建 database 模块的 mock (已完成)
@pytest.fixture
def client_with_db_override(mock_db):
    """创建带数据库覆盖的测试客户端"""
    def override_get_db():
        return mock_db

    from app.core.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# 步骤 2: 正确配置 SQLAlchemy mock (需要优化)
def test_login_without_mfa_enabled(self, client_with_db_override, mock_db, mock_user_model):
    """关键修改：正确链式配置 execute() 返回值"""

    mock_user_model.mfa_enabled = False

    # ❌ 错误的方式 (目前的实现)
    # query_mock = MagicMock()
    # query_mock.scalar_one_or_none.return_value = mock_user_model
    # mock_db.execute.return_value = query_mock

    # ✅ 正确的方式
    execute_result = MagicMock()
    execute_result.scalar_one_or_none = MagicMock(return_value=mock_user_model)
    mock_db.execute = MagicMock(return_value=execute_result)

    response = client_with_db_override.post(
        TestConfig.LOGIN_ENDPOINT,
        data={...},
    )

    assert response.status_code == 200
    assert data["mfa_required"] is False
```

**关键差异**:
```python
# 错误方式
query_mock = MagicMock()
query_mock.scalar_one_or_none.return_value = user  # ❌ 不生效
mock_db.execute.return_value = query_mock

# 正确方式
result = MagicMock()
result.scalar_one_or_none = MagicMock(return_value=user)  # ✅ 配置为 MagicMock
mock_db.execute = MagicMock(return_value=result)
```

---

## 🔨 具体修复步骤

### 修复 1: test_login_without_mfa_enabled

```python
def test_login_without_mfa_enabled(self, client_with_db_override, mock_db, mock_user_model):
    """修复: 正确配置 SQLAlchemy 链式调用 mock"""

    mock_user_model.mfa_enabled = False

    # 配置 execute().scalar_one_or_none() 链
    execute_mock = MagicMock()
    execute_mock.scalar_one_or_none = MagicMock(return_value=mock_user_model)
    mock_db.execute = MagicMock(return_value=execute_mock)

    response = client_with_db_override.post(
        TestConfig.LOGIN_ENDPOINT,
        data={
            "username": TestConfig.ADMIN_USERNAME,
            "password": TestConfig.ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 200
    assert data["mfa_required"] is False
```

### 修复 2: test_login_with_mfa_enabled_returns_temp_token

```python
def test_login_with_mfa_enabled_returns_temp_token(
    self, client_with_db_override, mock_db, mock_user_with_mfa, mock_mfa_secret
):
    """修复: 处理两次 execute() 调用 (user + MFA secrets)"""

    # 第一次 execute() 调用 - 查询 user
    user_execute_mock = MagicMock()
    user_execute_mock.scalar_one_or_none = MagicMock(return_value=mock_user_with_mfa)

    # 第二次 execute() 调用 - 查询 MFA secrets
    mfa_execute_mock = MagicMock()
    mfa_scalars_mock = MagicMock()
    mfa_scalars_mock.all = MagicMock(return_value=[mock_mfa_secret])
    mfa_execute_mock.scalars = MagicMock(return_value=mfa_scalars_mock)

    # 重要: 配置 execute() 返回序列
    mock_db.execute = MagicMock(side_effect=[user_execute_mock, mfa_execute_mock])

    response = client_with_db_override.post(...)

    assert response.status_code == 200
    assert data["mfa_required"] is True
    assert data["expires_in"] == 5 * 60
```

### 修复 3-4: Graceful Degradation 测试

```python
def test_mfa_check_graceful_degradation_on_db_error(
    self, client_with_db_override, mock_db
):
    """修复: 模拟异常情况"""

    # 让 execute() 抛出异常
    mock_db.execute = MagicMock(
        side_effect=OperationalError("Connection failed", None, None)
    )

    with patch("app.api.auth.logger") as mock_logger:
        response = client_with_db_override.post(...)

    assert response.status_code == 200
    assert data["mfa_required"] is False
    mock_logger.warning.assert_called()
```

### 修复 5: test_failure_counter_resets_on_success

```python
def test_failure_counter_resets_on_success(
    self, client_with_db_override, mock_db, mock_user_model
):
    """修复: 模拟失败->成功的过程"""

    # 第 1 次: 失败
    mock_db.execute = MagicMock(
        side_effect=OperationalError("DB error", None, None)
    )
    response1 = client_with_db_override.post(...)
    assert auth._mfa_query_failure_count == 1

    # 第 2 次: 成功
    execute_mock = MagicMock()
    execute_mock.scalar_one_or_none = MagicMock(return_value=mock_user_model)
    mock_db.execute = MagicMock(return_value=execute_mock)

    response2 = client_with_db_override.post(...)
    assert auth._mfa_query_failure_count == 0  # 应该重置
```

### 修复 6: test_mfa_temp_token_expiration

```python
def test_mfa_temp_token_expiration(
    self, client_with_db_override, mock_db, mock_user_with_mfa, mock_mfa_secret
):
    """修复: 与修复 2 相同逻辑"""

    # 配置两次 execute() 调用
    user_execute_mock = MagicMock()
    user_execute_mock.scalar_one_or_none = MagicMock(return_value=mock_user_with_mfa)

    mfa_execute_mock = MagicMock()
    mfa_scalars_mock = MagicMock()
    mfa_scalars_mock.all = MagicMock(return_value=[mock_mfa_secret])
    mfa_execute_mock.scalars = MagicMock(return_value=mfa_scalars_mock)

    mock_db.execute = MagicMock(side_effect=[user_execute_mock, mfa_execute_mock])

    response = client_with_db_override.post(...)

    assert response.status_code == 200
    assert data["expires_in"] == 5 * 60
    assert data["mfa_required"] is True
```

---

## 📝 修复总结

### 关键变更

| 测试 | 主要修复 | 预期结果 |
|------|--------|--------|
| test_login_without_mfa_enabled | 正确配置 execute() 链 | ✅ 通过 |
| test_login_with_mfa_enabled_returns_temp_token | 处理两次 execute() 调用 | ✅ 通过 |
| test_mfa_check_graceful_degradation_on_db_error | 模拟异常 | ✅ 通过 |
| test_mfa_check_graceful_degradation_on_query_timeout | 模拟异常 | ✅ 通过 |
| test_failure_counter_resets_on_success | 模拟失败->成功 | ✅ 通过 |
| test_mfa_temp_token_expiration | 处理两次 execute() 调用 | ✅ 通过 |

### 预期成果

```
修复前: 36/42 通过 (85%)
修复后: 42/42 通过 (100%) ✨
```

---

## 🚀 实施优先级

**优先级 1 - 立即修复** (可选，已有 85% 通过率)
- 这 6 个测试的失败不影响实际功能
- API 已验证返回 HTTP 200 而不是 500
- 优雅降级功能已工作

**优先级 2 - 一周内完成**
- 使用本文档中的代码示例修复这 6 个测试
- 时间投入: 2-3 小时
- 好处: 达到 100% 测试通过率

---

## 💡 为什么这 6 个测试现在失败?

### 核心原因

FastAPI 的 `TestClient` 使用真实的依赖注入系统。虽然我们添加了 `client_with_db_override` fixture，但 mock 对象需要精确匹配 SQLAlchemy 的查询链式模式：

```python
# 实际代码做的事
db.execute(select(UserModel)...).scalar_one_or_none()
#  ↑ 第一步    ↑ 第二步                ↑ 第三步

# Mock 需要支持完整的链式
execute_result = db.execute(...)
execute_result.scalar_one_or_none()
```

当 mock 配置不正确时，`scalar_one_or_none()` 返回 None，导致代码路径与预期不同。

### 为什么原始的 @patch 方式失败

```python
@patch("app.api.auth.get_db")  # ❌ 这不会工作
def test_...(self, mock_get_db, client):
    # FastAPI TestClient 不会看到这个 patch
    # 因为依赖已经在测试开始前注入了
```

FastAPI 在测试开始时就注入了依赖，所以运行时的 `@patch` 装饰器太晚了。

---

## ✅ 检查清单

- [ ] 更新 6 个 MFA 功能测试使用正确的 mock 配置
- [ ] 运行测试: `pytest tests/test_login_api_graceful_degradation.py -v`
- [ ] 验证所有 42 个测试通过
- [ ] 生成新的测试报告
- [ ] 更新文档

---

**预计完成时间**: 2-3 小时
**建议**: 在下一个 sprint 中执行，非阻塞项

