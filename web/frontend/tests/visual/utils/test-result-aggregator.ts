import { TestResult, formatTestResults, categorizeDiff, getRecommendation } from './notification';

export interface AggregatedResults {
  summary: {
    total: number;
    passed: number;
    failed: number;
    diffs: number;
    passRate: number;
  };
  byPriority: {
    P0: { total: number; passed: number; failed: number };
    P1: { total: number; passed: number; failed: number };
    P2: { total: number; passed: number; failed: number };
  };
  majorDiffs: Array<{
    testName: string;
    diffPixels: number;
    category: string;
    recommendation: string;
  }>;
  timestamp: string;
}

export function aggregateResults(results: TestResult[]): AggregatedResults {
  const passed = results.filter(r => r.status === 'passed').length;
  const failed = results.filter(r => r.status === 'failed').length;
  const diffs = results.filter(r => r.status === 'diff').length;

  const majorDiffs: AggregatedResults['majorDiffs'] = [];
  for (const result of results.filter(r => r.status === 'diff' && r.diffPixels)) {
    const category = categorizeDiff(result.diffPixels!);
    if (category === 'major') {
      majorDiffs.push({
        testName: result.testName,
        diffPixels: result.diffPixels!,
        category,
        recommendation: getRecommendation(category, result.testName)
      });
    }
  }

  return {
    summary: {
      total: results.length,
      passed,
      failed,
      diffs,
      passRate: results.length > 0 ? (passed / results.length) * 100 : 0
    },
    byPriority: {
      P0: { total: 0, passed: 0, failed: 0 },
      P1: { total: 0, passed: 0, failed: 0 },
      P2: { total: 0, passed: 0, failed: 0 }
    },
    majorDiffs,
    timestamp: new Date().toISOString()
  };
}

export function printSummary(results: AggregatedResults): void {
  console.log('\n📊 Visual Test Summary');
  console.log('='.repeat(50));
  console.log(`Total Tests: ${results.summary.total}`);
  console.log(`Passed: ${results.summary.passed} (${results.summary.passRate.toFixed(1)}%)`);
  console.log(`Failed: ${results.summary.failed}`);
  console.log(`Visual Diffs: ${results.summary.diffs}`);

  if (results.majorDiffs.length > 0) {
    console.log('\n⚠️ Major Visual Diffs Detected:');
    for (const diff of results.majorDiffs) {
      console.log(`  - ${diff.testName}: ${diff.diffPixels}px diff`);
      console.log(`    Recommendation: ${diff.recommendation}`);
    }
  }
  console.log('');
}
