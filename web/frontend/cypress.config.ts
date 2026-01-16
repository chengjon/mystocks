import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    // We'll serve the app using a dev server
    baseUrl: 'http://localhost:3000',
    // Support video recording
    video: false,
    // Screenshot configuration
    screenshotOnRunFailure: true,
    // Viewport size
    viewportWidth: 1920,
    viewportHeight: 1080,
    // Default command timeout
    defaultCommandTimeout: 10000,
    // Page load timeout
    pageLoadTimeout: 60000,
    // Response timeout
    responseTimeout: 30000,
    // Support Chrome devtools
    chromeWebSecurity: false,
    // Experimental features
    experimentalStudio: true,
    // Test retries
    retries: {
      runMode: 2,
      openMode: 0,
    },
    // Reporter configuration
    reporter: 'junit',
    reporterOptions: {
      mochaFile: 'cypress-results/junit.xml',
      toConsole: true,
    },
  },

  component: {
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
    excludeSpecPattern: ['**/node_modules/**', '**/dist/**'],
  },
});
