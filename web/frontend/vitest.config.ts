import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom',
    include: [
      'src/**/*.{test,spec}.{js,ts}',
      'src/**/__tests__/**/*.{js,ts}',
      'tests/unit/**/*.{js,ts}',
    ],
    exclude: [
      'node_modules',
      'dist',
      'tests/e2e',
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: [
        'src/api/**/*.{js,ts}',
        'src/composables/**/*.{js,ts}',
        'src/adapters/**/*.{js,ts}',
        'src/services/**/*.{js,ts}',
        'src/utils/**/*.{js,ts}', // 添加 utils 目录
      ],
      exclude: [
        'src/api/types/**',
        'src/mock/**',
        '**/*.test.{js,ts}',
        '**/*.spec.{js,ts}',
        '**/types/**',
      ],
      statements: 80,      // 目标语句覆盖率 80%
      branches: 75,        // 目标分支覆盖率 75%
      functions: 80,       // 目标函数覆盖率 80%
      lines: 80,           // 目标行覆盖率 80%
    },
    setupFiles: [],
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
});
