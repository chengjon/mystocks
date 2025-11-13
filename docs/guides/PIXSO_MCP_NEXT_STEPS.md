# Swagger UI 访问 - 快速解决步骤

> **问题**: http://localhost:8000/api/docs 和 http://172.26.26.12:8000/api/docs 浏览器无法打开
> **诊断结果**: ✅ 后端服务完全正常，问题在客户端
> **完整报告**: 参见 `PIXSO_MCP_TROUBLESHOOTING.md`

---

## 🚀 立即尝试（3 分钟内解决）

### 步骤 1: 测试 ReDoc 备用界面（30 秒）

**直接访问**:
```
http://172.26.26.12:8000/api/redoc
```

或

```
http://localhost:8000/api/redoc
```

**说明**: ReDoc 是另一个 API 文档界面，如果它能打开，说明是 Swagger UI 的 CDN 资源问题。

---

### 步骤 2: 清除浏览器缓存（1 分钟）

**方法 A: 强制刷新**
- Windows: `Ctrl + F5`
- Mac: `Cmd + Shift + R`

**方法 B: 无痕模式测试**
- Chrome: `Ctrl + Shift + N`
- Firefox: `Ctrl + Shift + P`
- 在无痕窗口访问: http://172.26.26.12:8000/api/docs

---

### 步骤 3: 检查浏览器错误（1 分钟）

1. 访问 http://172.26.26.12:8000/api/docs
2. 按 `F12` 打开开发者工具
3. 查看 **Console** 标签（是否有红色错误）
4. 查看 **Network** 标签（哪些资源加载失败）

**常见错误截图并反馈给我**:
- CORS 错误
- CDN 资源加载失败
- JavaScript 执行错误

---

## 💡 如果以上都无效

### 选项 A: 使用 Postman（推荐）

```bash
# 1. 下载 API 规范
curl http://172.26.26.12:8000/openapi.json > mystocks-api.json

# 2. 在 Postman 中:
Import → Upload Files → 选择 mystocks-api.json

# 3. 自动生成 204 个 API 端点
```

### 选项 B: 使用命令行测试

```bash
# 获取 CSRF Token
curl http://172.26.26.12:8000/api/csrf-token

# 登录（替换 <csrf-token>）
curl -X POST http://172.26.26.12:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <your-csrf-token>" \
  -d '{"username": "admin", "password": "your-password"}'

# 测试 API（替换 <jwt-token>）
curl http://172.26.26.12:8000/api/market/realtime?symbols=000001.SZ \
  -H "Authorization: Bearer <your-jwt-token>"
```

---

## 🔧 长期解决方案

如果确认是 CDN 资源被墙的问题，我可以帮您：

1. **配置本地 Swagger UI**（下载静态文件到本地）
2. **配置国内 CDN 镜像**
3. **配置 Windows 端口转发**（让 localhost:8000 直接工作）

请告诉我上面哪个步骤帮您解决了问题，或者遇到了什么具体错误。

---

## 📊 当前服务状态

✅ **后端服务**: 正常运行
✅ **端口监听**: 0.0.0.0:8000
✅ **Windows 访问**: 已验证成功
✅ **HTTP 响应**: 200 OK
✅ **API 数量**: 204 个端点
✅ **认证系统**: JWT + CSRF

---

## 📞 需要帮助？

如果遇到任何问题，请提供：
1. 浏览器控制台的错误截图（F12 → Console）
2. Network 标签中失败的请求（F12 → Network）
3. 使用的浏览器和版本

我会根据具体错误提供精准的解决方案。
