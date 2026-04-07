# TypeScript类型定义生成指南

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


## 📚 概述

本文档介绍如何从OpenAPI契约自动生成TypeScript类型定义，实现前端和后端的类型安全。

### 核心功能

- ✅ **自动生成**: 从OpenAPI契约自动生成TypeScript类型
- ✅ **类型安全**: 编译时类型检查，减少运行时错误
- ✅ **代码提示**: IDE自动完成和智能提示
- ✅ **多工具支持**: openapi-typescript、dtsgenerator、openapi-generator

---

## 🚀 快速开始

### 方法1: 使用Python脚本 (推荐)

```bash
# 使用默认工具 (openapi-typescript)
python scripts/generate-types/generate_ts_types.py

# 使用dtsgenerator
python scripts/generate-types/generate_ts_types.py --tool dtsgenerator

# 指定契约目录
python scripts/generate-types/generate_ts_types.py \
  --contracts-dir docs/api/contracts \
  --output-dir web/frontend/src/types/api
```

### 方法2: 使用Shell脚本

```bash
# 使用默认工具
bash scripts/generate-types/generate_ts_types.sh

# 指定工具
TOOL=dtsgenerator bash scripts/generate-types/generate_ts_types.sh
```

---

## 🛠️ 生成工具对比

| 工具 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **openapi-typescript** | 轻量级、类型准确、无依赖 | 功能较单一 | **Vue 3 + TypeScript** |
| **dtsgenerator** | 功能丰富、可配置 | 依赖较多 | 复杂项目 |
| **openapi-generator** | 功能完整、生成客户端 | 体积大、配置复杂 | 需要完整SDK |

### 推荐: openapi-typescript

```bash
# 全局安装
npm install -g openapi-typescript-codegen

# 生成类型
openapi-typescript-codegen docs/api/contracts/market-api.yaml \
  -o web/frontend/src/types/api/market-api.ts
```

---

## 📖 使用指南

### 1. 生成类型定义

```bash
# 1. 更新OpenAPI契约
vim docs/api/contracts/market-api.yaml

# 2. 生成TypeScript类型
python scripts/generate-types/generate_ts_types.py

# 3. 查看生成的文件
ls web/frontend/src/types/api/
# market-api.ts
# trade-api.ts
# technical-api.ts
# index.ts
# README.md
```

---

### 2. 在Vue 3中使用

```typescript
// web/frontend/src/types/api/index.ts
import * as MarketAPI from '@/types/api/market-api';
import * as TradeAPI from '@/types/api/trade-api';

// 使用类型
export interface StockData extends MarketAPI.StockSymbol {
  price: number;
  change: number;
}

// API调用
async function fetchStockList(): Promise<MarketAPI.StockListResponse> {
  const response = await fetch('/api/market/symbols');
  return response.json();
}
```

---

### 3. 在Pinia Store中使用

```typescript
// web/frontend/src/stores/market.ts
import { defineStore } from 'pinia';
import * as MarketAPI from '@/types/api/market-api';

export const useMarketStore = defineStore('market', {
  state: () => ({
    stocks: [] as MarketAPI.StockSymbol[],
  }),

  actions: {
    async fetchStocks() {
      const response = await fetch('/api/market/symbols');
      const data: MarketAPI.StockListResponse = await response.json();
      this.stocks = data.data || [];
    }
  }
});
```

---

### 4. 在API Service中使用

```typescript
// web/frontend/src/services/market.service.ts
import * as MarketAPI from '@/types/api/market-api';

export class MarketService {
  /**
   * 获取股票列表
   */
  async getStocks(): Promise<MarketAPI.StockListResponse> {
    const response = await fetch('/api/market/symbols');
    return response.json();
  }

  /**
   * 获取股票行情
   */
  async getQuote(symbol: string): Promise<MarketAPI.QuoteResponse> {
    const response = await fetch(`/api/market/quote?symbol=${symbol}`);
    return response.json();
  }

  /**
   * 创建自选股
   */
  async addToWatchlist(data: MarketAPI.WatchlistCreateRequest): Promise<MarketAPI.WatchlistResponse> {
    const response = await fetch('/api/market/watchlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }
}
```

---

## 📦 生成的文件结构

```
web/frontend/src/types/api/
├── index.ts                    # 导出所有类型
├── README.md                   # 使用文档
├── market-api.ts              # Market API类型
├── trade-api.ts               # Trade API类型
└── technical-api.ts           # Technical API类型
```

### 生成的类型示例

```typescript
// market-api.ts (由openapi-typescript-codegen生成)
export interface StockSymbol {
  symbol: string;
  name: string;
  industry?: string;
  sector?: string;
  market?: string;
}

export interface StockListResponse {
  code: string;
  message: string;
  data?: StockSymbol[];
  request_id?: string;
}

export interface QuoteRequest {
  symbol: string;
  fields?: string[];
}

export interface QuoteResponse {
  code: string;
  message: string;
  data?: QuoteData;
  request_id?: string;
}

// ... 更多类型定义
```

---

## 🔄 工作流程

### 开发流程

```
1. 修改后端API
    ↓
2. 更新OpenAPI契约 (docs/api/contracts/*.yaml)
    ↓
3. 验证契约 (pre-commit hooks)
    ↓
4. 生成TypeScript类型 (python scripts/generate-types/generate_ts_types.py)
    ↓
5. 前端使用新类型 (IDE自动补全)
```

---

### CI/CD集成

```yaml
# .github/workflows/generate-types.yml
name: 生成TypeScript类型

on:
  push:
    paths:
      - 'docs/api/contracts/**'

jobs:
  generate-types:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: 设置Python环境
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: 安装依赖
        run: |
          pip install pyyaml
          npm install -g openapi-typescript-codegen

      - name: 生成TypeScript类型
        run: |
          python scripts/generate-types/generate_ts_types.py

      - name: 提交生成的类型
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add web/frontend/src/types/api/
          git commit -m "chore: 自动生成TypeScript类型" || true
          git push
```

---

## 🎯 最佳实践

### 1. 版本控制

**✅ 推荐**: 提交生成的类型文件

```bash
# 添加到Git
git add web/frontend/src/types/api/
git commit -m "chore: 更新API类型定义"
```

**❌ 不推荐**: 添加到.gitignore

**原因**:
- 确保团队使用相同的类型定义
- 避免每次都重新生成
- 便于代码审查

---

### 2. 类型导入

**✅ 推荐**: 使用命名空间导入

```typescript
import * as MarketAPI from '@/types/api/market-api';

const stock: MarketAPI.StockSymbol = { ... };
```

**❌ 不推荐**: 直接导入所有类型

```typescript
import { StockSymbol, QuoteData, ... } from '@/types/api/market-api';
```

---

### 3. 类型扩展

**✅ 推荐**: 使用接口扩展

```typescript
import * as MarketAPI from '@/types/api/market-api';

interface ExtendedStock extends MarketAPI.StockSymbol {
  price: number;
  changePercent: number;
}
```

**❌ 不推荐**: 修改生成的类型

```typescript
// ❌ 不要直接修改生成的文件
// web/frontend/src/types/api/market-api.ts
```

---

### 4. 类型断言

**✅ 推荐**: 最小化类型断言

```typescript
const response = await fetch('/api/market/symbols');
const data = await response.json() as MarketAPI.StockListResponse;
```

**❌ 不推荐**: 过度使用any

```typescript
const data = await response.json() as any; // ❌ 失去类型安全
```

---

### 5. 错误处理

**✅ 推荐**: 使用统一的错误类型

```typescript
import * as CommonAPI from '@/types/api/common';

async function fetchStocks(): Promise<MarketAPI.StockListResponse> {
  try {
    const response = await fetch('/api/market/symbols');
    if (!response.ok) {
      throw new Error('API请求失败');
    }
    return response.json();
  } catch (error) {
    const errorResponse: CommonAPI.APIErrorResponse = {
      code: 'NETWORK_ERROR',
      message: error.message,
      data: null,
    };
    throw errorResponse;
  }
}
```

---

## 🔧 高级用法

### 1. 自定义生成器

```python
# scripts/generate-types/custom_generator.py
from typing import Dict, Any

class CustomTypeGenerator:
    """自定义TypeScript类型生成器"""

    def generate_types(self, spec: Dict[str, Any]) -> str:
        """生成自定义类型"""
        types = []

        for schema_name, schema in spec.get('components', {}).get('schemas', {}).items():
            types.append(self.generate_interface(schema_name, schema))

        return '\n\n'.join(types)

    def generate_interface(self, name: str, schema: Dict[str, Any]) -> str:
        """生成单个接口"""
        properties = schema.get('properties', {})
        required = set(schema.get('required', []))

        lines = [f"export interface {name} {", "  /**"]

        # 添加JSDoc注释
        if 'description' in schema:
            lines.append(f"   * {schema['description']}")
        lines.append("   */")

        # 添加属性
        for prop_name, prop_spec in properties.items():
            prop_type = self.get_type_string(prop_spec)
            optional = '' if prop_name in required else '?'
            lines.append(f"  {prop_name}{optional}: {prop_type};")

        lines.append("}")
        return '\n'.join(lines)

    def get_type_string(self, spec: Dict[str, Any]) -> str:
        """获取TypeScript类型字符串"""
        type_map = {
            'string': 'string',
            'number': 'number',
            'integer': 'number',
            'boolean': 'boolean',
            'array': 'any[]',
            'object': 'Record<string, any>',
        }

        t = spec.get('type')
        if t in type_map:
            return type_map[t]

        # 引用其他类型
        if '$ref' in spec:
            ref = spec['$ref']
            return ref.split('/')[-1]

        return 'any'
```

---

### 2. 批量生成脚本

```bash
#!/bin/bash
# scripts/generate-types/batch-generate.sh

CONTRACTS=(
  "market-api"
  "trade-api"
  "technical-api"
)

for contract in "${CONTRACTS[@]}"; do
  echo "生成 $contract 类型..."
  npx openapi-typescript-codegen \
    "docs/api/contracts/${contract}.yaml" \
    -o "web/frontend/src/types/api/${contract}.ts"
done

echo "✅ 批量生成完成"
```

---

### 3. 监听文件变化自动生成

```bash
#!/bin/bash
# scripts/generate-types/watch.sh

watchmedo shell-command \
  --pattern="*.yaml" \
  --recursive \
  --command='python scripts/generate-types/generate_ts_types.py' \
  docs/api/contracts/
```

---

## 🐛 故障排除

### 问题1: 生成失败 - "Cannot find module"

**错误**: `Cannot find module 'openapi-typescript-codegen'`

**解决方案**:
```bash
# 全局安装工具
npm install -g openapi-typescript-codegen

# 或使用npx
npx openapi-typescript-codegen docs/api/contracts/market-api.yaml
```

---

### 问题2: 类型不匹配

**错误**: TypeScript类型错误 - "Property 'xxx' does not exist"

**解决方案**:
1. 确认OpenAPI契约是最新的
2. 重新生成类型定义
3. 检查前端使用的版本与后端是否一致

---

### 问题3: 生成类型不完整

**错误**: 生成的类型缺少某些定义

**解决方案**:
```bash
# 1. 检查OpenAPI契约是否完整
python scripts/ci/validate_contracts.sh docs/api/contracts/market-api.yaml

# 2. 尝试使用不同的工具
python scripts/generate-types/generate_ts_types.py --tool dtsgenerator
```

---

## 📊 性能优化

### 1. 增量生成

```bash
# 仅生成修改的契约
git diff --name-only main docs/api/contracts/*.yaml | \
  while read file; do
    python scripts/generate-types/generate_ts_types.py --contracts "$file"
  done
```

---

### 2. 并发生成

```python
# scripts/generate-types/generate_parallel.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def generate_types_parallel(contract_files):
    """并发生成类型定义"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, generate_types, contract)
            for contract in contract_files
        ]
        await asyncio.gather(*tasks)
```

---

## 🔗 相关文档

- [API契约管理平台文档](./CONTRACT_MANAGEMENT_API.md)
- [CLI工具使用指南](./CLI_TOOL_GUIDE.md)
- [CI/CD集成指南](./CI_CD_INTEGRATION_GUIDE.md)
- [openapi-typescript官方文档](https://openapi-ts.pages.dev/)

---

**历史文档版本快照**: v1.0.0
**历史最后更新快照**: 2025-12-29
**历史维护者快照**: MyStocks Frontend Team
