# 前端路由 History 模式部署指南

## 概述

本文档说明如何在生产环境中配置 Web 服务器以支持 Vue Router 的 History 模式，确保 SPA 路由正常工作。

## 背景

迁移到 History 模式后，URL 格式从 `/#/path` 变为 `/path`。这提高了 SEO 友好性和 URL 美观性，但需要在 Web 服务器上配置路由回退规则，将所有非静态文件请求重定向到 `index.html`。

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

## Web 服务器配置

### Nginx 配置

1. **复制配置文件**
```bash
sudo cp config/nginx.production.conf /etc/nginx/sites-available/mystocks
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
sudo cp config/apache.production.conf /etc/apache2/sites-available/mystocks.conf
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

*配置创建时间*: 2026-01-12
*适用于*: History 模式迁移后的生产环境部署