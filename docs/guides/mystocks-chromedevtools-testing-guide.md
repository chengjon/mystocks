# MyStocks 项目测试指引 - Chrome DevTools 实践

## 📋 项目概述

**MyStocks** 是一个专业的量化交易数据管理系统，采用前后端分离架构：
- **前端**: Vue 3 + Element Plus + Web Workers（实时技术指标计算）
- **后端**: FastAPI + WebSocket（实时数据推送）
- **数据库**: TDengine（高频时序数据）+ PostgreSQL（参考数据）
- **核心特性**: 实时行情监控、技术指标计算、多数据源集成

本测试指引专门针对MyStocks项目的测试场景，结合Chrome DevTools的使用方法，提供完整的测试流程和实用技巧。

---

## 🎯 测试环境准备

### 1. 启动项目环境

```bash
# 后端服务 (FastAPI)
cd web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端服务 (Vue 3)
cd web/frontend
npm run dev  # 默认端口 5173
```

### 2. 配置Chrome DevTools远程调试

**WSL2环境配置**（详见 `docs/guides/chrome-devtools-wsl2-guide.md`）

```powershell
# Windows PowerShell (管理员)
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$profileDir = "$env:USERPROFILE\ChromeProfiles\mystocks"

Start-Process -FilePath $chromePath -ArgumentList @(
    "--user-data-dir=`"$profileDir`"",
    "--remote-debugging-port=9230",
    "--remote-debugging-address=0.0.0.0"
)
```

### 3. 访问测试页面

- **前端界面**: http://localhost:5173
- **API文档**: http://localhost:8000/docs
- **WebSocket测试**: http://localhost:8000/ws-test

---

## 🔧 核心测试场景与DevTools使用

### 场景1：实时行情监控功能测试

#### 测试目标
- 实时股票数据更新
- WebSocket连接稳定性
- 数据格式验证
- 异常情况处理

#### DevTools测试步骤

**1. Network面板 - WebSocket连接验证**
```
操作步骤：
1. 打开 Network 面板
2. 勾选 "WS" 过滤器
3. 刷新页面，观察WebSocket连接建立
4. 验证连接状态为 "101 Switching Protocols"
5. 检查心跳包（ping/pong）正常发送
```

**2. Console面板 - 实时数据日志监控**
```
操作步骤：
1. 打开 Console 面板
2. 过滤日志：输入 "websocket" 或 "realtime"
3. 观察数据接收日志：
   - ✅ "WebSocket connected to ws://localhost:8000/ws/market"
   - ✅ "Received realtime data: [股票数据]"
   - ❌ 红色错误：连接断开、数据格式异常
```

**3. Application面板 - 数据存储验证**
```
操作步骤：
1. 打开 Application → IndexedDB
2. 查看 "MyStocksDB" → "realtime_quotes" 表
3. 验证数据是否正确存储和更新
4. 检查数据过期清理机制
```

#### 预期结果
- WebSocket连接稳定无断开
- 数据更新频率符合配置（默认5秒）
- 异常数据自动过滤和警告
- IndexedDB存储量控制在合理范围内

### 场景2：技术指标计算功能测试

#### 测试目标
- Web Workers计算准确性
- 计算性能（响应时间<100ms）
- 内存使用合理性
- 多指标并发计算

#### DevTools测试步骤

**1. Performance面板 - Web Workers性能分析**
```
操作步骤：
1. 打开 Performance 面板
2. 点击 "Start profiling and reload page"
3. 执行技术指标计算操作
4. 分析火焰图中的Web Workers耗时
5. 验证主线程未被阻塞
```

**2. Application面板 - Web Workers资源监控**
```
操作步骤：
1. 打开 Application → Shared Workers
2. 查看 "indicator-calculator" Worker状态
3. 监控内存使用情况
4. 检查Worker错误日志
```

**3. Console面板 - 计算结果验证**
```
操作步骤：
1. 打开 Console 面板
2. 执行计算操作，观察日志：
   - ✅ "Web Worker calculation completed in 45ms"
   - ✅ "MACD values: [计算结果]"
   - ❌ "Worker calculation timeout"
```

**4. Network面板 - Worker通信监控**
```
操作步骤：
1. 过滤 "WS" 或自定义协议
2. 观察Worker消息传递
3. 验证消息格式正确性
```

#### 性能基准
- **响应时间**: <100ms（从请求到结果）
- **内存使用**: <50MB（Worker独立内存）
- **CPU使用**: 主线程占用<10%
- **并发处理**: 支持同时计算8个指标

### 场景3：API接口功能测试

#### 测试目标
- RESTful API正确性
- 数据格式验证
- 错误处理机制
- 认证授权功能

#### DevTools测试步骤

**1. Network面板 - API请求分析**
```
操作步骤：
1. 打开 Network 面板
2. 执行API调用操作
3. 检查请求详情：
   - 请求方法：GET/POST/PUT/DELETE
   - 请求头：Authorization, Content-Type
   - 请求参数和Body
   - 响应状态码：200/201/400/401/500
   - 响应时间：<500ms
```

**2. Console面板 - API错误调试**
```
操作步骤：
1. 观察API调用日志
2. 检查错误信息：
   - 网络错误：超时、连接失败
   - 业务错误：参数验证失败
   - 认证错误：Token过期、无权限
```

**3. Application面板 - 认证状态检查**
```
操作步骤：
1. 查看 Cookies/LocalStorage
2. 验证JWT Token存在和有效性
3. 检查SessionStorage中的临时数据
```

#### API端点测试清单
```javascript
// 在Console中执行的测试脚本
const testAPIs = async () => {
  // 1. 健康检查
  const health = await fetch('/api/health');
  console.log('Health check:', health.status);

  // 2. 股票列表
  const stocks = await fetch('/api/stocks');
  console.log('Stocks API:', stocks.status);

  // 3. 技术指标计算
  const indicators = await fetch('/api/indicators/macd?symbol=600000');
  console.log('MACD API:', indicators.status);

  // 4. 实时行情（需要认证）
  const realtime = await fetch('/api/market/realtime', {
    headers: { 'Authorization': 'Bearer ' + token }
  });
  console.log('Realtime API:', realtime.status);
};
```

### 场景4：数据库连接与数据完整性测试

#### 测试目标
- TDengine时序数据连接
- PostgreSQL参考数据访问
- 数据同步机制
- 异常数据处理

#### DevTools测试步骤

**1. Network面板 - 数据库API调用**
```
操作步骤：
1. 过滤API请求到数据库服务
2. 检查响应时间和数据量
3. 验证分页和过滤功能
4. 测试大数据集加载性能
```

**2. Application面板 - 客户端数据缓存**
```
操作步骤：
1. 查看IndexedDB存储结构
2. 验证数据同步状态
3. 检查缓存过期机制
4. 监控存储使用量
```

**3. Performance面板 - 数据加载性能**
```
操作步骤：
1. 录制大数据加载过程
2. 分析网络请求和数据处理耗时
3. 识别性能瓶颈
4. 验证内存使用情况
```

### 场景5：响应式布局与移动端适配测试

#### 测试目标
- 桌面端布局完整性
- 移动端适配效果
- 触摸操作响应
- 不同分辨率兼容性

#### DevTools测试步骤

**1. Device Toolbar - 移动端模拟**
```
操作步骤：
1. 打开 Device Toolbar (Ctrl+Shift+M)
2. 选择不同设备：iPhone 15, iPad, Android
3. 测试关键功能：
   - 股票列表滚动
   - 图表缩放和拖拽
   - 表单输入和提交
   - 导航菜单折叠
```

**2. Elements面板 - 响应式样式验证**
```
操作步骤：
1. 调整浏览器宽度
2. 观察@media查询断点
3. 验证flex布局自适应
4. 检查元素重叠和溢出
```

**3. Performance面板 - 移动端性能**
```
操作步骤：
1. 模拟移动网络环境
2. 测试页面加载性能
3. 验证触摸事件响应
4. 监控内存使用
```

### 场景6：Web Workers异常情况测试

#### 测试目标
- Worker崩溃恢复
- 内存泄漏检测
- 超时处理机制
- 并发计算冲突

#### DevTools测试步骤

**1. Console面板 - Worker错误监控**
```
操作步骤：
1. 观察Worker相关错误日志
2. 测试Worker重启机制
3. 验证降级处理逻辑
```

**2. Application面板 - Worker状态检查**
```
操作步骤：
1. 查看Shared Workers列表
2. 监控Worker内存使用
3. 检查Worker生命周期
```

**3. Performance面板 - 资源使用分析**
```
操作步骤：
1. 录制长时间运行的Worker操作
2. 分析内存使用趋势
3. 检测潜在的内存泄漏
4. 验证垃圾回收机制
```

---

## 🧪 自动化测试脚本

### 1. API自动化测试脚本

在Console中执行以下脚本进行批量API测试：

```javascript
// MyStocks API自动化测试脚本
const runAPITests = async () => {
  console.log('🚀 开始MyStocks API自动化测试');

  const results = {
    total: 0,
    passed: 0,
    failed: 0,
    errors: []
  };

  // 测试用例定义
  const testCases = [
    {
      name: '健康检查',
      url: '/api/health',
      method: 'GET',
      expectedStatus: 200
    },
    {
      name: '获取股票列表',
      url: '/api/stocks',
      method: 'GET',
      expectedStatus: 200
    },
    {
      name: '技术指标计算',
      url: '/api/indicators/macd?symbol=600000',
      method: 'GET',
      expectedStatus: 200
    }
  ];

  for (const testCase of testCases) {
    results.total++;
    try {
      const response = await fetch(testCase.url, {
        method: testCase.method,
        headers: {
          'Authorization': localStorage.getItem('authToken') ?
            `Bearer ${localStorage.getItem('authToken')}` : undefined
        }
      });

      if (response.status === testCase.expectedStatus) {
        results.passed++;
        console.log(`✅ ${testCase.name}: 通过`);
      } else {
        results.failed++;
        results.errors.push(`${testCase.name}: 期望状态码 ${testCase.expectedStatus}, 实际 ${response.status}`);
        console.error(`❌ ${testCase.name}: 失败 - 状态码 ${response.status}`);
      }
    } catch (error) {
      results.failed++;
      results.errors.push(`${testCase.name}: ${error.message}`);
      console.error(`❌ ${testCase.name}: 错误 - ${error.message}`);
    }
  }

  // 输出测试报告
  console.log(`\n📊 测试完成报告:`);
  console.log(`总测试数: ${results.total}`);
  console.log(`通过: ${results.passed}`);
  console.log(`失败: ${results.failed}`);
  console.log(`成功率: ${((results.passed / results.total) * 100).toFixed(1)}%`);

  if (results.errors.length > 0) {
    console.log('\n❌ 失败详情:');
    results.errors.forEach(error => console.log(`  - ${error}`));
  }
};

// 执行测试
runAPITests();
```

### 2. 性能基准测试脚本

```javascript
// 性能测试脚本
const runPerformanceTests = async () => {
  console.log('📈 开始MyStocks性能测试');

  const metrics = {
    apiResponseTime: [],
    workerCalculationTime: [],
    pageLoadTime: 0,
    memoryUsage: []
  };

  // 1. API响应时间测试
  console.log('⏱️ 测试API响应时间...');
  for (let i = 0; i < 10; i++) {
    const start = performance.now();
    await fetch('/api/stocks');
    const end = performance.now();
    metrics.apiResponseTime.push(end - start);
  }

  // 2. Web Worker计算性能测试
  console.log('⚡ 测试Web Worker计算性能...');
  if (window.Worker) {
    // 这里可以添加具体的Worker性能测试
    console.log('Worker性能测试需要具体实现');
  }

  // 3. 内存使用监控
  if (performance.memory) {
    metrics.memoryUsage.push({
      used: performance.memory.usedJSHeapSize,
      total: performance.memory.totalJSHeapSize,
      limit: performance.memory.jsHeapSizeLimit
    });
  }

  // 输出性能报告
  console.log('\n📊 性能测试报告:');
  console.log(`API平均响应时间: ${metrics.apiResponseTime.reduce((a,b)=>a+b,0)/metrics.apiResponseTime.length}ms`);
  console.log(`API响应时间范围: ${Math.min(...metrics.apiResponseTime)}ms - ${Math.max(...metrics.apiResponseTime)}ms`);

  if (metrics.memoryUsage.length > 0) {
    const mem = metrics.memoryUsage[0];
    console.log(`内存使用: ${(mem.used / 1024 / 1024).toFixed(2)}MB / ${(mem.total / 1024 / 1024).toFixed(2)}MB`);
  }
};

// 执行性能测试
runPerformanceTests();
```

---

## 🎯 测试检查清单

### 每日测试检查点

- [ ] 前端页面正常加载，无JS错误
- [ ] WebSocket连接稳定，实时数据更新正常
- [ ] Web Workers计算响应时间<100ms
- [ ] API接口返回正确数据格式
- [ ] 数据库连接正常，数据同步无误
- [ ] 响应式布局在不同设备正常显示
- [ ] 内存使用稳定，无明显泄漏

### 发布前测试检查点

- [ ] Lighthouse性能评分>90
- [ ] 所有API接口响应时间<500ms
- [ ] Web Workers并发计算无冲突
- [ ] 大数据集加载性能符合要求
- [ ] 移动端触摸操作正常
- [ ] 跨浏览器兼容性测试通过

---

## 🐛 常见问题与解决方案

### 1. WebSocket连接问题
**症状**: 实时数据不更新，Console显示连接错误
**解决**:
- 检查后端WebSocket服务是否启动
- 验证防火墙设置允许端口8000
- 在Network面板检查WebSocket握手过程

### 2. Web Workers计算缓慢
**症状**: 技术指标计算耗时>200ms
**解决**:
- 检查Worker文件是否正确加载
- 验证Worker消息格式正确
- 在Performance面板分析Worker执行时间

### 3. API请求失败
**症状**: 接口返回400/500错误
**解决**:
- 检查请求参数格式
- 验证认证Token有效性
- 在Network面板查看请求详情

### 4. 内存泄漏
**症状**: 页面使用时间越长内存占用越大
**解决**:
- 使用Performance面板录制内存使用
- 检查IndexedDB清理机制
- 验证Worker内存释放

---

## 📊 测试报告生成

### 使用Lighthouse生成自动化报告

```
操作步骤：
1. 打开 Lighthouse 面板
2. 选择测试类别：Performance, Accessibility, Best Practices, SEO
3. 点击 "Generate report"
4. 导出HTML报告作为测试依据
```

### 自定义测试报告脚本

```javascript
// 生成MyStocks测试报告
const generateTestReport = () => {
  const report = {
    timestamp: new Date().toISOString(),
    environment: {
      userAgent: navigator.userAgent,
      url: window.location.href,
      viewport: `${window.innerWidth}x${window.innerHeight}`
    },
    tests: {
      websocket: checkWebSocketConnection(),
      webworkers: checkWebWorkersStatus(),
      apis: checkAPIsHealth(),
      performance: measurePerformance()
    }
  };

  console.log('📋 MyStocks测试报告:', report);
  return report;
};
```

---

## 📚 相关文档

- **Chrome DevTools基础教程**: `docs/04-测试/ChromeDevTools使用说明.md`
- **WSL2环境配置指南**: `docs/guides/chrome-devtools-wsl2-guide.md`
- **项目架构文档**: `docs/architecture/`
- **API文档**: `web/backend/docs/`
- **前端组件文档**: `web/frontend/docs/`

---

**测试环境**: WSL2 + Windows + Chrome
**最后更新**: 2026年1月23日
**测试人员**: Claude Code
**覆盖范围**: 前端功能、网络、性能、兼容性、安全性</content>
<parameter name="filePath">docs/guides/MYSTOCKS_TESTING_GUIDE.md