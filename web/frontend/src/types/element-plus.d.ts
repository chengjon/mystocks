/**
 * Element Plus 类型声明补充
 * 修复 el-tab-pane 组件的类型定义问题
 */

import 'element-plus'

declare module 'element-plus' {
  import { ElTabs } from 'element-plus'

  export interface ElTabsProps {
    type?: string
  }

  export interface TabPaneProps {
    label?: string
  }
}
