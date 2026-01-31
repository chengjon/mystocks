#!/usr/bin/env node
/**
 * Auto-fix common errors in generated-types.ts
 * Run this after type generation to fix TypeScript syntax errors
 */

const fs = require('fs');
const path = require('path');

// Calculate correct path: scripts/ -> src/api/types/generated-types.ts
const typesFile = path.join(__dirname, '../src/api/types/generated-types.ts');

console.log('🔧 Fixing generated-types.ts...');

// Read the file
let content = fs.readFileSync(typesFile, 'utf-8');

// Fix 1: Rename duplicate UnifiedResponse to UnifiedResponseLegacy (line 3214+)
content = content.replace(
  /^export interface UnifiedResponse \{\s*success\?: boolean;\s*message\?: string \| null;\s*data\?: Record<string, any> \| null;\s*\}/gm,
  `// Renamed to avoid conflict with UnifiedResponse<TData> at line 5
export interface UnifiedResponseLegacy {
  success?: boolean;
  message?: string | null;
  data?: Record<string, any> | null;
}`
);

// Fix 2: Replace undefined HMMConfig with Record<string, any>
content = content.replace(
  /hmm_config\?: HMMConfig;/g,
  'hmm_config?: Record<string, any>; // Fixed: HMMConfig undefined'
);

// Fix 3: Replace undefined NeuralNetworkConfig with Record<string, any>
content = content.replace(
  /nn_config\?: NeuralNetworkConfig;/g,
  'nn_config?: Record<string, any>; // Fixed: NeuralNetworkConfig undefined'
);

// Fix 4: Fix Python syntax list[string] to TypeScript string[]
content = content.replace(
  /list\[string\]/g,
  'string[]'
);

// Fix 5: Comment out duplicate StockSearchResult interface (line 3640+)
// The second definition has market?: string while first has market?: string | null
content = content.replace(
  /\/\/ Stock search result\nexport interface StockSearchResult \{\n {2}symbol\?: string;\n {2}name\?: string;\n {2}market\?: string;\n {2}type\?: string;\n {2}current\?: number;\n {2}change\?: number;\n {2}changePercent\?: number;\n\}/,
  `// Stock search result - DUPLICATE (commented out, see line 2669)
// export interface StockSearchResult {
//   symbol?: string;
//   name?: string;
//   market?: string;
//   type?: string;
//   current?: number;
//   change?: number;
//   changePercent?: number;
// }`
);

// Write back
fs.writeFileSync(typesFile, content, 'utf-8');

console.log('✅ Fixed generated-types.ts');
console.log('   - Renamed duplicate UnifiedResponse → UnifiedResponseLegacy');
console.log('   - Replaced HMMConfig → Record<string, any>');
console.log('   - Replaced NeuralNetworkConfig → Record<string, any>');
console.log('   - Fixed list[string] → string[]');
console.log('   - Commented out duplicate StockSearchResponse (if exists)');
