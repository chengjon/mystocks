# API与Web前端数据使用分析工具

## 概述

这个工具用于扫描和分析MyStocks项目中的API端点和前端页面的数据请求情况，生成详细的对比报告，帮助发现API使用情况和潜在的问题。

## 功能特性

- ✅ **API端点扫描**：自动扫描后端API路由，提取端点信息
- ✅ **前端调用分析**：分析Vue/TS/JS文件中的API调用
- ✅ **数据使用对比**：对比API返回数据和前端实际使用情况
- ✅ **数据源识别**：识别API使用的数据源（PostgreSQL/TDengine/Mock）
- ✅ **增量分析**：支持只分析修改的文件，提高分析速度
- ✅ **详细报告**：生成Markdown和JSON格式的详细报告
- ✅ **可视化展示**：使用图表和表格展示分析结果

## 项目结构

```
scripts/
├── analyze_api_data_usage.py          # 主入口（向后兼容）
├── analyze_api_data_usage/            # 核心模块
│   ├── __init__.py                    # 模块导出
│   ├── api_analyzer.py                # API分析器 + 前端分析器
│   └── report_generator.py            # 报告生成器
└── dev/
    └── analyze_api_data_usage_quick.sh # 快速启动脚本
```

## 使用方法

### 方式1: 使用快速启动脚本（推荐）

```bash
# 完整分析
bash scripts/dev/analyze_api_data_usage_quick.sh

# 增量分析（只分析修改的文件）
bash scripts/dev/analyze_api_data_usage_quick.sh --incremental
```

### 方式2: 直接运行Python脚本

```bash
# 完整分析
python scripts/analyze_api_data_usage.py

# 增量分析
python scripts/analyze_api_data_usage.py --incremental
```

### 命令行参数

- `--incremental, -i`：增量分析模式，只分析修改的文件
- `--help`：显示帮助信息

## 输出文件

工具会在 `docs/reports/` 目录下生成以下文件：

### 1. API_WEB_DATA_USAGE_REPORT.md

主要的Markdown报告，包含：
- **概览统计**：API端点总数、前端页面总数、API调用总数、已使用/未使用的API
- **API使用情况可视化**：ASCII字符画展示使用率
- **API端点统计**：按HTTP方法分类（GET/POST/PUT/DELETE）
- **API端点详情**：按路径分组，包含方法、返回模型、数据源、文件位置
- **前端页面API调用清单**：每个页面调用的API列表
- **数据使用分析**：未使用的API、未实现的API
- **数据库依赖分析**：各API依赖的数据库表
- **数据源类型统计**：PostgreSQL/TDengine/Mock使用情况
- **推荐改进建议**：基于分析结果的优化建议

### 2. api_data_inventory.json

API数据清单的JSON格式，包含：
```json
{
  "generated_at": "2026-01-02T00:32:22",
  "total_endpoints": 356,
  "endpoints": [
    {
      "path": "/api/endpoint",
      "method": "GET",
      "return_model": "Dict",
      "data_source": "postgresql",
      "file": "api_file.py",
      "line": 123
    }
  ]
}
```

### 3. web_api_calls.json

Web前端API调用清单的JSON格式，包含：
```json
{
  "generated_at": "2026-01-02T00:32:22",
  "total_pages": 22,
  "total_api_calls": 64,
  "pages": [...],
  "api_calls": [
    {
      "page": "PageName.vue",
      "api_endpoint": "/api/endpoint",
      "call_type": "HTTP",
      "method": "get",
      "line": 45
    }
  ]
}
```

## 分析维度

### API端点维度

- 路由路径
- HTTP方法（GET/POST/PUT/DELETE）
- 返回模型/Schema
- 数据字段列表
- 依赖的数据库表
- 数据源类型（PostgreSQL/TDengine/Mock）
- 源文件位置和行号

### Web页面维度

- 页面路径
- 调用的API端点
- API调用类型（HTTP/API对象）
- 调用的方法
- 使用的行号

## 报告解读

### 概览统计（基于最新数据）

根据最新的分析报告（2026-01-02）：

- **API端点总数**: 356个
- **前端页面总数**: 22个
- **API调用总数**: 64次
- **已使用的API**: 1个（0.3%）
- **未使用的API**: 355个（99.7%）
- **前端请求但未实现的API**: 0个

### HTTP方法分布

| 方法 | 数量 | 占比 |
|------|------|------|
| GET | 217 | 61.0% |
| POST | 114 | 32.0% |
| DELETE | 14 | 3.9% |
| PUT | 11 | 3.1% |

### 可视化图表

报告包含ASCII字符画的可视化图表，直观展示API使用情况：

```
已使用:  1 (0.3%)
未使用: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 355 (99.7%)
```

### 推荐改进

报告会根据分析结果提供改进建议：

| 优先级 | 类别 | 建议 |
|--------|------|------|
| 高 | 代码清理 | 有355个API端点未被前端使用，建议评估是否需要删除或标记为deprecated |
| 中 | API集成 | 前端仅使用了0.3%的API，建议检查前端是否正确集成后端接口 |
| 低 | 文档完善 | 建议为所有API端点添加文档说明 |

## 技术实现

### API分析（api_analyzer.py）

使用正则表达式解析Python FastAPI路由：
- 识别 `@router.get("/path")` 和 `@app.get("/path")` 格式的装饰器
- 提取HTTP方法和路径
- 解析async函数定义
- 识别返回模型类型注解
- 分析数据源类型（通过导入和数据库操作模式）

**核心类**：
- `APIAnalyzer`: 扫描后端API目录，提取所有端点信息
- `FrontendAnalyzer`: 扫描前端目录，提取API调用

### 前端分析（api_analyzer.py）

使用正则表达式解析Vue/TS/JS文件：
- 识别HTTP调用（`axios.get()`, `request.post()`等）
- 识别API对象调用（`dataApi.xxx()`, `authApi.xxx()`等）
- 提取API端点路径
- 统计API调用次数

### 报告生成（report_generator.py）

**核心类**：
- `ReportGenerator`: 生成Markdown和JSON格式报告

**主要方法**：
- `generate_json_reports()`: 生成JSON清单
- `generate_markdown_report()`: 生成Markdown报告
- `_generate_overview()`: 生成概览统计
- `_generate_api_statistics()`: 生成API统计
- `_generate_recommendations()`: 生成改进建议

### 增量分析

使用文件MD5哈希值检测文件变化：
- 首次运行：分析所有文件，记录文件哈希
- 增量运行：只分析哈希值变化的文件
- 缓存文件：`.analysis_cache.json`（存储在项目根目录）

**缓存结构**：
```json
{
  "last_run": "2026-01-02T00:32:22",
  "file_hashes": {
    "web/backend/app/api/file.py": "abc123...",
    "web/frontend/src/views/Page.vue": "def456..."
  }
}
```

## 注意事项

1. **文件编码**：工具假设所有文件使用UTF-8编码
2. **正则表达式限制**：某些复杂的API调用模式可能无法识别
3. **类型推断**：返回模型和数据字段的提取基于简单的正则匹配，可能不完全准确
4. **数据库依赖**：数据库表依赖检测基于常见的数据库操作模式，可能遗漏某些依赖
5. **路径依赖**：工具必须在项目根目录运行，依赖以下目录结构：
   - `web/backend/app/api/` - 后端API目录
   - `web/frontend/src/` - 前端源码目录
   - `docs/reports/` - 报告输出目录

## 常见问题

### Q: 为什么有些API调用没有被检测到？

A: 工具使用正则表达式匹配，如果API调用使用了动态构建、字符串拼接等复杂方式，可能无法检测到。可以手动检查相关文件。

**示例**：
```javascript
// ✅ 可以检测到
axios.get('/api/users')

// ❌ 可能检测不到
const endpoint = '/api/' + resource
axios.get(endpoint)
```

### Q: 如何更新分析结果？

A: 直接重新运行工具即可。如果文件没有修改，可以使用`--incremental`参数加快分析速度。

```bash
# 完整重新分析
bash scripts/dev/analyze_api_data_usage_quick.sh

# 增量分析（更快）
bash scripts/dev/analyze_api_data_usage_quick.sh --incremental
```

### Q: 报告中显示的"未使用的API"是否一定需要删除？

A: 不一定。这些API可能是：
- 为未来的功能预留的
- 供其他系统或第三方使用的
- 用于内部管理的API
- 移动端或其他客户端使用的API

建议结合实际业务需求评估。

### Q: 为什么API使用率这么低（0.3%）？

A: 可能的原因：
1. 前端使用了API封装层，工具未能识别
2. 部分API为历史遗留，已不再使用
3. 部分API为预留接口，尚未实现前端功能
4. 工具的正则表达式匹配规则需要优化

建议：
- 检查前端API调用封装方式
- 评估是否需要清理历史API
- 优化工具的匹配规则

### Q: 如何清理缓存重新分析？

A: 删除项目根目录下的 `.analysis_cache.json` 文件：

```bash
rm .analysis_cache.json
bash scripts/dev/analyze_api_data_usage_quick.sh
```

## 扩展和定制

如果需要添加自定义的分析逻辑，可以修改以下部分：

### 1. API提取规则

修改 `scripts/analyze_api_data_usage/api_analyzer.py` 中的 `APIAnalyzer._analyze_python_file_with_regex()` 方法：

```python
def _analyze_python_file_with_regex(self, file_path: Path) -> List[Dict]:
    # 添加自定义的正则表达式模式
    custom_pattern = r'@custom_decorator\("([^"]+)"\)'
    # ...
```

### 2. 前端调用提取

修改 `scripts/analyze_api_data_usage/api_analyzer.py` 中的 `FrontendAnalyzer._extract_vue_api_calls()` 方法：

```python
def _extract_vue_api_calls(self, content: str, file_path: str) -> List[Dict]:
    # 添加自定义的API调用模式
    custom_patterns = [
        r'customApi\.(\w+)\(["\']([^"\']+)["\']',
    ]
    # ...
```

### 3. 报告生成

修改 `scripts/analyze_api_data_usage/report_generator.py` 中的 `ReportGenerator` 类方法：

```python
def _generate_custom_section(self) -> str:
    """生成自定义报告章节"""
    # 添加自定义的报告内容
    return "## 自定义分析\n\n..."
```

### 4. 数据源识别

修改 `scripts/analyze_api_data_usage/api_analyzer.py` 中的 `APIAnalyzer._determine_source_type()` 方法：

```python
def _determine_source_type(self, content: str) -> str:
    # 添加自定义的数据源识别逻辑
    if 'custom_db' in content:
        return 'custom_database'
    # ...
```

## 性能优化

### 增量分析性能

- **首次运行**：扫描所有文件（~356个API文件 + ~22个前端文件）
- **增量运行**：仅扫描修改的文件（通常<10个文件）
- **性能提升**：约10-50倍（取决于修改文件数量）

### 建议

1. **日常开发**：使用 `--incremental` 参数
2. **重大变更后**：运行完整分析
3. **定期清理**：每周清理一次缓存，运行完整分析

## 相关文档

- **详细使用文档**: `docs/reports/ANALYSIS_TOOL_README.md`
- **最新分析报告**: `docs/reports/API_WEB_DATA_USAGE_REPORT.md`
- **API清单**: `docs/reports/api_data_inventory.json`
- **前端调用清单**: `docs/reports/web_api_calls.json`

## 许可证

本工具是MyStocks项目的一部分，遵循项目的开源许可证。

## 联系方式

如有问题或建议，请通过GitHub Issues反馈。

---

**最后更新**: 2026-03-04
**工具版本**: 1.0
**兼容项目版本**: MyStocks v1.0+
