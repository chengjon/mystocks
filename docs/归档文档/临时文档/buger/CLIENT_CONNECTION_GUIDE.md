# BUGer 客户端连接指南

## 概述

本指南帮助您正确配置和验证客户端与 BUGer 服务器的连接，避免端口不匹配等常见问题。

## 快速检查清单

在开始集成之前，请完成以下检查：

- [ ] 确认 BUGer 服务器运行端口
- [ ] 验证客户端配置的 URL 和端口
- [ ] 使用健康检查验证连接
- [ ] 使用连接验证端点确认配置

## 1. 确认服务器端口

### 自动端口选择机制

BUGer v1.1.0 支持**自动端口选择**：

- **默认端口范围**：3003-3013
- **自动重试**：如果首选端口被占用，自动尝试下一个端口
- **智能选择**：从 `.env` 配置的 PORT 开始尝试，如果未设置则从 3003 开始

### 查看服务器启动日志

当 BUGer 服务器启动时，会显示自动选择的端口：

```bash
🔍 在端口范围 3003-3013 内查找可用端口...
⚠️  端口 3003 已被占用，尝试下一个端口...
✓ 成功绑定端口 3004

╔════════════════════════════════════════╗
║   🎉 BUGer API Server Started          ║
║   Listening on: http://localhost:3004   ║
╚════════════════════════════════════════╝

📊 System Status:
  ✓ Port: 3004 (Auto-selected from 3003-3013)

⚠️  客户端配置提醒：
   请确保客户端 BUGER_API_URL 配置为: http://localhost:3004/api
   或使用健康检查验证连接: curl http://localhost:3004/health
```

### 查看配置文件

```bash
# 查看 backend/.env 文件
cat backend/.env | grep PORT

# 输出示例（首选端口，可能会被自动调整）
PORT=3003
```

### 端口范围完全占用时的处理

如果端口范围 3003-3013 全部被占用，服务器会报错并退出：

```bash
❌ 所有端口 (3003-3013) 都已被占用！请释放端口或修改端口范围。

💡 解决方案：
   1. 释放占用的端口：
      - Linux/Mac: lsof -ti:3003 | xargs kill -9
      - Windows: netstat -ano | findstr :3003 然后 taskkill /PID <PID> /F
   2. 修改代码中的端口范围（src/index.js）：
      const PORT_START = 3003;
      const PORT_END = 3020;  // 扩大范围
```

## 2. 客户端配置

### 配置示例

在客户端项目的 `.env` 文件中：

```bash
# BUGer 服务配置
BUGER_API_URL=http://localhost:3003/api
BUGER_API_KEY=sk_your_api_key_here
PROJECT_ID=your_project_id
```

### 配置检查清单

| 配置项 | 说明 | 示例 |
|--------|------|------|
| BUGER_API_URL | BUGer API 基础URL（**必须包含正确的端口**） | `http://localhost:3003/api` |
| BUGER_API_KEY | 项目 API Key | `sk_xxxxxxxxxxxxx` |
| PROJECT_ID | 项目标识符 | `my-project` |

⚠️ **常见错误：**
- ❌ `http://localhost:3050/api` - 端口错误（旧版本端口）
- ❌ `http://localhost:3003` - 缺少 `/api` 路径
- ✅ `http://localhost:3003/api` - 正确配置（默认端口）

💡 **注意**：由于自动端口选择机制，实际端口可能是 3003-3013 范围内的任何端口。建议使用健康检查验证实际端口。

## 3. 验证连接

### 方法 1: 健康检查（推荐）

使用健康检查端点验证服务器状态和配置：

```bash
curl http://localhost:3003/health
```

**响应示例：**

```json
{
  "status": "ok",
  "timestamp": "2025-10-31T10:00:00.000Z",
  "server": {
    "name": "BUGer API",
    "version": "1.1.0",
    "port": 3003,
    "baseUrl": "http://localhost:3003/api",
    "environment": "development"
  },
  "uptime": 3600,
  "memory": {
    "rss": "128MB",
    "heapUsed": "64MB",
    "heapTotal": "96MB"
  },
  "services": {
    "mongodb": {
      "status": "connected",
      "readyState": 1
    },
    "redis": {
      "status": "connected"
    }
  },
  "monitoring": {
    "activeProjects": 2,
    "totalRequests": 150,
    "requestsPerSecond": "2.50"
  }
}
```

**关键信息：**
- `server.port` - 服务器实际运行端口
- `server.baseUrl` - 客户端应该使用的 API URL
- `services` - 数据库连接状态

### 方法 2: 连接验证端点（高级）

使用专用的连接验证端点，自动检查配置匹配：

```bash
curl -X POST http://localhost:3003/health/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "apiUrl": "http://localhost:3003/api",
    "port": 3003
  }'
```

**响应示例（配置正确）：**

```json
{
  "success": true,
  "timestamp": "2025-10-31T10:00:00.000Z",
  "server": {
    "name": "BUGer API",
    "version": "1.1.0",
    "port": 3003,
    "expectedBaseUrl": "http://localhost:3003/api"
  },
  "client": {
    "providedUrl": "http://localhost:3003/api",
    "providedPort": 3003
  },
  "project": {
    "projectId": "my-project",
    "projectName": "MyProject",
    "authenticated": true
  },
  "warnings": [],
  "recommendations": []
}
```

**响应示例（端口不匹配）：**

```json
{
  "success": true,
  "timestamp": "2025-10-31T10:00:00.000Z",
  "server": {
    "name": "BUGer API",
    "version": "1.1.0",
    "port": 3004,
    "expectedBaseUrl": "http://localhost:3004/api"
  },
  "client": {
    "providedUrl": "http://localhost:3003/api",
    "providedPort": 3003
  },
  "project": null,
  "warnings": [
    "客户端配置的端口与服务器不匹配。服务器运行在端口 3004，但客户端配置为 http://localhost:3003/api"
  ],
  "recommendations": [
    "请将客户端 BUGER_API_URL 修改为: http://localhost:3004/api"
  ]
}
```

### 方法 3: 测试 BUG 上报

完整的端到端测试：

```bash
curl -X POST http://localhost:3003/api/bugs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "errorCode": "TEST_001",
    "title": "连接测试",
    "message": "测试客户端连接",
    "severity": "low",
    "stackTrace": "Test stack trace"
  }'
```

**成功响应：**

```json
{
  "success": true,
  "data": {
    "bugId": "bug_xxxxxxxxxxxxx",
    "projectId": "my-project",
    "status": "OPEN",
    "createdAt": "2025-10-31T10:00:00.000Z"
  },
  "message": "Bug reported successfully"
}
```

如果看到此响应，说明连接配置完全正确！

## 4. 客户端集成代码

### Node.js 客户端示例

```javascript
// buger-client.js
const axios = require('axios');

class BugerClient {
  constructor(config) {
    this.apiUrl = config.apiUrl || process.env.BUGER_API_URL;
    this.apiKey = config.apiKey || process.env.BUGER_API_KEY;
    this.projectId = config.projectId || process.env.PROJECT_ID;

    if (!this.apiUrl || !this.apiKey) {
      throw new Error('BUGER_API_URL and BUGER_API_KEY are required');
    }
  }

  // 验证连接配置
  async verifyConnection() {
    try {
      const response = await axios.post(
        `${this.apiUrl.replace('/api', '')}/health/verify`,
        {
          apiUrl: this.apiUrl,
          port: new URL(this.apiUrl).port || 80,
        },
        {
          headers: {
            'X-API-Key': this.apiKey,
            'Content-Type': 'application/json',
          },
        }
      );

      const result = response.data;

      // 检查警告
      if (result.warnings && result.warnings.length > 0) {
        console.warn('⚠️  BUGer 连接配置警告：');
        result.warnings.forEach((warning) => console.warn(`   - ${warning}`));

        if (result.recommendations && result.recommendations.length > 0) {
          console.warn('\n💡 建议：');
          result.recommendations.forEach((rec) => console.warn(`   - ${rec}`));
        }

        return false;
      }

      console.log('✅ BUGer 连接验证成功！');
      if (result.project) {
        console.log(`   项目: ${result.project.projectName} (${result.project.projectId})`);
      }
      return true;
    } catch (error) {
      console.error('❌ BUGer 连接验证失败：', error.message);
      if (error.response) {
        console.error('   状态码:', error.response.status);
        console.error('   响应:', error.response.data);
      }
      return false;
    }
  }

  // 上报 BUG
  async reportBug(bugData) {
    try {
      const response = await axios.post(`${this.apiUrl}/bugs`, bugData, {
        headers: {
          'X-API-Key': this.apiKey,
          'Content-Type': 'application/json',
        },
      });
      return response.data;
    } catch (error) {
      console.error('BUG 上报失败:', error.message);
      throw error;
    }
  }
}

// 使用示例
async function main() {
  const client = new BugerClient({
    apiUrl: 'http://localhost:3003/api',
    apiKey: 'sk_your_api_key',
    projectId: 'my-project',
  });

  // 首次连接时验证配置
  const isValid = await client.verifyConnection();

  if (isValid) {
    // 上报测试 BUG
    await client.reportBug({
      errorCode: 'TEST_001',
      title: '测试BUG',
      message: '这是一个测试',
      severity: 'low',
      stackTrace: 'Test stack',
    });
  }
}

module.exports = BugerClient;
```

### Python 客户端示例

```python
# buger_client.py
import os
import requests
from typing import Dict, Optional

class BugerClient:
    def __init__(self, api_url: str = None, api_key: str = None, project_id: str = None):
        self.api_url = api_url or os.getenv('BUGER_API_URL')
        self.api_key = api_key or os.getenv('BUGER_API_KEY')
        self.project_id = project_id or os.getenv('PROJECT_ID')

        if not self.api_url or not self.api_key:
            raise ValueError('BUGER_API_URL and BUGER_API_KEY are required')

    def verify_connection(self) -> bool:
        """验证连接配置"""
        try:
            base_url = self.api_url.replace('/api', '')
            response = requests.post(
                f'{base_url}/health/verify',
                json={
                    'apiUrl': self.api_url,
                    'port': self._extract_port(self.api_url)
                },
                headers={
                    'X-API-Key': self.api_key,
                    'Content-Type': 'application/json'
                }
            )

            result = response.json()

            # 检查警告
            if result.get('warnings'):
                print('⚠️  BUGer 连接配置警告：')
                for warning in result['warnings']:
                    print(f'   - {warning}')

                if result.get('recommendations'):
                    print('\n💡 建议：')
                    for rec in result['recommendations']:
                        print(f'   - {rec}')

                return False

            print('✅ BUGer 连接验证成功！')
            if result.get('project'):
                print(f"   项目: {result['project']['projectName']} ({result['project']['projectId']})")
            return True

        except Exception as e:
            print(f'❌ BUGer 连接验证失败：{str(e)}')
            return False

    def report_bug(self, bug_data: Dict) -> Optional[Dict]:
        """上报 BUG"""
        try:
            response = requests.post(
                f'{self.api_url}/bugs',
                json=bug_data,
                headers={
                    'X-API-Key': self.api_key,
                    'Content-Type': 'application/json'
                }
            )
            return response.json()
        except Exception as e:
            print(f'BUG 上报失败: {str(e)}')
            raise

    @staticmethod
    def _extract_port(url: str) -> int:
        """从 URL 中提取端口"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.port or (443 if parsed.scheme == 'https' else 80)

# 使用示例
if __name__ == '__main__':
    client = BugerClient(
        api_url='http://localhost:3003/api',
        api_key='sk_your_api_key',
        project_id='my-project'
    )

    # 首次连接时验证配置
    if client.verify_connection():
        # 上报测试 BUG
        client.report_bug({
            'errorCode': 'TEST_001',
            'title': '测试BUG',
            'message': '这是一个测试',
            'severity': 'low',
            'stackTrace': 'Test stack'
        })
```

## 5. 常见问题排查

### 问题 1: 连接超时

**症状：** `ECONNREFUSED` 或连接超时

**原因：**
- BUGer 服务器未启动
- 端口配置错误
- 防火墙阻止

**解决方案：**
```bash
# 1. 检查 BUGer 是否运行
curl http://localhost:3003/health

# 2. 检查端口是否监听（检查 3003-3013 范围）
netstat -an | grep -E "300[3-9]|301[0-3]"  # Linux/Mac
netstat -an | findstr /R "300[3-9] 301[0-3]"  # Windows

# 3. 启动 BUGer 服务器
cd backend && npm run dev
```

### 问题 2: 401 Unauthorized

**症状：** API 返回 401 错误

**原因：**
- API Key 缺失或错误
- API Key 格式不正确
- 项目未在数据库中注册

**解决方案：**
```bash
# 验证 API Key
curl http://localhost:3003/health/verify \
  -H "X-API-Key: your_api_key"

# 检查响应中的 warnings 字段
```

### 问题 3: 端口不匹配

**症状：** 提交到错误的端口，服务器无响应

**原因：**
- 客户端配置的端口与服务器不一致
- 服务器端口在启动后改变

**解决方案：**
1. 查看服务器启动日志确认端口
2. 使用健康检查验证：`curl http://localhost:PORT/health`
3. 更新客户端配置
4. 使用连接验证端点确认

## 6. 最佳实践

### 应用启动时验证连接

```javascript
// 在应用启动时验证 BUGer 连接
async function initializeBuger() {
  const client = new BugerClient({...});

  const isValid = await client.verifyConnection();

  if (!isValid) {
    console.error('❌ BUGer 配置无效，BUG上报功能将不可用');
    console.error('   请检查 BUGER_API_URL 和 BUGER_API_KEY 配置');
    // 可以选择继续运行但禁用 BUG 上报，或者退出
  } else {
    console.log('✅ BUGer 已就绪');
  }
}

initializeBuger();
```

### 定期健康检查

```javascript
// 每5分钟检查一次连接
setInterval(async () => {
  try {
    await axios.get(`${process.env.BUGER_API_URL.replace('/api', '')}/health`);
  } catch (error) {
    console.warn('⚠️  BUGer 健康检查失败，服务可能不可用');
  }
}, 5 * 60 * 1000);
```

### 优雅降级

```javascript
async function reportBug(bugData) {
  try {
    await client.reportBug(bugData);
  } catch (error) {
    // BUGer 不可用时，记录到本地日志
    console.error('Failed to report to BUGer:', error.message);
    logToFile(bugData); // 备用方案
  }
}
```

## 总结

✅ **连接前检查清单：**
1. 确认 BUGer 服务器运行端口（查看启动日志）
2. 配置正确的客户端 URL（包含端口和 /api 路径）
3. 使用 `/health` 验证服务器状态
4. 使用 `/health/verify` 验证配置匹配
5. 在应用启动时验证连接

📚 **相关文档：**
- `backend/README.md` - 服务器配置和启动
- `REALTIME_MONITORING.md` - 实时监控功能
- API 端点文档

---

**文档版本：** 1.0
**最后更新：** 2025-10-31
**维护者：** BUGer Team
