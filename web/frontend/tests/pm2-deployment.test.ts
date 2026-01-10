import { test, expect } from '@playwright/test';
import { execSync } from 'child_process';
import { readFileSync } from 'fs';
import { join } from 'path';

/**
 * MyStocks Frontend - PM2 Deployment Verification Tests
 * Phase 3: Bloomberg Terminal Style Deployment
 *
 * Tests for verifying PM2 deployment configuration and runtime status.
 * These tests ensure the frontend application is properly deployed and accessible.
 */

const APP_NAME = 'mystocks-frontend';
const PORT = 8080;
const BASE_URL = `http://localhost:${PORT}`;

test.describe('PM2 Configuration File Validation', () => {
  test('should have valid ecosystem.config.js', () => {
    const configPath = join(process.cwd(), 'ecosystem.config.js');
    const configExists = require('fs').existsSync(configPath);
    expect(configExists, 'ecosystem.config.js should exist').toBeTruthy();

    // Load and validate configuration
    const config = require(configPath);
    expect(config.apps).toBeDefined();
    expect(config.apps.length).toBeGreaterThan(0);

    const appConfig = config.apps[0];
    expect(appConfig.name).toBe(APP_NAME);
    expect(appConfig.port || (appConfig.env && appConfig.env.PORT)).toBeDefined();
  });

  test('should have proper logging configuration', () => {
    const configPath = join(process.cwd(), 'ecosystem.config.js');
    const config = require(configPath);
    const appConfig = config.apps[0];

    expect(appConfig.error_file).toBeDefined();
    expect(appConfig.out_file).toBeDefined();
    expect(appConfig.log_date_format).toBeDefined();
  });

  test('should have restart strategy configured', () => {
    const configPath = join(process.cwd(), 'ecosystem.config.js');
    const config = require(configPath);
    const appConfig = config.apps[0];

    expect(appConfig.autorestart).toBe(true);
    expect(appConfig.max_restarts).toBeGreaterThan(0);
    expect(appConfig.min_uptime).toBeDefined();
  });
});

test.describe('PM2 Process Status Verification', () => {
  test.beforeAll(async () => {
    // Check if PM2 is installed
    try {
      execSync('pm2 --version', { stdio: 'pipe' });
    } catch (error) {
      test.skip('PM2 is not installed');
    }
  });

  test('should have application running in PM2', () => {
    try {
      const output = execSync('pm2 list --json', { encoding: 'utf-8' });
      const pm2List = JSON.parse(output);

      const app = pm2List.find((p: any) => p.name === APP_NAME);
      expect(app, `${APP_NAME} should be in PM2 process list`).toBeDefined();

      // Check if status is online
      expect(
        app.pm2_env.status,
        `${APP_NAME} should be online`
      ).toBe('online');
    } catch (error: any) {
      test.fail(`PM2 list failed: ${error.message}`);
    }
  });

  test('should have correct port configuration', () => {
    try {
      const output = execSync('pm2 list --json', { encoding: 'utf-8' });
      const pm2List = JSON.parse(output);

      const app = pm2List.find((p: any) => p.name === APP_NAME);
      expect(app).toBeDefined();

      // Check if port is listening (using lsof)
      try {
        execSync(`lsof -Pi :${PORT} -sTCP:LISTEN -t`, { stdio: 'pipe' });
        // If we get here, port is listening
        expect(true).toBeTruthy();
      } catch {
        throw new Error(`Port ${PORT} is not listening`);
      }
    } catch (error: any) {
      test.fail(`Port check failed: ${error.message}`);
    }
  });

  test('should have no recent restarts', () => {
    try {
      const output = execSync('pm2 list --json', { encoding: 'utf-8' });
      const pm2List = JSON.parse(output);

      const app = pm2List.find((p: any) => p.name === APP_NAME);
      expect(app).toBeDefined();

      const restartCount = app.pm2_env.restart_time || 0;
      expect(
        restartCount,
        `${APP_NAME} should not have restarted frequently (count: ${restartCount})`
      ).toBeLessThanOrEqual(2);
    } catch (error: any) {
      test.fail(`Restart check failed: ${error.message}`);
    }
  });
});

test.describe('Application Accessibility', () => {
  test('should respond to HTTP requests', async ({ request }) => {
    const response = await request.get(BASE_URL);
    expect(response.status()).toBe(200);
  });

  test('should serve HTML content', async ({ page }) => {
    await page.goto(BASE_URL);
    const content = await page.content();
    expect(content).toContain('<!DOCTYPE html>');
    expect(content).toContain('<html');
  });

  test('should have proper charset encoding', async ({ page }) => {
    await page.goto(BASE_URL);
    const charset = await page.locator('meta[charset]').getAttribute('charset');
    expect(charset).toBe('utf-8');
  });

  test('should load JavaScript bundle', async ({ page }) => {
    await page.goto(BASE_URL);

    // Wait for page load
    await page.waitForLoadState('networkidle');

    // Check for script tags
    const scripts = await page.locator('script[src]').count();
    expect(scripts, 'Should have loaded JavaScript bundles').toBeGreaterThan(0);
  });

  test('should load CSS styles', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Check for link tags with CSS
    const stylesheets = await page.locator('link[rel="stylesheet"]').count();
    expect(stylesheets, 'Should have loaded CSS styles').toBeGreaterThan(0);
  });
});

test.describe('PM2 Logs Verification', () => {
  test.beforeAll(async () => {
    try {
      execSync('pm2 --version', { stdio: 'pipe' });
    } catch (error) {
      test.skip('PM2 is not installed');
    }
  });

  test('should not have SCSS compilation errors', () => {
    const logPath = join(process.cwd(), 'logs', 'pm2-error.log');

    if (!require('fs').existsSync(logPath)) {
      test.skip('Log file does not exist yet');
    }

    const logs = readFileSync(logPath, 'utf-8');

    // Check for SCSS/Sass errors
    const scssErrors = [
      'SCSS compilation error',
      'Sass compilation error',
      'ModuleBuildError',
      'sass-loader',
    ];

    for (const errorPattern of scssErrors) {
      expect(
        logs.toLowerCase(),
        `Should not contain ${errorPattern} in logs`
      ).not.toContain(errorPattern.toLowerCase());
    }
  });

  test('should not have runtime crashes', () => {
    const logPath = join(process.cwd(), 'logs', 'pm2-error.log');

    if (!require('fs').existsSync(logPath)) {
      test.skip('Log file does not exist yet');
    }

    const logs = readFileSync(logPath, 'utf-8');

    // Check for crash indicators
    const crashPatterns = [
      'UnhandledPromiseRejection',
      'Uncaught Exception',
      'SIGSEGV',
      'Segmentation fault',
      'FATAL ERROR',
    ];

    for (const pattern of crashPatterns) {
      expect(
        logs,
        `Should not contain crash pattern: ${pattern}`
      ).not.toContain(pattern);
    }
  });

  test('should have successful startup message', () => {
    const logPath = join(process.cwd(), 'logs', 'pm2-out.log');

    if (!require('fs').existsSync(logPath)) {
      test.skip('Log file does not exist yet');
    }

    const logs = readFileSync(logPath, 'utf-8');

    // Check for successful startup
    expect(logs, 'Should have serve startup message').toContain('Accepting connections');
  });
});

test.describe('Build Artifacts Verification', () => {
  test('should have dist directory', () => {
    const distPath = join(process.cwd(), 'dist');
    const distExists = require('fs').existsSync(distPath);
    expect(distExists, 'dist directory should exist after build').toBeTruthy();
  });

  test('should have index.html in dist', () => {
    const indexPath = join(process.cwd(), 'dist', 'index.html');
    const indexExists = require('fs').existsSync(indexPath);
    expect(indexExists, 'index.html should exist in dist').toBeTruthy();
  });

  test('should have assets in dist', () => {
    const distPath = join(process.cwd(), 'dist');
    const files = require('fs').readdirSync(distPath);

    // Should have assets directory or some JS/CSS files
    const hasAssets =
      files.includes('assets') ||
      files.some(f => f.endsWith('.js')) ||
      files.some(f => f.endsWith('.css'));

    expect(hasAssets, 'dist should contain built assets').toBeTruthy();
  });

  test('should have no build errors in logs', () => {
    const logPath = join(process.cwd(), 'logs', 'pm2-error.log');

    if (!require('fs').existsSync(logPath)) {
      test.skip('Log file does not exist yet');
    }

    const logs = readFileSync(logPath, 'utf-8');

    // Check for build error patterns
    const buildErrors = [
      'Build failed',
      'Cannot compile',
      'Unexpected token',
      'Module not found',
    ];

    for (const pattern of buildErrors) {
      expect(
        logs,
        `Should not contain build error: ${pattern}`
      ).not.toContain(pattern);
    }
  });
});

test.describe('Environment Variables', () => {
  test('should have NODE_ENV set to production', () => {
    try {
      const output = execSync('pm2 list --json', { encoding: 'utf-8' });
      const pm2List = JSON.parse(output);

      const app = pm2List.find((p: any) => p.name === APP_NAME);
      expect(app).toBeDefined();

      const env = app.pm2_env;
      expect(env.NODE_ENV || (env.env && env.env.NODE_ENV)).toBe('production');
    } catch (error: any) {
      test.fail(`Environment check failed: ${error.message}`);
    }
  });

  test('should have PORT configured', () => {
    try {
      const output = execSync('pm2 list --json', { encoding: 'utf-8'});
      const pm2List = JSON.parse(output);

      const app = pm2List.find((p: any) => p.name === APP_NAME);
      expect(app).toBeDefined();

      const env = app.pm2_env;
      expect(env.PORT || (app.pm2_env.PORT)).toBeDefined();
    } catch (error: any) {
      test.fail(`Port configuration check failed: ${error.message}`);
    }
  });
});
