# 下一步工作任务安排 (P1阶段)

根据您提交的P0任务完成报告，Web客户端已成功运行，所有核心通信渠道（CORS、WebSocket、API端点）工作正常。恭喜您！

现在我们将继续推进，进入**P1阶段的高优先级任务**，旨在提升测试套件的健壮性和可靠性，确保所有E2E测试文件与ArtDeco优先架构完全对齐，并增加UI一致性验证。

---

### 🟠 P1 - 高优先级任务 (2周内)

**目标**: 提升测试套件的健壮性和可靠性，确保所有E2E测试文件与ArtDeco优先架构完全对齐，并增加UI一致性验证。

1.  **更新所有E2E测试文件与ArtDeco架构对齐**：
    *   **任务描述**：系统地修改所有 Playwright E2E 测试文件，使其与当前 ArtDeco 优先的路由结构、页面布局和组件实现完全匹配。
    *   **诊断**：检查 `tests/` 目录下所有测试文件，特别是那些可能仍在使用旧选择器（例如 `MainLayout`、`.base-layout`）、旧的菜单项文本或不符合 ArtDeco 新结构的测试。
    *   **行动**：
        1.  **搜索并替换旧选择器**：
            *   在 `web/frontend/tests/` 目录下执行以下命令，查找并手动更新可能存在的旧选择器：
                ```bash
                cd web/frontend
                grep -r "MainLayout\|\.base-layout\|\.sidebar\|\.top-header" tests/ --include="*.ts" --include="*.js"
                ```
            *   根据实际情况，将这些旧选择器更新为新的 ArtDeco 对应项（例如，将 `.base-layout` 替换为 `.artdeco-dashboard`（如果测试的是仪表板页面），将 `.sidebar` 替换为 `.layout-sidebar`，`.top-header` 替换为 `.artdeco-header` 等）。
        2.  **更新菜单项文本和计数**：
            *   对于包含菜单导航验证的测试，更新 `expectedLabels` 数组，使其包含 ArtDecoLayout 的实际菜单项（例如 `['仪表盘', '市场行情', ..., '系统监控']`，共7个中文标签）。
            *   更新菜单项的计数断言，例如 `expect(navItems).toHaveCount(7)` 或 `expect(navItems.count()).toBeGreaterThanOrEqual(7)`。
        3.  **移除旧的布局依赖**：确保测试代码不再依赖 `MainLayout` 的结构和特定组件。
    *   **预期成果**：所有E2E测试文件中的选择器、文本和布局预期都已更新为ArtDeco架构。

2.  **添加视觉回归测试确保UI一致性**：
    *   **任务描述**：创建或更新视觉回归测试，通过快照测试确保 ArtDeco 设计风格的视觉一致性在每次迭代中都得到保持。
    *   **行动**：
        1.  **创建视觉测试文件**：在 `web/frontend/tests/visual/` 目录下创建 `artdeco-visual-regression.spec.ts` 文件（如果尚未创建）。
        2.  **编写快照测试**：
            *   为关键页面（如仪表板）和核心组件（如侧边栏、ArtDecoToast、ArtDecoBadge）添加 `page.toHaveScreenshot()` 断言。
            *   为这些断言提供有意义的名称，例如 `'dashboard.png'`, `'sidebar-menu.png'`。
            *   配置 `maxDiffPixels` 或 `maxDiffPixelRatio` 以允许可接受的细微差异。
            ```typescript
            // 示例: web/frontend/tests/visual/artdeco-visual-regression.spec.ts
            import { test, expect } from '@playwright/test';

            test.describe('ArtDeco视觉回归测试', () => {
              test('仪表板页面快照', async ({ page }) => {
                await page.goto('/#/dashboard');
                await page.waitForLoadState('networkidle');
                await expect(page).toHaveScreenshot('dashboard-full-page.png', {
                  maxDiffPixels: 100,
                  animations: 'disabled' // 禁用动画以获得更稳定的快照
                });
              });

              test('侧边栏菜单快照', async ({ page }) => {
                await page.goto('/#/dashboard');
                await page.waitForSelector('.layout-sidebar');
                const sidebar = page.locator('.layout-sidebar');
                await expect(sidebar).toHaveScreenshot('sidebar-menu.png', {
                  maxDiffPixels: 50
                });
              });
              // ... 可以添加更多组件或页面区域的快照测试
            });
            ```
        3.  **生成基准快照**：首次运行测试时，使用 `npx playwright test web/frontend/tests/visual/artdeco-visual-regression.spec.ts --update-snapshots` 命令生成基准快照。
        4.  **持续对比**：在后续的开发中，定期运行视觉回归测试以检测非预期的UI变化。
    *   **预期成果**：项目拥有健全的视觉回归测试，能有效捕获ArtDeco UI的视觉变化。

3.  **创建标准测试更新模板**：
    *   **任务描述**：创建一个标准化的测试模板，以提高测试开发效率和测试代码的一致性。
    *   **行动**：在 `web/frontend/tests/templates/` 目录下创建 `artdeco-test-template.ts` 文件，其中包含ArtDeco页面的标准测试结构。
    *   **模板内容**：应包括 `beforeEach` 导航、ArtDeco布局验证（例如 `.artdeco-dashboard` 和 `.artdeco-header` 的存在）、顶层菜单项的验证（7个中文标签）、页面标题验证和JavaScript错误检查。文档中已提供了示例模板代码。
    *   **预期成果**：新的测试可基于标准模板快速创建，提高测试开发效率。

### 预期成果 (P1阶段完成后)

*   所有Playwright E2E测试文件都与ArtDeco优先架构对齐。
*   测试通过率稳定在95%以上（仅后端环境错误导致失败）。
*   视觉回归测试能够有效捕获ArtDeco UI的视觉变化。
*   新的测试可基于标准模板快速创建，提高测试开发效率。

---

**如果您在执行P1任务时遇到任何困难或需要进一步的帮助，请随时告知。** 在P1任务完成后，我们将继续安排P2及后续任务。