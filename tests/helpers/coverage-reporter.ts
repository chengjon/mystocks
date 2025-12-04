/**
 * Phase 3: Coverage Reporter & Analysis
 *
 * Comprehensive coverage collection, analysis, and reporting utilities.
 * Integrates with Playwright test results to generate coverage dashboards,
 * track trends, and validate against configured thresholds.
 *
 * @module tests/helpers/coverage-reporter
 */

import fs from 'fs';
import path from 'path';
import {
  COVERAGE_THRESHOLDS,
  PAGE_COVERAGE_REQUIREMENTS,
  TEST_CATEGORIES,
  BROWSER_COVERAGE,
  DEVICE_COVERAGE,
  calculateCoverageScore,
  validateCoverage,
  getCoverageRecommendations,
  OverallCoverageMetrics,
  PageCoverageRequirement,
} from '../config/coverage-config';

/**
 * Coverage metrics for a single page
 */
export interface PageCoverageMetrics {
  page: string;
  testCount: number;
  passingTests: number;
  failingTests: number;
  skippedTests: number;
  passRate: number;
  browsers: string[];
  viewports: string[];
  hasVisualBaseline: boolean;
  hasPerformanceBudget: boolean;
  categories: Record<string, number>;
}

/**
 * Coverage metrics for a test category
 */
export interface CategoryCoverageMetrics {
  category: string;
  totalTests: number;
  passingTests: number;
  failingTests: number;
  passRate: number;
  weight: number;
  weightedScore: number;
}

/**
 * Overall coverage report
 */
export interface CoverageReport {
  timestamp: string;
  totalTests: number;
  passingTests: number;
  failingTests: number;
  skippedTests: number;
  overallPassRate: number;
  pages: PageCoverageMetrics[];
  categories: CategoryCoverageMetrics[];
  browsers: Record<string, { total: number; passed: number; rate: number }>;
  devices: Record<string, { total: number; passed: number; rate: number }>;
  thresholdValidation: {
    pages: ReturnType<typeof validateCoverage>;
    tests: ReturnType<typeof validateCoverage>;
    functionality: ReturnType<typeof validateCoverage>;
    errorScenarios: ReturnType<typeof validateCoverage>;
    performance: ReturnType<typeof validateCoverage>;
  };
  overallScore: number;
  recommendations: string[];
}

/**
 * Coverage trend data for historical analysis
 */
export interface CoverageTrend {
  date: string;
  overallScore: number;
  pagesCovered: number;
  totalTests: number;
  passRate: number;
  trends: {
    pages: { current: number; previous: number; change: number };
    tests: { current: number; previous: number; change: number };
    passRate: { current: number; previous: number; change: number };
  };
}

/**
 * Coverage reporter class for managing coverage data and generating reports
 */
export class CoverageReporter {
  private reportDir: string;
  private trendFile: string;

  constructor(reportDir: string = 'playwright-report') {
    this.reportDir = reportDir;
    this.trendFile = path.join(reportDir, 'coverage-trends.json');

    // Ensure report directory exists
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
  }

  /**
   * Parse Playwright test results and extract coverage metrics
   *
   * @param resultsPath - Path to Playwright JSON results file
   * @returns Coverage report with detailed metrics
   */
  public async generateCoverageReport(resultsPath: string): Promise<CoverageReport> {
    if (!fs.existsSync(resultsPath)) {
      throw new Error(`Results file not found: ${resultsPath}`);
    }

    const results = JSON.parse(fs.readFileSync(resultsPath, 'utf-8'));
    const suites = this.flattenSuites(results.suites || []);

    // Aggregate metrics
    let totalTests = 0;
    let passingTests = 0;
    let failingTests = 0;
    let skippedTests = 0;

    const pageMetrics: Map<string, PageCoverageMetrics> = new Map();
    const categoryMetrics: Map<string, CategoryCoverageMetrics> = new Map();
    const browserMetrics: Record<string, { total: number; passed: number }> = {};
    const deviceMetrics: Record<string, { total: number; passed: number }> = {};

    // Process each test
    for (const suite of suites) {
      for (const test of suite.tests || []) {
        totalTests++;

        const testName = test.title || '';
        const [page] = testName.split('::');
        const browser = test.projectName || 'chromium';
        const viewport = this.extractViewport(testName);

        // Update test status
        if (test.status === 'passed') passingTests++;
        else if (test.status === 'failed') failingTests++;
        else if (test.status === 'skipped') skippedTests++;

        // Update page metrics
        const pageKey = page || 'unknown';
        if (!pageMetrics.has(pageKey)) {
          pageMetrics.set(pageKey, {
            page: pageKey,
            testCount: 0,
            passingTests: 0,
            failingTests: 0,
            skippedTests: 0,
            passRate: 0,
            browsers: [],
            viewports: [],
            hasVisualBaseline: testName.includes('visual'),
            hasPerformanceBudget: testName.includes('performance'),
            categories: this.initializeCategoryMetrics(),
          });
        }

        const pageMetric = pageMetrics.get(pageKey)!;
        pageMetric.testCount++;
        if (test.status === 'passed') pageMetric.passingTests++;
        else if (test.status === 'failed') pageMetric.failingTests++;
        else if (test.status === 'skipped') pageMetric.skippedTests++;

        if (!pageMetric.browsers.includes(browser)) {
          pageMetric.browsers.push(browser);
        }
        if (viewport && !pageMetric.viewports.includes(viewport)) {
          pageMetric.viewports.push(viewport);
        }

        // Update category metrics
        const category = this.getTestCategory(testName);
        pageMetric.categories[category] = (pageMetric.categories[category] || 0) + 1;

        // Update browser/device metrics
        browserMetrics[browser] = {
          total: (browserMetrics[browser]?.total || 0) + 1,
          passed: (browserMetrics[browser]?.passed || 0) + (test.status === 'passed' ? 1 : 0),
        };

        if (viewport) {
          deviceMetrics[viewport] = {
            total: (deviceMetrics[viewport]?.total || 0) + 1,
            passed: (deviceMetrics[viewport]?.passed || 0) + (test.status === 'passed' ? 1 : 0),
          };
        }
      }
    }

    // Calculate pass rates
    const overallPassRate = totalTests > 0 ? (passingTests / totalTests) * 100 : 0;

    // Process page metrics
    const pages: PageCoverageMetrics[] = Array.from(pageMetrics.values()).map(metric => ({
      ...metric,
      passRate: metric.testCount > 0 ? (metric.passingTests / metric.testCount) * 100 : 0,
    }));

    // Process category metrics
    const categories: CategoryCoverageMetrics[] = Object.entries(TEST_CATEGORIES).map(
      ([key, config]) => {
        let totalTests = 0;
        let passingTests = 0;

        pages.forEach(page => {
          const count = page.categories[key] || 0;
          totalTests += count;
          passingTests += Math.round((count * page.passRate) / 100);
        });

        return {
          category: config.name,
          totalTests,
          passingTests,
          failingTests: totalTests - passingTests,
          passRate: totalTests > 0 ? (passingTests / totalTests) * 100 : 0,
          weight: config.weight,
          weightedScore: totalTests > 0 ? (passingTests / totalTests) * 100 * config.weight : 0,
        };
      },
    );

    // Validate coverage
    const thresholdValidation = {
      pages: validateCoverage(
        pages.length,
        COVERAGE_THRESHOLDS.pages,
        'pages',
      ),
      tests: validateCoverage(
        totalTests,
        COVERAGE_THRESHOLDS.tests,
        'tests',
      ),
      functionality: validateCoverage(
        pages.filter(p => p.categories['functional'] > 0).length,
        COVERAGE_THRESHOLDS.functionality,
        'functionality',
      ),
      errorScenarios: validateCoverage(
        pages.filter(p => p.categories['edge-case'] > 0).length,
        COVERAGE_THRESHOLDS.errorScenarios,
        'error scenarios',
      ),
      performance: validateCoverage(
        pages.filter(p => p.hasPerformanceBudget).length,
        COVERAGE_THRESHOLDS.performanceBenchmarks,
        'performance',
      ),
    };

    // Calculate overall score
    const overallScore = calculateCoverageScore({
      pages: pages.length,
      tests: Math.min(100, (totalTests / COVERAGE_THRESHOLDS.tests.target) * 100),
      functionality: thresholdValidation.functionality.current,
      errorScenarios: thresholdValidation.errorScenarios.current,
      performance: thresholdValidation.performance.current,
    });

    // Generate recommendations
    const recommendations = getCoverageRecommendations(
      {
        pages: pages.length,
        tests: totalTests,
        errorScenarios: thresholdValidation.errorScenarios.current,
        performance: thresholdValidation.performance.current,
        visual: pages.filter(p => p.hasVisualBaseline).length,
        browsers: Object.keys(browserMetrics).length,
        devices: Object.keys(deviceMetrics).length,
      },
      COVERAGE_THRESHOLDS,
    );

    const report: CoverageReport = {
      timestamp: new Date().toISOString(),
      totalTests,
      passingTests,
      failingTests,
      skippedTests,
      overallPassRate,
      pages,
      categories,
      browsers: Object.fromEntries(
        Object.entries(browserMetrics).map(([browser, metrics]) => [
          browser,
          {
            total: metrics.total,
            passed: metrics.passed,
            rate: (metrics.passed / metrics.total) * 100,
          },
        ]),
      ),
      devices: Object.fromEntries(
        Object.entries(deviceMetrics).map(([device, metrics]) => [
          device,
          {
            total: metrics.total,
            passed: metrics.passed,
            rate: (metrics.passed / metrics.total) * 100,
          },
        ]),
      ),
      thresholdValidation,
      overallScore,
      recommendations,
    };

    return report;
  }

  /**
   * Save coverage report to file
   *
   * @param report - Coverage report to save
   * @param format - Output format (json, html, csv, markdown)
   */
  public async saveCoverageReport(
    report: CoverageReport,
    format: 'json' | 'html' | 'csv' | 'markdown' = 'json',
  ): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `coverage-report-${timestamp}.${this.getExtension(format)}`;
    const filepath = path.join(this.reportDir, filename);

    let content: string;
    switch (format) {
      case 'json':
        content = JSON.stringify(report, null, 2);
        break;
      case 'html':
        content = this.generateHtmlReport(report);
        break;
      case 'csv':
        content = this.generateCsvReport(report);
        break;
      case 'markdown':
        content = this.generateMarkdownReport(report);
        break;
      default:
        throw new Error(`Unsupported format: ${format}`);
    }

    fs.writeFileSync(filepath, content, 'utf-8');
    console.log(`Coverage report saved to: ${filepath}`);

    return filepath;
  }

  /**
   * Track coverage trends over time
   *
   * @param report - Current coverage report
   */
  public async trackTrend(report: CoverageReport): Promise<void> {
    let trends: CoverageTrend[] = [];

    if (fs.existsSync(this.trendFile)) {
      trends = JSON.parse(fs.readFileSync(this.trendFile, 'utf-8'));
    }

    const previous = trends[trends.length - 1];
    const trend: CoverageTrend = {
      date: new Date().toISOString().split('T')[0],
      overallScore: report.overallScore,
      pagesCovered: report.pages.length,
      totalTests: report.totalTests,
      passRate: report.overallPassRate,
      trends: {
        pages: {
          current: report.pages.length,
          previous: previous?.pagesCovered || 0,
          change: previous ? report.pages.length - previous.pagesCovered : 0,
        },
        tests: {
          current: report.totalTests,
          previous: previous?.totalTests || 0,
          change: previous ? report.totalTests - previous.totalTests : 0,
        },
        passRate: {
          current: report.overallPassRate,
          previous: previous?.passRate || 0,
          change: previous ? report.overallPassRate - previous.passRate : 0,
        },
      },
    };

    trends.push(trend);

    // Keep only last 90 days
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - 90);
    trends = trends.filter(t => new Date(t.date) >= cutoff);

    fs.writeFileSync(this.trendFile, JSON.stringify(trends, null, 2), 'utf-8');
  }

  /**
   * Generate HTML coverage report
   *
   * @param report - Coverage report to format
   * @returns HTML string
   */
  private generateHtmlReport(report: CoverageReport): string {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>E2E Test Coverage Report</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }
    .header { background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
    .metric { background: #fff; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; }
    .metric-value { font-size: 32px; font-weight: bold; color: #007bff; }
    .metric-label { color: #666; font-size: 14px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #f5f5f5; font-weight: 600; }
    .passed { color: #28a745; }
    .failed { color: #dc3545; }
    .recommendation { background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 4px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>E2E Test Coverage Report</h1>
    <p>Generated: ${new Date(report.timestamp).toLocaleString()}</p>
  </div>

  <div class="metrics">
    <div class="metric">
      <div class="metric-value">${report.totalTests}</div>
      <div class="metric-label">Total Tests</div>
    </div>
    <div class="metric">
      <div class="metric-value">${report.pages.length}</div>
      <div class="metric-label">Pages Covered</div>
    </div>
    <div class="metric">
      <div class="metric-value">${report.overallScore}%</div>
      <div class="metric-label">Overall Score</div>
    </div>
    <div class="metric">
      <div class="metric-value">${report.overallPassRate.toFixed(1)}%</div>
      <div class="metric-label">Pass Rate</div>
    </div>
  </div>

  <h2>Page Coverage</h2>
  <table>
    <thead>
      <tr>
        <th>Page</th>
        <th>Tests</th>
        <th>Pass Rate</th>
        <th>Browsers</th>
        <th>Viewports</th>
      </tr>
    </thead>
    <tbody>
      ${report.pages.map(p => `
        <tr>
          <td>${p.page}</td>
          <td>${p.testCount}</td>
          <td class="${p.passRate >= 80 ? 'passed' : 'failed'}">${p.passRate.toFixed(1)}%</td>
          <td>${p.browsers.join(', ')}</td>
          <td>${p.viewports.join(', ')}</td>
        </tr>
      `).join('')}
    </tbody>
  </table>

  <h2>Test Categories</h2>
  <table>
    <thead>
      <tr>
        <th>Category</th>
        <th>Tests</th>
        <th>Pass Rate</th>
        <th>Weight</th>
      </tr>
    </thead>
    <tbody>
      ${report.categories.map(c => `
        <tr>
          <td>${c.category}</td>
          <td>${c.totalTests}</td>
          <td class="${c.passRate >= 80 ? 'passed' : 'failed'}">${c.passRate.toFixed(1)}%</td>
          <td>${(c.weight * 100).toFixed(0)}%</td>
        </tr>
      `).join('')}
    </tbody>
  </table>

  <h2>Recommendations</h2>
  ${report.recommendations.map(r => `<div class="recommendation">✓ ${r}</div>`).join('')}
</body>
</html>
    `;
  }

  /**
   * Generate CSV coverage report
   *
   * @param report - Coverage report to format
   * @returns CSV string
   */
  private generateCsvReport(report: CoverageReport): string {
    const lines: string[] = [];

    lines.push('Coverage Report Summary');
    lines.push(`Generated: ${new Date(report.timestamp).toLocaleString()}`);
    lines.push('');
    lines.push('Metrics');
    lines.push(`Total Tests,${report.totalTests}`);
    lines.push(`Passing Tests,${report.passingTests}`);
    lines.push(`Failing Tests,${report.failingTests}`);
    lines.push(`Overall Pass Rate,${report.overallPassRate.toFixed(2)}%`);
    lines.push(`Overall Score,${report.overallScore}%`);
    lines.push('');
    lines.push('Page Coverage');
    lines.push('Page,Test Count,Pass Rate,Browsers,Viewports');
    report.pages.forEach(p => {
      lines.push(
        `"${p.page}",${p.testCount},${p.passRate.toFixed(2)}%,"${p.browsers.join(', ')}","${p.viewports.join(', ')}"`,
      );
    });

    return lines.join('\n');
  }

  /**
   * Generate Markdown coverage report
   *
   * @param report - Coverage report to format
   * @returns Markdown string
   */
  private generateMarkdownReport(report: CoverageReport): string {
    const lines: string[] = [];

    lines.push('# E2E Test Coverage Report\n');
    lines.push(`**Generated**: ${new Date(report.timestamp).toLocaleString()}\n`);

    lines.push('## Summary\n');
    lines.push(`| Metric | Value |`);
    lines.push(`|--------|-------|`);
    lines.push(`| Total Tests | ${report.totalTests} |`);
    lines.push(`| Passing Tests | ${report.passingTests} |`);
    lines.push(`| Failing Tests | ${report.failingTests} |`);
    lines.push(`| Overall Pass Rate | ${report.overallPassRate.toFixed(2)}% |`);
    lines.push(`| Overall Score | ${report.overallScore}% |`);
    lines.push(`| Pages Covered | ${report.pages.length} |`);
    lines.push('');

    lines.push('## Page Coverage\n');
    lines.push(`| Page | Tests | Pass Rate | Browsers | Viewports |`);
    lines.push(`|------|-------|-----------|----------|-----------|`);
    report.pages.forEach(p => {
      lines.push(
        `| ${p.page} | ${p.testCount} | ${p.passRate.toFixed(1)}% | ${p.browsers.join(', ')} | ${p.viewports.join(', ')} |`,
      );
    });
    lines.push('');

    lines.push('## Recommendations\n');
    report.recommendations.forEach(r => {
      lines.push(`- ${r}`);
    });
    lines.push('');

    return lines.join('\n');
  }

  /**
   * Flatten nested test suites into flat list
   *
   * @param suites - Playwright suite objects
   * @returns Flattened suite list
   */
  private flattenSuites(
    suites: any[],
  ): Array<{ title?: string; tests: Array<{ title?: string; status: string; projectName?: string }> }> {
    const result: any[] = [];

    const flatten = (items: any[]) => {
      items.forEach(item => {
        if (item.suites) {
          flatten(item.suites);
        }
        if (item.tests) {
          result.push(item);
        }
      });
    };

    flatten(suites);
    return result;
  }

  /**
   * Extract viewport size from test name
   *
   * @param testName - Test name containing viewport info
   * @returns Viewport identifier (mobile, tablet, desktop) or undefined
   */
  private extractViewport(testName: string): string | undefined {
    if (testName.includes('mobile') || testName.includes('375')) return 'mobile';
    if (testName.includes('tablet') || testName.includes('768')) return 'tablet';
    if (testName.includes('desktop') || testName.includes('1920')) return 'desktop';
    return undefined;
  }

  /**
   * Classify test into category
   *
   * @param testName - Test name
   * @returns Test category
   */
  private getTestCategory(testName: string): string {
    if (testName.includes('visual')) return 'responsive';
    if (testName.includes('performance') || testName.includes('budget')) return 'performance';
    if (testName.includes('error') || testName.includes('edge')) return 'edge-case';
    if (testName.includes('smoke')) return 'smoke';
    return 'functional';
  }

  /**
   * Get file extension for format
   *
   * @param format - Report format
   * @returns File extension
   */
  private getExtension(format: string): string {
    switch (format) {
      case 'json':
        return 'json';
      case 'html':
        return 'html';
      case 'csv':
        return 'csv';
      case 'markdown':
        return 'md';
      default:
        return 'txt';
    }
  }

  /**
   * Initialize category metrics for a page
   *
   * @returns Empty category metrics object
   */
  private initializeCategoryMetrics(): Record<string, number> {
    return Object.keys(TEST_CATEGORIES).reduce(
      (acc, key) => {
        acc[key] = 0;
        return acc;
      },
      {} as Record<string, number>,
    );
  }
}

/**
 * Create coverage reporter instance with default settings
 *
 * @returns CoverageReporter instance
 */
export function createCoverageReporter(): CoverageReporter {
  return new CoverageReporter();
}

export default {
  CoverageReporter,
  createCoverageReporter,
};
