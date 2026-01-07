import js from '@eslint/js'
import tseslintPlugin from '@typescript-eslint/eslint-plugin'
import tseslintParser from '@typescript-eslint/parser'
import vue from 'eslint-plugin-vue'
import * as parserVue from 'vue-eslint-parser'
import eslintConfigPrettier from 'eslint-config-prettier/flat'

export default [
  // Apply recommended configs for JavaScript and TypeScript
  js.configs.recommended,

  // Global ignores
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'reports/**',
      '*.min.js',
      'src/**/*.spec.ts',
      'src/**/*.test.ts'
    ]
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
        'error',
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
      'prefer-const': 'error',
      'no-var': 'error'
    }
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
        process: true
      }
    },
    rules: {
      'no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_'
        }
      ]
    }
  },

  // Apply Prettier config last to override other formatting rules
  eslintConfigPrettier
]
