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
      // ESM兼容性保障 - 强制使用dayjs ESM版本
      'dayjs': 'dayjs/esm/index.js',
      // 修复dayjs插件导入问题 - Element Plus需要的ESM兼容导入
      'dayjs/plugin/advancedFormat': 'dayjs/esm/plugin/advancedFormat',
      'dayjs/plugin/customParseFormat': 'dayjs/esm/plugin/customParseFormat',
      'dayjs/plugin/localeData': 'dayjs/esm/plugin/localeData',
      'dayjs/plugin/weekday': 'dayjs/esm/plugin/weekday',
      'dayjs/plugin/weekOfYear': 'dayjs/esm/plugin/weekOfYear',
      'dayjs/plugin/weekYear': 'dayjs/esm/plugin/weekYear',
      '@': resolve(__dirname, './src'),
    },
  },
  // ESM模块优化配置
  optimizeDeps: {
    exclude: ['dayjs'] // 排除dayjs，避免预构建问题
  },
});
