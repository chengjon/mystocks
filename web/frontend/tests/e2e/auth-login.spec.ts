import { expect, test } from "@playwright/test";
const { loadPortEnv } = require("./helpers/port-env.js");

loadPortEnv(process.cwd());

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
  await page.route(/https?:\/\/[^/]+\/api\/.*/, async (route) => {
    const { pathname } = new URL(route.request().url());

    if (pathname === "/api/health/ready") {
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
      return;
    }

    if (pathname === "/api/csrf-token") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          code: 200,
          message: "csrf ok",
          data: { csrf_token: "e2e-auth-csrf" },
        }),
      });
      return;
    }

    if (pathname === "/api/v1/auth/login") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          code: 200,
          message: "LOGIN SUCCESSFUL",
          data: {
            token: "e2e-auth-token",
            token_type: "bearer",
            expires_in: 7200,
            user: {
              id: 1,
              username: "admin",
              email: "admin@example.com",
              role: "admin",
              permissions: ["*"],
            },
          },
          request_id: "e2e-auth-login",
        }),
      });
      return;
    }

    if (pathname === "/api/v1/market/overview" || pathname === "/api/v1/data/markets/overview") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          code: 200,
          message: "ok",
          data: {
            up_count: 1856,
            down_count: 1044,
            turnover: 9123,
          },
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        code: 200,
        message: "ok",
        data: [],
      }),
    });
  });
}

test.describe("Authentication Login Smoke", () => {
  test.beforeEach(async ({ page }) => {
    await stubReadinessProbe(page);
  });

  test("redirects root requests through the canonical dashboard login redirect", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });

    await page.waitForURL(/\/login\?redirect=\/dashboard/, { timeout: 15000 });
    await expect(page.getByTestId("username-input")).toBeVisible({ timeout: 15000 });
  });

  test("redirects unauthenticated users to login with return URL", async ({ page }) => {
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    await page.waitForURL(/\/login\?redirect=\/dashboard/, { timeout: 15000 });
    await expect(page.getByTestId("username-input")).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId("password-input")).toBeVisible();
    await expect(page.getByRole("button", { name: "SIGN IN" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "LOGIN" })).toBeVisible();
  });

  test("redirects legacy dealing-room requests through the canonical dashboard login redirect", async ({ page }) => {
    await page.goto("/dealing-room", { waitUntil: "domcontentloaded" });

    await page.waitForURL(/\/login\?redirect=\/dashboard/, { timeout: 15000 });
    await expect(page.getByTestId("username-input")).toBeVisible({ timeout: 15000 });
  });

  test("logs in through the UI and lands on the requested protected route", async ({ page }) => {
    await stubDashboardApi(page);

    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });
    await page.waitForURL(/\/login\?redirect=\/dashboard/, { timeout: 15000 });
    await expect(page.getByTestId("username-input")).toBeVisible({ timeout: 15000 });

    await page.getByTestId("username-input").fill("admin");
    await page.getByTestId("password-input").fill("admin123");
    await page.getByRole("button", { name: "SIGN IN" }).click();

    await expect.poll(() => new URL(page.url()).pathname, { timeout: 20000 }).toBe("/dashboard");
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
