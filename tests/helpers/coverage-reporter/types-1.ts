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

