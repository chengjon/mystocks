const { test, expect } = require("@playwright/test");

test.describe("MyStocks 健康检查测试", () => {
  test("CASE-API-HEALTH-001: API健康检查", async ({ request }) => {
    console.log("CASE-API-HEALTH-001: 开始API健康检查");
    const response = await request.get("http://localhost:8000/health");
    expect(response.status()).toBe(200);
    console.log("✅ CASE-API-HEALTH-001: API健康检查通过");
  });

  test("CASE-FRONTEND-HEALTH-001: 前端健康检查", async ({ page }) => {
    console.log("CASE-FRONTEND-HEALTH-001: 开始前端健康检查");
    await page.goto("http://localhost:3001");
    await expect(page.locator("body")).toBeVisible();
    console.log("✅ CASE-FRONTEND-HEALTH-001: 前端健康检查通过");
  });
});
