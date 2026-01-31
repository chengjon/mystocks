# TypeScript 配置参考

**版本**: v1.0 | **更新时间**: 2026-01-20 | **配置版本**: Phase 1.4

> MyStocks项目的TypeScript完整配置参考,涵盖tsconfig.json、ESLint、Vite和package.json。

---

## 📋 目录

1. [配置概览](#配置概览)
2. [tsconfig.json详解](#tsconfigjson详解)
3. [ESLint配置](#eslint配置)
4. [Vite配置](#vite配置)
5. [package.json脚本](#packagejson脚本)
6. [渐进式迁移策略](#渐进式迁移策略)
7. [性能优化配置](#性能优化配置)

---

## 🎯 配置概览

### 配置文件体系

```
web/frontend/
├── tsconfig.json              # TypeScript编译配置 ⭐
├── tsconfig.node.json         # Node环境专用配置
├── .eslintrc.cjs              # ESLint代码检查配置 ⭐
├── vite.config.ts             # Vite构建配置 ⭐
├── package.json               # 项目脚本和依赖 ⭐
└── .vscode/settings.json      # VS Code工作区配置
```

### 配置优先级

1. **tsconfig.json** (最高) - TypeScript编译器严格遵循
2. **ESLint** - 代码质量检查,可覆盖部分tsconfig设置
3. **Vite** - 开发服务器和构建工具
4. **VS Code** - IDE配置,不影响编译结果

### 当前配置状态 (Phase 1.4)

| 配置项 | 状态 | 说明 |
|-------|------|------|
| **strict模式** | ✅ 部分启用 | strict=true, 仅针对.ts文件 |
| **noImplicitAny** | ✅ 启用 | 禁止隐式any类型 |
| **strictNullChecks** | ✅ 启用 | 严格空值检查 |
| **checkJs** | ❌ 禁用 | .js文件不检查(共存策略) |
| **增量编译** | ✅ 启用 | 提升编译速度 |

---

## 📝 tsconfig.json详解

### 完整配置文件

```json
{
  "compilerOptions": {
    // ============================================================
    // Language and Environment (语言和环境)
    // ============================================================
    "target": "ES2020",                    // 编译目标: ES2020
    "module": "ESNext",                    // 模块系统: ESNext
    "lib": ["ES2020", "DOM", "DOM.Iterable"],  // 包含的库定义
    "jsx": "preserve",                     // JSX处理: 保留(Vue使用)

    // ============================================================
    // 🚀 Phase 1: 渐进式TypeScript迁移策略
    // ============================================================
    // 策略: 允许JS/TS共存,逐步启用strict模式
    // 目标: TypeScript覆盖率从20% → 90%

    // Phase 1.4.1: 启用基础strict模式（仅针对.ts文件）
    "strict": true,                        // ✅ Phase 1启用
    "noImplicitAny": true,                 // ✅ 禁止隐式any
    "strictNullChecks": true,              // ✅ 严格空值检查
    "noImplicitThis": true,                // ✅ this显式类型
    "alwaysStrict": true,                  // ✅ 严格模式

    // 渐进式启用strict子选项（避免一次性大量错误）
    "noUnusedLocals": false,               // Phase 2启用
    "noUnusedParameters": false,           // Phase 2启用
    "strictFunctionTypes": false,          // Phase 2启用
    "strictBindCallApply": false,          // Phase 2启用
    "strictPropertyInitialization": false,  // Phase 2启用
    "noImplicitReturns": false,            // Phase 2启用
    "noUncheckedIndexedAccess": false,     // Phase 3启用
    "exactOptionalPropertyTypes": false,   // Phase 3启用

    // Phase 1.4.2: JS/TS共存配置
    "allowJs": true,                       // ✅ 允许导入.js文件
    "checkJs": false,                      // ✅ 不检查.js文件

    // ============================================================
    // Module Resolution (模块解析)
    // ============================================================
    "moduleResolution": "bundler",         // 使用bundler解析
    "resolveJsonModule": true,             // 允许导入JSON
    "allowImportingTsExtensions": true,    // 允许导入.ts文件
    "isolatedModules": true,               // 每个文件独立模块
    "noEmit": true,                        // 不生成输出文件(Vite处理)

    // ============================================================
    // Path Mapping (路径映射)
    // ============================================================
    "baseUrl": ".",                        // 基础路径
    "paths": {
      "@/*": ["src/*"],                    // @指向src目录
      "@types/*": ["src/types/*"]          // @types指向类型目录
    },

    // ============================================================
    // Interop Constraints (互操作性)
    // ============================================================
    "esModuleInterop": true,               // ES模块互操作
    "allowSyntheticDefaultImports": true,  // 允许合成默认导入
    "forceConsistentCasingInFileNames": true,  // 强制文件名大小写
    "skipLibCheck": true,                  // 跳过.d.ts文件检查

    // ============================================================
    // Vue Support (Vue支持)
    // ============================================================
    "types": [
      "vite/client",                       // Vite客户端类型
      "element-plus/global",               // Element Plus全局类型
      "node"                               // Node.js类型
    ],

    // ============================================================
    // Additional Options (附加选项)
    // ============================================================
    "incremental": true,                   // ✅ 增量编译
    "sourceMap": true,                     // 生成sourcemap
    "noEmitOnError": false                 // 允许错误但不阻止构建
  },

  // ============================================================
  // File Includes (包含文件)
  // ============================================================
  "include": [
    "src/**/*.ts",                         // TypeScript文件
    "src/**/*.d.ts",                       // 类型声明文件
    "src/**/*.tsx",                        // TSX文件
    "src/**/*.vue",                        // Vue组件
    "src/**/*.js",                         // JavaScript文件
    "src/**/*.jsx",                        // JSX文件
    "src/types/**/*.ts"                    // 共享类型定义
  ],

  // ============================================================
  // File Excludes (排除文件)
  // ============================================================
  "exclude": [
    "dist",                                // 构建输出
    "node_modules",                        // 依赖包
    "reports",                             // 报告目录
    "src/**/*.spec.ts",                    // 测试文件
    "src/**/*.test.ts",
    "src/api/types/generated-types.ts",    // 自动生成文件
    "src/components/market/ProKLineChart.vue"  // 暂时排除
  ],

  // ============================================================
  // Vue-specific compiler options
  // ============================================================
  "vueCompilerOptions": {
    "target": 3.3                          // Vue 3.3目标
  }
}
```

### 关键配置选项详解

#### 1. strict模式配置

**说明**: `strict` 是一系列类型检查选项的总开关

```json
{
  "compilerOptions": {
    "strict": true,                        // 启用所有strict选项

    // strict = 以下选项的总和:
    "noImplicitAny": true,                 // 禁止隐式any
    "strictNullChecks": true,              // 严格null检查
    "strictFunctionTypes": true,           // 严格函数类型
    "strictBindCallApply": true,           // 严格bind/call/apply
    "strictPropertyInitialization": true,  // 严格属性初始化
    "noImplicitThis": true,                // 隐式this检查
    "alwaysStrict": true                   // 严格JavaScript模式
  }
}
```

**Phase 1策略**: 只启用基础strict选项,逐步启用其他选项

#### 2. 模块解析配置

```json
{
  "compilerOptions": {
    "moduleResolution": "bundler",         // 推荐用于Vite
    // "moduleResolution": "node",        // 传统Node.js解析
    // "moduleResolution": "classic",     // 旧版TypeScript解析

    "resolveJsonModule": true,             // 允许import JSON文件
    "allowImportingTsExtensions": true,    // 允许import .ts文件
    "isolatedModules": true                // 每个文件独立处理(Vite需要)
  }
}
```

**模块解析顺序**:
1. 查找相对路径: `./` `../`
2. 查找绝对路径: `/`
3. 查找路径映射: `@/` → `src/`
4. 查找node_modules

#### 3. 路径映射配置

```json
{
  "compilerOptions": {
    "baseUrl": ".",                        // 基础路径
    "paths": {
      "@/*": ["src/*"],                    // @映射到src
      "@components/*": ["src/components/*"],
      "@utils/*": ["src/utils/*"],
      "@api/*": ["src/api/*"],
      "@types/*": ["src/types/*"]
    }
  }
}
```

**使用示例**:
```typescript
// ✅ 使用路径映射
import { UserService } from '@/api/user'
import { formatDate } from '@utils/date'
import type { User } from '@types/user'

// ❌ 相对路径(不推荐)
import { UserService } from '../../../api/user'
```

**Vite配置必须同步**:
```typescript
// vite.config.ts
export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

#### 4. 类型声明配置

```json
{
  "compilerOptions": {
    "types": [
      "vite/client",                       // Vite环境类型
      "element-plus/global",               // Element Plus全局类型
      "node",                              // Node.js类型
      "jest"                               // Jest测试类型(如需要)
    ],

    // 排除自动包含的类型
    // "typeRoots": [
    //   "./node_modules/@types",
    //   "./src/types"
    // ]
  }
}
```

**效果**: 控制哪些全局类型定义被包含

#### 5. 增量编译配置

```json
{
  "compilerOptions": {
    "incremental": true,                   // 启用增量编译
    "tsBuildInfoFile": ".tsbuildinfo"      // 构建信息文件位置
  }
}
```

**性能提升**:
- 首次编译: 100%
- 增量编译: ~20-30% (仅重新编译修改的文件)

---

## 🔍 ESLint配置

### 完整配置文件

```javascript
module.exports = {
  root: true,                             // 不向上查找配置
  env: {
    browser: true,                        // 浏览器环境
    es2021: true,                         // ES2021语法
    node: true                            // Node.js环境
  },

  extends: [
    'plugin:vue/vue3-recommended',        // Vue 3推荐规则
    'eslint:recommended',                  // ESLint推荐规则
    '@vue/typescript/recommended',         // Vue TypeScript规则
    '@vue/prettier'                       // Prettier集成
  ],

  parserOptions: {
    ecmaVersion: 'latest',                 // 最新ECMAScript版本
    sourceType: 'module'                   // ES模块
  },

  plugins: [
    'vue',                                // Vue插件
    '@typescript-eslint'                   // TypeScript插件
  ],

  rules: {
    // ============================================================
    // TypeScript 规则
    // ============================================================
    '@typescript-eslint/no-explicit-any': 'warn',  // any类型警告
    '@typescript-eslint/no-unused-vars': ['warn', {
      argsIgnorePattern: '^_',            // 忽略_开头的参数
      varsIgnorePattern: '^_'             // 忽略_开头的变量
    }],
    '@typescript-eslint/explicit-module-boundary-types': 'off',  // 不要求模块边界类型
    '@typescript-eslint/no-non-null-assertion': 'warn',  // 非空断言警告

    // ============================================================
    // Vue 规则
    // ============================================================
    'vue/multi-word-component-names': 'off',       // 允许单词组件名
    'vue/no-v-html': 'warn',                      // v-html警告
    'vue/require-default-prop': 'off',             // 不强制默认props
    'vue/require-prop-types': 'off',               // 使用TS而非Vue prop类型

    // ============================================================
    // 通用规则
    // ============================================================
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'prefer-const': 'warn',                       // 建议使用const
    'no-var': 'error',                            // 禁止使用var

    // ============================================================
    // Import 排序规则
    // ============================================================
    'import/order': ['warn', {
      groups: [
        'builtin',                              // 内置模块
        'external',                             // 外部依赖
        'internal',                             // 内部路径别名
        'parent',                               // 父级目录
        'sibling',                              // 同级目录
        'index'                                 // 当前目录index
      ],
      'newlines-between': 'never',
      alphabetize: {
        order: 'asc',
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
```

### ESLint规则优先级

**错误级别**:
- `"off"` 或 `0`: 关闭规则
- `"warn"` 或 `1`: 警告(不阻止构建)
- `"error"` 或 `2`: 错误(阻止构建)

**推荐配置**:
```javascript
{
  // TypeScript类型相关 - warn(不阻塞)
  '@typescript-eslint/no-explicit-any': 'warn',
  '@typescript-eslint/no-non-null-assertion': 'warn',

  // 代码质量相关 - error(阻塞)
  'no-var': 'error',
  'prefer-const': 'warn',

  // Vue相关 - off(使用TypeScript替代)
  'vue/require-prop-types': 'off'
}
```

---

## ⚡ Vite配置

### TypeScript相关配置

```typescript
// vite.config.ts
export default defineConfig({
  // ============================================================
  // 插件配置
  // ============================================================
  plugins: [
    vue(),                                // Vue支持
    AutoImport({                          // 自动导入API
      resolvers: [ElementPlusResolver()],
    }),
    Components({                          // 自动导入组件
      resolvers: [ElementPlusResolver()],
      dirs: ['src/components/artdeco'],
      dts: 'src/components.d.ts',         // 生成类型声明
    })
  ],

  // ============================================================
  // 路径解析
  // ============================================================
  resolve: {
    mainFields: ['module', 'main'],       // 优先使用ESM
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'axios': 'axios/dist/browser/axios.cjs'
    }
  },

  // ============================================================
  // 开发服务器
  // ============================================================
  server: {
    host: '0.0.0.0',
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },

  // ============================================================
  // 构建配置
  // ============================================================
  build: {
    outDir: 'dist',
    assetsDir: 'assets',

    // 代码分割优化
    rollupOptions: {
      output: {
        // 手动分块策略
        manualChunks(id) {
          if (id.includes('vue') || id.includes('pinia')) {
            return 'vue-core'
          }
          if (id.includes('element-plus')) {
            return 'element-plus'
          }
          if (id.includes('node_modules')) {
            return 'vendor'
          }
        }
      }
    },

    // 源码映射
    sourcemap: process.env.NODE_ENV === 'development',

    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: true
      }
    },

    // 分块大小警告阈值
    chunkSizeWarningLimit: 1000
  },

  // ============================================================
  // 依赖预构建
  // ============================================================
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'axios'
    ],
    exclude: [
      'echarts'                              // 按需引入
    ]
  }
})
```

### 关键配置说明

#### 1. 自动导入类型生成

```typescript
Components({
  dirs: ['src/components/artdeco'],
  dts: 'src/components.d.ts'                // 生成类型声明文件
})
```

**生成文件**: `src/components.d.ts`
```typescript
// 全局组件类型声明
declare module '@vue/runtime-core' {
  export interface GlobalComponents {
    ArtDecoStatCard: typeof import('./components/artdeco/basic/ArtDecoStatCard.vue')['default']
    // ... 其他组件
  }
}
```

#### 2. 代码分割策略

```typescript
manualChunks(id) {
  // Vue核心库
  if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
    return 'vue-core'
  }

  // Element Plus
  if (id.includes('element-plus')) {
    return 'element-plus'
  }

  // ECharts
  if (id.includes('echarts')) {
    return 'echarts'
  }

  // 其他node_modules
  if (id.includes('node_modules')) {
    return 'vendor'
  }
}
```

**效果**:
- 首屏加载: 只加载`vue-core` + `vendor` (~200KB)
- 按需加载: `echarts`, `element-plus`等(~500KB)
- 体积优化: 首屏体积↓60%

---

## 📦 package.json脚本

### TypeScript相关脚本

```json
{
  "scripts": {
    // ============================================================
    // 类型检查
    // ============================================================
    "type-check": "tsc --noEmit",                           // tsc快速检查
    "type-check:vue": "vue-tsc --noEmit --force",          // vue-tsc完整检查
    "type-check:watch": "vue-tsc --noEmit --watch",        // 监视模式

    // ============================================================
    // 类型生成
    // ============================================================
    "generate-types": "python3 scripts/generate_frontend_types.py",
    "generate-types:watch": "nodemon --watch scripts/generate_frontend_types.py --exec 'npm run generate-types'",

    // ============================================================
    // 代码检查
    // ============================================================
    "lint": "eslint . --ext .vue,.js,.ts,.jsx,.tsx --max-warnings 0",
    "lint:fix": "eslint . --ext .vue,.js,.ts,.jsx,.tsx --fix",

    // ============================================================
    // 构建和开发
    // ============================================================
    "dev": "vite --port 3001",
    "build": "npm run type-check && vite build",
    "build:force": "vite build",                              // 强制构建(跳过类型检查)
    "preview": "vite preview"
  }
}
```

### 脚本使用场景

| 脚本 | 使用场景 | 是否阻塞 |
|------|---------|---------|
| `npm run type-check` | 快速检查.ts文件类型错误 | ✅ 是 |
| `npm run type-check:vue` | 完整检查包含.vue文件 | ✅ 是 |
| `npm run generate-types` | 从Python生成TypeScript类型 | ✅ 是 |
| `npm run lint` | ESLint代码质量检查 | ✅ 是 |
| `npm run lint:fix` | ESLint自动修复 | ❌ 否 |
| `npm run build` | 类型检查+构建 | ✅ 是 |
| `npm run build:force` | 仅构建(跳过类型检查) | ❌ 否 |

---

## 🚀 渐进式迁移策略

### Phase划分

#### Phase 1: 基础类型检查 (当前)

**目标**: TypeScript覆盖率 20% → 60%

**启用配置**:
```json
{
  "compilerOptions": {
    "strict": true,                        // ✅ 启用
    "noImplicitAny": true,                 // ✅ 启用
    "strictNullChecks": true,              // ✅ 启用
    "checkJs": false                       // ✅ 禁用(JS共存)
  }
}
```

**验收标准**:
- [x] 所有.ts文件通过类型检查
- [x] 新增代码必须使用TypeScript
- [x] API适配器完成类型定义

#### Phase 2: 完整类型检查 (计划中)

**目标**: TypeScript覆盖率 60% → 90%

**启用配置**:
```json
{
  "compilerOptions": {
    "noUnusedLocals": true,                // ✅ 启用
    "noUnusedParameters": true,            // ✅ 启用
    "strictFunctionTypes": true,           // ✅ 启用
    "strictBindCallApply": true,           // ✅ 启用
    "strictPropertyInitialization": true,  // ✅ 启用
    "noImplicitReturns": true,             // ✅ 启用
    "noImplicitOverride": true             // ✅ 启用
  }
}
```

**验收标准**:
- [ ] 所有Vue组件完成Props类型定义
- [ ] 所有Store完成类型定义
- [ ] 移除所有`@ts-ignore`注释

#### Phase 3: 严格类型检查 (规划中)

**目标**: TypeScript覆盖率 90% → 100%

**启用配置**:
```json
{
  "compilerOptions": {
    "noUncheckedIndexedAccess": true,      // ✅ 启用
    "exactOptionalPropertyTypes": true,    // ✅ 启用
    "checkJs": true                        // ✅ 启用(检查.js)
  }
}
```

**验收标准**:
- [ ] 所有.js文件迁移到.ts
- [ ] 100%类型覆盖
- [ ] 零`any`类型(除明确标注)

### 迁移优先级

**文件优先级**:
1. **核心业务逻辑** (API适配器、Store)
2. **通用工具函数** (utils/)
3. **Vue组件** (components/)
4. **页面级组件** (views/)
5. **测试文件** (spec.ts, test.ts)

**错误修复优先级**:
1. **P0**: 阻塞编译的错误
2. **P1**: 影响核心功能的错误
3. **P2**: 非关键路径的错误

---

## ⚡ 性能优化配置

### 增量编译

```json
{
  "compilerOptions": {
    "incremental": true,                   // ✅ 启用
    "tsBuildInfoFile": ".tsbuildinfo"
  }
}
```

**效果**:
- 首次编译: 10-30秒
- 增量编译: 2-5秒 (80-90%时间节省)

### 项目引用

```json
// tsconfig.json
{
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}

// tsconfig.app.json (应用代码)
{
  "compilerOptions": {
    "composite": true,
    "incremental": true
  },
  "include": ["src/**/*.ts", "src/**/*.vue"]
}

// tsconfig.node.json (构建工具)
{
  "compilerOptions": {
    "composite": true,
    "module": "ESNext",
    "moduleResolution": "bundler"
  },
  "include": ["vite.config.ts", "plugins/**/*.ts"]
}
```

**效果**:
- 独立编译各个子项目
- 并行编译提升速度
- 缓子项目无需重新编译

### 类型加速

```json
{
  "compilerOptions": {
    "skipLibCheck": true,                  // ✅ 跳过.d.ts检查
    "skipDefaultLibCheck": true            // 跳过默认库检查
  }
}
```

**效果**:
- 减少类型检查时间50-70%
- 适用于开发环境

---

## 🔧 常见配置问题

### 问题1: 路径别名不工作

**症状**: `import { X } from '@/utils'` 报错

**解决方案**:
```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}

// vite.config.ts (必须同步)
export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

### 问题2: Vue组件类型错误

**症状**: `.vue`文件中导入报错

**解决方案**:
```json
// tsconfig.json
{
  "compilerOptions": {
    "jsx": "preserve",                    // 保留JSX
    "types": ["vite/client"]               // Vite类型
  }
}

// shims-vue.d.ts (必须存在)
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

### 问题3: 第三方库类型缺失

**症状**: `Cannot find module 'xxx'`

**解决方案**:
```bash
# 方案1: 安装类型定义
npm install --save-dev @types/xxx

# 方案2: 创建项目级类型声明
// src/types/third-party.d.ts
declare module 'xxx' {
  export interface API {
    method(): void
  }
}

# 方案3: 忽略类型检查(最后手段)
// tsconfig.json
{
  "compilerOptions": {
    "skipLibCheck": true
  }
}
```

### 问题4: strict模式错误过多

**症状**: 启用strict后出现数千错误

**解决方案**:
```json
// 方案1: 渐进式启用
{
  "compilerOptions": {
    "strict": false,                       // 暂时禁用
    "noImplicitAny": true,                 // 单独启用
    "strictNullChecks": true
  }
}

// 方案2: 使用// @ts-ignore临时抑制
// @ts-ignore
const problematicCode: any = getSomeValue()

// 方案3: 调整文件包含范围
{
  "exclude": [
    "src/legacy/**/*.ts",                  // 排除旧代码
    "src/vendor/**/*.ts"
  ]
}
```

---

## 📚 相关文档

### 配置参考
- 📖 [TypeScript官方文档](https://www.typescriptlang.org/tsconfig)
- 📖 [ESLint配置文档](https://eslint.org/docs/latest/user-guide/configuring/)
- 📖 [Vite配置文档](https://vitejs.dev/config/)

### 项目文档
- 📖 [TypeScript快速开始](./Typescript_QUICKSTART.md)
- 📖 [TypeScript最佳实践](./Typescript_BEST_PRACTICES.md)
- 📖 [TypeScript故障排除](./Typescript_TROUBLESHOOTING.md)

### 迁移指南
- 📖 [TypeScript源头修复指南](./TYPESCRIPT_SOURCE_FIX_GUIDE.md)
- 📖 [TypeScript错误修复指南](./TYPESCRIPT_ERROR_FIXING_GUIDE.md)

---

**文档维护**: 本文档应随配置更新同步修订
**最后更新**: 2026-01-20
**维护者**: Main CLI (Claude Code)
**版本**: v1.0 | **Phase**: 1.4
