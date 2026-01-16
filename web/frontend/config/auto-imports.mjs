/**
 * Element Plus 自动导入配置
 *
 * 指定需要全局可用的Element Plus API（不需要手动导入）
 */

export function defineElementPlusAutoImport() {
  return {
    // Element Plus组件和API
    imports: ['element-plus'],
    dts: 'auto-imports.d.ts',
    resolvers: [],
    // 明确指定需要自动导入的API
    include: [
      /\b(El[A-Z][a-zA-Z]*)\b/, // 匹配ElMessage, ElMessageBox等
    ],
    // 自动导入的API列表
    api: [
      // 通用
      'ElMessage',

      // 消息提示
      'ElMessageBox',
      'ElNotification',

      // 加载
      'ElLoading',

      // 其他可能需要的全局API
      'ElInfiniteScroll',
      'ElScrollbar',
    ]
  }
}
