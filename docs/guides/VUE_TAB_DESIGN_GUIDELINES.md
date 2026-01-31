### Vue Component Design Proposal: "One Tab, One Component" vs. "One Component, Multiple Tabs"

**Guiding Principle: "Tab Panel Business Relevance"**

The choice between implementing tabbed interfaces using "One Tab, One Component" (1T1C) or "One Component, Multiple Tabs" (1C-MT) should primarily be driven by the **business relevance and logical cohesion of the content within each tab panel**. Rather than a rigid, one-size-fits-all rule, a nuanced approach that prioritizes high cohesion and low coupling at the appropriate level is essential for maintainable, scalable, and performant frontend architecture, especially in complex financial applications.

---

#### 1. "One Tab, One Component" (1T1C) Design Proposal

**Description:**
In this approach, each logical tab panel is represented by its own, independent Vue component. A parent component typically handles only the tab navigation (e.g., using a UI component library's tab group or simple `router-link`s) and uses a `router-view` to dynamically render the active tab's component. The state, data fetching, and specific logic for each tab are encapsulated within its respective component.

**Applicable Scenarios (High Cohesion, Low Coupling):**

*   **高度独立业务 (Highly Independent Business Logic):** Each tab panel represents a distinct, low-coupling business module. The functionality and data presented in one tab are largely unrelated to others, or their interdependencies are minimal and well-defined.
*   **复杂状态管理 (Complex Independent State):** Each tab's internal state is complex but largely independent of other tabs, preventing state conflicts and simplifying local state management within each component.
*   **独立数据源 (Independent Data Sources):** Each tab often corresponds to entirely different API endpoints or data services, fetching its own data without relying on a shared context beyond potentially a common identifier (e.g., a `stock_symbol` passed via route params).
*   **性能优化 (Performance Optimization):** Ideal for scenarios where initial load time is critical, and users might not visit all tabs. Lazy loading ensures only the necessary code and data for the active tab are loaded.
*   **示例 (Example):** A "Trading Details" (交易详情) page for a specific stock or order, where "Order Information" (订单信息), "Trade History" (成交记录), and "Chart Analysis" (图表分析) are distinct functionalities. While all relate to a single stock/order, their data structures, update frequencies, and user interactions are sufficiently different to warrant separate components.

**Financial Project Specific Boundaries for 1T1C:**
This pattern is most suitable when tab panels' data models, business logic, and user interaction patterns **differ significantly**, and there is **no strong, explicit requirement for data sharing or deep interdependence** that would complicate individual component design. For instance, in an "Account Overview" (账户总览) page, "Asset Details" (资产详情), "Transaction Flow" (交易流水), and "Risk Rating" (风险评级) can be treated as distinct modules. Each might fetch its own data, have its own filters, and display unique visualizations.

**Implementation Strategy:**

*   **Component Structure:**
    *   Each tab content is a full-fledged Vue component (e.g., `OrderInfoTab.vue`, `TradeHistoryTab.vue`, `ChartAnalysisTab.vue`).
    *   These components are typically located in `web/frontend/src/views/` or a dedicated subfolder (e.g., `web/frontend/src/views/trading-details/`).
*   **State Management:**
    *   Each 1T1C component manages its own internal state using Vue's reactive data properties.
    *   For any global state (e.g., user authentication, application-wide preferences), Vuex or Pinia should be used.
    *   If a specific `stock_symbol` or `order_id` is the common context, it's typically passed as a route parameter.
*   **Routing Design:**
    *   Utilize Vue Router's **nested routes** feature. The parent route defines the container component with `router-view`, and child routes define each tab component.
    ```javascript
    // router/index.js (example)
    {
      path: '/trading-details/:id',
      component: TradingDetailsLayout, // Parent component with tab navigation and <router-view>
      children: [
        { path: '', redirect: 'order-info' }, // Default tab
        {
          path: 'order-info',
          name: 'OrderInfo',
          component: () => import('@/views/trading-details/OrderInfoTab.vue'),
        },
        {
          path: 'trade-history',
          name: 'TradeHistory',
          component: () => import('@/views/trading-details/TradeHistoryTab.vue'),
        },
        {
          path: 'chart-analysis',
          name: 'ChartAnalysis',
          component: () => import('@/views/trading-details/ChartAnalysisTab.vue'),
        },
      ],
    }
    ```
    *   **Lazy Loading:** Always use dynamic imports (`() => import(...)`) for tab components to enable lazy loading, reducing the initial bundle size and improving perceived performance.
    *   **`keep-alive`:** If a tab's state needs to be preserved when switching away and back (e.g., retaining form input or scroll position), wrap the `<router-view>` in `<keep-alive>`. Use its `include` or `exclude` props to control which components are cached.
*   **API Calls:** Each tab component makes its own API calls upon creation or activation, ensuring it fetches only the data it needs.
*   **Code Maintainability:** Components are smaller, more focused, and easier to test, debug, and understand in isolation.

**Benefits:**
*   **High Component Reusability:** Individual tab components are highly reusable as they are independent.
*   **Clear Separation of Concerns:** Each component has a single responsibility, leading to higher cohesion.
*   **Scalability:** Easy to add, remove, or refactor tabs without impacting others.
*   **Enhanced Maintainability & Testability:** Isolated components simplify development and debugging.
*   **Optimal Performance:** Lazy loading reduces initial bundle size, and only the active tab's resources are loaded and rendered.
*   **Superior User Experience:** Supports deep linking and browser history for each tab.

---

#### 2. "One Component, Multiple Tabs" (1C-MT) Design Proposal

**Description:**
In this pattern, a single "container" Vue component is responsible for managing all tab panels. The tab content itself might be rendered conditionally within the container's template (e.g., using `v-if` or `v-show`) or by rendering smaller, focused sub-components that receive data and callbacks from the parent. The parent component holds the shared state and logic relevant to all its tab panels.

**Applicable Scenarios (Strong Contextual Cohesion):**

*   **强业务关联 (Strong Business Association):** All tab panels revolve around a single core business entity or context, where information in one tab frequently influences or is directly related to another.
*   **数据复用与联动 (Data Reuse & Linkage):** Tabs share a common dataset, and there's a strong need for frequent data linkage, synchronization, or dynamic interaction between them.
*   **统一操作入口 (Unified Operation Entry):** The single component provides different views or operations on the same entity, where the user expects a seamless, unified experience.
*   **用户习惯 (User Expectation):** Conforms to user expectations for aggregated information about a single entity, where switching views is quick and contextually aware.
*   **示例 (Example):** A "Customer Details" (客户详情) page where "Basic Information" (基本信息), "Holdings" (持仓), "Transaction History" (交易记录), and "Risk Assessment" (风险评估) all pertain to the *same customer*. Changes or updates in one tab (e.g., risk assessment) might directly impact the display in another (e.g., holdings).

**Financial Project Specific Boundaries for 1C-MT:**
This approach is ideal when tab panels coalesce around a **single, central financial entity** (e.g., a customer, an account, a specific financial product, or an order). They share the entity's core data, and the user's workflow demands a unified view to switch between different dimensions or aspects of this entity. For instance, a "Product Details" (产品详情) page for an investment fund, where "Product Introduction" (产品介绍), "Net Value Trends" (净值走势), "Holder Analysis" (持有人分析), and "Related Announcements" (相关公告) are all intimately linked to that particular fund, benefiting from shared data and a consistent context.

**Implementation Strategy:**

*   **Component Structure:**
    *   A single parent component (e.g., `CustomerDetailsPage.vue`) acts as the container.
    *   Tab content can be rendered inline using `v-if` or `v-show`, or as smaller, focused sub-components (e.g., `BasicInfoPanel.vue`, `HoldingsPanel.vue`) located in `web/frontend/src/components/customer-details/`.
*   **State Management:**
    *   The parent component manages the `activeTab` and the primary data for the core entity (e.g., `customerData`).
    *   This shared `customerData` can be passed down to child panels via props.
    *   For highly interconnected logic or complex shared state modifications, Vuex/Pinia can be used to centralize actions and mutations.
*   **Routing Design:**
    *   The main route points to the single container component (e.g., `/customer-details/:customerId`).
    *   Tab selection can be managed internally via component state or by using **query parameters** (`/customer-details/123?tab=holdings`) or **hash fragments** (`/customer-details/123#holdings`) to reflect the active tab in the URL for basic bookmarking, though full deep linking to specific states within a tab might require more effort.
*   **API Calls:** The parent component is often responsible for fetching the main entity data once. This data is then distributed to the sub-components. Subsequent, tab-specific data fetches might still occur within sub-components if additional, non-core data is needed (e.g., `HoldingsPanel` fetching detailed transaction history after receiving `customerId`).
*   **Code Maintainability:** Requires careful design to prevent the parent component from becoming too large. Breaking down tab content into smaller, focused sub-components and utilizing a centralized store for shared state is crucial.

**Benefits:**
*   **Strong Contextual Cohesion:** Maintains a unified context around a single entity, making navigation between related information seamless.
*   **Efficient Data Handling:** Shared data for the core entity can be fetched once and reused across tabs, reducing redundant API calls.
*   **Simplified Inter-tab Communication:** Direct communication between related child components is easier via props/events from the shared parent.
*   **Intuitive User Experience:** Users perceive it as different views of the same object, aligning with their mental model.

---

### Implementation Suggestions (General)

1.  **组件粒度 (Component Granularity):**
    *   **Views (`web/frontend/src/views/`):** Should generally house 1T1C components or parent container components for 1C-MT scenarios. These are top-level components associated with a route.
    *   **Components (`web/frontend/src/components/`):** Contains reusable UI elements and smaller, focused sub-components. For 1C-MT, the tab *panels themselves* (e.g., `BasicInfoPanel.vue`) should reside here if they are reusable or part of a larger, single-view component.
    *   **Shared/Utilities (`web/frontend/src/shared/`, `web/frontend/src/utils/`):** Common logic, helper functions, and truly generic UI elements.
    *   **Atomic Design:** Consider applying atomic design principles (atoms, molecules, organisms, templates, pages) to guide component granularity.

2.  **状态管理 (State Management):**
    *   **Local State:** For tab-specific, non-shared data, use `ref` or `reactive` within the component.
    *   **Global/Shared State (Vuex/Pinia):** Absolutely essential for any data shared across routes, between loosely coupled components, or for complex inter-tab communication in 1C-MT scenarios. Design stores with modularity, namespace them by feature, and use getters for derived state.
    *   **Props/Events:** For direct parent-child communication in 1C-MT, use props to pass data down and events (`emit`) to pass changes up.

3.  **路由设计 (Routing Design):**
    *   **Vue Router:** The standard. For 1T1C, nested routes are the clean solution.
    *   **Lazy Loading (Dynamic Imports):** Always enable this for route components (`component: () => import(...)`) to optimize bundle size and initial load time.
    *   **Route Parameters & Query Parameters:** Use route parameters (`/trading-details/:id`) for mandatory identifiers (e.g., `stockId`). Use query parameters (`?tab=history`) for optional, non-essential state like active tabs in 1C-MT, or filters that modify the view but not the core resource.
    *   **`keep-alive` with `<router-view>`:** For 1T1C, use this judiciously. If a tab is expensive to re-initialize or losing its state is detrimental to UX, `keep-alive` can cache it. Be mindful of memory usage; don't `keep-alive` everything.

4.  **可维护性 (Maintainability):**
    *   **Code Standards:** Consistent formatting (e.g., ESLint, Prettier), clear naming conventions.
    *   **Documentation:** Clear component props, events, and slots. Inline comments for complex logic.
    *   **Testing:** Unit tests for components, integration tests for critical user flows.
    *   **Folder Structure:** Organize files logically (e.g., by feature or domain, rather than just `components` and `views`).

---

**Summary Recommendation:**

The project should adopt a **hybrid approach**, intelligently applying either "One Tab, One Component" (1T1C) or "One Component, Multiple Tabs" (1C-MT) based on the **business relevance and logical cohesion of the tabbed content**.

*   **Prioritize 1T1C** for tabs that represent distinct, largely independent business modules, leveraging Vue Router's nested routes and lazy loading for optimal performance and maintainability.
*   **Employ 1C-MT** for tabs that are tightly coupled around a single core entity, sharing data and requiring frequent inter-tab communication, managed by a coherent parent component and potentially a shared Vuex/Pinia store.

This strategy ensures that the frontend architecture remains highly cohesive, loosely coupled, scalable, and performant, addressing the specific needs of a complex financial application like MyStocks.