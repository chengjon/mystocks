import { defineConfig } from '@playwright/test';

export default defineConfig({
    testDir: '.',
    testMatch: '**/*.spec.ts',
    timeout: 60000,
    use: {
        headless: true,
        ignoreHTTPSErrors: true,
        baseURL: `http://localhost:${process.env.FRONTEND_PORT || 3020}`,
    },
    projects: [
        {
            name: 'chromium',
            use: { browserName: 'chromium' },
        },
    ],
});
