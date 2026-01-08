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
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 0;
  margin-top: 24px;

  :deep(.el-pagination) {
    .el-pagination__total {
      font-family: 'Inter', -apple-system, sans-serif;
      font-size: 13px;
      color: #909399;
      font-weight: 500;
    }

    .el-pagination__sizes {
      .el-select .el-input__wrapper {
        background: transparent;
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 0;
        box-shadow: none;
        transition: all 0.3s;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
        }

        .el-input__inner {
          font-family: 'Inter', system-ui, sans-serif;
          color: #409eff;
          font-weight: 600;
          text-transform: uppercase;
        }
      }
    }

    .btn-prev,
    .btn-next {
      background: transparent;
      border: 2px solid rgba(212, 175, 55, 0.3);
      border-radius: 0;
      color: #409eff;
      font-weight: 600;
      font-family: 'Inter', system-ui, sans-serif;
      transition: all 0.3s;

      &:hover {
        background: rgba(212, 175, 55, 0.1);
        border-color: #409eff;
        box-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
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
        border-radius: 0;
        color: #409eff;
        font-weight: 600;
        font-family: 'Inter', system-ui, sans-serif;
        transition: all 0.3s;

        &:hover {
          background: rgba(212, 175, 55, 0.1);
          border-color: #409eff;
          box-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
        }

        &.is-active {
          background: #409eff;
          border-color: #409eff;
          color: #ffffff;
          box-shadow: 0 4px 8px rgba(64, 158, 255, 0.2);
        }
      }

      .more {
        background: transparent;
        color: #909399;
        font-weight: 600;

        &:hover {
          background: transparent;
          color: #409eff;
        }
      }
    }

    .el-pagination__jump {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #909399;
      font-weight: 600;
      text-transform: uppercase;

      .el-input__wrapper {
        background: transparent;
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 0;
        box-shadow: none;
        transition: all 0.3s;
        margin: 0 8px;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
        }

        .el-input__inner {
          font-family: 'Inter', system-ui, sans-serif;
          color: #409eff;
          font-weight: 600;
          text-align: center;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .pagination {
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
