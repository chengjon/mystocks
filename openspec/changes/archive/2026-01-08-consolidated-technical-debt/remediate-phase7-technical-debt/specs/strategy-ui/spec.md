# Strategy UI Capability Spec (Delta)

## MODIFIED Requirements

### Requirement: 策略管理页面MUST提供完整CRUD功能 (MUST)

**ID**: RQ-STRATEGYUI-001
**Priority**: Medium
**Status**: Modified

**Description**:
策略管理页面MUST提供策略的创建、读取、更新、删除（CRUD）功能，支持策略列表展示、搜索筛选、分页。

**Rationale**:
当前策略管理页面功能不完整，缺少创建和编辑功能，用户体验差。

**Original Requirement**:
策略管理页面应该能查看策略列表。

**Modified Requirement**:
策略管理页面MUST提供完整的CRUD功能，包括列表展示、创建表单、编辑对话框、删除确认。

#### Scenario: 查看策略列表

**Given**:
- 用户已登录
- 用户访问策略管理页面 `/strategy-hub/management`

**When**:
- 页面加载完成
- 后端API返回策略列表数据

**Then**:
- 显示策略列表表格
- 每行显示: 策略名称、类型、状态、创建时间、操作按钮
- 表格顶部有搜索框和筛选器
- 表格底部有分页组件

**Verification Steps**:
1. 访问 `/strategy-hub/management`
2. 验证表格组件正确渲染（`el-table`）
3. 验证表格列包含: 名称、类型、状态、创建时间、操作
4. 验证搜索框和筛选器存在
5. 验证分页组件存在
6. 检查网络请求: `GET /api/strategy/?page=1&page_size=20`

#### Scenario: 创建新策略

**Given**:
- 用户在策略管理页面
- 用户点击"创建策略"按钮

**When**:
- 打开创建策略对话框
- 用户填写策略信息:
  - 策略名称: "双均线策略"
  - 策略类型: "技术分析"
  - 策略参数: `{"short_period": 5, "long_period": 20}`
- 用户点击"提交"按钮

**Then**:
- 表单验证通过（名称、类型、参数必填）
- 发送POST请求到 `/api/strategy/`
- 创建成功后关闭对话框
- 刷新策略列表，新策略出现在列表中
- 显示成功提示"策略创建成功"

**Verification Steps**:
1. 点击"创建策略"按钮，验证对话框打开
2. 检查表单包含: 名称输入框、类型选择器、参数编辑器
3. 填写表单并提交，检查网络请求: `POST /api/strategy/`
4. 验证请求体包含正确的字段
5. 验证创建成功后列表刷新
6. 验证显示成功提示（ElMessage）

#### Scenario: 编辑现有策略

**Given**:
- 策略列表中存在策略 "双均线策略"
- 用户点击该策略的"编辑"按钮

**When**:
- 打开编辑策略对话框
- 对话框预填充当前策略信息
- 用户修改策略参数为 `{"short_period": 10, "long_period": 30}`
- 用户点击"保存"按钮

**Then**:
- 表单验证通过
- 发送PUT请求到 `/api/strategy/{id}`
- 保存成功后关闭对话框
- 刷新策略列表，策略参数已更新
- 显示成功提示"策略更新成功"

**Verification Steps**:
1. 点击"编辑"按钮，验证对话框打开
2. 检查表单预填充了当前策略信息
3. 修改参数并保存，检查网络请求: `PUT /api/strategy/{id}`
4. 验证请求体包含更新后的字段
5. 验证列表中策略参数已更新
6. 验证显示成功提示

#### Scenario: 删除策略

**Given**:
- 策略列表中存在策略 "测试策略"
- 用户点击该策略的"删除"按钮

**When**:
- 打开删除确认对话框
- 对话框提示: "确定要删除策略 '测试策略' 吗？此操作不可恢复。"
- 用户点击"确认"按钮

**Then**:
- 发送DELETE请求到 `/api/strategy/{id}`
- 删除成功后关闭对话框
- 刷新策略列表，该策略不再显示
- 显示成功提示"策略删除成功"

**Verification Steps**:
1. 点击"删除"按钮，验证确认对话框打开
2. 检查对话框包含警告信息和确认/取消按钮
3. 点击"确认"，检查网络请求: `DELETE /api/strategy/{id}`
4. 验证列表中该策略已移除
5. 验证显示成功提示

---

### Requirement: 策略表单MUST验证输入合法性 (MUST)

**ID**: RQ-STRATEGYUI-002
**Priority**: Medium
**Status**: Added

**Description**:
策略创建和编辑表单MUST验证用户输入，包括必填字段、数据格式、取值范围。

**Rationale**:
防止非法数据提交到后端，提高用户体验。

#### Scenario: 表单验证必填字段

**Given**:
- 用户打开创建策略对话框
- 对话框包含必填字段: 策略名称、策略类型、策略参数

**When**:
- 用户不填写任何字段，直接点击"提交"按钮

**Then**:
- 表单验证失败
- 每个必填字段下方显示错误提示: "此字段为必填项"
- 不发送网络请求
- 对话框保持打开

**Verification Steps**:
1. 打开创建对话框，不填写任何字段
2. 点击"提交"按钮
3. 验证表单显示3个错误提示（名称、类型、参数）
4. 验证网络面板无POST请求
5. 验证对话框未关闭

#### Scenario: 策略参数MUST是有效JSON

**Given**:
- 用户填写策略名称和类型
- 策略参数字段期望JSON格式

**When**:
- 用户输入无效JSON: `{short_period: 5}` （缺少引号）
- 用户点击"提交"按钮

**Then**:
- 表单验证失败
- 参数字段下方显示错误提示: "参数MUST是有效的JSON格式"
- 不发送网络请求

**Verification Steps**:
1. 填写名称和类型，参数输入无效JSON
2. 点击"提交"
3. 验证显示JSON格式错误提示
4. 修正JSON为 `{"short_period": 5}`，验证错误提示消失

---

## Related Capabilities

- **code-quality**: 策略管理组件代码MUST通过Ruff和MyPy检查
- **type-safety**: 策略数据结构MUST有TypeScript类型定义
- **e2e-testing**: 策略CRUD操作MUST有E2E测试覆盖
