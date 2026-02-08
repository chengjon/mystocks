# 将HTML文档转换为ArtDeco风格的Vue页面指南

作为Web开发专家，我将指导您如何将现有的HTML文档转换为符合本项目ArtDeco设计风格的Vue页面。这个过程将涉及组件化、样式集成和数据绑定，旨在确保页面不仅功能完善，而且视觉上与ArtDeco设计系统高度一致。

## 🎯 核心原则

1.  **组件化**：将HTML文档分解为可复用、独立的Vue组件。
2.  **样式统一**：充分利用本项目已有的ArtDeco设计令牌（`artdeco-tokens.scss`）和组件样式。
3.  **动态响应**：利用Vue的响应式系统实现数据绑定和交互逻辑。
4.  **复用优先**：优先使用本项目已有的ArtDeco基础组件（如 `ArtDecoIcon`, `ArtDecoBadge`, `ArtDecoToast` 等）。

## 🚀 转换步骤

### 步骤1：分析HTML结构与内容

在开始转换之前，彻底理解原始HTML文档的结构和内容是关键。

1.  **识别主要区块**：将HTML文档划分为逻辑区域，例如：头部 (Header)、侧边栏 (Sidebar)、主内容区 (Main Content)、卡片 (Card)、表单 (Form)、列表 (List) 等。
2.  **提取可复用元素**：找出在文档中重复出现的UI模式，例如按钮、输入框、标题、段落、图标、数据展示块。这些是未来可以抽象为独立Vue组件的候选。
3.  **明确交互需求**：文档中的哪些部分需要用户交互？哪些需要显示动态数据？这有助于规划Vue组件的逻辑和数据流。

### 步骤2：创建Vue单文件组件 (.vue)

为您的新ArtDeco页面创建一个 `.vue` 文件。

1.  **文件结构**：
    ```vue
    <!-- web/frontend/src/views/YourNewArtDecoPage.vue -->
    <template>
      <!-- 在这里放置转换后的HTML结构 -->
    </template>

    <script setup lang="ts">
    // 在这里放置组件的逻辑
    </script>

    <style scoped lang="scss">
    // 在这里放置组件的局部样式
    </style>
    ```

2.  **迁移HTML**：将原始HTML文档的 `<head>` 和 `<body>` 内部的核心内容小心地复制到 `<template>` 标签中。暂时保留原始的HTML标签和类名，我们稍后会逐步ArtDeco化。

### 步骤3：集成ArtDeco设计系统（样式篇）

这是将页面转换为ArtDeco风格的核心步骤。

1.  **导入ArtDeco设计令牌**：在 `<style scoped lang="scss">` 标签的顶部，导入项目核心的ArtDeco设计令牌文件。
    ```scss
    // web/frontend/src/views/YourNewArtDecoPage.vue (style block)
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-menu.scss'; // 如果有通用的ArtDeco组件样式
    ```
    这将使您能够直接使用 `--artdeco-bg-global`, `--artdeco-gold-primary`, `--artdeco-text-base` 等CSS变量。

2.  **应用ArtDeco CSS类/Mixin**：
    *   **背景和颜色**：将背景颜色替换为 `--artdeco-bg-global`, `--artdeco-bg-base`, `--artdeco-bg-card` 等，将字体颜色替换为 `--artdeco-fg-primary`, `--artdeco-fg-muted` 等。
    *   **字体和排版**：为标题、正文应用 `--artdeco-font-heading` 和 `--artdeco-font-body`。使用 `--artdeco-text-xl`, `--artdeco-text-base` 等调整字体大小。
    *   **间距**：利用 `--artdeco-spacing-sm`, `--artdeco-spacing-md` 等 ArtDeco 间距变量来控制元素之间的距离。
    *   **边框和圆角**：利用 `--artdeco-border-default`, `--artdeco-radius-sm` 等。记住 ArtDeco 风格偏爱尖锐的线条和最小的圆角。
    *   **阴影和发光**：使用 `--artdeco-shadow-md` 或 `--artdeco-glow-subtle` 来取代普通的灰暗阴影，以实现ArtDeco特有的金色光晕效果。
    *   **利用Mixin**：项目在 `artdeco-tokens.scss` 中定义了许多有用的 SCSS Mixin，例如 `@include artdeco-corner-brackets`, `@include artdeco-hover-lift-glow`, `@include artdeco-gradient-text` 等。将这些 Mixin 应用到相应的元素上，以快速赋予ArtDeco风格的装饰和交互效果。

    **示例**：
    ```scss
    .my-card {
      background: var(--artdeco-bg-card);
      border: 1px solid var(--artdeco-border-default);
      padding: var(--artdeco-spacing-lg);
      box-shadow: var(--artdeco-shadow-md);
      @include artdeco-geometric-corners(var(--artdeco-gold-dim), 12px, 1px);
    }

    .my-heading {
      font-family: var(--artdeco-font-heading);
      color: var(--artdeco-gold-primary);
      font-size: var(--artdeco-text-2xl);
      @include artdeco-gradient-text;
    }
    ```

### 步骤4：替换为ArtDeco组件（组件化篇）

这是实现组件复用和维护统一风格的关键。

1.  **引入 ArtDeco 基础组件**：
    *   根据步骤1的分析，将原始HTML中对应的通用元素替换为本项目已有的ArtDeco组件。
    *   **图标**：将 `<i>` 标签或图片图标替换为 `ArtDecoIcon` 组件 (`@/components/artdeco/core/ArtDecoIcon.vue`)。
        ```html
        <!-- 之前: <i class="fa fa-home"></i> -->
        <ArtDecoIcon name="Home" size="sm" color="var(--artdeco-gold-primary)" variant="decorative" animated />
        ```
    *   **徽章**：将普通的 `<span>` 徽章替换为 `ArtDecoBadge` 组件 (`@/components/artdeco/core/ArtDecoBadge.vue`)。
        ```html
        <!-- 之前: <span class="badge">New</span> -->
        <ArtDecoBadge text="New" type="primary" />
        <ArtDecoBadge type="danger">API Error</ArtDecoBadge>
        ```
    *   **通知**：对于页面内的通知/提示，使用 `useToastManager` 提供的 `ArtDecoToast`。

2.  **创建新的 ArtDeco 业务组件**：
    *   如果HTML文档中有特定业务逻辑或复杂结构的重复UI模式（如一个自定义的数据展示卡片，或一个复杂的筛选表单），将其抽取为独立的Vue组件。
    *   在这些新组件内部，重复步骤3和步骤4的过程，确保它们也遵循ArtDeco风格。
    *   **例如**：如果您有一个展示股票实时行情的复杂卡片，可以创建一个 `ArtDecoStockQuoteCard.vue` 组件，并在其中集成 `ArtDecoIcon` 和 `ArtDecoBadge`。

### 步骤5：数据绑定与交互（逻辑篇）

将静态页面转换为动态可交互的Vue应用。

1.  **定义响应式数据**：在 `<script setup>` 中使用 `ref` 或 `reactive` 定义页面所需的数据。
    ```typescript
    import { ref } from 'vue';
    const pageTitle = ref('My ArtDeco Page');
    const items = ref([]);
    ```

2.  **事件处理**：将HTML元素上的事件监听器转换为Vue的 `@event` 语法，并在 `<script setup>` 中定义相应的处理函数。
    ```html
    <ArtDecoButton @click="handleButtonClick">Click Me</ArtDecoButton>
    ```
    ```typescript
    const handleButtonClick = () => {
      console.log('Button was clicked!');
      // ... 更多逻辑
    };
    ```

3.  **条件渲染和列表渲染**：使用 `v-if`, `v-for` 等Vue指令，根据数据动态显示或隐藏元素，以及渲染列表内容。
    ```html
    <div v-if="isLoading">Loading data...</div>
    <ul v-else>
      <li v-for="item in items" :key="item.id">{{ item.name }}</li>
    </ul>
    ```

### 步骤6：集成API数据（数据流篇）

如果页面需要动态数据，请利用项目已有的数据服务。

1.  **数据获取服务**：利用 `menuDataFetcher.ts` (如果您的页面数据结构与菜单数据获取逻辑兼容) 或创建新的服务文件，封装页面的API请求。
    ```typescript
    // web/frontend/src/services/yourPageDataService.ts
    import { menuDataFetcher } from '@/services/menuDataFetcher'; // 或自定义fetcher
    
    export const fetchPageData = async () => {
        // ... 调用后端API的逻辑
        // return await menuDataFetcher.fetch('GET', '/api/your-page-data');
    };
    ```

2.  **在组件中调用API**：在Vue组件的 `onMounted` 钩子中调用服务层方法获取数据，并更新组件的响应式状态。
    ```typescript
    import { onMounted } from 'vue';
    // ... 导入数据服务

    onMounted(async () => {
      try {
        // data.value = await fetchPageData();
      } catch (error) {
        // useToastManager.showError('Failed to load page data.');
      }
    });
    ```

3.  **实时数据更新**：如果页面需要实时数据显示（例如市场行情），可以使用 `useWebSocketEnhanced` composable 来订阅相关WebSocket频道，并根据接收到的消息更新UI。

### 步骤7：路由配置 (如果需要)

如果这个ArtDeco页面是一个独立的视图，请将其添加到项目的路由配置中。

1.  **编辑 `web/frontend/src/router/index.ts`**：
    ```typescript
    // ... 其他路由
    {
      path: '/your-artdeco-page',
      name: 'your-artdeco-page',
      component: () => import('@/views/YourNewArtDecoPage.vue'), // 指向您创建的Vue文件
      meta: {
        title: '我的ArtDeco页面',
        icon: '💎', // 选择一个合适的ArtDecoIcon名称
        requiresAuth: true // 根据需要设置
      }
    },
    // ...
    ```
2.  **集成布局**：确保您的页面在 `ArtDecoLayout.vue` 内部渲染，以保持一致的导航和整体布局。

## 关键注意事项

*   **逐步替换，而非一次性重构**：将一个大型HTML文档转换为Vue页面和ArtDeco风格是一个迭代过程。从小部分开始，逐步替换和组件化，每次都进行测试。
*   **性能考量**：避免在ArtDeco样式中过度使用复杂的CSS滤镜和动画，尤其是在低端设备上。利用 `artdeco-tokens.scss` 中的过渡变量来保持动画的流畅和性能。
*   **响应式设计**：尽管ArtDeco风格最初并非为响应式设计而生，但在现代Web应用中仍需考虑不同屏幕尺寸的适应性。利用CSS媒体查询和Vue组件的响应式逻辑来调整布局。
*   **可访问性 (Accessibility)**：在转换过程中，确保保留或增强了页面的可访问性，例如正确的语义化HTML、键盘导航支持和屏幕阅读器兼容性。

遵循这些步骤，您将能够高效且高质量地将任何HTML文档转换为具有本项目独特ArtDeco设计风格的Vue页面。