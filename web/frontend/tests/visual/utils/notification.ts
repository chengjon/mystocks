export interface TestResult {
  testName: string;
  status: 'passed' | 'failed' | 'diff';
  diffPixels?: number;
  diffPercentage?: number;
  timestamp: string;
}

export function formatTestResults(results: TestResult[]): string {
  const passed = results.filter(r => r.status === 'passed').length;
  const failed = results.filter(r => r.status === 'failed').length;
  const diffs = results.filter(r => r.status === 'diff').length;

  return `📊 Visual Test Results:
- **Passed**: ${passed}
- **Failed**: ${failed}
- **Visual Diffs**: ${diffs}
- **Total**: ${results.length}`;
}

export function shouldFailCI(diffPixels: number, threshold: number): boolean {
  return diffPixels > threshold;
}

export function categorizeDiff(diffPixels: number): 'minor' | 'moderate' | 'major' {
  if (diffPixels < 50) return 'minor';
  if (diffPixels < 150) return 'moderate';
  return 'major';
}

export function getRecommendation(diffCategory: 'minor' | 'moderate' | 'major', testName: string): string {
  switch (diffCategory) {
    case 'minor':
      return `Minor diff detected in ${testName}. Likely rendering variation. Consider updating baseline if intentional.`;
    case 'moderate':
      return `Moderate diff detected in ${testName}. Review recommended before updating baseline.`;
    case 'major':
      return `Major diff detected in ${testName}. Investigation required before updating baseline.`;
  }
}
