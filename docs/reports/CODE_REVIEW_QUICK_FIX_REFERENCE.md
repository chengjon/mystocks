# ⚡ Quick Fix Reference - Top 3 Priority Issues

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


## 🟡 Issue #1: Add Health Check Endpoints (MEDIUM)

**File**: `web/frontend/config/nginx-history-mode.conf` (Line 17-35)

**Quick Fix**:
```nginx
server {
    listen 80;
    server_name mystocks.local;
    root /var/www/mystocks/dist;
    
    # ✅ ADD THESE LINES
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    location /ready {
        access_log off;
        try_files $uri /index.html;
        return 200;
    }
    # ✅ END ADD
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    # ... rest of config ...
}
```

**Apache Equivalent**:
```apache
# Add to server config
<Location "/health">
    Require all granted
    Header unset Content-Type
    Header set Content-Type "text/plain"
</Location>
```

---

## 🟡 Issue #2: Complete Apache Security Headers (MEDIUM)

**File**: `web/frontend/config/apache-history-mode.conf` (Line 67-71)

**Quick Fix**:
```apache
<IfModule mod_headers.c>
    # Existing headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    
    # ✅ ADD THESE LINES
    # HSTS (uncomment after enabling HTTPS)
    # Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    
    # Content Security Policy
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    
    # Referrer Policy
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    
    # Permissions Policy
    Header always set Permissions-Policy "geolocation=(), microphone=(), camera=()"
    # ✅ END ADD
</IfModule>
```

---

## 🟡 Issue #3: Graceful Degradation for IE9 (MEDIUM)

**File**: `web/frontend/src/router/index.ts` (Line 1, 797)

**Quick Fix**:
```typescript
// ✅ MODIFY LINE 1
import { createRouter, createWebHistory, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

// ✅ ADD BEFORE LINE 797
// Detect History API support
const supportsHistory = 'pushState' in window.history && 
                        'replaceState' in window.history &&
                        !!(window.navigator.userAgent.indexOf('MSIE') === -1 || 
                           window.navigator.userAgent.indexOf('Trident/') === -1)

// ✅ MODIFY LINE 797
const router = createRouter({
  history: supportsHistory 
    ? createWebHistory(import.meta.env.BASE_URL)
    : createWebHashHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// ✅ ADD LOGGING (optional)
if (import.meta.env.DEV) {
  console.log(`🚀 Router mode: ${supportsHistory ? 'HTML5 History' : 'Hash (fallback)'}`)
}
```

---

## 🧪 Verification Commands

**Test Health Endpoints**:
```bash
# Test health endpoint
curl http://localhost:3020/health

# Expected output:
# healthy

# Test readiness endpoint
curl -I http://localhost:3020/ready

# Expected output:
# HTTP/1.1 200 OK
```

**Test Security Headers**:
```bash
# Check security headers
curl -I http://your-domain.com/ | grep -E "X-Frame-Options|X-Content-Type-Options|Content-Security-Policy"

# Expected output:
# X-Frame-Options: SAMEORIGIN
# X-Content-Type-Options: nosniff
# Content-Security-Policy: default-src 'self'; ...
```

**Test Router Fallback**:
```bash
# In browser console (IE9 or simulate old browser)
console.log('pushState' in window.history)
// Expected: false (triggers Hash mode fallback)
```

---

## 📋 Pre-Production Checklist

```bash
#!/bin/bash
# pre-deploy-check.sh

echo "🔍 Pre-Production Deployment Checklist"
echo "======================================="

# 1. Check health endpoints
echo -n "1. Health endpoint... "
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3020/health)
if [ "$HEALTH" -eq 200 ]; then echo "✅ PASS"; else echo "❌ FAIL ($HEALTH)"; fi

# 2. Check security headers
echo -n "2. Security headers... "
HEADERS=$(curl -s -I http://localhost:3020/ | grep -c "X-Frame-Options")
if [ "$HEADERS" -gt 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

# 3. Test all routes
echo -n "3. Route testing... "
ROUTES=("/dashboard" "/market/realtime" "/risk/alerts" "/strategy/management")
FAIL=0
for route in "${ROUTES[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3020$route")
    if [ "$STATUS" -ne 200 ]; then
        echo "❌ FAIL: $route ($STATUS)"
        FAIL=1
    fi
done
if [ $FAIL -eq 0 ]; then echo "✅ PASS"; fi

# 4. Check router mode
echo -n "4. Router mode... "
MODE=$(curl -s http://localhost:3020/ | grep -o "createWebHistory" | head -1)
if [ -n "$MODE" ]; then echo "✅ PASS (HTML5 History)"; else echo "❌ FAIL"; fi

echo "======================================="
echo "✅ Pre-production checks complete!"
```

---

**Estimated Time to Apply Fixes**: 15-30 minutes  
**Risk Level**: Low (backwards compatible)  
**Rollback**: Git revert if issues arise

