# API契约管理平台使用文档

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


## 📚 概述

API契约管理平台提供完整的OpenAPI规范版本管理、差异检测、验证和同步功能。

### 核心功能

- **版本管理**: 创建、查询、更新、删除契约版本
- **差异检测**: 自动检测破坏性变更和非破坏性变更
- **契约验证**: OpenAPI规范校验和最佳实践检查
- **契约同步**: 代码与契约的双向同步

### 设计原则

1. **Schema First Architecture** - Pydantic模型作为单一真相源
2. **Contract First Development** - 先更新契约，再修改代码
3. **语义化版本控制** - 遵循SemVer版本规范
4. **自动化验证** - 集成CI/CD流水线

---

## 🔌 API端点清单

### 1. 契约版本管理 (Version Management)

#### 1.1 创建契约版本

**端点**: `POST /api/contracts/versions`

**描述**: 创建新的契约版本，自动激活首个版本

**请求体**:
```json
{
  "name": "market-api",
  "version": "1.0.0",
  "spec": {
    "openapi": "3.0.0",
    "info": {
      "title": "Market API",
      "version": "1.0.0"
    },
    "paths": {},
    "components": {
      "schemas": {}
    }
  },
  "commit_hash": "abc123def456",  # pragma: allowlist secret
  "author": "developer-team",
  "description": "初始版本",
  "tags": ["v1", "stable"]
}
```

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "契约版本创建成功",
  "data": {
    "id": 1,
    "name": "market-api",
    "version": "1.0.0",
    "spec": { /* OpenAPI规范 */ },
    "commit_hash": "abc123def456",  # pragma: allowlist secret
    "author": "developer-team",
    "description": "初始版本",
    "tags": ["v1", "stable"],
    "is_active": true,
    "created_at": "2025-12-29T10:30:00Z"
  },
  "request_id": "req_123456"
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 契约名称 (如: market-api, trade-api) |
| version | string | ✅ | 版本号 (遵循SemVer: MAJOR.MINOR.PATCH) |
| spec | object | ✅ | OpenAPI 3.0规范内容 |
| commit_hash | string | ❌ | Git commit hash (用于追溯) |
| author | string | ❌ | 作者或团队名称 |
| description | string | ❌ | 版本变更说明 |
| tags | array | ❌ | 版本标签 (如: stable, beta, deprecated) |

**自动激活规则**:
- 如果是该契约的首个版本，自动设置为激活状态
- 后续版本需要手动调用激活接口

---

#### 1.2 获取指定契约版本

**端点**: `GET /api/contracts/versions/{version_id}`

**描述**: 根据版本ID获取完整的契约信息

**路径参数**:
- `version_id` (integer): 契约版本ID

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "获取成功",
  "data": {
    "id": 1,
    "name": "market-api",
    "version": "1.0.0",
    "spec": { /* OpenAPI规范 */ },
    "commit_hash": "abc123def456",  # pragma: allowlist secret
    "author": "developer-team",
    "description": "初始版本",
    "tags": ["v1", "stable"],
    "is_active": true,
    "created_at": "2025-12-29T10:30:00Z"
  },
  "request_id": "req_123456"
}
```

**错误响应** (404 Not Found):
```json
{
  "code": "CONTRACT_VERSION_NOT_FOUND",
  "message": "契约版本不存在",
  "data": null,
  "request_id": "req_123456"
}
```

---

#### 1.3 获取当前激活版本

**端点**: `GET /api/contracts/versions/{name}/active`

**描述**: 获取指定契约的当前激活版本

**路径参数**:
- `name` (string): 契约名称 (如: market-api)

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "获取成功",
  "data": {
    "id": 3,
    "name": "market-api",
    "version": "1.2.0",
    "spec": { /* OpenAPI规范 */ },
    "commit_hash": "xyz789abc012",
    "author": "developer-team",
    "description": "新增技术指标接口",
    "tags": ["v1", "stable"],
    "is_active": true,
    "created_at": "2025-12-29T14:20:00Z"
  },
  "request_id": "req_123456"
}
```

**使用场景**:
- 前端获取最新的API契约
- API网关加载当前生效的契约
- 文档站点显示最新API规范

---

#### 1.4 列出契约版本

**端点**: `GET /api/contracts/versions`

**描述**: 分页查询契约版本历史

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| name | string | ❌ | null | 按契约名称过滤 |
| limit | integer | ❌ | 50 | 每页数量 |
| offset | integer | ❌ | 0 | 偏移量 |

**请求示例**:
```
GET /api/contracts/versions?name=market-api&limit=10&offset=0
```

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "market-api",
      "version": "1.0.0",
      "spec": { /* OpenAPI规范 */ },
      "commit_hash": "abc123",
      "author": "developer-team",
      "description": "初始版本",
      "tags": ["v1"],
      "is_active": false,
      "created_at": "2025-12-29T10:00:00Z"
    },
    {
      "id": 2,
      "name": "market-api",
      "version": "1.1.0",
      "spec": { /* OpenAPI规范 */ },
      "commit_hash": "def456",
      "author": "developer-team",
      "description": "新增行情数据接口",
      "tags": ["v1"],
      "is_active": false,
      "created_at": "2025-12-29T12:00:00Z"
    }
  ],
  "request_id": "req_123456"
}
```

---

#### 1.5 更新契约版本

**端点**: `PUT /api/contracts/versions/{version_id}`

**描述**: 更新契约版本的元数据 (不修改spec内容)

**路径参数**:
- `version_id` (integer): 契约版本ID

**请求体**:
```json
{
  "description": "更新版本说明",
  "tags": ["v1", "stable", "verified"]
}
```

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "契约版本更新成功",
  "data": {
    "id": 1,
    "name": "market-api",
    "version": "1.0.0",
    "spec": { /* OpenAPI规范 (未修改) */ },
    "commit_hash": "abc123",
    "author": "developer-team",
    "description": "更新版本说明",
    "tags": ["v1", "stable", "verified"],
    "is_active": true,
    "created_at": "2025-12-29T10:30:00Z"
  },
  "request_id": "req_123456"
}
```

**注意**: 此接口仅更新元数据，不修改OpenAPI规范内容。如需修改spec，请创建新版本。

---

#### 1.6 激活契约版本

**端点**: `POST /api/contracts/versions/{version_id}/activate`

**描述**: 激活指定版本，同时停用同契约的其他版本

**路径参数**:
- `version_id` (integer): 契约版本ID

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "版本已激活",
  "data": {
    "success": true,
    "message": "版本已激活"
  },
  "request_id": "req_123456"
}
```

**激活流程**:
1. 将该契约的所有版本设置为 `is_active=False`
2. 将指定版本设置为 `is_active=True`
3. 记录激活操作到审计日志

---

#### 1.7 删除契约版本

**端点**: `DELETE /api/contracts/versions/{version_id}`

**描述**: 删除指定契约版本 (谨慎操作)

**路径参数**:
- `version_id` (integer): 契约版本ID

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "版本已删除",
  "data": {
    "success": true,
    "message": "版本已删除"
  },
  "request_id": "req_123456"
}
```

**删除限制**:
- 不能删除当前激活的版本
- 删除操作不可逆，建议先备份

---

### 2. 契约列表 (Contract List)

#### 2.1 列出所有契约

**端点**: `GET /api/contracts/contracts`

**描述**: 获取系统中所有契约及其元数据

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "查询成功",
  "data": {
    "contracts": [
      {
        "name": "market-api",
        "active_version": "1.2.0",
        "total_versions": 5,
        "last_updated": "2025-12-29T14:20:00Z",
        "tags": ["stable", "v1"]
      },
      {
        "name": "trade-api",
        "active_version": "2.0.0",
        "total_versions": 3,
        "last_updated": "2025-12-28T16:45:00Z",
        "tags": ["stable", "v2"]
      }
    ],
    "total": 2
  },
  "request_id": "req_123456"
}
```

**使用场景**:
- 查看系统中所有契约的概览
- 发现需要更新的契约
- 监控契约版本演进

---

### 3. 契约差异检测 (Diff Detection)

#### 3.1 对比契约版本

**端点**: `POST /api/contracts/diff`

**描述**: 对比两个契约版本的差异，自动分类破坏性/非破坏性变更

**请求体**:
```json
{
  "from_version_id": 1,
  "to_version_id": 2
}
```

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "差异检测完成",
  "data": {
    "from_version": "1.0.0",
    "to_version": "1.1.0",
    "total_changes": 15,
    "breaking_changes": 2,
    "non_breaking_changes": 13,
    "diffs": [
      {
        "path": "paths./api/market/symbols",
        "type": "breaking",
        "change": "removed",
        "message": "删除API端点: GET /api/market/symbols",
        "detail": {
          "old_value": { /* 端点定义 */ },
          "new_value": null
        }
      },
      {
        "path": "paths./api/market/quote",
        "type": "non-breaking",
        "change": "added",
        "message": "新增API端点: GET /api/market/quote",
        "detail": {
          "old_value": null,
          "new_value": { /* 端点定义 */ }
        }
      },
      {
        "path": "components.schemas.StockSymbol.properties.symbol",
        "type": "non-breaking",
        "change": "modified",
        "message": "修改字段: symbol (string → string, maxLength: 10)",
        "detail": {
          "old_value": { "type": "string" },
          "new_value": { "type": "string", "maxLength": 10 }
        }
      }
    ],
    "summary": "检测到2个破坏性变更和13个非破坏性变更。主要变更: 删除了 /api/market/symbols 端点，新增了 /api/market/quote 端点。"
  },
  "request_id": "req_123456"
}
```

**差异类型**:

| 类型 | 说明 | 示例 |
|------|------|------|
| breaking | 破坏性变更 | 删除端点、删除必填字段、修改字段类型 |
| non-breaking | 非破坏性变更 | 新增端点、新增可选字段、添加描述 |

**破坏性变更检测规则**:
- 删除API端点
- 删除HTTP方法
- 删除Schema定义
- 删除必填请求参数
- 删除响应字段
- 修改字段类型 (不兼容)
- 添加必填请求参数

**使用场景**:
- 发布前审查版本变更
- 评估升级风险
- 生成变更日志
- CI/CD流水线质量门禁

---

### 4. 契约验证 (Contract Validation)

#### 4.1 验证OpenAPI规范

**端点**: `POST /api/contracts/validate`

**描述**: 验证OpenAPI规范的正确性和最佳实践

**请求体**:
```json
{
  "spec": {
    "openapi": "3.0.0",
    "info": {
      "title": "Market API",
      "version": "1.0.0"
    },
    "paths": {
      "/api/market/symbols": {
        "get": {
          "summary": "获取股票列表",
          "responses": {
            "200": {
              "description": "成功",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/StockList"
                  }
                }
              }
            }
          }
        }
      }
    },
    "components": {
      "schemas": {
        "StockList": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "symbol": {
                "type": "string"
              },
              "name": {
                "type": "string"
              }
            }
          }
        }
      }
    }
  },
  "check_breaking_changes": true,
  "compare_to_version_id": 1
}
```

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "验证完成",
  "data": {
    "is_valid": true,
    "errors": 0,
    "warnings": 2,
    "validation_results": [
      {
        "level": "error",
        "category": "structure",
        "message": "OpenAPI规范缺少必需字段: info.title",
        "path": "info"
      },
      {
        "level": "warning",
        "category": "best_practices",
        "message": "建议为所有端点添加operationId",
        "path": "paths./api/market/symbols.get"
      },
      {
        "level": "warning",
        "category": "best_practices",
        "message": "建议为响应添加示例",
        "path": "paths./api/market/symbols.get.responses.200"
      }
    ],
    "breaking_changes": [
      {
        "path": "paths./api/market/symbols",
        "change": "removed",
        "message": "删除API端点"
      }
    ]
  },
  "request_id": "req_123456"
}
```

**验证级别**:

| 级别 | 说明 | 是否阻断 |
|------|------|----------|
| error | 严重错误 (规范不合法) | ✅ 是 |
| warning | 警告 (不符合最佳实践) | ❌ 否 |

**验证类别**:

1. **structure**: 结构验证
   - 必需字段检查
   - 数据类型验证
   - 引用完整性

2. **openapi**: OpenAPI规范验证
   - 使用prance库进行深度验证
   - 检测Schema引用错误
   - 验证路径和HTTP方法

3. **breaking_changes**: 破坏性变更检测
   - 对比指定版本
   - 分类破坏性/非破坏性变更

4. **best_practices**: 最佳实践检查
   - operationId完整性
   - 描述和示例完整性
   - 响应码规范性

**使用场景**:
- 提交前验证契约
- CI/CD流水线质量检查
- 代码审查辅助工具

---

### 5. 契约同步 (Contract Sync)

#### 5.1 同步契约

**端点**: `POST /api/contracts/sync`

**描述**: 同步契约 (代码 → 数据库 或 数据库 → 代码)

**请求体**:
```json
{
  "name": "market-api",
  "source_path": "/path/to/openapi.yaml",
  "direction": "code-to-db",
  "version": "1.3.0",
  "commit": true
}
```

**响应** (200 OK):
```json
{
  "code": "SUCCESS",
  "message": "同步完成",
  "data": {
    "sync_id": "sync-abc123",
    "status": "completed",
    "results": [
      {
        "file": "/path/to/openapi.yaml",
        "action": "created",
        "version": "1.3.0",
        "success": true
      }
    ],
    "started_at": "2025-12-29T15:00:00Z",
    "completed_at": "2025-12-29T15:00:05Z"
  },
  "request_id": "req_123456"
}
```

**同步方向**:

| 方向 | 说明 | 使用场景 |
|------|------|----------|
| code-to-db | 代码契约 → 数据库 | 开发完成后同步契约 |
| db-to-code | 数据库 → 代码契约 | 从数据库生成契约文件 |
| bidirectional | 双向同步 (谨慎使用) | 合并契约变更 |

**同步流程** (code-to-db):
1. 读取源文件 (OpenAPI YAML/JSON)
2. 验证规范合法性
3. 检测与当前激活版本的差异
4. 创建新版本
5. 可选: 提交到Git仓库

**注意**: 当前版本返回模拟结果，实际同步逻辑需根据项目需求实现。

---

## 🔧 错误码参考

### 通用错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| SUCCESS | 200 | 操作成功 |
| VALIDATION_ERROR | 422 | 请求参数验证失败 |
| NOT_FOUND | 404 | 资源不存在 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 契约管理专属错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| CONTRACT_VERSION_NOT_FOUND | 404 | 契约版本不存在 |
| CONTRACT_NOT_FOUND | 404 | 契约不存在或无激活版本 |
| CONTRACT_ALREADY_EXISTS | 409 | 契约版本已存在 |
| CONTRACT_VALIDATION_FAILED | 422 | 契约验证失败 |
| CONTRACT_DELETE_ACTIVE_VERSION | 409 | 不能删除激活版本 |
| CONTRACT_DIFF_FAILED | 500 | 差异检测失败 |
| CONTRACT_SYNC_FAILED | 500 | 同步失败 |

---

## 📖 使用示例

### 示例1: 完整的契约发布流程

```bash
# 1. 创建契约版本
curl -X POST http://localhost:8020/api/contracts/versions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "market-api",
    "version": "1.0.0",
    "spec": { /* OpenAPI规范 */ },
    "author": "developer-team",
    "description": "初始版本",
    "tags": ["v1", "stable"]
  }'

# 2. 获取版本ID (假设返回 id=1)
VERSION_ID=1

# 3. 验证契约 (可选)
curl -X POST http://localhost:8020/api/contracts/validate \
  -H "Content-Type: application/json" \
  -d '{
    "spec": { /* OpenAPI规范 */ },
    "check_breaking_changes": false
  }'

# 4. 激活版本
curl -X POST http://localhost:8020/api/contracts/versions/${VERSION_ID}/activate

# 5. 验证激活状态
curl http://localhost:8020/api/contracts/versions/market-api/active
```

---

### 示例2: 版本升级与差异检测

```bash
# 1. 创建新版本 (1.1.0)
curl -X POST http://localhost:8020/api/contracts/versions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "market-api",
    "version": "1.1.0",
    "spec": { /* 修改后的OpenAPI规范 */ },
    "description": "新增行情数据接口"
  }'

# 2. 对比版本差异
curl -X POST http://localhost:8020/api/contracts/diff \
  -H "Content-Type: application/json" \
  -d '{
    "from_version_id": 1,
    "to_version_id": 2
  }'

# 3. 检查是否有破坏性变更
# 如果 breaking_changes > 0，需要评估影响

# 4. 激活新版本 (如果差异可接受)
curl -X POST http://localhost:8020/api/contracts/versions/2/activate
```

---

### 示例3: Python客户端封装

```python
import requests
from typing import Dict, Any, List

class ContractManagementClient:
    """API契约管理客户端"""

    def __init__(self, base_url: str = "http://localhost:8020"):
        self.base_url = base_url
        self.api_prefix = "/api/contracts"

    def create_version(
        self,
        name: str,
        version: str,
        spec: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """创建契约版本"""
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/versions",
            json={
                "name": name,
                "version": version,
                "spec": spec,
                **kwargs
            }
        )
        response.raise_for_status()
        return response.json()

    def get_active_version(self, name: str) -> Dict[str, Any]:
        """获取当前激活版本"""
        response = requests.get(
            f"{self.base_url}{self.api_prefix}/versions/{name}/active"
        )
        response.raise_for_status()
        return response.json()

    def compare_versions(
        self,
        from_version_id: int,
        to_version_id: int
    ) -> Dict[str, Any]:
        """对比两个版本"""
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/diff",
            json={
                "from_version_id": from_version_id,
                "to_version_id": to_version_id
            }
        )
        response.raise_for_status()
        return response.json()

    def validate_spec(
        self,
        spec: Dict[str, Any],
        check_breaking_changes: bool = True,
        compare_to_version_id: int = None
    ) -> Dict[str, Any]:
        """验证OpenAPI规范"""
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/validate",
            json={
                "spec": spec,
                "check_breaking_changes": check_breaking_changes,
                "compare_to_version_id": compare_to_version_id
            }
        )
        response.raise_for_status()
        return response.json()

# 使用示例
client = ContractManagementClient()

# 创建版本
with open("openapi.yaml", "r") as f:
    spec = yaml.safe_load(f)

result = client.create_version(
    name="market-api",
    version="1.0.0",
    spec=spec,
    author="developer-team",
    description="初始版本"
)

version_id = result["data"]["id"]
print(f"创建版本成功，ID: {version_id}")

# 验证规范
validation = client.validate_spec(spec, check_breaking_changes=False)
if validation["data"]["is_valid"]:
    print("契约验证通过")
else:
    print(f"验证失败: {validation['data']['errors']} 个错误")
```

---

## 🎯 最佳实践

### 1. 版本管理

✅ **推荐做法**:
- 遵循语义化版本规范 (SemVer)
- 为每个版本编写清晰的描述
- 使用标签标记版本状态 (stable, beta, deprecated)
- 定期清理过期的旧版本

❌ **避免**:
- 随意使用版本号
- 修改已发布的版本内容
- 删除仍在使用的旧版本

---

### 2. 变更管理

✅ **推荐做法**:
- 发布前运行差异检测
- 评估破坏性变更的影响
- 提前通知客户端开发者
- 维护版本升级指南

❌ **避免**:
- 跳过差异检测直接发布
- 忽略破坏性变更警告
- 频繁修改公共API

---

### 3. 契约验证

✅ **推荐做法**:
- 提交前验证契约
- 在CI/CD流水线中集成验证
- 修复所有error级别的错误
- 逐步优化warning级别的警告

❌ **避免**:
- 跳过验证直接发布
- 忽略验证错误
- 使用不规范的OpenAPI语法

---

### 4. 团队协作

✅ **推荐做法**:
- 建立契约审查流程
- 使用Git commit hash追溯变更
- 为不同环境维护不同版本
- 定期同步契约与代码

❌ **避免**:
- 个人随意修改契约
- 不通知团队的变更
- 契约与代码脱节

---

## 🔐 权限与安全

### 访问控制

当前版本未实现权限控制，生产环境建议添加:

1. **认证机制**: JWT或API Key
2. **权限分级**:
   - 读取权限: 所有开发者
   - 创建/更新权限: API开发者
   - 删除/激活权限: 技术负责人
3. **审计日志**: 记录所有敏感操作

---

## 📊 数据库Schema

### contract_versions表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 主键 |
| name | string(100) | 契约名称 (索引) |
| version | string(50) | 版本号 |
| spec | json | OpenAPI规范内容 |
| commit_hash | string(100) | Git commit hash |
| author | string(100) | 作者 |
| description | text | 版本描述 |
| tags | json | 版本标签 |
| is_active | boolean | 是否激活 |
| created_at | datetime | 创建时间 |

### contract_diffs表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 主键 |
| from_version_id | integer | 源版本ID |
| to_version_id | integer | 目标版本ID |
| diffs | json | 差异详情 |
| summary | text | 差异摘要 |
| created_at | datetime | 创建时间 |

### contract_validations表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 主键 |
| version_id | integer | 版本ID |
| is_valid | boolean | 是否通过验证 |
| errors | integer | 错误数 |
| warnings | integer | 警告数 |
| results | json | 验证结果 |
| created_at | datetime | 创建时间 |

---

## 🚀 未来规划

### Phase 4.2: CLI工具 (T2.11)
- 命令行工具快速操作契约
- 批量导入/导出契约
- 自动生成变更日志

### Phase 4.3: CI/CD集成 (T2.12)
- GitHub Actions工作流
- 自动化契约验证
- 契约变更告警通知

### Phase 4.4: 前端集成 (T2.13-T2.14)
- TypeScript类型定义生成
- Service适配器层
- Swagger UI集成

---

## 📞 支持与反馈

### 问题反馈
- GitHub Issues: [项目地址]
- 邮件: support@example.com

### 文档更新
- 文档版本: v1.0.0
- 最后更新: 2025-12-29

---

**文档作者**: Claude Code (AI Assistant)
**项目**: MyStocks API契约管理平台
**版本**: Phase 4 T2.10
