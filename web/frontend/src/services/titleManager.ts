/**
 * 页面标题管理服务
 *
 * 提供统一的页面标题和Meta标签管理功能
 * 支持静态标题、动态标题生成、SEO优化
 */

export interface TitleConfig {
    title: string
    subtitle?: string
    separator?: string
    suffix?: string
    dynamic?: boolean
}

export interface MetaConfig {
    description?: string
    keywords?: string[]
    author?: string
    robots?: string
    ogTitle?: string
    ogDescription?: string
    ogImage?: string
    ogType?: string
    ogUrl?: string
    twitterCard?: string
    twitterTitle?: string
    twitterDescription?: string
    twitterImage?: string
}

class TitleManager {
    private defaultConfig: TitleConfig = {
        title: 'MyStocks',
        subtitle: '',
        separator: ' - ',
        suffix: 'Platform',
        dynamic: false
    }

    private currentMeta: MetaConfig = {}

    // 设置页面标题
    setTitle(config: Partial<TitleConfig> | string): void {
        const finalConfig =
            typeof config === 'string' ? { ...this.defaultConfig, title: config } : { ...this.defaultConfig, ...config }

        const parts = [finalConfig.title, finalConfig.subtitle, finalConfig.suffix].filter(Boolean)

        const title = parts.join(finalConfig.separator)
        document.title = title

        // 在开发环境下输出标题变化日志
        if (import.meta.env.DEV) {
            console.log(`📄 Page title updated: "${title}"`, finalConfig.dynamic ? '(dynamic)' : '(static)')
        }
    }

    // 设置Meta标签
    setMeta(config: MetaConfig): void {
        this.currentMeta = { ...this.currentMeta, ...config }

        // 基础Meta标签
        this.updateMetaTag('description', config.description)
        this.updateMetaTag('keywords', config.keywords?.join(', '))
        this.updateMetaTag('author', config.author)
        this.updateMetaTag('robots', config.robots || 'index, follow')

        // Open Graph标签
        this.updateMetaTag('og:title', config.ogTitle, 'property')
        this.updateMetaTag('og:description', config.ogDescription, 'property')
        this.updateMetaTag('og:image', config.ogImage, 'property')
        this.updateMetaTag('og:type', config.ogType || 'website', 'property')
        this.updateMetaTag('og:url', config.ogUrl || window.location.href, 'property')

        // Twitter Card标签
        this.updateMetaTag('twitter:card', config.twitterCard || 'summary_large_image', 'name')
        this.updateMetaTag('twitter:title', config.twitterTitle, 'name')
        this.updateMetaTag('twitter:description', config.twitterDescription, 'name')
        this.updateMetaTag('twitter:image', config.twitterImage, 'name')

        // 开发环境下输出Meta变化日志
        if (import.meta.env.DEV) {
            console.log('🏷️ Meta tags updated:', Object.keys(config))
        }
    }

    // 更新或创建Meta标签
    private updateMetaTag(name: string, content?: string, attribute: string = 'name'): void {
        if (!content) return

        let element = document.querySelector(`meta[${attribute}="${name}"]`) as HTMLMetaElement
        if (!element) {
            element = document.createElement('meta')
            element.setAttribute(attribute, name)
            document.head.appendChild(element)
        }
        element.content = content
    }

    // 获取当前标题配置
    getCurrentTitle(): string {
        return document.title
    }

    // 获取当前Meta配置
    getCurrentMeta(): MetaConfig {
        return { ...this.currentMeta }
    }

    // 重置为默认标题和Meta
    reset(): void {
        this.setTitle(this.defaultConfig)
        this.setMeta({
            description: '专业的量化交易数据管理平台',
            keywords: ['量化交易', '股票分析', '数据管理', '投资平台'],
            author: 'MyStocks Team',
            ogType: 'website',
            twitterCard: 'summary_large_image'
        })
    }

    // 批量更新标题和Meta
    updatePage(config: { title?: Partial<TitleConfig> | string; meta?: MetaConfig }): void {
        if (config.title) {
            this.setTitle(config.title)
        }
        if (config.meta) {
            this.setMeta(config.meta)
        }
    }

    // 为SEO优化的完整页面设置
    setSEOOptimized(config: {
        title: string
        description: string
        keywords?: string[]
        image?: string
        url?: string
        type?: 'website' | 'article'
    }): void {
        this.setTitle(config.title)
        this.setMeta({
            description: config.description,
            keywords: config.keywords,
            ogTitle: config.title,
            ogDescription: config.description,
            ogImage: config.image,
            ogType: config.type || 'website',
            ogUrl: config.url,
            twitterTitle: config.title,
            twitterDescription: config.description,
            twitterImage: config.image
        })
    }
}

// 创建全局实例
export const titleManager = new TitleManager()

// 便捷函数
export const setPageTitle = (config: Partial<TitleConfig> | string) => titleManager.setTitle(config)
export const setPageMeta = (config: MetaConfig) => titleManager.setMeta(config)
export const resetPageTitle = () => titleManager.reset()
export const setSEOOptimized = (config: Parameters<typeof titleManager.setSEOOptimized>[0]) =>
    titleManager.setSEOOptimized(config)

export default titleManager
