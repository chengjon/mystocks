import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Task T1.1 - Directory Structure Initialization', () => {
  const rootDir = path.resolve(__dirname, '../../src');

  it('should have the artdeco-pages root directory', () => {
    const artDecoPagesDir = path.join(rootDir, 'views/artdeco-pages');
    expect(fs.existsSync(artDecoPagesDir)).toBe(true);
  });

  it('should have domain folders in artdeco-pages', () => {
    const domains = ['market', 'trade', 'risk'];
    domains.forEach(domain => {
      const domainDir = path.join(rootDir, `views/artdeco-pages/${domain}`);
      expect(fs.existsSync(domainDir)).toBe(true);
    });
  });

  it('should have the centralized api directory', () => {
    const apiDir = path.join(rootDir, 'api/artdeco-api');
    expect(fs.existsSync(apiDir)).toBe(true);
  });
});
