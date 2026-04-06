import js from '@eslint/js'
import tseslintPlugin from '@typescript-eslint/eslint-plugin'
import tseslintParser from '@typescript-eslint/parser'
import vue from 'eslint-plugin-vue'
import * as parserVue from 'vue-eslint-parser'
import eslintConfigPrettier from 'eslint-config-prettier/flat'

const STRICT_TS_BOUNDARY_FILES = ['src/api/**/*.ts', 'src/services/**/*.ts', 'src/utils/**/*.ts']
const STRICT_IMPORT_FILES = ['src/api/**/*.{ts,js}', 'src/services/**/*.{ts,js}', 'src/utils/**/*.{ts,js}']

const LEGACY_ANY_ALLOWLIST = [
  'src/api/index.ts',
  'src/api/monitoring.ts',
  'src/services/WencaiQueryEngine.ts',
  'src/utils/adapters.ts',
  'src/utils/monitoring-adapters.ts',
  'src/utils/performance/part-2.ts',
  'src/utils/sse/part-1.ts',
  'src/utils/strategy-adapters.ts',
  'src/utils/trade-adapters.ts',
  'src/utils/websocket-manager.ts',
]

export default [
  // Apply recommended configs for JavaScript and TypeScript
  js.configs.recommended,

  // Global ignores
  {
    ignores: [
      'dist/**',
      'dist-lighthouse/**',
      'dist-ssr/**',
      'build/**',
      'node_modules/**',
      'reports/**',
      'coverage/**',
      '.nyc_output/**',
      '*.min.js',
      '*.local',
      '.env.local',
      '.env.*.local',
      'logs/**',
      '*.log',
      '.vscode/**',
      '.idea/**',
      '.DS_Store',
      '*.suo',
      '*.ntvs*',
      '*.njsproj',
      '*.sln',
      '*.sw?',
      'auto-imports.d.ts',
      'src/components.d.ts',
      'src/**/*.spec.ts',
      'src/**/*.test.ts',
      // 诊断和测试文件（临时文件）
      '*.mjs',
      '*-diagnostic.mjs',
      '*-test*.mjs',
      'test_*.js',
      'test_*.mjs',
      'e2e-test-runner.mjs',
      'web_test*.mjs',
      'verify-*.mjs',
      'check-*.mjs',
      'console-error-diagnostic.mjs',
      'comprehensive-diagnostic.mjs',
      'browser-diagnostic.mjs',
      'artdeco-page-structure-diagnostic.mjs',
      'mainjs-check-detailed.mjs',
      'scripts/diagnostics/**',
      'tests/**',
      'tests.unit/**',
      'tests.utils/**',
      'tests.e2e/**',
      '**/*.spec.ts',
      '**/*.test.ts',
      '**/*.spec.js',
      '**/*.test.js',
      'cypress/**',
      // CommonJS 配置文件
      '.eslintrc.*',
      'ecosystem*.js',
      'run-comprehensive-e2e.js',
      'scripts/**/*.js',
      'validate-e2e-setup.js',
      'verify-mount.js',
      'validate-*.js',
      'verify-*.mjs',
      'test-*.js',
      // 备份文件
      'archives/**',
      '**/*.min.js'
    ]
  },

  // 类型声明文件和自动生成文件：允许 any（第三方库类型补充、API 自动生成）
  {
    files: [
      'src/types/**/*.d.ts',
      'src/api/types/generated-types.ts',
    ],
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-vars': 'off',
    },
  },

  // Vue and TypeScript configuration
  {
    files: ['**/*.vue', '**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: parserVue,
      parserOptions: {
        parser: tseslintParser,
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true
        },
        extraFileExtensions: ['.vue']
      },
      globals: {
        // Browser globals
        browser: true,
        es2021: true,
        node: true,
        console: true,
        window: true,
        document: true,
        navigator: true,
        history: true,
        location: true,
        localStorage: true,
        sessionStorage: true,
        setTimeout: true,
        clearTimeout: true,
        setInterval: true,
        clearInterval: true,
        URLSearchParams: true,
        process: true,
        globalThis: true,
        Blob: true,
        FormData: true,
        XMLHttpRequest: true,
        fetch: true,
        URL: true,
        Headers: true,
        Request: true,
        Response: true,

        // Browser APIs (missing TypeScript globals)
        MouseEvent: true,
        HTMLElement: true,
        HTMLInputElement: true,
        HTMLDivElement: true,
        HTMLButtonElement: true,
        HTMLCanvasElement: true,
        HTMLImageElement: true,
        Event: true,
        EventTarget: true,
        Node: true,
        Element: true,
        CSSStyleDeclaration: true,

        // Window methods
        alert: true,
        confirm: true,
        prompt: true
      }
    },
    plugins: {
      '@typescript-eslint': tseslintPlugin,
      vue
    },
    rules: {
      // Disable no-undef for TypeScript (TypeScript handles this)
      'no-undef': 'off',

      // TypeScript specific rules
      '@typescript-eslint/no-unused-vars': [
        'warn',  // Downgraded to warn for Phase 1 migration
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_'
        }
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-non-null-assertion': 'warn',

      // Vue specific rules
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'warn',
      'vue/require-default-prop': 'off',
      'vue/require-explicit-emits': 'off',
      'vue/html-self-closing': [
        'error',
        {
          html: {
            void: 'always',
            normal: 'never',
            component: 'always'
          }
        }
      ],

      // General JavaScript rules
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
      'no-unused-vars': 'off',
      'prefer-const': 'warn',  // Downgraded to warn for Phase 1
      'no-var': 'error',
      'no-empty': 'warn',  // Downgraded to warn for Phase 1
      'no-case-declarations': 'warn',  // Downgraded to warn for Phase 1
      'no-redeclare': 'warn'  // Downgraded to warn for Phase 1 (many in generated types)
    }
  },

  // Source JavaScript runtime globals
  {
    files: ['src/**/*.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        console: true,
        window: true,
        document: true,
        navigator: true,
        location: true,
        history: true,
        localStorage: true,
        sessionStorage: true,
        setTimeout: true,
        clearTimeout: true,
        setInterval: true,
        clearInterval: true,
        performance: true,
        fetch: true,
        URL: true,
        Headers: true,
        Request: true,
        Response: true,
      }
    }
  },

  // 前端业务层渐进式编码门禁：
  // 1) 导出函数边界必须显式声明返回类型
  // 2) 业务代码默认禁止新增裸 any
  {
    files: STRICT_TS_BOUNDARY_FILES,
    rules: {
      '@typescript-eslint/explicit-module-boundary-types': 'error',
      '@typescript-eslint/no-explicit-any': 'error',
    },
  },

  // 导入规范门禁：
  // 1) 本地/别名导入必须显式扩展名
  // 2) 第三方包导入必须位于本地导入之前
  // 3) 样式导入必须位于最后
  {
    files: STRICT_IMPORT_FILES,
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector:
            "ImportDeclaration[source.value=/^(@\\/|\\.\\.?\\/)(?!.*\\.(?:ts|js|vue|css|scss)$).+/]",
          message: 'Local and alias imports must use explicit file extensions.',
        },
        {
          selector:
            "Program > ImportDeclaration[source.value=/^(@\\/|\\.\\.?\\/)/] ~ ImportDeclaration[source.value=/^(?!@\\/|\\.\\.?\\/).+/]",
          message: 'External package imports must appear before alias and relative imports.',
        },
        {
          selector:
            "Program > ImportDeclaration[source.value=/\\.(?:css|scss)$/] ~ ImportDeclaration:not([source.value=/\\.(?:css|scss)$/])",
          message: 'Style imports must appear after all code imports.',
        },
      ],
    },
  },

  // 历史技术债白名单：保留增量治理空间，不阻断当前存量代码
  {
    files: LEGACY_ANY_ALLOWLIST,
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
    },
  },

  // Plain JavaScript files
  {
    files: ['**/*.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        browser: true,
        es2021: true,
        node: true,
        console: true,
        window: true,
        document: true,
        localStorage: true,
        sessionStorage: true,
        process: true,
        // Element Plus components (auto-imported)
        ElMessage: true,
        ElMessageBox: true,
        ElNotification: true,
        ElLoading: true,
        // Browser globals
        URLSearchParams: true,
        URL: true,
        Headers: true,
        Request: true,
        Response: true,
        fetch: true,
        Blob: true,
        FormData: true,
        XMLHttpRequest: true
      }
    },
    rules: {
      'no-unused-vars': [
        'warn',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_'
        }
      ],
      'no-undef': 'warn'
    }
  },

  // Node ESM scripts
  {
    files: ['scripts/**/*.mjs'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        process: true,
        console: true,
        URL: true,
        setTimeout: true,
        clearTimeout: true,
      }
    }
  },

  // CommonJS config files
  {
    files: ['playwright.config.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'script',
      globals: {
        require: true,
        module: true,
        __dirname: true,
        process: true,
      }
    }
  },

  // Root diagnostic scripts
  {
    files: ['check_console.js', 'check_page.js', 'debug_render.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'script',
      globals: {
        require: true,
        location: true,
      }
    }
  },

  // Service Worker runtime globals
  {
    files: ['public/sw.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'script',
      globals: {
        self: true,
        caches: true,
        clients: true,
        setTimeout: true,
        setInterval: true,
      }
    }
  },

  // Web Worker runtime globals
  {
    files: ['public/workers/**/*.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'script',
      globals: {
        self: true,
        importScripts: true,
        setInterval: true,
        performance: true,
        WorkerMessageUtils: true,
        WorkerMessageType: true,
      }
    }
  },

  // Apply Prettier config last to override other formatting rules
  eslintConfigPrettier,
  // 类型声明文件和自动生成的类型文件 - 禁用 no-explicit-any
  // 这些文件中的 any 是合理的：自动生成的类型、第三方库声明、通用 API 类型
  {
    files: [
      'src/types/**/*.d.ts',
      'src/shims-vue.d.ts',
      'src/api/types/generated-types.ts',
      'src/api/types/common.ts',
      'src/api/types/analysis.ts',
      'src/api/types/strategy.ts',
      'src/api/types/admin.ts',
      'src/api/types/global.d.ts',
      'src/types/klinecharts.d.ts',
    ],
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-vars': 'off',
    },
  },
]
