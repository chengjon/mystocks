/**
 * Phase 3: Coverage Configuration & Thresholds
 *
 * Defines coverage requirements and thresholds for E2E test suite.
 * Supports page-level, category-level, and overall coverage tracking.
 *
 * @module tests/config/coverage-config
 */

/**
 * Coverage threshold definition for individual metrics
 */
export interface CoverageThreshold {
  /** Minimum required coverage percentage (0-100) */
  minimum: number;
  /** Target coverage percentage (0-100) */
  target: number;
  /** Page or category this threshold applies to */
  appliesTo?: string[];
}

/**
 * Category-specific coverage requirements
 */
export interface CategoryCoverage {
  /** Category name (e.g., 'dashboard', 'market') */
  name: string;
  /** Number of pages in category */
  pageCount: number;
  /** Minimum tests required per page */
  testsPerPageMinimum: number;
  /** Target tests per page */
  testsPerPageTarget: number;
  /** Test categories for this domain */
  testCategories: Array<'smoke' | 'functional' | 'edge-case' | 'performance' | 'responsive'>;
}

/**
 * Overall coverage metrics thresholds
 */
export interface OverallCoverageMetrics {
  /** Total page coverage threshold */
  pages: CoverageThreshold;
  /** Total test count threshold */
  tests: CoverageThreshold;
  /** Functional scenario coverage threshold */
  functionality: CoverageThreshold;
  /** Error/edge case coverage threshold */
  errorScenarios: CoverageThreshold;
  /** Performance benchmark coverage threshold */
  performanceBenchmarks: CoverageThreshold;
  /** Visual regression baseline coverage */
  visualBaselines: CoverageThreshold;
  /** Browser coverage threshold */
  browsers: CoverageThreshold;
  /** Device/viewport coverage threshold */
  devices: CoverageThreshold;
}

/**
 * Per-page coverage requirements
 */
export interface PageCoverageRequirement {
  /** Page name or path */
  page: string;
  /** Page priority (P0, P1, P2, P3) */
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  /** Minimum tests required */
  minimumTests: number;
  /** Target tests */
  targetTests: number;
  /** Required test categories */
  requiredCategories: Array<'smoke' | 'functional' | 'edge-case' | 'performance' | 'responsive'>;
  /** Required browsers */
  browsers: Array<'chromium' | 'firefox' | 'webkit'>;
  /** Required viewports */
  viewports: Array<'mobile' | 'tablet' | 'desktop'>;
}

/**
 * Test category definitions with weighting
 */
export interface TestCategory {
  /** Category name */
  name: string;
  /** Category description */
  description: string;
  /** Weight in overall coverage calculation */
  weight: number;
  /** Examples of tests in this category */
  examples: string[];
}

/**
 * Phase 3 Coverage Thresholds - Overall Metrics
 *
 * Defines minimum and target coverage metrics for the entire E2E suite.
 *
 * **Rationale**:
 * - Pages: Must test all P0 + P1 pages (6 minimum target)
 * - Tests: Comprehensive coverage requires 200+ tests (minimum), 300+ target
 * - Functionality: Core features and workflows
 * - Error Scenarios: Edge cases, error states, recovery paths
 * - Performance: Page load, Core Web Vitals validation
 * - Visual Baselines: Visual regression detection
 * - Browsers: Multi-browser compatibility (Chrome, Firefox, Safari)
 * - Devices: Responsive design across device sizes
 */
export const COVERAGE_THRESHOLDS: OverallCoverageMetrics = {
  pages: {
    minimum: 6,      // All P0 pages + key P1 pages
    target: 12,      // Extended P1 + early P2 pages
    appliesTo: ['P0', 'P1', 'P2'],
  },

  tests: {
    minimum: 200,    // Comprehensive coverage
    target: 300,     // Deep scenario coverage
  },

  functionality: {
    minimum: 30,     // Core user flows
    target: 50,      // Extended workflows and edge cases
  },

  errorScenarios: {
    minimum: 10,     // Basic error handling
    target: 20,      // Comprehensive error scenarios
  },

  performanceBenchmarks: {
    minimum: 15,     // Basic performance validation
    target: 25,      // Performance tracking for all critical pages
  },

  visualBaselines: {
    minimum: 8,      // Core page layouts
    target: 15,      // Comprehensive visual coverage
  },

  browsers: {
    minimum: 2,      // Chrome + Firefox
    target: 3,       // Chrome, Firefox, Safari
  },

  devices: {
    minimum: 2,      // Desktop + Mobile
    target: 3,       // Desktop, Tablet, Mobile
  },
};

/**
 * Per-Page Coverage Requirements
 *
 * Defines minimum test counts and required test categories for each page.
 *
 * **Pages by Priority**:
 * - P0: Dashboard, Market, Stock Detail - Critical, must have 40+ tests each
 * - P1: Trading, Settings, IndicatorLibrary, Wencai - Important, must have 30+ tests each
 * - P2: Portfolio, Risk, Strategies - Secondary, must have 20+ tests each
 * - P3: Other pages - Low priority, minimum 10 tests
 */
export const PAGE_COVERAGE_REQUIREMENTS: PageCoverageRequirement[] = [
  // P0 - Critical Pages (Core Application Features)
  {
    page: 'Dashboard',
    priority: 'P0',
    minimumTests: 35,
    targetTests: 50,
    requiredCategories: ['smoke', 'functional', 'performance', 'responsive'],
    browsers: ['chromium', 'firefox', 'webkit'],
    viewports: ['mobile', 'tablet', 'desktop'],
  },
  {
    page: 'Market',
    priority: 'P0',
    minimumTests: 35,
    targetTests: 50,
    requiredCategories: ['smoke', 'functional', 'performance', 'responsive'],
    browsers: ['chromium', 'firefox', 'webkit'],
    viewports: ['mobile', 'tablet', 'desktop'],
  },
  {
    page: 'StockDetail',
    priority: 'P0',
    minimumTests: 40,
    targetTests: 55,
    requiredCategories: ['smoke', 'functional', 'edge-case', 'performance', 'responsive'],
    browsers: ['chromium', 'firefox', 'webkit'],
    viewports: ['mobile', 'tablet', 'desktop'],
  },

  // P1 - Important Pages (Extended Features)
  {
    page: 'Trading',
    priority: 'P1',
    minimumTests: 30,
    targetTests: 45,
    requiredCategories: ['smoke', 'functional', 'edge-case', 'performance'],
    browsers: ['chromium', 'firefox'],
    viewports: ['tablet', 'desktop'],
  },
  {
    page: 'Settings',
    priority: 'P1',
    minimumTests: 25,
    targetTests: 40,
    requiredCategories: ['smoke', 'functional', 'edge-case'],
    browsers: ['chromium', 'firefox'],
    viewports: ['tablet', 'desktop'],
  },
  {
    page: 'IndicatorLibrary',
    priority: 'P1',
    minimumTests: 30,
    targetTests: 45,
    requiredCategories: ['smoke', 'functional', 'performance'],
    browsers: ['chromium', 'firefox'],
    viewports: ['desktop'],
  },
  {
    page: 'Wencai',
    priority: 'P1',
    minimumTests: 30,
    targetTests: 45,
    requiredCategories: ['smoke', 'functional', 'edge-case'],
    browsers: ['chromium', 'firefox'],
    viewports: ['desktop'],
  },

  // P2 - Secondary Pages
  {
    page: 'Portfolio',
    priority: 'P2',
    minimumTests: 20,
    targetTests: 35,
    requiredCategories: ['smoke', 'functional'],
    browsers: ['chromium'],
    viewports: ['desktop'],
  },
  {
    page: 'Risk',
    priority: 'P2',
    minimumTests: 20,
    targetTests: 35,
    requiredCategories: ['smoke', 'functional'],
    browsers: ['chromium'],
    viewports: ['desktop'],
  },
  {
    page: 'Strategies',
    priority: 'P2',
    minimumTests: 20,
    targetTests: 35,
    requiredCategories: ['smoke', 'functional'],
    browsers: ['chromium'],
    viewports: ['desktop'],
  },
];

/**
 * Category Coverage Definitions
 *
 * Groups pages by functional category with per-category requirements.
 */
export const CATEGORY_COVERAGE_REQUIREMENTS: CategoryCoverage[] = [
  {
    name: 'Dashboard & Analytics',
    pageCount: 3,
    testsPerPageMinimum: 20,
    testsPerPageTarget: 30,
    testCategories: ['smoke', 'functional', 'performance', 'responsive'],
  },
  {
    name: 'Market & Stock Data',
    pageCount: 2,
    testsPerPageMinimum: 18,
    testsPerPageTarget: 28,
    testCategories: ['smoke', 'functional', 'edge-case', 'performance'],
  },
  {
    name: 'Trading',
    pageCount: 1,
    testsPerPageMinimum: 30,
    testsPerPageTarget: 45,
    testCategories: ['smoke', 'functional', 'edge-case', 'performance'],
  },
  {
    name: 'Portfolio Management',
    pageCount: 3,
    testsPerPageMinimum: 15,
    testsPerPageTarget: 25,
    testCategories: ['smoke', 'functional'],
  },
  {
    name: 'Tools & Settings',
    pageCount: 3,
    testsPerPageMinimum: 15,
    testsPerPageTarget: 25,
    testCategories: ['smoke', 'functional', 'edge-case'],
  },
];

/**
 * Test Category Definitions
 *
 * Describes different types of tests and their contribution to overall coverage.
 */
export const TEST_CATEGORIES: Record<string, TestCategory> = {
  smoke: {
    name: 'Smoke Tests',
    description: 'Basic functionality - page loads, critical elements visible',
    weight: 0.15,
    examples: [
      'Page should load and be visible',
      'Critical navigation elements should be present',
      'Basic data should display',
    ],
  },

  functional: {
    name: 'Functional Tests',
    description: 'Core features - user interactions, data operations',
    weight: 0.35,
    examples: [
      'User can search for stocks',
      'User can sort data by column',
      'User can filter results',
      'User can export data',
      'Data updates correctly',
    ],
  },

  'edge-case': {
    name: 'Edge Case Tests',
    description: 'Error handling, boundary conditions, unusual scenarios',
    weight: 0.25,
    examples: [
      'API errors display appropriate messages',
      'Empty results show helpful messaging',
      'Boundary values handled correctly',
      'Concurrent actions managed safely',
      'Offline behavior handled gracefully',
    ],
  },

  performance: {
    name: 'Performance Tests',
    description: 'Performance budgets, Core Web Vitals, load testing',
    weight: 0.15,
    examples: [
      'Page load time < 3000ms',
      'API response < 2000ms',
      'Largest Contentful Paint < 2500ms',
      'First Input Delay < 100ms',
      'Cumulative Layout Shift < 0.1',
    ],
  },

  responsive: {
    name: 'Responsive Design Tests',
    description: 'Multi-device compatibility, responsive layouts',
    weight: 0.10,
    examples: [
      'Layout renders correctly on mobile (375px)',
      'Layout renders correctly on tablet (768px)',
      'Layout renders correctly on desktop (1920px)',
      'Touch interactions work on mobile',
      'Responsive images load appropriately',
    ],
  },
};

/**
 * Browser Coverage Requirements
 *
 * Specifies which browsers must be tested for each page priority.
 */
export const BROWSER_COVERAGE = {
  P0: ['chromium', 'firefox', 'webkit'],  // All browsers
  P1: ['chromium', 'firefox'],             // Chrome + Firefox
  P2: ['chromium'],                        // Chrome only
  P3: ['chromium'],                        // Chrome only
} as const;

/**
 * Device/Viewport Coverage Requirements
 *
 * Specifies which viewports must be tested for each page priority.
 */
export const DEVICE_COVERAGE = {
  P0: ['mobile', 'tablet', 'desktop'],     // All viewports
  P1: ['tablet', 'desktop'],               // Tablet + Desktop
  P2: ['desktop'],                         // Desktop only
  P3: ['desktop'],                         // Desktop only
} as const;

/**
 * Coverage Report Configuration
 *
 * Settings for coverage report generation and visualization.
 */
export const COVERAGE_REPORT_CONFIG = {
  /** Output format for coverage reports */
  outputFormats: ['json', 'html', 'csv', 'markdown'],

  /** Metrics to include in reports */
  includeMetrics: [
    'pageCount',
    'testCount',
    'functionalCoverage',
    'errorScenarioCoverage',
    'performanceCoverage',
    'visualCoverage',
    'browserCoverage',
    'deviceCoverage',
    'testCategoryDistribution',
  ],

  /** Coverage trend tracking interval (days) */
  trendTrackingInterval: 7,

  /** Historical data retention (days) */
  historyRetention: 90,

  /** Generate coverage report on */
  generateOn: ['ci_pass', 'daily', 'weekly'],

  /** Coverage badge configuration */
  badge: {
    enabled: true,
    updateReadme: true,
    color: 'brightgreen',
  },
} as const;

/**
 * Milestone 5 Completion Checklist
 *
 * Verification items for coverage reporting completion.
 */
export const COVERAGE_COMPLETION_CHECKLIST = [
  {
    item: 'Coverage configuration module (coverage-config.ts)',
    status: true,
    description: 'Defines all coverage thresholds and requirements',
  },
  {
    item: 'Coverage reporter module (coverage-reporter.ts)',
    status: false,
    description: 'Collects and generates coverage reports',
  },
  {
    item: 'GitHub Actions reporting integration',
    status: false,
    description: 'Automated coverage dashboard generation',
  },
  {
    item: 'Coverage trend analysis',
    status: false,
    description: 'Historical tracking and regression detection',
  },
  {
    item: 'Slack/webhook notifications',
    status: false,
    description: 'Real-time coverage alerts',
  },
  {
    item: 'Documentation and guides',
    status: false,
    description: 'Coverage setup and interpretation guides',
  },
] as const;

/**
 * Calculate weighted coverage score
 *
 * Combines multiple coverage metrics into a single overall score.
 *
 * @param metrics - Coverage metrics object with individual scores (0-100)
 * @returns Weighted overall coverage score (0-100)
 *
 * @example
 * const score = calculateCoverageScore({
 *   pages: 80,
 *   tests: 75,
 *   functionality: 85,
 *   errorScenarios: 60,
 *   performance: 70,
 * });
 */
export function calculateCoverageScore(metrics: Record<string, number>): number {
  const weights: Record<string, number> = {
    pages: 0.20,
    tests: 0.25,
    functionality: 0.25,
    errorScenarios: 0.15,
    performance: 0.15,
  };

  let totalScore = 0;
  let totalWeight = 0;

  for (const [key, weight] of Object.entries(weights)) {
    if (metrics[key] !== undefined) {
      totalScore += metrics[key] * weight;
      totalWeight += weight;
    }
  }

  return totalWeight > 0 ? Math.round(totalScore / totalWeight) : 0;
}

/**
 * Validate coverage against thresholds
 *
 * Checks if current coverage meets minimum requirements.
 *
 * @param current - Current coverage metrics
 * @param threshold - Required threshold
 * @param metricName - Name of metric being validated
 * @returns Object with validation result and gap analysis
 */
export function validateCoverage(
  current: number,
  threshold: CoverageThreshold,
  metricName: string,
): {
  passed: boolean;
  current: number;
  required: number;
  gap: number;
  status: 'exceeds-target' | 'meets-target' | 'meets-minimum' | 'below-minimum';
} {
  const passed = current >= threshold.minimum;
  const exceedsTarget = current >= threshold.target;
  const meetsTarget = current >= threshold.target;

  let status: 'exceeds-target' | 'meets-target' | 'meets-minimum' | 'below-minimum';
  if (exceedsTarget) {
    status = 'exceeds-target';
  } else if (meetsTarget) {
    status = 'meets-target';
  } else if (passed) {
    status = 'meets-minimum';
  } else {
    status = 'below-minimum';
  }

  return {
    passed,
    current,
    required: threshold.minimum,
    gap: Math.max(0, threshold.minimum - current),
    status,
  };
}

/**
 * Get coverage recommendations
 *
 * Provides specific recommendations for improving coverage.
 *
 * @param currentCoverage - Current coverage metrics
 * @param targetCoverage - Target coverage thresholds
 * @returns Array of actionable recommendations
 */
export function getCoverageRecommendations(
  currentCoverage: Record<string, number>,
  targetCoverage: OverallCoverageMetrics,
): string[] {
  const recommendations: string[] = [];

  // Check page coverage
  if (currentCoverage.pages < targetCoverage.pages.target) {
    recommendations.push(
      `Add tests for ${targetCoverage.pages.target - currentCoverage.pages} more pages to reach target`,
    );
  }

  // Check test count
  if (currentCoverage.tests < targetCoverage.tests.target) {
    recommendations.push(
      `Add ${targetCoverage.tests.target - currentCoverage.tests} more tests to reach target`,
    );
  }

  // Check error scenarios
  if (currentCoverage.errorScenarios < targetCoverage.errorScenarios.target) {
    recommendations.push('Expand error handling and edge case test coverage');
  }

  // Check performance tests
  if (currentCoverage.performance < targetCoverage.performanceBenchmarks.target) {
    recommendations.push('Add performance benchmarks for critical pages');
  }

  // Check visual baselines
  if (currentCoverage.visual < targetCoverage.visualBaselines.target) {
    recommendations.push('Create visual regression baselines for more pages');
  }

  // Check browser coverage
  if (currentCoverage.browsers < targetCoverage.browsers.target) {
    recommendations.push('Extend testing to Safari for P0 and key P1 pages');
  }

  // Check device coverage
  if (currentCoverage.devices < targetCoverage.devices.target) {
    recommendations.push('Add tablet viewport testing for responsive design validation');
  }

  return recommendations;
}

export default {
  COVERAGE_THRESHOLDS,
  PAGE_COVERAGE_REQUIREMENTS,
  CATEGORY_COVERAGE_REQUIREMENTS,
  TEST_CATEGORIES,
  BROWSER_COVERAGE,
  DEVICE_COVERAGE,
  COVERAGE_REPORT_CONFIG,
  calculateCoverageScore,
  validateCoverage,
  getCoverageRecommendations,
};
