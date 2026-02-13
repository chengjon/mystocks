import { defineConfig } from '@playwright/test';

export default defineConfig({
    testDir: './tests',
    testMatch: 'full-page-validation.spec.ts',
    timeout: 60000,
    use: {
        headless: true,
        ignoreHTTPSErrors: true,
    },
    projects: [
        {
            name: 'chromium',
            use: { browserName: 'chromium' },
        },
    ],
});
