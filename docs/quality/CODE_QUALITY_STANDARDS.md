# MyStocks 代码质量标准

## 概述

本文档定义了 MyStocks 项目的代码质量标准和最佳实践。

## Python代码标准

### 命名规范

- **类名**: PascalCase (如 `StockDataManager`)
- **函数/变量名**: snake_case (如 `get_stock_data`, `user_id`)
- **常量名**: UPPER_SNAKE_CASE (如 `MAX_RETRY_COUNT`)
- **私有成员**: 以下划线前缀 (如 `_private_method`)

### 代码格式化

使用 Black 进行代码格式化：

```bash
black src/ tests/
```

**配置**:
- 行长度: 120字符
- 字符串引号: 双引号
- 缩进: 4空格

### 导入规范

```python
# 1. 标准库导入
import os
import sys
from typing import List, Optional

# 2. 第三方库导入
import pandas as pd
from fastapi import FastAPI

# 3. 本地导入
from src.core.config import settings
from src.api.models import StockData
```

### 类型提示

所有函数必须包含类型提示：

```python
from typing import List, Optional

def get_stock_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[StockData]:
    """
    获取股票数据

    Args:
        symbol: 股票代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    Returns:
        股票数据列表
    """
    pass
```

### 文档字符串

使用 Google 风格的文档字符串：

```python
def calculate_indicator(
    symbol: str,
    indicator_code: str,
    params: dict
) -> dict:
    """
    计算技术指标

    Args:
        symbol: 股票代码 (如 "000001")
        indicator_code: 指标代码 (如 "MACD", "RSI")
        params: 指标参数字典

    Returns:
        包含计算结果的字典

    Raises:
        ValueError: 当股票代码或指标代码无效时

    Examples:
        >>> calculate_indicator("000001", "MACD", {})
        {'macd': [...], 'signal': [...], 'histogram': [...]}
    """
    pass
```

### 错误处理

```python
from src.core.exceptions import MyStocksException

def process_data(data: dict) -> dict:
    """
    处理数据

    Raises:
        MyStocksException: 当数据处理失败时
    """
    try:
        # 数据处理逻辑
        if not data:
            raise MyStocksException(
                error_code="INVALID_DATA",
                message="数据不能为空"
            )
        return processed_data
    except Exception as e:
        logger.error(f"数据处理失败: {e}")
        raise MyStocksException(
            error_code="PROCESSING_ERROR",
            message="数据处理失败",
            details={"error": str(e)}
        )
```

## API设计规范

### 统一响应格式

所有API端点必须使用统一响应格式：

```python
from src.core.responses import create_success_response, create_error_response

@app.get("/api/stocks/{symbol}")
async def get_stock(symbol: str):
    """获取股票信息"""
    try:
        data = stock_service.get_stock(symbol)
        return create_success_response(data=data, message="获取成功")
    except StockNotFound as e:
        return create_error_response(
            error_code="STOCK_NOT_FOUND",
            message="股票不存在",
            details={"symbol": symbol}
        )
```

### 错误码规范

错误码使用3-4位数字，按模块分类：

- `1001-1999`: 通用错误
- `2001-2999`: 市场数据错误
- `3001-3999`: 指标计算错误
- `4001-4999`: AI筛选错误
- `5001-5999`: 策略执行错误

示例：

```python
class ErrorCode(Enum):
    STOCK_NOT_FOUND = "1001"
    INVALID_DATE_RANGE = "1002"
    INDICATOR_CALC_FAILED = "3001"
    STRATEGY_NOT_FOUND = "5001"
```

## TypeScript/Vue代码标准

### 命名规范

- **组件名**: PascalCase (如 `StockChart.vue`, `RecommendationList.vue`)
- **函数/变量名**: camelCase (如 `getStockData`, `userId`)
- **常量名**: UPPER_SNAKE_CASE (如 `API_BASE_URL`)
- **Type/Interface**: PascalCase (如 `StockData`, `ApiResponse`)

### 组件结构

```vue
<template>
  <!-- 模板 -->
</template>

<script setup lang="ts">
// 1. 导入
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 2. Props和Emits定义
interface Props {
  symbol: string
  interval?: string
}
const props = withDefaults(defineProps<Props>(), {
  interval: '1d'
})

// 3. 响应式状态
const loading = ref(false)
const data = ref<StockData[]>([])

// 4. 计算属性
const formattedData = computed(() => {
  return data.value.map(item => ({...}))
})

// 5. 方法
const fetchData = async () => {
  loading.value = true
  try {
    // 获取数据
  } finally {
    loading.value = false
  }
}

// 6. 生命周期
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* 样式 */
</style>
```

### API调用规范

```typescript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export const stockApi = {
  async getKlineData(symbol: string, interval: string) {
    const response = await apiClient.get(`/data/kline/${symbol}`, {
      params: { interval, limit: 100 }
    })
    return response.data.data
  },

  async calculateIndicator(symbol: string, indicator: string) {
    const response = await apiClient.get(`/indicators/${symbol}/${indicator}`)
    return response.data.data
  }
}
```

## 数据库规范

### 表命名

- 使用 snake_case
- 表名前缀按模块分类
- 示例: `stocks_`, `indicators_`, `strategies_`

### 字段命名

- 使用 snake_case
- 时间字段使用 `_at` 或 `_time` 后缀
- 示例: `created_at`, `updated_at`, `trade_time`

### 索引规范

- 主键: `id`
- 外键: `{table}_id`
- 唯一索引: `uk_{field}`
- 普通索引: `idx_{field}`

## 测试规范

### 单元测试

```python
import pytest
from src.services.stock_service import StockService

class TestStockService:
    """股票服务测试"""

    @pytest.fixture
    def stock_service(self):
        return StockService()

    def test_get_stock_data_success(self, stock_service):
        """测试成功获取股票数据"""
        data = stock_service.get_stock("000001")
        assert data.symbol == "000001"
        assert len(data.prices) > 0

    def test_get_stock_data_not_found(self, stock_service):
        """测试股票不存在"""
        with pytest.raises(StockNotFound):
            stock_service.get_stock("999999")
```

### 集成测试

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestStockAPI:
    """股票API集成测试"""

    def test_get_kline_data_endpoint(self):
        """测试K线数据接口"""
        response = client.get("/api/data/kline/000001", params={
            "interval": "1d",
            "limit": 100
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
```

## 文档规范

### 代码文档

- 所有公共函数必须有文档字符串
- 复杂逻辑必须添加注释
- 使用类型提示

### API文档

- 所有API端点必须有描述
- 请求参数必须有类型和说明
- 响应格式必须清晰
- 提供示例请求和响应

### README规范

每个模块目录应包含 README.md，说明：
- 模块功能
- 使用方法
- 依赖关系
- 示例代码

## 性能规范

### 数据库查询

- 使用索引优化查询
- 避免N+1查询
- 使用批量操作
- 合理使用缓存

### API响应

- 响应时间 < 500ms (P95)
- 使用分页处理大数据集
- 启用压缩
- 使用缓存减少重复计算

### 前端优化

- 代码分割和懒加载
- 图片懒加载
- 虚拟滚动处理长列表
- 使用缓存策略

## 安全规范

### 认证和授权

- 所有修改操作需要认证
- 使用JWT令牌
- 实现CSRF保护
- 敏感操作需要二次确认

### 数据验证

- 输入参数必须验证
- 使用Pydantic模型
- 防止SQL注入
- 防止XSS攻击

### 敏感信息

- 使用环境变量存储密钥
- 不在代码中硬编码凭证
- 加密存储密码
- 定期轮换密钥

## 代码审查清单

### 提交前检查

- [ ] 代码通过 Black 格式化
- [ ] 通过 Ruff 检查
- [ ] Pylint 评分 > 8.0
- [ ] 单元测试覆盖率 > 80%
- [ ] 通过 Bandit 安全扫描
- [ ] 文档字符串完整
- [ ] 类型提示完整
- [ ] 通过所有测试

### 代码审查要点

- [ ] 代码逻辑清晰易懂
- [ ] 命名规范一致
- [ ] 错误处理完善
- [ ] 性能优化合理
- [ ] 安全隐患已处理
- [ ] 文档准确完整

## 工具链

### 必需工具

```bash
# 代码格式化
pip install black

# 代码检查
pip install ruff pylint mypy

# 安全扫描
pip install bandit safety

# 测试
pip install pytest pytest-cov pytest-asyncio
```

### CI/CD集成

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: black --check src/ tests/
      - run: ruff check src/
      - run: pylint src/
      - run: pytest --cov=src --cov-fail-under=80
      - run: bandit -r src/
```

---

遵循这些标准将确保代码质量和可维护性。
