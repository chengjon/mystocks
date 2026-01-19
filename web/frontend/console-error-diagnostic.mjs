#!/usr/bin/env node

/**
 * Console Error Diagnostic Script
 * Checks the frontend for common rendering issues
 */

import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync, existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const frontendDir = __dirname;
const srcDir = join(frontendDir, 'src');

console.log('🔍 ArtDeco Frontend Diagnostic Tool\n');

// Check 1: Verify critical files exist
console.log('📁 Checking critical files...');
const criticalFiles = [
  'src/main.js',
  'src/App.vue',
  'src/router/index.ts',
  'src/components/artdeco/index.ts',
  'src/components/artdeco/base/index.ts',
  'src/components/artdeco/core/index.ts',
  'src/components/artdeco/specialized/index.ts'
];

let missingFiles = [];
for (const file of criticalFiles) {
  const fullPath = join(frontendDir, file);
  if (existsSync(fullPath)) {
    console.log(`  ✅ ${file}`);
  } else {
    console.log(`  ❌ ${file} - MISSING`);
    missingFiles.push(file);
  }
}

// Check 2: Verify ArtDeco component exports
console.log('\n📦 Checking ArtDeco component exports...');

try {
  const artdecoIndexPath = join(frontendDir, 'src/components/artdeco/index.ts');
  const artdecoIndex = readFileSync(artdecoIndexPath, 'utf-8');

  const baseIndexPath = join(frontendDir, 'src/components/artdeco/base/index.ts');
  const baseIndex = readFileSync(baseIndexPath, 'utf-8');

  const coreIndexPath = join(frontendDir, 'src/components/artdeco/core/index.ts');
  const coreIndex = readFileSync(coreIndexPath, 'utf-8');

  const specializedIndexPath = join(frontendDir, 'src/components/artdeco/specialized/index.ts');
  const specializedIndex = readFileSync(specializedIndexPath, 'utf-8');

  // Extract exported component names
  const extractExports = (content) => {
    const matches = content.matchAll(/export \{ default as (\w+) \}/g);
    return Array.from(matches).map(m => m[1]);
  };

  const baseExports = extractExports(baseIndex);
  const coreExports = extractExports(coreIndex);
  const specializedExports = extractExports(specializedIndex);

  console.log(`  ✅ Base components: ${baseExports.length}`);
  console.log(`  ✅ Core components: ${coreExports.length}`);
  console.log(`  ✅ Specialized components: ${specializedExports.length}`);

  // Check 3: Verify used components in ArtDecoDashboard
  console.log('\n🎨 Checking ArtDecoDashboard.vue imports...');

  const dashboardPath = join(frontendDir, 'src/views/artdeco-pages/ArtDecoDashboard.vue');
  const dashboardContent = readFileSync(dashboardPath, 'utf-8');

  // Extract import statement
  const importMatch = dashboardContent.match(/import \{ ([^}]+) \} from '@\/components\/artdeco'/);
  if (importMatch) {
    const importedComponents = importMatch[1].split(',').map(s => s.trim());
    console.log(`  📥 Dashboard imports: ${importedComponents.length} components`);

    const allExports = [...baseExports, ...coreExports, ...specializedExports];
    const missingComponents = [];

    for (const comp of importedComponents) {
      if (!allExports.includes(comp)) {
        console.log(`  ❌ ${comp} - NOT EXPORTED`);
        missingComponents.push(comp);
      } else {
        console.log(`  ✅ ${comp}`);
      }
    }

    if (missingComponents.length > 0) {
      console.log(`\n⚠️  Missing components: ${missingComponents.join(', ')}`);
    }
  }

} catch (error) {
  console.log(`  ❌ Error reading component files: ${error.message}`);
}

// Check 4: Verify Vue app mounting
console.log('\n🔧 Checking Vue app mounting...');

try {
  const mainJsPath = join(frontendDir, 'src/main.js');
  const mainJs = readFileSync(mainJsPath, 'utf-8');

  if (mainJs.includes("app.mount('#app')")) {
    console.log('  ✅ app.mount(\'#app\') found');
  } else {
    console.log('  ❌ app.mount(\'#app\') NOT found');
  }

  if (mainJs.includes('console.log')) {
    console.log('  ✅ Debug console.log found');
  }
} catch (error) {
  console.log(`  ❌ Error reading main.js: ${error.message}`);
}

// Check 5: Verify router configuration
console.log('\n🛣️  Checking router configuration...');

try {
  const routerPath = join(frontendDir, 'src/router/index.ts');
  const router = readFileSync(routerPath, 'utf-8');

  const dashboardRoute = router.includes('ArtDecoDashboard');
  const testRoute = router.includes('Test.vue');

  if (dashboardRoute) {
    console.log('  ✅ ArtDecoDashboard route configured');
  } else {
    console.log('  ❌ ArtDecoDashboard route NOT configured');
  }

  if (testRoute) {
    console.log('  ✅ Test route configured');
  }

  // Check home route
  if (router.includes("component: () => import('@/views/Test.vue')")) {
    console.log('  ⚠️  Home route points to Test.vue (temporary)');
  }

} catch (error) {
  console.log(`  ❌ Error reading router: ${error.message}`);
}

// Check 6: Check for common console errors
console.log('\n🐛 Common issues check...');

// Check for dayjs imports
try {
  const mainJsPath = join(frontendDir, 'src/main.js');
  const mainJs = readFileSync(mainJsPath, 'utf-8');

  if (mainJs.includes('dayjs')) {
    if (mainJs.includes("from './services/versionNegotiator.ts'")) {
      console.log('  ✅ dayjs imported with .ts extension');
    } else {
      console.log('  ⚠️  dayjs import may have missing .ts extension');
    }
  }
} catch (error) {
  console.log(`  ⚠️  Could not check dayjs imports`);
}

// Summary
console.log('\n' + '='.repeat(60));
console.log('📊 DIAGNOSTIC SUMMARY');
console.log('='.repeat(60));

if (missingFiles.length > 0) {
  console.log(`❌ Missing files: ${missingFiles.length}`);
  missingFiles.forEach(f => console.log(`   - ${f}`));
} else {
  console.log('✅ All critical files exist');
}

console.log('\n💡 Next steps:');
console.log('1. Check browser DevTools Console for actual errors');
console.log('2. Check Network tab for failed API calls');
console.log('3. Verify #app div has content after page load');
console.log('4. Run: npm run dev and navigate to http://localhost:3001');

console.log('\n✨ Diagnostic complete!\n');
