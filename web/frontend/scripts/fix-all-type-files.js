#!/usr/bin/env node
/**
 * Fix common errors in all generated type files
 * Fixes Python syntax in TypeScript type definitions
 */

const fs = require('fs');
const path = require('path');

const typesDir = path.join(__dirname, '../src/api/types');

console.log('🔧 Fixing all type files...');

// Get all TypeScript files in types directory
const files = fs.readdirSync(typesDir)
  .filter(file => file.endsWith('.ts'))
  .map(file => path.join(typesDir, file));

let totalFixes = 0;

files.forEach(file => {
  let content = fs.readFileSync(file, 'utf-8');
  let fixes = 0;

  // Fix 1: Record<(str, Any)> -> Record<string, any>
  const before1 = content.length;
  content = content.replace(/Record<\(str, Any\)>/g, 'Record<string, any>');
  fixes += (before1 - content.length) / 4; // Approximate count

  // Fix 2: (str, Any) -> string, any in other contexts
  const before2 = content.length;
  content = content.replace(/\(str, Any\)/g, 'string, any');
  fixes += (before2 - content.length) / 4;

  // Fix 3: (int, Any) -> number, any
  const before3 = content.length;
  content = content.replace(/\(int, Any\)/g, 'number, any');
  fixes += (before3 - content.length) / 4;

  // Fix 4: (bool, Any) -> boolean, any
  const before4 = content.length;
  content = content.replace(/\(bool, Any\)/g, 'boolean, any');
  fixes += (before4 - content.length) / 4;

  // Fix 5: (float, Any) -> number, any
  const before5 = content.length;
  content = content.replace(/\(float, Any\)/g, 'number, any');
  fixes += (before5 - content.length) / 4;

  // Fix 6: List[str] -> string[]
  const before6 = content.length;
  content = content.replace(/List\[str\]/g, 'string[]');
  fixes += (before6 - content.length) / 3;

  // Fix 7: List[int] -> number[]
  const before7 = content.length;
  content = content.replace(/List\[int\]/g, 'number[]');
  fixes += (before7 - content.length) / 3;

  if (fixes > 0) {
    fs.writeFileSync(file, content, 'utf-8');
    console.log(`✅ Fixed ${path.basename(file)} (${Math.round(fixes)} replacements)`);
    totalFixes += fixes;
  }
});

console.log(`\n📊 Total: Fixed ${Math.round(totalFixes)} errors across ${files.length} files`);
