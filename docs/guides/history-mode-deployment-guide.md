# 前端路由 History 模式部署指南

## ⚠️ 重要更新 (2026-01-22)

**HTML5 History 模式迁移已完成**！

- ✅ 路由配置已更新：`createWebHashHistory` → `createWebHistory`
- ✅ 服务器配置文件已创建：`config/nginx-history-mode.conf` 和 `config/apache-history-mode.conf`
- ✅ 所有路由测试通过（11/11，成功率 100%）

**详细报告**: 参见 [`docs/reports/HTML5_HISTORY_MODE_MIGRATION_COMPLETION_REPORT.md`](../reports/HTML5_HISTORY_MODE_MIGRATION_COMPLETION_REPORT.md)

---

## 概述

本文档说明如何在生产环境中配置 Web 服务器以支持 Vue Router 的 History 模式，确保 SPA 路由正常工作。

## 背景

迁移到 History 模式后，URL 格式从 `/#/path` 变为 `/path`。这提高了 SEO 友好性和 URL 美观性，但需要在 Web 服务器上配置路由回退规则，将所有非静态文件请求重定向到 `index.html`。

## 🚀 阶段式实施指南

本项目采用**分阶段部署策略**，确保生产环境稳定性：

### ✅ 阶段0：基础迁移（已完成）
- HTML5 History模式路由配置
- 基础Nginx/Apache配置文件
- 开发环境测试验证

### ✅ 阶段1：核心保障（已完成）
- **健康检查端点**：`/health`、`/ready`（监控集成）
- **安全头补全**：CSP、Referrer-Policy、Permissions-Policy
- **IE9降级**：History API检测 + Hash模式回退

### ✅ 阶段2：性能优化（已完成）
- **速率限制**：防止DDoS和API滥用
- **缓存策略优化**：基于哈希的智能缓存

---

## 部署前准备

### 1. 构建前端应用
```bash
cd web/frontend
npm run build
```
构建输出将在 `dist/` 目录中。

### 2. 上传文件到服务器
将 `dist/` 目录上传到 Web 服务器的静态文件目录：
- Nginx: `/var/www/mystocks/dist`
- Apache: `/var/www/mystocks/dist`

### 3. 预部署检查清单 ⭐
```bash
# 运行自动化验证脚本（开发环境）
bash web/frontend/scripts/validate-production-deployment.sh http://localhost:3020

# 查看完整检查清单
cat web/frontend/scripts/PRE_DEPLOYMENT_CHECKLIST.md
```

## Web 服务器配置

### Nginx 配置

1. **复制配置文件**
```bash
sudo cp web/frontend/config/nginx-history-mode.conf /etc/nginx/sites-available/mystocks
```

2. **修改配置**
编辑 `/etc/nginx/sites-available/mystocks`：
- 将 `your-domain.com` 替换为实际域名
- 确认 `root` 路径正确
- 如需要 SSL，取消注释 SSL 配置块

3. **启用站点**
```bash
sudo ln -s /etc/nginx/sites-available/mystocks /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl reload nginx
```

### Apache 配置

1. **复制配置文件**
```bash
sudo cp web/frontend/config/apache-history-mode.conf /etc/apache2/sites-available/mystocks.conf
```

2. **修改配置**
编辑 `/etc/apache2/sites-available/mystocks.conf`：
- 将 `your-domain.com` 替换为实际域名
- 确认 `DocumentRoot` 路径正确
- 如需要 SSL，取消注释 SSL 配置块

3. **启用模块和站点**
```bash
sudo a2enmod rewrite proxy proxy_http headers
sudo a2ensite mystocks
sudo systemctl reload apache2
```

## 验证部署

### 1. 基本功能测试
```bash
# 测试主页
curl -I https://your-domain.com/

# 测试路由页面
curl -I https://your-domain.com/dashboard
curl -I https://your-domain.com/analysis

# 测试动态路由
curl -I https://your-domain.com/stock-detail/600519

# 预期结果：所有请求返回 200 OK
```

### 2. 浏览器测试
在浏览器中访问以下 URL，确认页面正常加载：
- `https://your-domain.com/dashboard`
- `https://your-domain.com/analysis`
- `https://your-domain.com/stock-detail/600519`

### 3. SEO 测试
- 检查页面标题是否正确显示
- 验证 URL 在地址栏中显示为干净格式（无 # 符号）

## 故障排除

### 404 错误
如果访问路由页面时出现 404：
1. 检查 Web 服务器配置中的 `try_files` 或 `RewriteRule` 规则
2. 确认 `index.html` 文件存在且可访问
3. 检查文件权限

### 静态资源加载失败
如果 CSS/JS 文件无法加载：
1. 检查文件路径是否正确
2. 验证构建输出目录结构
3. 确认 Web 服务器有读取权限

### API 请求失败
如果前端无法访问后端 API：
1. 检查代理配置（`/api/` 路径）
2. 确认后端服务正在运行
3. 验证 CORS 配置

---

## 🚀 阶段2：性能优化配置

### 速率限制（Rate Limiting）

#### 配置说明
Nginx配置已包含速率限制功能，防止DDoS攻击和API滥用：
- **API路径** (`/api/`): 10请求/秒，突发20
- **通用路径** (`/`): 30请求/秒，突发50
- **认证路径** (`/api/auth/*`): 5请求/秒（如需要）

#### 验证速率限制
```bash
# 测试API速率限制
for i in {1..25}; do
    curl http://your-domain.com/api/test &
done
wait
# 前20个请求应该成功，第21+个应该返回429
```

#### 429响应示例
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

#### 调整速率限制
如果需要调整速率限制，编辑Nginx配置中的以下行：
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
# 修改rate=10r/s为所需的速率
```

---

### 智能缓存策略

#### 配置说明
Nginx配置已优化为基于文件名的智能缓存：

| 资源类型 | 缓存策略 | 原因 |
|---------|---------|------|
| **哈希JS/CSS** (`app.abc123.js`) | 1年，不可变 | 文件名变更时自动失效 |
| **图片** (png, jpg, svg) | 1个月，需验证 | 更新频率较低 |
| **字体** (woff, woff2) | 1年，不可变 | 很少变更 |
| **index.html** | 不缓存 | 确保始终获取最新版本 |

#### 验证缓存策略
```bash
# 检查哈希文件的缓存头
curl -I http://your-domain.com/assets/app.abc123.js | grep -i cache-control
# 预期输出: Cache-Control: public, immutable

# 检查index.html的缓存头
curl -I http://your-domain.com/ | grep -i cache-control
# 预期输出: Cache-Control: no-store, no-cache, must-revalidate
```

#### Vite构建验证
确认Vite生成带哈希的文件名：
```bash
npm run build
ls -la dist/assets/*.js
# 应该看到: app.abc123def.js, vendor.456789ghi.js
```

---

### 监控集成

#### Prometheus健康检查
```yaml
# blackbox.yml 示例
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      method: GET
      valid_status_codes: [200]
      valid_http_versions: ["HTTP/1.1", "HTTP/2"]
```

#### Kubernetes探针配置
```yaml
# deployment.yaml
livenessProbe:
  httpGet:
    path: /health
    port: 80
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 80
  initialDelaySeconds: 5
  periodSeconds: 5
```

#### AWS ALB目标组健康检查
```
Target Group Health Settings:
- Health Check Path: /health
- Interval: 30 seconds
- Timeout: 5 seconds
- Healthy Threshold: 3
- Unhealthy Threshold: 3
- Success Codes: 200
```

---

## 故障排除
3. 验证 CORS 配置

## 监控和维护

### 日志监控
- Nginx: `/var/log/nginx/mystocks_*.log`
- Apache: `/var/log/apache2/mystocks_*.log`

### 性能监控
- 监控 404 错误率
- 检查静态资源缓存命中率
- 关注 SPA 路由的响应时间

## 回滚计划

如果需要回滚到 Hash 模式：
1. 修改前端代码：将 `createWebHistory` 改回 `createWebHashHistory`
2. 重新构建和部署前端
3. 无需修改 Web 服务器配置（Hash 模式不需要特殊配置）

---

**文档版本**: v2.0 (HTML5 History 模式迁移完成)
*配置创建时间*: 2026-01-22
*适用于*: History 模式迁移后的生产环境部署
*状态*: ✅ 已完成并通过验证

**相关文档**:
- [HTML5 History 模式迁移完成报告](../reports/HTML5_HISTORY_MODE_MIGRATION_COMPLETION_REPORT.md)
- [前端路由优化分析报告](../reviews/frontend_routing_optimization_report.md)
- [前端 History 迁移任务](../tasks/FRONTEND_HISTORY_MIGRATION.md)