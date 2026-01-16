import { defineConfig, devices } from '@playwright/test';

const config = defineConfig({
  testDir: './playwright-tests',
  retries: process.env.CI ? 2 : 0,
  use: process.env.CI ? 'chromium' : 'chromium',
  headless: false,
  video: 'retain-on-failure',
  timeout: 60000,
  expect: {
    timeout: 10000
  }
});

export default config;
