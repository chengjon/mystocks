# TradingView 图表加载故障排查指南

## 问题：图表不显示，提示 "TradingView JS 库未加载"

### 原因分析

TradingView 官方 CDN (`https://s3.tradingview.com/tv.js`) 在中国大陆可能存在访问问题：
- 网络连接速度慢
- 被防火墙屏蔽
- DNS 解析失败

### 解决方案

#### 方案 1：使用代理（推荐）

如果您有 VPN 或代理，请启用后刷新页面。

#### 方案 2：检查浏览器控制台

1. 打开浏览器开发者工具（F12）
2. 切换到"控制台"（Console）标签
3. 刷新页面并查看是否有错误信息
4. 查找关于 `tv.js` 的加载错误

#### 方案 3：验证 TradingView CDN 可访问性

在浏览器中直接访问：`https://s3.tradingview.com/tv.js`

- ✅ **如果可以访问**：显示 JavaScript 代码，说明 CDN 正常
- ❌ **如果无法访问**：显示错误或超时，需要使用其他方案

#### 方案 4：使用替代方案（暂时关闭 TradingView）

如果 TradingView 无法使用，系统提供其他图表方案：

1. **使用 ECharts 图表**（已集成）
   - 访问"技术分析"页面查看 K 线图
   - 完全国内可用，无需外部依赖

2. **使用第三方图表库**（如需要可集成）
   - AntV G2
   - Chart.js
   - Highcharts

### 调试步骤

#### 第 1 步：检查网络请求

打开浏览器开发者工具 → 网络（Network）标签：

```
查找：tv.js
状态：
  - 200 OK ✅ 正常加载
  - 404/403 ❌ CDN 问题
  - 超时 ❌ 网络问题
```

#### 第 2 步：检查控制台日志

点击"加载图表"按钮后，查看控制台输出：

```javascript
// 正常情况
Checking TradingView availability...
TradingView library is available
Creating TradingView widget with config: {...}

// 异常情况
Checking TradingView availability...
TradingView not available: Error: TradingView 库加载超时
Please check if https://s3.tradingview.com/tv.js is accessible
```

#### 第 3 步：手动测试 TradingView 对象

在浏览器控制台输入：

```javascript
typeof window.TradingView
// 应该返回 "object" 或 "function"
// 如果返回 "undefined"，说明库未加载
```

### 临时解决方案

#### 选项 1：使用 API 返回的配置（仅配置生成）

虽然无法显示 TradingView 图表，但后端 API 仍然可以生成标准的配置：

```bash
# 获取图表配置
curl -X POST http://localhost:8000/api/tradingview/chart/config \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600000",
    "market": "CN",
    "theme": "dark"
  }'
```

配置可用于：
- 导出到其他支持 TradingView 的平台
- 作为参考配置自定义图表

#### 选项 2：使用其他功能

OpenStock 演示页面的其他功能不依赖 TradingView：
- ✅ 股票搜索 - 完全可用
- ✅ 实时行情 - 完全可用
- ✅ 股票新闻 - 完全可用
- ✅ 自选股管理 - 完全可用
- ⚠️ TradingView 图表 - 需要外网访问

### 为开发者：集成替代图表方案

如果需要完全国内化的图表解决方案，可以考虑：

#### 使用 ECharts（推荐）

```vue
<template>
  <div ref="chartContainer" style="width: 100%; height: 500px"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const chartContainer = ref(null)

onMounted(() => {
  const chart = echarts.init(chartContainer.value)

  const option = {
    // K线图配置
    xAxis: { type: 'category', data: [...] },
    yAxis: { type: 'value' },
    series: [{
      type: 'candlestick',
      data: [...]
    }]
  }

  chart.setOption(option)
})
</script>
```

#### 安装 ECharts

```bash
cd /opt/claude/mystocks_spec/web/frontend
npm install echarts
```

### 常见问题

**Q: 为什么 TradingView 加载这么慢？**
A: TradingView 的服务器在海外，中国大陆访问速度较慢。建议使用代理或等待完全加载。

**Q: 能否使用国内 CDN？**
A: TradingView 官方不提供国内 CDN 镜像。如需国内方案，建议使用 ECharts 等国产图表库。

**Q: 其他功能是否受影响？**
A: 不受影响。只有 TradingView 图表依赖外部 CDN，其他功能均使用国内数据源。

**Q: 如何完全移除 TradingView 依赖？**
A: 删除 `index.html` 中的 TradingView script 标签，并在演示页面中隐藏或移除该标签页。

### 推荐方案总结

| 场景 | 推荐方案 | 优先级 |
|------|---------|--------|
| 有外网访问 | 使用 TradingView（当前方案） | ⭐⭐⭐⭐⭐ |
| 无外网访问 | 集成 ECharts | ⭐⭐⭐⭐ |
| 快速开发 | 使用系统现有技术分析页面 | ⭐⭐⭐ |
| 临时使用 | 仅使用 API 配置生成 | ⭐⭐ |

### 获取帮助

- 项目文档：`OPENSTOCK_DEMO_PAGE_GUIDE.md`
- API 文档：http://localhost:8000/api/docs
- 技术支持：查看项目 README.md

---

**文档版本**: v1.0
**最后更新**: 2025-10-20
