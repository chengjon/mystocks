<template>
  <div class="artdeco-pagination">
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

.artdeco-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: var(--artdeco-spacing-4) 0;
  margin-top: var(--artdeco-spacing-6);

  :deep(.el-pagination) {
    .el-pagination__total {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-small);
      color: var(--artdeco-fg-muted);
      font-weight: 500;
    }

    .el-pagination__sizes {
      .el-select .el-input__wrapper {
        background: transparent;
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: var(--artdeco-radius-none);
        box-shadow: none;
        transition: all var(--artdeco-transition-base);

        &:hover {
          border-color: var(--artdeco-accent-gold);
          box-shadow: var(--artdeco-glow-subtle);
        }

        .el-input__inner {
          font-family: var(--artdeco-font-display);
          color: var(--artdeco-accent-gold);
          font-weight: 600;
          text-transform: uppercase;
        }
      }
    }

    .btn-prev,
    .btn-next {
      background: transparent;
      border: 2px solid rgba(212, 175, 55, 0.3);
      border-radius: var(--artdeco-radius-none);
      color: var(--artdeco-accent-gold);
      font-weight: 600;
      font-family: var(--artdeco-font-display);
      transition: all var(--artdeco-transition-base);

      &:hover {
        background: rgba(212, 175, 55, 0.1);
        border-color: var(--artdeco-accent-gold);
        box-shadow: var(--artdeco-glow-subtle);
      }

      &:disabled {
        opacity: 0.3;
        cursor: not-allowed;
        background: transparent;
        border-color: rgba(212, 175, 55, 0.1);
        box-shadow: none;
      }

      .el-icon {
        font-size: 14px;
      }
    }

    .el-pager {
      .number {
        background: transparent;
        border: 2px solid rgba(212, 175, 55, 0.3);
        border-radius: var(--artdeco-radius-none);
        color: var(--artdeco-accent-gold);
        font-weight: 600;
        font-family: var(--artdeco-font-display);
        transition: all var(--artdeco-transition-base);

        &:hover {
          background: rgba(212, 175, 55, 0.1);
          border-color: var(--artdeco-accent-gold);
          box-shadow: var(--artdeco-glow-subtle);
        }

        &.is-active {
          background: var(--artdeco-accent-gold);
          border-color: var(--artdeco-accent-gold);
          color: var(--artdeco-bg-primary);
          box-shadow: var(--artdeco-glow-medium);
        }
      }

      .more {
        background: transparent;
        color: var(--artdeco-fg-muted);
        font-weight: 600;

        &:hover {
          background: transparent;
          color: var(--artdeco-accent-gold);
        }
      }
    }

    .el-pagination__jump {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-small);
      color: var(--artdeco-fg-muted);
      font-weight: 600;
      text-transform: uppercase;

      .el-input__wrapper {
        background: transparent;
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: var(--artdeco-radius-none);
        box-shadow: none;
        transition: all var(--artdeco-transition-base);
        margin: 0 var(--artdeco-spacing-2);

        &:hover {
          border-color: var(--artdeco-accent-gold);
          box-shadow: var(--artdeco-glow-subtle);
        }

        .el-input__inner {
          font-family: var(--artdeco-font-display);
          color: var(--artdeco-accent-gold);
          font-weight: 600;
          text-align: center;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .artdeco-pagination {
    :deep(.el-pagination) {
      .el-pagination__sizes,
      .el-pagination__jump {
        display: none;
      }

      .btn-prev,
      .btn-next {
        padding: 0 8px;
        min-width: 32px;
      }

      .el-pager .number {
        min-width: 28px;
        height: 28px;
        line-height: 28px;
        font-size: 12px;
      }
    }
  }
}
</style>
