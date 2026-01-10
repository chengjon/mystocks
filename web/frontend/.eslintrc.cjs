module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: [
    'plugin:vue/vue3-recommended',
    'eslint:recommended',
    '@vue/typescript/recommended',
    '@vue/prettier'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  plugins: ['vue', '@typescript-eslint'],
  rules: {
    // TypeScript 规则
    '@typescript-eslint/no-explicit-any': 'warn', // 警告而非禁止any
    '@typescript-eslint/no-unused-vars': ['warn', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_'
    }],
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-non-null-assertion': 'warn',
    
    // Vue 规则
    'vue/multi-word-component-names': 'off', // 允许单词组件名
    'vue/no-v-html': 'warn', // 警告使用v-html
    'vue/require-default-prop': 'off', // 不强制默认props
    'vue/require-prop-types': 'off', // 不强制prop类型（使用TypeScript）
    
    // 通用规则
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'prefer-const': 'warn', // 建议使用const
    'no-var': 'error', // 禁止使用var
    
    // Import 排序规则
    'sort-imports': 'off', // 使用eslint-plugin-import的排序
    'import/order': ['warn', {
      groups: [
        'builtin', // 内置模块
        'external', // 外部依赖
        'internal', // 内部路径别名
        'parent', // 父级目录
        'sibling', // 同级目录
        'index' // 当前目录index
      ],
      'newlines-between': 'never',
      alphabetize: {
        order: 'asc', // 按字母顺序
        caseInsensitive: true
      }
    }]
  },
  globals: {
    defineProps: 'readonly',
    defineEmits: 'readonly',
    defineExpose: 'readonly',
    withDefaults: 'readonly'
  }
}
