# 问财筛选功能测试指南

## ⚠️ 重要提示

**请按照以下步骤操作，确保浏览器加载最新代码**

## 测试步骤

### 第一步：清除浏览器缓存（必须！）

选择以下任一方法：

**方法 A：硬刷新**
- Windows/Linux: `Ctrl + Shift + R` 或 `Ctrl + F5`
- Mac: `Cmd + Shift + R`

**方法 B：使用开发者工具**
1. 按 `F12` 打开开发者工具
2. 右键点击浏览器刷新按钮
3. 选择"清空缓存并硬性重新加载"

**方法 C：手动清除**
1. 打开浏览器设置
2. 清除浏览器缓存和 Cookie
3. 重新访问 http://localhost:3001

### 第二步：登录系统

访问：http://localhost:3001

使用测试账号：
- 用户名：`admin`
- 密码：`admin123`

### 第三步：测试菜单导航

1. 登录后，查看左侧菜单
2. 点击"市场数据"展开子菜单
3. 点击"问财筛选"

**预期结果**：右侧页面应显示问财筛选界面，包含9个查询卡片

### 第四步：验证路由

打开浏览器开发者工具（F12），切换到 Console 标签页

**在地址栏中应该看到**：`http://localhost:3001/market-data/wencai`

**在 Console 中应该看到**：`Menu selected: /market-data/wencai`

### 第五步：测试功能

如果页面正常显示，测试以下功能：

1. **查看查询列表**：应显示 9 个查询卡片
2. **执行查询**：点击任一卡片的"执行查询"按钮
3. **查看结果**：执行完成后应显示数据表格
4. **导出CSV**：测试导出功能

## 常见问题排查

### 问题 1：点击菜单后页面没有变化

**原因**：浏览器缓存了旧版本的代码

**解决方案**：
1. 执行硬刷新（Ctrl + Shift + R）
2. 或清除浏览器缓存

### 问题 2：页面显示空白或报错

**检查步骤**：
1. 打开开发者工具（F12）
2. 查看 Console 标签页的错误信息
3. 查看 Network 标签页，检查 API 请求是否正常

**常见错误**：
- `Failed to fetch`：后端服务未启动
- `404 Not Found`：路由配置错误
- `500 Internal Server Error`：后端代码错误

### 问题 3：API 请求失败

**检查后端服务**：
```bash
# 检查后端是否运行
ps aux | grep uvicorn

# 测试后端 API
curl http://localhost:8000/api/market/wencai/health

# 预期返回：
# {"status":"healthy","service":"wencai","version":"1.0.0"}
```

### 问题 4：路由显示但组件不加载

**检查方法**：
1. 打开开发者工具 → Network 标签
2. 刷新页面
3. 查找 `WencaiPanel.vue` 相关的请求
4. 如果显示 404，说明组件路径错误

## 调试命令

### 在浏览器 Console 中执行：

```javascript
// 查看当前路由
console.log('Current route:', this.$route)

// 手动导航到问财页面
this.$router.push('/market-data/wencai')

// 查看路由是否已注册
console.log('Router:', this.$router.getRoutes())
```

### 在服务器上检查：

```bash
# 检查前端服务
ps aux | grep vite

# 检查后端服务
ps aux | grep uvicorn

# 查看前端日志
tail -f /tmp/frontend.log

# 查看后端日志
tail -f /tmp/backend.log
```

## 确认配置

### 路由配置（已验证 ✅）
路径：`src/router/index.js`
```javascript
{
  path: 'market-data/wencai',
  name: 'market-data-wencai',
  component: () => import('@/components/market/WencaiPanel.vue'),
  meta: { title: '问财筛选', icon: 'Search' }
}
```

### 菜单配置（已验证 ✅）
路径：`src/layout/index.vue`
```vue
<el-menu-item index="/market-data/wencai">
  <el-icon><Search /></el-icon>
  <template #title>问财筛选</template>
</el-menu-item>
```

### 菜单处理器（已验证 ✅）
```javascript
const handleMenuSelect = (index) => {
  console.log('Menu selected:', index)
  if (index && index.startsWith('/')) {
    router.push(index)
  }
}
```

## 服务状态

**前端服务**：
- URL: http://localhost:3001
- 状态: ✅ 运行中

**后端服务**：
- URL: http://localhost:8000
- 状态: ✅ 运行中

**API 端点**：
- 健康检查: `GET /api/market/wencai/health`
- 查询列表: `GET /api/market/wencai/queries`
- 执行查询: `POST /api/market/wencai/query`

## 联系支持

如果按照以上步骤仍然无法解决问题，请提供：
1. 浏览器 Console 中的错误信息（截图）
2. Network 标签页中失败的请求详情
3. 浏览器名称和版本
4. 操作系统信息
