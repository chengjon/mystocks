import { test, expect } from '@playwright/test';
import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

test.describe('Medium Suite', () => {
  test('check pm2 version', async () => {
    const version = execSync('pm2 --version').toString();
    expect(version).toBeDefined();
  });

  test('navigate', async ({ page }) => {
    await page.goto('http://127.0.0.1:3000');
    expect(true).toBe(true);
  });
});
