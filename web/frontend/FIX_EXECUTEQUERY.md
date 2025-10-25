# 修复说明：qs_* 查询执行失败问题

## 问题描述
用户报告：在查询列表选择 qs_* 进行查询时，提示"执行失败"

## 根本原因
树形节点的数据结构不匹配导致参数传递错误。

### 问题代码
```vue
<!-- 错误：传递的是整个节点对象 -->
<el-button @click.stop="executeQuery(data)">
  执行
</el-button>
```

**数据结构**：
```javascript
// 树形节点结构
{
  label: 'qs_1',      // 显示名称
  type: 'query',       // 节点类型
  data: {              // ← 真正的查询数据在这里
    query_name: 'qs_1',
    query_text: '请列举出...',
    description: '...',
    // ...其他字段
  }
}
```

当点击执行时，`data` 是整个节点对象，所以 `data.query_name` 是 `undefined`！

## 修复方案

### 修改点
**文件**: `src/components/market/WencaiPanelV2.vue`

**修改**: 第 73 行
```vue
<!-- 修复：传递节点的data属性（真正的查询对象） -->
<el-button @click.stop="executeQuery(data.data)">
  执行
</el-button>
```

### 额外改进
添加了详细的错误日志：
```javascript
const executeQuery = async (queryData) => {
  console.log('executeQuery called with:', queryData)
  console.log('Calling API with query_name:', queryData.query_name)
  console.log('Response status:', response.status)
  console.log('Query response:', data)
  console.error('Execute query error:', error)
}
```

## 测试步骤

1. **硬刷新浏览器**
   ```
   Ctrl + Shift + R (Windows/Linux)
   Cmd + Shift + R (Mac)
   ```

2. **打开开发者工具**
   - 按 `F12`
   - 切换到 Console 标签

3. **执行查询**
   - 点击左侧树形："默认查询" → "qs_1"
   - 鼠标悬停在 qs_1 上
   - 点击"执行"按钮

4. **观察结果**

   **成功的Console输出**：
   ```
   executeQuery called with: {query_name: 'qs_1', query_text: '...', ...}
   Calling API with query_name: qs_1
   Response status: 200
   Query response: {success: true, total_records: 13, ...}
   ```

   **成功的页面显示**：
   - ✅ 右上角显示：查询完成：13 条数据
   - ✅ 表格上方显示：查询语句：...
   - ✅ 表格显示数据

   **如果仍然失败**：
   - 检查 Console 中的错误信息
   - 截图错误信息并反馈

## 后端验证

可以直接测试后端API：
```bash
curl -X POST http://localhost:8000/api/market/wencai/query \
  -H "Content-Type: application/json" \
  -d '{"query_name":"qs_1","pages":1}'
```

**预期返回**：
```json
{
  "success": true,
  "message": "数据获取成功",
  "query_name": "qs_1",
  "total_records": 13,
  "new_records": 0,
  "duplicate_records": 13,
  "table_name": "wencai_qs_1",
  "fetch_time": "2025-10-18T16:19:01.977921"
}
```

## 其他修复

如果后端API正常但前端仍有问题，检查：

1. **CORS问题**
   - Console中是否有CORS错误
   - 后端服务是否允许前端域名

2. **网络问题**
   - 检查 Network 标签
   - 查看请求是否发送成功
   - 查看响应状态码和内容

3. **浏览器缓存**
   - 清除浏览器缓存
   - 禁用浏览器扩展

## 验证清单

测试以下所有qs_*查询：
- [ ] qs_1 执行成功
- [ ] qs_2 执行成功
- [ ] qs_3 执行成功
- [ ] qs_4 执行成功
- [ ] qs_5 执行成功
- [ ] qs_6 执行成功
- [ ] qs_7 执行成功
- [ ] qs_8 执行成功
- [ ] qs_9 执行成功

---

**修复时间**: 2025-10-18
**修复文件**: WencaiPanelV2.vue
**修复行数**: 第 73 行
**状态**: ✅ 已修复
