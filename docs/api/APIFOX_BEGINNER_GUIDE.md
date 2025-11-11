# Apifox 新手完全指南 - 从零开始测试 API

## 📚 目录

1. [什么是 API 测试](#什么是-api-测试)
2. [Apifox 基础界面介绍](#apifox-基础界面介绍)
3. [第一次测试 - 健康检查](#第一次测试---健康检查)
4. [配置环境变量](#配置环境变量)
5. [测试需要认证的 API](#测试需要认证的-api)
6. [常见问题和解决方案](#常见问题和解决方案)
7. [进阶技巧](#进阶技巧)

---

## 什么是 API 测试？

### 简单理解

**API** 就像餐厅的服务员：
- 你（前端/客户端）告诉服务员你要什么菜（发送请求）
- 服务员去厨房（后端服务器）拿菜
- 服务员把菜端给你（返回响应）

**API 测试** 就是检查这个服务员是否：
- 听懂了你的要求？（请求格式正确）
- 拿到了正确的菜？（响应数据正确）
- 速度够快？（性能测试）

### MyStocks 项目的 API

我们的项目有 **218 个 API**，分为几大类：
- 📊 **市场数据**: 获取股票行情、K线、资金流向
- 🔐 **认证**: 登录、登出
- 📋 **自选股**: 管理你关注的股票
- 🤖 **策略**: 量化交易策略
- ... 等等

---

## Apifox 基础界面介绍

### 打开项目

1. 访问: https://app.apifox.com/project/7376246
2. 如果没有账号，先注册一个（免费）
3. 登录后会看到主界面

### 主界面布局

```
┌─────────────────────────────────────────────────────────┐
│  [项目名]  [环境选择器: 未选择]  [设置]  [帮助]        │
├───────────────┬─────────────────────────────────────────┤
│               │                                         │
│  [左侧边栏]   │           [中间主区域]                  │
│               │                                         │
│  📁 接口目录   │  显示选中的 API 详情                    │
│  ├ 系统管理   │  - 请求参数                             │
│  ├ 认证授权   │  - 请求体                               │
│  ├ 市场数据   │  - 响应示例                             │
│  └ ...       │  - [发送] 按钮                          │
│               │                                         │
│  📊 测试管理   │                                         │
│  🎭 Mock     │                                         │
│  📖 文档      │                                         │
│               │                                         │
├───────────────┴─────────────────────────────────────────┤
│                 [底部响应区域]                          │
│  显示 API 响应结果、日志等                              │
└─────────────────────────────────────────────────────────┘
```

---

## 第一次测试 - 健康检查

### 为什么从健康检查开始？

**健康检查** 是最简单的 API：
- ✅ 不需要登录
- ✅ 不需要参数
- ✅ 只要服务器运行就能成功
- ✅ 最适合新手入门

### 操作步骤（详细图文）

#### 步骤 1: 配置服务器地址（重要！）

**在测试任何 API 之前，必须先配置服务器地址**

1. **点击顶部的环境选择器**
   ```
   [环境选择器: 未选择] ← 点这里
   ```

2. **新建环境**
   - 点击 "+" 按钮或 "新建环境"
   - 环境名称输入: `本地开发`
   - 点击 "确定"

3. **配置环境变量**

   在变量列表中添加：

   | 变量名 | 初始值 | 当前值 | 说明 |
   |--------|--------|--------|------|
   | base_url | `http://localhost:8000` | `http://localhost:8000` | 服务器地址 |
   | auth_token | (留空) | (留空) | JWT认证令牌 |
   | csrf_token | (留空) | (留空) | CSRF令牌 |

4. **保存并选择环境**
   - 点击 "保存"
   - 在环境选择器中选择 "本地开发"

#### 步骤 2: 找到健康检查 API

1. 在左侧边栏找到 **📁 系统管理** 目录
2. 点击展开
3. 找到 **GET /health - 健康检查**
4. 点击它

#### 步骤 3: 查看 API 详情

点击后，中间区域会显示 API 详情：

```
GET /health
健康检查

【基础信息】
请求方式: GET
请求路径: /health
完整URL: {{base_url}}/health  ← 注意这里会自动替换成 http://localhost:8000/health

【请求参数】
无需参数 ✅

【请求头】
无特殊要求 ✅

【响应示例】
200 OK - 成功
{
  "status": "healthy",
  "timestamp": 1762776837.329407,
  "service": "mystocks-web-api"
}
```

#### 步骤 4: 发送请求

1. 直接点击右上角的蓝色 **[发送]** 按钮
2. 等待 1-2 秒

#### 步骤 5: 查看响应结果

在底部响应区域，您会看到：

**成功的响应** ✅:
```
状态码: 200 OK  ← 绿色显示
响应时间: 123 ms
响应大小: 98 bytes

【响应体】(Body 标签页)
{
  "status": "healthy",
  "timestamp": 1762776837.329407,
  "service": "mystocks-web-api"
}
```

**如果看到这个，恭喜！您已经成功测试了第一个 API！** 🎉

---

## 配置环境变量

### 为什么需要环境变量？

想象一下：
- 您有 218 个 API
- 每个 API 的 URL 都是 `http://localhost:8000/api/...`
- 如果服务器地址改了（比如从本地变成生产环境）
- 您需要修改 218 次！😱

**使用环境变量后**：
- 只写一次地址: `{{base_url}}`
- 所有 API 都用这个变量
- 改地址？只需要改一个地方！😎

### 环境变量的作用

| 变量名 | 用途 | 何时设置 |
|--------|------|----------|
| `base_url` | 服务器地址 | 第一次配置 |
| `auth_token` | 登录后的身份令牌 | 登录成功后 |
| `csrf_token` | 防攻击令牌 | 每次需要写数据时 |

### 完整配置示例

```json
{
  "base_url": "http://localhost:8000",
  "auth_token": "",
  "csrf_token": ""
}
```

**使用方法**: 在 API 中用 `{{变量名}}` 引用

例如:
- URL: `{{base_url}}/api/market/realtime/000001`
- Header: `Authorization: Bearer {{auth_token}}`

---

## 测试需要认证的 API

### 为什么需要认证？

就像去银行：
- 查询大厅公告 → 不需要登录 ✅
- 查询**你的**账户余额 → 需要登录 🔐

我们的 API 也一样：
- `/health` (健康检查) → 公开的，不需要登录
- `/api/market/realtime/{symbol}` (实时行情) → 需要登录
- `/api/watchlist` (我的自选股) → 需要登录

### 认证流程（3步走）

```
第1步: 获取 CSRF Token
   ↓
第2步: 用 CSRF Token 登录，获取 JWT Token
   ↓
第3步: 用 JWT Token 访问受保护的 API
```

### 详细步骤

#### 第1步: 获取 CSRF Token

**什么是 CSRF Token？**
- 一个防护令牌，防止恶意攻击
- 就像进门时的临时通行证

**操作**:

1. 在左侧找到 **📁 认证授权** → **GET /api/auth/csrf-token**
2. 点击它
3. 点击 **[发送]**

**响应示例**:
```json
{
  "success": true,
  "data": {
    "token": "abc123def456..."  ← 这就是 CSRF Token
  }
}
```

4. **保存 Token**:
   - 复制 `data.token` 的值（不包括引号）
   - 点击顶部 **环境选择器** → **本地开发** → **编辑**
   - 在 `csrf_token` 的 **当前值** 中粘贴
   - 保存

#### 第2步: 登录获取 JWT Token

**什么是 JWT Token？**
- 您的身份证明
- 有了它，服务器就知道"这是某某用户"

**操作**:

1. 在左侧找到 **📁 认证授权** → **POST /api/auth/login**
2. 点击它

3. **配置请求头**:
   - 切换到 **Header** 标签页
   - 添加（如果没有的话）:
     ```
     X-CSRF-Token: {{csrf_token}}
     ```

4. **配置请求体**:
   - 切换到 **Body** 标签页
   - 选择 **JSON** 格式
   - 输入（⚠️ 需要修改密码）:
   ```json
   {
     "username": "admin",
     "password": "你的密码"
   }
   ```

5. 点击 **[发送]**

**成功响应**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...很长的字符串",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

6. **保存 JWT Token**:
   - 复制 `data.access_token` 的值
   - 环境变量 → 编辑 → `auth_token` 的当前值 → 粘贴
   - 保存

#### 第3步: 使用 JWT Token 访问 API

**现在您已经"登录"了！可以访问受保护的 API 了。**

**测试实时行情 API**:

1. 在左侧找到 **📁 市场数据** → **GET /api/market/realtime/{symbol}**
2. 点击它

3. **修改路径参数**:
   - 看到 URL 中的 `{symbol}` 吗？这是占位符
   - 在 **路径参数** 区域，将 `symbol` 改为: `000001`（平安银行）

4. **配置请求头** (非常重要！):
   - 切换到 **Header** 标签页
   - 添加（如果没有的话）:
     ```
     Authorization: Bearer {{auth_token}}
     ```

5. 点击 **[发送]**

**成功响应**:
```json
{
  "success": true,
  "data": {
    "symbol": "000001",
    "name": "平安银行",
    "price": 12.34,
    "change": 0.12,
    "change_pct": 0.98,
    "volume": 1234567,
    "timestamp": "2025-11-10 14:30:00"
  }
}
```

**恭喜！您已经掌握了完整的认证流程！** 🎊

---

## 常见问题和解决方案

### ❌ 问题1: 401 Unauthorized（未授权）

**错误示例**:
```json
{
  "detail": "Not authenticated"
}
```

**原因**: 没有提供 JWT Token，或 Token 无效/过期

**解决方案**:
1. 检查环境变量中 `auth_token` 是否有值
2. 检查请求头中是否有: `Authorization: Bearer {{auth_token}}`
3. Token 可能过期了，重新登录获取新 Token

---

### ❌ 问题2: 403 CSRF Token Invalid（CSRF 令牌无效）

**错误示例**:
```json
{
  "detail": "CSRF token validation failed"
}
```

**原因**: POST/PUT/DELETE 请求缺少 CSRF Token，或 Token 无效

**解决方案**:
1. 先调用 `/api/auth/csrf-token` 获取新 Token
2. 在请求头中添加: `X-CSRF-Token: {{csrf_token}}`

---

### ❌ 问题3: 404 Not Found（找不到）

**错误示例**:
```json
{
  "detail": "Not Found"
}
```

**原因**: API 路径错误

**解决方案**:
1. 检查 URL 是否正确
2. 检查路径参数是否填写（比如 `{symbol}` 需要替换成具体的股票代码）
3. 检查 `base_url` 是否正确配置

---

### ❌ 问题4: 500 Internal Server Error（服务器错误）

**错误示例**:
```
Internal Server Error
```

**原因**: 服务器内部出错了

**解决方案**:
1. 检查服务器是否正常运行
2. 检查请求参数是否正确（类型、格式等）
3. 查看服务器日志（技术问题，可能需要开发人员处理）

---

### ⚠️ 问题5: 网络请求超时

**错误示例**:
```
Request timeout
```

**原因**:
- 服务器未运行
- 网络问题
- `base_url` 配置错误

**解决方案**:
1. 确认服务器正在运行: 访问 http://localhost:8000/health
2. 检查 `base_url` 是否配置正确
3. 检查防火墙设置

---

## 进阶技巧

### 技巧1: 自动登录脚本

**痛点**: 每次测试都要手动获取 Token 很麻烦

**解决方案**: 使用前置脚本自动登录

**配置步骤**:

1. 点击环境选择器 → 本地开发 → 编辑
2. 切换到 **前置操作** 标签页
3. 粘贴以下脚本:

```javascript
// 自动获取 CSRF Token 和 JWT Token
const baseUrl = pm.environment.get('base_url');

// 第1步: 获取 CSRF Token
pm.sendRequest({
  url: baseUrl + '/api/auth/csrf-token',
  method: 'GET'
}, (err, res) => {
  if (!err && res.code === 200) {
    const csrfToken = res.json().data.token;
    pm.environment.set('csrf_token', csrfToken);
    console.log('✅ CSRF Token 已获取');

    // 第2步: 使用 CSRF Token 登录
    pm.sendRequest({
      url: baseUrl + '/api/auth/login',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken
      },
      body: {
        mode: 'raw',
        raw: JSON.stringify({
          username: 'admin',
          password: '你的密码'  // ⚠️ 修改这里
        })
      }
    }, (err, res) => {
      if (!err && res.code === 200) {
        const jwtToken = res.json().data.access_token;
        pm.environment.set('auth_token', jwtToken);
        console.log('✅ JWT Token 已获取');
        console.log('🎉 自动登录成功！');
      } else {
        console.error('❌ 登录失败:', err || res.json());
      }
    });
  } else {
    console.error('❌ 获取 CSRF Token 失败:', err || res.json());
  }
});
```

4. ⚠️ **重要**: 修改脚本中的密码
5. 保存

**效果**:
- 打开 Apifox 时自动登录
- 环境变量中自动填充 Token
- 无需手动操作！

---

### 技巧2: 批量测试

**场景**: 测试多个相关的 API

**步骤**:

1. 点击左侧 **📊 测试管理**
2. 新建测试用例集 → 命名: "市场数据测试"
3. 添加测试用例:
   - 添加 "健康检查"
   - 添加 "实时行情 - 000001"
   - 添加 "实时行情 - 000002"
   - 添加 "K线数据"
4. 点击 **运行测试用例集**
5. 查看测试报告

---

### 技巧3: 使用 Mock 数据

**场景**: 后端还没开发完，但前端想提前调试

**步骤**:

1. 选择任意 API
2. 点击 **Mock** 标签
3. 复制 Mock URL
4. 在前端代码中使用这个 URL

**好处**:
- 前后端可以并行开发
- Apifox 会根据 API 定义自动生成假数据
- 前端无需等待后端完成

---

### 技巧4: 导出 API 文档

**场景**: 需要分享 API 文档给团队

**步骤**:

1. 点击右上角 **⋯** (更多)
2. 选择 **导出**
3. 选择格式:
   - **Markdown**: 适合放到 GitHub
   - **HTML**: 可以直接浏览器打开
   - **PDF**: 适合打印或发邮件
4. 下载文件

---

## 📋 测试检查清单

作为初学者，按这个顺序测试：

### 第一阶段: 基础测试（无需认证）

- [ ] ✅ 健康检查: `GET /health`
- [ ] 系统信息: `GET /api/system/info`
- [ ] Socket.IO状态: `GET /api/socketio-status`

### 第二阶段: 认证流程

- [ ] 获取CSRF Token: `GET /api/auth/csrf-token`
- [ ] 用户登录: `POST /api/auth/login`
- [ ] 刷新Token: `POST /api/auth/refresh`

### 第三阶段: 业务 API（需要认证）

- [ ] 实时行情: `GET /api/market/realtime/000001`
- [ ] K线数据: `GET /api/market/kline?symbol=000001&period=daily`
- [ ] 资金流向: `GET /api/market/fund-flow`

### 第四阶段: 复杂场景

- [ ] 批量行情: `GET /api/market/v2/realtime-batch?symbols=000001,000002`
- [ ] 行业资金流向: `GET /api/market/v3/fund-flow?industry_type=sw_l1`
- [ ] 自选股管理: `POST /api/watchlist/add`

---

## 🎓 学习路径建议

### 第1周: 基础操作
- 熟悉 Apifox 界面
- 测试简单的 GET 请求
- 理解环境变量

### 第2周: 认证流程
- 掌握 CSRF Token 和 JWT Token
- 学会手动登录
- 配置自动登录脚本

### 第3周: 进阶功能
- 创建测试用例
- 使用 Mock 数据
- 导出 API 文档

### 第4周: 实战应用
- 测试完整业务流程
- 发现和报告 Bug
- 协助前端开发

---

## 📞 获取帮助

### 遇到问题时

1. **查看错误信息**: 仔细阅读响应中的错误提示
2. **检查配置**:
   - `base_url` 是否正确？
   - Token 是否有值？
   - 请求头是否正确？
3. **查看文档**:
   - [APIFOX_QUICK_START.md](APIFOX_QUICK_START.md)
   - [API_GUIDE.md](API_GUIDE.md)
4. **咨询他人**:
   - 询问团队成员
   - Apifox 官方文档
   - 技术社区

---

## 🎉 恭喜您！

如果您完成了这份指南中的所有步骤，那么您已经：

✅ 学会了使用 Apifox 测试 API
✅ 理解了 API 认证流程
✅ 掌握了环境变量的使用
✅ 能够独立测试各种 API

**记住**:
- 从简单开始，循序渐进
- 多练习，熟能生巧
- 遇到问题不要慌，仔细检查配置
- API 测试是一项非常实用的技能！

---

**快速访问**: https://app.apifox.com/project/7376246

开始您的 API 测试之旅吧！💪
