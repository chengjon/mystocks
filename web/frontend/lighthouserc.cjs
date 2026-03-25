/* global process */

const lighthouseBaseUrl = (
  process.env.LIGHTHOUSE_BASE_URL ||
  process.env.FRONTEND_BASE_URL ||
  "http://127.0.0.1:4273"
).replace(/\/$/, "");

module.exports = {
  ci: {
    collect: {
      chromePath: process.env.LIGHTHOUSE_CHROME_PATH,
      puppeteerScript: "./scripts/lighthouse-auth.cjs",
      puppeteerLaunchOptions: {
        args: ["--no-sandbox"],
      },
      startServerCommand: "npm run preview:lighthouse",
      startServerReadyPattern: "http://",
      startServerReadyTimeout: 30000,
      url: [
        `${lighthouseBaseUrl}/login`,
        `${lighthouseBaseUrl}/dashboard`,
        `${lighthouseBaseUrl}/market/realtime`,
        `${lighthouseBaseUrl}/strategy/repo`,
      ],
      numberOfRuns: 1,
      settings: {
        preset: "desktop",
        disableStorageReset: true,
      },
    },
    assert: {
      assertions: {
        "categories:performance": ["warn", { minScore: 0.6 }],
        "categories:accessibility": ["error", { minScore: 0.85 }],
        "categories:best-practices": ["warn", { minScore: 0.75 }],
        "categories:seo": "off",
      },
    },
    upload: {
      target: "filesystem",
      outputDir: ".lighthouseci",
    },
  },
};
