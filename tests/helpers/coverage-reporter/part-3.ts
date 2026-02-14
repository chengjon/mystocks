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

