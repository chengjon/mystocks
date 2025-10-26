/**
 * Pagination Composable
 *
 * Reusable pagination logic for tables (FR-002, FR-003, FR-010, FR-011)
 * Supports configurable page sizes, auto-hide on single page, and persistence
 */

import { ref, computed, Ref } from 'vue'
import { useUserPreferences } from './useUserPreferences'

export interface PaginationOptions {
  initialPageSize?: number
  pageSizes?: number[]
  preferenceKey?: keyof ReturnType<typeof useUserPreferences>['preferences']['value']
}

export function usePagination<T>(
  data: Ref<T[]>,
  options: PaginationOptions = {}
) {
  const {
    initialPageSize = 20,
    pageSizes = [10, 20, 50, 100],
    preferenceKey
  } = options

  // Load saved page size from preferences if available
  const { preferences, updatePreference } = useUserPreferences()

  const currentPage = ref(1)
  const pageSize = ref(
    preferenceKey && preferences.value[preferenceKey]
      ? preferences.value[preferenceKey] as number
      : initialPageSize
  )

  /**
   * Total number of items
   */
  const totalItems = computed(() => data.value.length)

  /**
   * Total number of pages
   */
  const totalPages = computed(() =>
    Math.ceil(totalItems.value / pageSize.value)
  )

  /**
   * Whether pagination controls should be visible
   * Auto-hide when only one page exists (FR-003, FR-011)
   */
  const showPagination = computed(() => totalPages.value > 1)

  /**
   * Paginated data for current page
   */
  const paginatedData = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return data.value.slice(start, end)
  })

  /**
   * Handle page size change
   * Resets to page 1 to avoid empty pages
   */
  const handleSizeChange = (newSize: number): void => {
    pageSize.value = newSize
    currentPage.value = 1

    // Save to preferences if key provided
    if (preferenceKey) {
      updatePreference(preferenceKey, newSize)
    }

    console.log(`[Pagination] Page size changed to: ${newSize}`)
  }

  /**
   * Handle current page change
   */
  const handleCurrentChange = (newPage: number): void => {
    currentPage.value = newPage
    console.log(`[Pagination] Current page changed to: ${newPage}`)
  }

  /**
   * Go to first page
   */
  const goToFirstPage = (): void => {
    currentPage.value = 1
  }

  /**
   * Go to last page
   */
  const goToLastPage = (): void => {
    currentPage.value = totalPages.value
  }

  /**
   * Go to next page (if available)
   */
  const goToNextPage = (): void => {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
    }
  }

  /**
   * Go to previous page (if available)
   */
  const goToPreviousPage = (): void => {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }

  /**
   * Reset pagination to defaults
   */
  const resetPagination = (): void => {
    currentPage.value = 1
    pageSize.value = initialPageSize
  }

  return {
    // State
    currentPage,
    pageSize,
    totalItems,
    totalPages,
    showPagination,

    // Data
    paginatedData,

    // Methods
    handleSizeChange,
    handleCurrentChange,
    goToFirstPage,
    goToLastPage,
    goToNextPage,
    goToPreviousPage,
    resetPagination,

    // Available page sizes for el-select
    pageSizes
  }
}
