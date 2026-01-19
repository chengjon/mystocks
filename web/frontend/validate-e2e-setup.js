#!/usr/bin/env node

/**
 * E2E Test Suite Validation Script
 * 验证测试套件的语法和基本结构完整性
 */

const fs = require('fs');
const path = require('path');

function validateTestFile() {
  const testFile = path.join(__dirname, 'tests', 'comprehensive-e2e-validation.spec.ts');

  console.log('🔍 Validating E2E test file...');

  if (!fs.existsSync(testFile)) {
    console.error('❌ Test file not found:', testFile);
    return false;
  }

  const content = fs.readFileSync(testFile, 'utf-8');

  // 检查必要的导入
  const requiredImports = [
    '@playwright/test',
    'child_process',
    'fs',
    'path'
  ];

  for (const importName of requiredImports) {
    if (!content.includes(importName)) {
      console.error(`❌ Missing import: ${importName}`);
      return false;
    }
  }

  // 检查必要的测试阶段
  const requiredPhases = [
    'Phase 1: 前置校验',
    'Phase 2: 页面加载完整性',
    'Phase 3: 前后端联动',
    'Phase 4: 基础交互'
  ];

  for (const phase of requiredPhases) {
    if (!content.includes(phase)) {
      console.error(`❌ Missing test phase: ${phase}`);
      return false;
    }
  }

  // 检查必要的辅助函数
  const requiredFunctions = [
    'checkPM2Process',
    'checkPortConnectivity',
    'validateApiResponse',
    'recordTestResult'
  ];

  for (const func of requiredFunctions) {
    if (!content.includes(`function ${func}`)) {
      console.error(`❌ Missing helper function: ${func}`);
      return false;
    }
  }

  console.log('✅ Test file validation passed');
  return true;
}

function validateRunnerScript() {
  const runnerFile = path.join(__dirname, 'run-comprehensive-e2e.js');

  console.log('🔍 Validating runner script...');

  if (!fs.existsSync(runnerFile)) {
    console.error('❌ Runner script not found:', runnerFile);
    return false;
  }

  const content = fs.readFileSync(runnerFile, 'utf-8');

  // 检查必要的函数
  const requiredFunctions = [
    'checkPM2Service',
    'checkPort',
    'runTests',
    'showReport'
  ];

  for (const func of requiredFunctions) {
    if (!content.includes(`function ${func}`)) {
      console.error(`❌ Missing function in runner: ${func}`);
      return false;
    }
  }

  console.log('✅ Runner script validation passed');
  return true;
}

function validatePackageJson() {
  const packageFile = path.join(__dirname, 'package.json');

  console.log('🔍 Validating package.json scripts...');

  if (!fs.existsSync(packageFile)) {
    console.error('❌ package.json not found:', packageFile);
    return false;
  }

  const packageJson = JSON.parse(fs.readFileSync(packageFile, 'utf-8'));

  if (!packageJson.scripts || !packageJson.scripts['test:e2e:comprehensive']) {
    console.error('❌ Missing test:e2e:comprehensive script in package.json');
    return false;
  }

  if (!packageJson.scripts['test:e2e:comprehensive'].includes('run-comprehensive-e2e.js')) {
    console.error('❌ test:e2e:comprehensive script not pointing to runner');
    return false;
  }

  console.log('✅ Package.json validation passed');
  return true;
}

function validateReadme() {
  const readmeFile = path.join(__dirname, 'tests', 'README-E2E.md');

  console.log('🔍 Validating README documentation...');

  if (!fs.existsSync(readmeFile)) {
    console.error('❌ README not found:', readmeFile);
    return false;
  }

  const content = fs.readFileSync(readmeFile, 'utf-8');

  const requiredSections = [
    'MyStocks 端到端自动化测试套件',
    'Phase 1: 前置校验',
    'Phase 2: 页面加载完整性',
    'Phase 3: 前后端联动',
    'Phase 4: 基础交互',
    'npm run test:e2e:comprehensive'
  ];

  for (const section of requiredSections) {
    if (!content.includes(section)) {
      console.error(`❌ Missing documentation section: ${section}`);
      return false;
    }
  }

  console.log('✅ README validation passed');
  return true;
}

function main() {
  console.log('🚀 MyStocks E2E Test Suite Validation');
  console.log('=====================================');

  let allPassed = true;

  allPassed &= validateTestFile();
  allPassed &= validateRunnerScript();
  allPassed &= validatePackageJson();
  allPassed &= validateReadme();

  console.log('=====================================');

  if (allPassed) {
    console.log('✅ All validations passed! E2E test suite is ready.');
    console.log('\n📋 Next steps:');
    console.log('1. Start MyStocks services via PM2');
    console.log('2. Run: npm run test:e2e:comprehensive');
    console.log('3. Check results in test-results/ directory');
  } else {
    console.log('❌ Validation failed. Please fix the issues above.');
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { validateTestFile, validateRunnerScript, validatePackageJson, validateReadme };