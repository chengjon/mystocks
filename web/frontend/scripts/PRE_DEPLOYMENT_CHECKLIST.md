# 🚀 HTML5 History模式 - 预部署检查清单

**适用环境**: 生产环境部署前  
**目的**: 确保所有配置正确，避免部署后出现问题  
**最后更新**: 2026-01-22

---

## 📋 部署前检查清单

### 1️⃣ 服务器配置验证

#### Nginx服务器

- [ ] **Nginx版本** ≥ 1.18.0
  ```bash
  nginx -v
  ```

- [ ] **必需模块已启用**
  ```bash
  nginx -V 2>&1 | grep -E "http_ssl_module|http_v2_module|headers_module"
  ```

- [ ] **配置文件语法正确**
  ```bash
  nginx -t -c /path/to/nginx-history-mode.conf
  ```

- [ ] **配置文件已部署到正确位置**
  ```bash
  ls -la /etc/nginx/sites-available/mystocks
  ```

- [ ] **站点已启用**
  ```bash
  ls -la /etc/nginx/sites-enabled/mystocks
  ```

- [ ] **端口80和443未被占用**（如果使用标准端口）
  ```bash
  netstat -tuln | grep -E ":80|:443"
  ```

#### Apache服务器（如适用）

- [ ] **Apache版本** ≥ 2.4
  ```bash
  apache2 -v
  ```

- [ ] **必需模块已启用**
  ```bash
  apachectl -M | grep -E "rewrite_module|headers_module|expires_module|deflate_module"
  ```

- [ ] **配置文件语法正确**
  ```bash
  apachectl configtest -f /path/to/apache-history-mode.conf
  ```

- [ ] **模块已启用**
  ```bash
  a2enmod rewrite proxy proxy_http headers expires deflate
  ```

---

### 2️⃣ 前端构建验证

#### 构建文件检查

- [ ] **构建成功无错误**
  ```bash
  npm run build
  ```

- [ ] **dist/目录包含必需文件**
  ```bash
  ls -la dist/
  # 应该看到: index.html, assets/ 目录
  ```

- [ ] **哈希文件名已生成**（缓存策略验证）
  ```bash
  ls dist/assets/*.js | grep -E '[a-f0-9]{8}\.js$'
  # 示例: app.abc123def.js
  ```

- [ ] **index.html文件存在且非空**
  ```bash
  wc -l dist/index.html
  # 应该大于100行
  ```

#### 路由配置验证

- [ ] **路由配置已更新**
  ```bash
  grep "createWebHistory" src/router/index.ts
  # 应该找到导入和使用
  ```

- [ ] **IE9降级逻辑已添加**
  ```bash
  grep "supportsHistory" src/router/index.ts
  # 应该找到检测逻辑
  ```

- [ ] **TypeScript编译无错误**
  ```bash
  npm run build
  # 检查输出中无TypeScript错误
  ```

---

### 3️⃣ 健康检查端点验证

#### 端点可访问性

- [ ] **健康检查端点响应正确**
  ```bash
  curl http://your-domain.com/health
  # 预期: HTTP 200 + JSON响应
  ```

- [ ] **就绪检查端点响应正确**
  ```bash
  curl http://your-domain.com/ready
  # 预期: HTTP 200
  ```

#### JSON响应格式验证

- [ ] **健康检查包含必需字段**
  ```bash
  curl -s http://your-domain.com/health | jq .
  # 应该包含: status, timestamp, service, version
  ```

- [ ] **响应时间 < 100ms**
  ```bash
  time curl -s http://your-domain.com/health
  # 验证快速响应
  ```

---

### 4️⃣ 安全头验证

#### 安全头完整性

- [ ] **所有必需安全头已配置**
  ```bash
  curl -I http://your-domain.com/ | grep -E "X-Frame-Options|X-Content-Type-Options|X-XSS-Protection|Content-Security-Policy|Referrer-Policy"
  ```

#### CSP策略验证

- [ ] **CSP策略正确配置**
  ```bash
  curl -I http://your-domain.com/ | grep Content-Security-Policy
  ```

- [ ] **CSP策略包含必要指令**
  ```bash
  curl -I http://your-domain.com/ | grep -o "default-src '[^']*'" | head -1
  ```

#### 安全评分验证

- [ ] **使用安全头检测工具**
  ```
  访问: https://securityheaders.com/
  输入域名: your-domain.com
  目标评分: A级 (≥ 9/10)
  ```

---

### 5️⃣ 路由功能验证

#### 主要路由测试

- [ ] **首页访问正常**
  ```bash
  curl -I http://your-domain.com/
  # 预期: HTTP 200
  ```

- [ ] **所有ArtDeco域路由可访问**
  ```bash
  for route in /dashboard /market/realtime /risk/alerts /strategy/management /trading/signals /system/monitoring; do
    curl -I "http://your-domain.com$route"
  done
  ```

- [ ] **直接访问路由（非根路径）正常**
  ```bash
  # 测试深度链接
  curl -I http://your-domain.com/market/realtime
  curl -I http://your-domain.com/risk/alerts
  ```

#### 页面刷新验证

- [ ] **页面刷新（F5）正常工作**
  ```bash
  # 在浏览器中手动测试：
  # 1. 访问 http://your-domain.com/dashboard
  # 2. 按F5刷新页面
  # 3. 验证页面仍正常显示
  ```

- [ ] **浏览器前进/后退按钮正常**
  ```bash
  # 在浏览器中手动测试：
  # 1. 访问多个页面
  # 2. 点击后退按钮
  # 3. 点击前进按钮
  # 4. 验证导航正常
  ```

---

### 6️⃣ API代理验证

#### API连接性

- [ ] **API代理配置正确**
  ```bash
  curl -I http://your-domain.com/api/health
  # 或者后端的任何健康检查端点
  ```

- [ ] **后端服务运行正常**
  ```bash
  curl http://localhost:8000/health
  # 或者后端的健康检查端点
  ```

#### WebSocket支持

- [ ] **WebSocket升级配置正确**
  ```bash
  # 在浏览器控制台中测试WebSocket连接
  # 或使用wscat命令行工具
  ```

---

### 7️⃣ 性能验证

#### 响应时间

- [ ] **首页响应时间 < 1秒**
  ```bash
  time curl -s http://your-domain.com/ > /dev/null
  ```

- [ ] **API响应时间可接受**
  ```bash
  time curl -s http://your-domain.com/api/endpoint > /dev/null
  ```

#### 静态资源加载

- [ ] **JS/CSS文件正确加载**
  ```bash
  # 在浏览器DevTools中检查Network标签
  # 验证所有资源HTTP 200
  ```

- [ ] **缓存策略正确应用**
  ```bash
  curl -I http://your-domain.com/assets/ | grep -i cache-control
  # 哈希文件应该有: public, immutable
  # index.html应该有: no-store, no-cache
  ```

---

### 8️⃣ 浏览器兼容性验证

#### 现代浏览器

- [ ] **Chrome 最新版测试通过**
  ```bash
  # 在Chrome中手动测试所有主要功能
  ```

- [ ] **Firefox 最新版测试通过**
  ```bash
  # 在Firefox中手动测试所有主要功能
  ```

- [ ] **Safari/Edge 测试通过**（如适用）
  ```bash
  # 在Safari/Edge中手动测试所有主要功能
  ```

#### 旧版浏览器（可选）

- [ ] **IE11测试通过**（如需要支持）
  ```bash
  # 在IE11中手动测试
  # 验证Hash模式降级是否工作
  ```

---

### 9️⃣ 监控和日志

#### 日志配置

- [ ] **Nginx/Apache访问日志已启用**
  ```bash
  tail -f /var/log/nginx/mystocks_access.log
  # 或
  tail -f /var/log/apache2/mystocks_access.log
  ```

- [ ] **错误日志可访问**
  ```bash
  tail -f /var/log/nginx/mystocks_error.log
  # 或
  tail -f /var/log/apache2/mystocks_error.log
  ```

#### 监控集成

- [ ] **健康检查已集成到监控系统**
  ```bash
  # Prometheus: 配置blackbox exporter
  # Kubernetes: 配置liveness/readiness probes
  # AWS: 配置ALB target group health checks
  ```

---

### 🔟 回滚计划准备

#### 回滚脚本

- [ ] **回滚脚本已准备**
  ```bash
  # 创建回滚脚本示例
  cat > rollback.sh << 'SCRIPT'
  #!/bin/bash
  echo "执行回滚..."
  # 1. 恢复旧配置
  cp /etc/nginx/sites-available/mystocks.old /etc/nginx/sites-available/mystocks
  # 2. 测试配置
  nginx -t
  # 3. 重载Nginx
  systemctl reload nginx
  echo "回滚完成"
  SCRIPT
  chmod +x rollback.sh
  ```

#### 备份验证

- [ ] **旧配置已备份**
  ```bash
  ls -la /etc/nginx/sites-available/mystocks.old
  ```

- [ ] **数据库已备份**（如适用）
  ```bash
  # 根据实际情况验证
  ```

---

## 🧪 自动化验证

### 运行验证脚本

在完成所有手动检查后，运行自动化验证脚本：

```bash
# 基础验证
./scripts/validate-production-deployment.sh http://your-domain.com

# 完整验证（包括所有测试）
./scripts/validate-production-deployment.sh http://your-domain.com --full
```

### 预期输出

```
══════════════════════════════════════════════════════
  🚀 MyStocks 生产部署验证
══════════════════════════════════════════════════════

1️⃣  健康检查端点验证
✅ 健康检查端点: HTTP 200
✅ 就绪检查端点: HTTP 200

...

══════════════════════════════════════════════════════
📊 验证结果总结
══════════════════════════════════════════════════════

总检查项: 25
通过检查: 25
失败检查: 0
通过率: 100%

✅ 🎉 所有检查通过！部署验证成功。
```

---

## ✅ 部署决策

### 通过标准

- **所有CRITICAL项必须通过** (100%)
- **HIGH优先级项通过率 ≥ 90%**
- **整体通过率 ≥ 95%**

### 警告标准

- **整体通过率 80% - 95%**: 可部署，但需监控失败项
- **整体通过率 < 80%**: 建议修复后再部署

### 阻塞标准

- **任何CRITICAL项失败**: 必须修复才能部署
- **安全头验证失败**: 建议修复后再部署

---

## 📞 问题上报

如遇到问题，请参考：

1. **故障排除指南**: `docs/guides/history-mode-deployment-guide.md`
2. **代码审查报告**: `docs/reports/CODE_REVIEW_HTML5_HISTORY_MIGRATION.md`
3. **阶段1修复报告**: `docs/reports/STAGE1_MEDIUM_PRIORITY_FIXES_COMPLETION_REPORT.md`

---

**检查清单版本**: v1.0  
**最后更新**: 2026-01-22  
**维护者**: Claude Code

🎯 **祝部署顺利！**
