"use strict";

const { URL } = require("node:url");

const LHCI_USER = {
  id: 1,
  username: "lhci-admin",
  email: "lhci-admin@mystocks.local",
  role: "admin",
  permissions: ["*"],
};

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

module.exports = async (browser, { url }) => {
  const page = await browser.newPage();

  try {
    const targetUrl = new URL(url);
    const loginUrl = new URL("/login", targetUrl.origin);

    await page.goto(loginUrl.href, { waitUntil: "domcontentloaded" });
    await page.evaluate((user) => {
      globalThis.localStorage.setItem("auth_token", "lhci-auth-token");
      globalThis.localStorage.setItem("auth_user", JSON.stringify(user));
    }, LHCI_USER);

    if (targetUrl.pathname !== "/login") {
      await page.goto(targetUrl.href, { waitUntil: "domcontentloaded" });
      await delay(250);
    }
  } finally {
    await page.close();
  }
};
