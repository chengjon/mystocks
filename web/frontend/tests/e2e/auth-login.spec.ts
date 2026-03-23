import { expect, test } from "@playwright/test";
const { loadPortEnv, resolveBackendConfig } = require("./helpers/port-env.js");

loadPortEnv(process.cwd());

const BACKEND_BASE_URL = resolveBackendConfig().baseUrl;

async function stubReadinessProbe(page: Parameters<typeof test>[0]["page"]) {
  for (const endpoint of ["**/api/health/ready", "**/health/ready"]) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          code: 200,
          message: "system ready",
          request_id: "e2e-auth-ready",
          data: { status: "ready" },
        }),
      });
    });
  }
}

async function stubDashboardApi(page: Parameters<typeof test>[0]["page"]) {
  await page.route("**/api/v1/market/overview", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          up_count: 1856,
          down_count: 1044,
          turnover: 9123,
        },
      }),
    });
  });
}

test.describe("Authentication Login Smoke", () => {
  test.beforeEach(async ({ page }) => {
    await stubReadinessProbe(page);
  });

  test("redirects unauthenticated users to login with return URL", async ({ page }) => {
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    await page.waitForURL(/\/login\?redirect=\/dashboard/, { timeout: 15000 });
    await expect(page.getByTestId("username-input")).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId("password-input")).toBeVisible();
    await expect(page.getByRole("button", { name: "SIGN IN" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "LOGIN" })).toBeVisible();
  });

  test("logs in through the UI and lands on the requested protected route", async ({ page, request }) => {
    await stubDashboardApi(page);
    await page.route("**/api/v1/auth/login", async (route) => {
      const response = await request.post(`${BACKEND_BASE_URL}/api/v1/auth/login`, {
        data: route.request().postData() ?? "",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      await route.fulfill({
        status: response.status(),
        headers: {
          "content-type": "application/json",
        },
        body: await response.text(),
      });
    });

    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });
    await page.waitForURL(/\/login\?redirect=\/dashboard/, { timeout: 15000 });
    await expect(page.getByTestId("username-input")).toBeVisible({ timeout: 15000 });

    await page.getByTestId("username-input").fill("admin");
    await page.getByTestId("password-input").fill("admin123");
    await page.getByRole("button", { name: "SIGN IN" }).click();

    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 });
    await expect.poll(
      async () =>
        page.evaluate(() => ({
          token: localStorage.getItem("auth_token"),
          user: localStorage.getItem("auth_user"),
        })),
      { timeout: 10000 },
    ).toMatchObject({
      token: expect.any(String),
      user: expect.stringContaining('"username":"admin"'),
    });
  });
});
