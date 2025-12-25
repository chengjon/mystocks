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
      ],
      exclude: [
        'src/api/types/**',
        'src/mock/**',
        '**/*.test.{js,ts}',
        '**/*.spec.{js,ts}',
        '**/types/**',
      ],
    },
    setupFiles: [],
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
});
