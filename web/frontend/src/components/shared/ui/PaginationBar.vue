<template>
  <div class="pagination">
    <el-pagination
      :current-page="currentPage"
      :page-size="currentPageSize"
      :page-sizes="pageSizes"
      :total="total"
      :layout="layout"
      :background="false"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  page?: number
  pageSize?: number
  total: number
  pageSizes?: number[]
  layout?: string
  disabled?: boolean
}

interface Emits {
  (e: 'page-change', page: number): void
  (e: 'size-change', size: number): void
  (e: 'update:page', page: number): void
  (e: 'update:pageSize', size: number): void
}

const props = withDefaults(defineProps<Props>(), {
  page: 1,
  pageSize: 20,
  pageSizes: () => [10, 20, 50, 100],
  layout: 'total, sizes, prev, pager, next, jumper',
  disabled: false
})

const emit = defineEmits<Emits>()

const currentPage = computed({
  get: () => props.page,
  set: (val) => emit('update:page', val)
})

const currentPageSize = computed({
  get: () => props.pageSize,
  set: (val) => emit('update:pageSize', val)
})

const handleSizeChange = (val: number) => {
  emit('size-change', val)
}

const handleCurrentChange = (val: number) => {
  emit('page-change', val)
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: var(--artdeco-spacing-4) 0;
  margin-top: var(--artdeco-spacing-6);

  :deep(.el-pagination) {
    .el-pagination__total {
      font-family: var(--font-body);
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-muted);
      font-weight: 500;
    }

    .el-pagination__sizes {
      .el-select .el-input__wrapper {
        background: transparent;
        border: 1px solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-none);
        box-shadow: none;
        transition:
          border-color var(--artdeco-transition-base) var(--artdeco-ease-out),
          box-shadow var(--artdeco-transition-base) var(--artdeco-ease-out);

        &:hover {
          border-color: var(--artdeco-gold-primary);
          box-shadow: var(--artdeco-shadow-sm);
        }

        .el-input__inner {
          font-family: var(--font-body);
          color: var(--artdeco-gold-primary);
          font-weight: 600;
          text-transform: uppercase;
        }
      }
    }

    .btn-prev,
    .btn-next {
      background: transparent;
      border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-border-default);
      border-radius: var(--artdeco-radius-none);
      color: var(--artdeco-gold-primary);
      font-weight: 600;
      font-family: var(--font-body);
      transition:
        background-color var(--artdeco-transition-base) var(--artdeco-ease-out),
        border-color var(--artdeco-transition-base) var(--artdeco-ease-out),
        box-shadow var(--artdeco-transition-base) var(--artdeco-ease-out),
        color var(--artdeco-transition-base) var(--artdeco-ease-out);

      &:hover {
        background: var(--artdeco-gold-opacity-10);
        border-color: var(--artdeco-gold-primary);
        box-shadow: var(--artdeco-shadow-sm);
      }

      &:disabled {
        opacity: 0.3;
        cursor: not-allowed;
        background: transparent;
        border-color: var(--artdeco-gold-opacity-10);
        box-shadow: none;
      }

      .el-icon {
        font-size: var(--artdeco-text-sm);
      }
    }

    .el-pager {
      .number {
        background: transparent;
        border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-none);
        color: var(--artdeco-gold-primary);
        font-weight: 600;
        font-family: var(--font-body);
        transition:
          background-color var(--artdeco-transition-base) var(--artdeco-ease-out),
          border-color var(--artdeco-transition-base) var(--artdeco-ease-out),
          box-shadow var(--artdeco-transition-base) var(--artdeco-ease-out),
          color var(--artdeco-transition-base) var(--artdeco-ease-out);

        &:hover {
          background: var(--artdeco-gold-opacity-10);
          border-color: var(--artdeco-gold-primary);
          box-shadow: var(--artdeco-shadow-sm);
        }

        &.is-active {
          background: var(--artdeco-gold-primary);
          border-color: var(--artdeco-gold-primary);
          color: var(--artdeco-bg-global);
          box-shadow: var(--artdeco-shadow-md);
        }
      }

      .more {
        background: transparent;
        color: var(--artdeco-fg-muted);
        font-weight: 600;

        &:hover {
          background: transparent;
          color: var(--artdeco-gold-primary);
        }
      }
    }

    .el-pagination__jump {
      font-family: var(--font-body);
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-muted);
      font-weight: 600;
      text-transform: uppercase;

      .el-input__wrapper {
        background: transparent;
        border: 1px solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-none);
        box-shadow: none;
        transition:
          border-color var(--artdeco-transition-base) var(--artdeco-ease-out),
          box-shadow var(--artdeco-transition-base) var(--artdeco-ease-out);
        margin: 0 var(--artdeco-spacing-2);

        &:hover {
          border-color: var(--artdeco-gold-primary);
          box-shadow: var(--artdeco-shadow-sm);
        }

        .el-input__inner {
          font-family: var(--font-body);
          color: var(--artdeco-gold-primary);
          font-weight: 600;
          text-align: center;
        }
      }
    }
  }
}

@media (width <= var(--artdeco-breakpoint-md)) {
  .pagination {
    :deep(.el-pagination) {
      .el-pagination__sizes,
      .el-pagination__jump {
        display: none;
      }

      .btn-prev,
      .btn-next {
        padding: 0 var(--artdeco-spacing-2);
        min-width: var(--artdeco-spacing-8);
      }

      .el-pager .number {
        min-width: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
        height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
        line-height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
        font-size: var(--artdeco-text-xs);
      }
    }
  }
}
</style>
