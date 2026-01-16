// ============================================
//   ARTDECO COMPONENT LIBRARY
//   ArtDeco 组件库主入口
//
//   Design System: Art Deco (The "Gatsby" Aesthetic)
//   - 几何装饰与金色强调
//   - 戏剧性对比与平衡
//   - 奢华的视觉体验
// ============================================

// 基础UI组件
export * from './base'

// 核心分析组件
export * from './core'

// 高级分析组件
export * from './advanced'

// 专用功能组件
export * from './specialized'

// 样式常量
export const ARTDECO_STYLES = {
    // 主色调
    primary: '#D4AF37', // 金色
    secondary: '#1E3D59', // 深蓝色
    accent: '#F2E8C4', // 香槟色

    // 功能色
    success: '#67C23A',
    warning: '#E6A23C',
    danger: '#F56C6C',
    info: '#909399',

    // 金融色 (A股标准)
    rise: '#FF5252', // 涨 - 红色
    fall: '#00E676', // 跌 - 绿色
    flat: '#888888', // 平 - 灰色

    // 背景色
    background: '#0A0A0A', // 黑曜石黑
    surface: '#141414', // 丰富的炭黑
    elevated: '#1a1a1a', // 提升表面

    // 文字色
    text: '#F2F0E4', // 香槟奶油
    textMuted: '#888888', // 锡色
    textSubtle: 'rgba(255,255,255,0.6)', // 微妙

    // 边框和分割线
    border: '#2A2A2A',
    divider: '#1F1F1F',

    // 阴影
    shadow: {
        sm: '0 2px 4px rgba(0,0,0,0.3)',
        md: '0 4px 12px rgba(0,0,0,0.4)',
        lg: '0 8px 24px rgba(0,0,0,0.5)',
        gold: '0 4px 12px rgba(212,175,55,0.2)'
    },

    // 间距
    spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '32px'
    }
}

export default {
    ARTDECO_STYLES
}
