#!/usr/bin/env node

/**
 * Summarize Lighthouse Reports
 * Extracts key metrics from all JSON reports and creates a summary
 */

const fs = require('fs');
const path = require('path');

const REPORT_DIR = process.argv[2] || './reports';
const TIMESTAMP = process.argv[3];

// Get all JSON report files
const reportFiles = fs.readdirSync(REPORT_DIR)
  .filter(file => file.endsWith('.json') && file.includes(TIMESTAMP))
  .sort();

console.log(`Found ${reportFiles.length} report files`);

// Summary structure
const summary = {
  timestamp: TIMESTAMP,
  totalAudits: reportFiles.length,
  pages: [],
  averages: {
    performance: 0,
    accessibility: 0,
    bestPractices: 0,
    seo: 0,
    fcp: 0,
    lcp: 0,
    tbt: 0,
    cls: 0,
    si: 0
  },
  issues: {
    critical: [],
    warnings: [],
    opportunities: []
  }
};

// Process each report
reportFiles.forEach(file => {
  const reportPath = path.join(REPORT_DIR, file);
  const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));

  const pageName = file.replace(/lighthouse-/, '').replace(`-${TIMESTAMP}.json`, '');

  // Extract scores
  const categories = report.categories;
  const audits = report.audits;

  const pageData = {
    name: pageName,
    url: report.requestedUrl,
    scores: {
      performance: categories.performance?.score || 0,
      accessibility: categories.accessibility?.score || 0,
      bestPractices: categories['best-practices']?.score || 0,
      seo: categories.seo?.score || 0
    },
    metrics: {
      fcp: audits['first-contentful-paint']?.displayValue || 'N/A',
      lcp: audits['largest-contentful-paint']?.displayValue || 'N/A',
      tbt: audits['total-blocking-time']?.displayValue || 'N/A',
      cls: audits['cumulative-layout-shift']?.displayValue || 'N/A',
      si: audits['speed-index']?.displayValue || 'N/A'
    }
  };

  summary.pages.push(pageData);

  // Check for critical issues
  const failedAudits = Object.values(audits).filter(audit =>
    audit.score !== null && audit.score < 0.5 && audit.scoreDisplayMode === 'binary'
  );

  failedAudits.forEach(audit => {
    summary.issues.critical.push({
      page: pageName,
      title: audit.title,
      description: audit.description
    });
  });
});

// Calculate averages
const totalPages = summary.pages.length;
if (totalPages > 0) {
  summary.averages.performance = (summary.pages.reduce((sum, p) => sum + p.scores.performance, 0) / totalPages * 100).toFixed(0);
  summary.averages.accessibility = (summary.pages.reduce((sum, p) => sum + p.scores.accessibility, 0) / totalPages * 100).toFixed(0);
  summary.averages.bestPractices = (summary.pages.reduce((sum, p) => sum + p.scores.bestPractices, 0) / totalPages * 100).toFixed(0);
  summary.averages.seo = (summary.pages.reduce((sum, p) => sum + p.scores.seo, 0) / totalPages * 100).toFixed(0);
}

// Save summary
const summaryPath = path.join(REPORT_DIR, `lighthouse-summary-${TIMESTAMP}.json`);
fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));

console.log('\n========================================');
console.log('LIGHTHOUSE AUDIT SUMMARY');
console.log('========================================\n');

console.log('Average Scores:');
console.log(`  Performance:     ${summary.averages.performance}/100`);
console.log(`  Accessibility:   ${summary.averages.accessibility}/100`);
console.log(`  Best Practices:  ${summary.averages.bestPractices}/100`);
console.log(`  SEO:            ${summary.averages.seo}/100`);
console.log('');

console.log('Page-by-Page Results:');
summary.pages.forEach(page => {
  console.log(`\n  ${page.name}:`);
  console.log(`    Performance:    ${page.scores.performance * 100}/100`);
  console.log(`    Accessibility:  ${page.scores.accessibility * 100}/100`);
  console.log(`    Best Practices: ${page.scores.bestPractices * 100}/100`);
  console.log(`    SEO:           ${page.scores.seo * 100}/100`);
});

if (summary.issues.critical.length > 0) {
  console.log('\n\nCritical Issues:');
  summary.issues.critical.slice(0, 10).forEach(issue => {
    console.log(`\n  [${issue.page}] ${issue.title}`);
  });
  console.log(`\n  ... and ${summary.issues.critical.length - 10} more`);
}

console.log('\n========================================\n');
