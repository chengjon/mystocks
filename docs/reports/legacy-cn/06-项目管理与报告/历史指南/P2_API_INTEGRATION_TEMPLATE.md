# P2 Page API Integration Template

This document provides a standard template for integrating APIs into P2 priority pages, following the patterns established in P0 and P1 pages.

## Template Structure

### 1. Component Setup with Script Setup Syntax

```vue
<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { dataApi } from '@/api'  // Import the appropriate API module

// ==================== STATE MANAGEMENT ====================

// Loading and error states
const loading = ref(false)
const error = ref(null)

// Data state
const data = ref([])
const filters = ref({
  // Define your filter properties
})

// ==================== COMPUTED PROPERTIES ====================

// Example computed property for derived data
const processedData = computed(() => {
  if (!data.value) return []
  // Your data processing logic
  return data.value
})

// ==================== API FUNCTIONS ====================

/**
 * Main data loading function
 * Follows error handling pattern:
 * 1. Set loading state
 * 2. Clear previous errors
 * 3. Try to fetch data
 * 4. Handle errors with user feedback
 * 5. Finally clear loading state
 */
const fetchData = async (params = {}) => {
  loading.value = true
  error.value = null

  try {
    // Make API call with parameters
    const response = await dataApi.getSomeData({
      ...filters.value,
      ...params
    })

    // Process response
    if (response && response.data) {
      data.value = response.data
    } else {
      throw new Error('Invalid response format')
    }

  } catch (err) {
    // Error handling with user feedback
    error.value = err.message || 'Failed to load data'
    ElMessage.error(`Error: ${error.value}`)
    console.error('Data fetch error:', err)

  } finally {
    // Always clear loading state
    loading.value = false
  }
}

/**
 * Refresh data function
 * Called when user wants to reload data
 */
const refreshData = async () => {
  await fetchData()
}

/**
 * Handle filter changes
 * Called when user modifies filters
 */
const onFilterChange = async () => {
  filters.value = {
    // Update filter values
  }
  await fetchData()
}

// ==================== LIFECYCLE HOOKS ====================

/**
 * Load initial data when component mounts
 */
onMounted(() => {
  fetchData()
})

</script>
```

### 2. Template Structure with Error Handling

```vue
<template>
  <div class="page-container">
    <!-- Header with title and actions -->
    <div class="page-header">
      <h1>Page Title</h1>
      <button @click="refreshData" :disabled="loading">
        Refresh
      </button>
    </div>

    <!-- Error message display -->
    <div v-if="error" class="error-container">
      <el-alert :title="`Error: ${error}`" type="error" closable />
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- Main content -->
    <div v-else class="content-container">
      <!-- Filters section -->
      <div class="filters-section">
        <el-input
          v-model="filters.search"
          placeholder="Search..."
          @change="onFilterChange"
        />
        <!-- Add more filter controls as needed -->
      </div>

      <!-- Data display -->
      <div class="data-section">
        <el-table :data="processedData" stripe>
          <el-table-column prop="id" label="ID" />
          <el-table-column prop="name" label="Name" />
          <!-- Add more columns as needed -->
        </el-table>
      </div>

      <!-- Empty state -->
      <div v-if="!loading && processedData.length === 0" class="empty-state">
        <p>No data available. Try adjusting your filters.</p>
      </div>
    </div>
  </div>
</template>
```

### 3. Styles

```vue
<style scoped>
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.error-container {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px;
}

.filters-section {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
}

.data-section {
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #999;
}
</style>
```

## Best Practices

### 1. Error Handling

✅ **DO:**
```javascript
try {
  const response = await dataApi.method(params)
  data.value = response
} catch (err) {
  error.value = err.message
  ElMessage.error(`Failed: ${err.message}`)
  console.error('Error:', err)
}
```

❌ **DON'T:**
```javascript
// Don't ignore errors
dataApi.method(params).then(res => data.value = res)

// Don't use alert()
alert('Error occurred')

// Don't silently fail
try {
  // ...
} catch (err) {
  // Nothing
}
```

### 2. Loading States

✅ **DO:**
```javascript
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    // API call
  } finally {
    loading.value = false
  }
}
```

❌ **DON'T:**
```javascript
// Don't forget to clear loading state
const fetchData = async () => {
  loading.value = true
  const response = await api.get()
  data.value = response
  // loading.value is still true!
}
```

### 3. User Feedback

✅ **DO:**
```javascript
ElMessage.success('Data loaded successfully')
ElMessage.error('Failed to load data')
ElMessage.warning('Please check your input')
```

❌ **DON'T:**
```javascript
// Don't use console.log for user-facing messages
console.log('Error occurred')

// Don't use alert()
alert('Something went wrong')
```

### 4. API Integration Pattern

✅ **DO:**
```javascript
import { dataApi } from '@/api'

const data = await dataApi.getStocks({
  limit: 10,
  offset: 0
})
```

❌ **DON'T:**
```javascript
// Don't use fetch directly
const data = await fetch('/api/stocks')

// Don't hardcode API URLs
const data = await axios.get('http://localhost:8000/api/stocks')

// Don't mix different API patterns
const a = await dataApi.method1()
const b = await fetch('/api/method2')
```

### 5. Component Size

- **Target**: Keep components under 500 lines
- **Maximum**: 800 lines (requires refactoring plan)
- **If larger**: Split into sub-components

```
Good structure:
├─ StockDetail.vue (300 lines, main component)
├─ StockHeader.vue (100 lines, header info)
├─ StockChart.vue (150 lines, chart display)
└─ StockNews.vue (120 lines, news section)

Avoid:
├─ StockDetail.vue (1200 lines, everything in one)
```

## Quality Checklist

Before marking a page as "Integrated", verify:

### API Integration (✅ All Required)
- [ ] Page imports API module (`import { dataApi } from '@/api'`)
- [ ] Page makes at least 1 API call
- [ ] API calls have proper parameters
- [ ] Response handling is implemented
- [ ] Error cases are handled

### Error Handling (✅ All Required)
- [ ] Try-catch blocks wrap API calls
- [ ] Error messages are user-friendly
- [ ] ElMessage feedback is provided
- [ ] Console logging for debugging
- [ ] Loading state is properly managed

### User Experience (✅ All Required)
- [ ] Loading indicators (skeleton/spinner)
- [ ] Error messages displayed
- [ ] Empty state message
- [ ] Refresh/retry functionality
- [ ] Filter/search functionality (if applicable)

### Code Quality (✅ All Required)
- [ ] Vue 3 Composition API used
- [ ] Script setup syntax used
- [ ] Proper variable naming
- [ ] No console errors
- [ ] Type-safe where possible

## Common Patterns

### Pattern 1: Simple Data Fetch

```javascript
const items = ref([])
const loading = ref(false)

const fetchItems = async () => {
  loading.value = true
  try {
    items.value = await dataApi.getItems()
  } catch (err) {
    ElMessage.error('Failed to load items')
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchItems())
```

### Pattern 2: Data Fetch with Filters

```javascript
const items = ref([])
const filters = ref({ category: '', search: '' })
const loading = ref(false)

const fetchItems = async () => {
  loading.value = true
  try {
    items.value = await dataApi.getItems(filters.value)
  } catch (err) {
    ElMessage.error('Failed to load items')
  } finally {
    loading.value = false
  }
}

const applyFilters = async () => {
  await fetchItems()
}

onMounted(() => fetchItems())
```

### Pattern 3: Multiple Data Sources

```javascript
const data1 = ref([])
const data2 = ref([])
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const [res1, res2] = await Promise.all([
      dataApi.getSource1(),
      dataApi.getSource2()
    ])
    data1.value = res1
    data2.value = res2
  } catch (err) {
    ElMessage.error('Failed to load data')
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchData())
```

## Integration Scoring

Use this to evaluate page integration quality:

| Aspect | Score 0-10 | Criteria |
|--------|-----------|----------|
| API Integration | | Has API imports and calls |
| Error Handling | | Has try-catch and user feedback |
| Loading States | | Shows loading/empty states |
| Code Quality | | Well-organized, no duplicates |
| User Experience | | Clear feedback and flow |
| **Average** | | Sum / 5 |

**Target Score**: 8.0+/10 for production readiness

---

## Next Steps

1. **Assess Current State**: Check which P2 pages need integration
2. **Apply Template**: Use this template as starting point
3. **Test Thoroughly**: Add E2E tests following P1 patterns
4. **Code Review**: Ensure quality standards met
5. **Document**: Add comments explaining API calls

---

**Version**: 1.0
**Created**: 2025-11-27
**Updated**: 2025-11-27
