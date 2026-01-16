/**
 * 动态标题生成器
 *
 * 支持模板变量插值和条件逻辑的标题生成
 */

export interface TitleContext {
    user?: {
        username?: string
        role?: string
        id?: string
    }
    route?: {
        params: Record<string, string>
        query: Record<string, string>
        name?: string
        path?: string
    }
    data?: Record<string, any>
    app?: {
        name?: string
        version?: string
        environment?: string
    }
}

export interface ConditionalTitleRule {
    condition: (context: TitleContext) => boolean
    template: string
}

export class TitleGenerator {
    // 模板变量替换 - 支持嵌套对象访问
    generate(template: string, context: TitleContext = {}): string {
        return template.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
            const value = this.getValueByPath(path.trim(), context)
            return value !== undefined ? String(value) : match
        })
    }

    // 通过路径获取对象值 (支持点号分隔)
    private getValueByPath(path: string, context: TitleContext): any {
        const keys = path.split('.')
        let current: any = context

        for (const key of keys) {
            if (current && typeof current === 'object' && key in current) {
                current = current[key]
            } else {
                return undefined
            }
        }

        return current
    }

    // 条件标题生成 - 按顺序检查条件，返回第一个匹配的模板
    generateConditional(rules: ConditionalTitleRule[], context: TitleContext = {}): string {
        for (const rule of rules) {
            try {
                if (rule.condition(context)) {
                    return this.generate(rule.template, context)
                }
            } catch (error) {
                console.warn('TitleGenerator: Error evaluating condition:', error)
                continue
            }
        }

        // 默认标题
        return context.app?.name || 'MyStocks'
    }

    // 高级模板函数 - 支持函数调用
    generateAdvanced(template: string, context: TitleContext = {}): string {
        let result = template

        // 支持基本变量插值
        result = this.generate(result, context)

        // 支持条件表达式 {{condition ? trueValue : falseValue}}
        result = result.replace(/\{\{([^?]+)\?([^:]+):([^}]+)\}\}/g, (match, condition, trueValue, falseValue) => {
            try {
                const conditionResult = this.evaluateCondition(condition.trim(), context)
                const value = conditionResult ? trueValue.trim() : falseValue.trim()
                return this.generate(value, context)
            } catch (error) {
                console.warn('TitleGenerator: Error evaluating ternary expression:', error)
                return match
            }
        })

        return result
    }

    // 评估条件表达式
    private evaluateCondition(condition: string, context: TitleContext): boolean {
        // 简单条件评估 - 可以扩展支持更复杂的表达式
        if (condition.startsWith('user.')) {
            const userValue = this.getValueByPath(condition, context)
            return Boolean(userValue)
        }

        if (condition.startsWith('data.')) {
            const dataValue = this.getValueByPath(condition, context)
            return Boolean(dataValue)
        }

        if (condition.startsWith('route.')) {
            const routeValue = this.getValueByPath(condition, context)
            return Boolean(routeValue)
        }

        // 直接布尔值
        return condition === 'true'
    }

    // 预定义标题模板
    static readonly TEMPLATES = {
        STOCK_DETAIL: '{{data.name}} ({{data.symbol}}) - 股票详情',
        USER_DASHBOARD: '{{user.username}}的仪表盘',
        STRATEGY_DETAIL: '{{data.name}} - 量化策略',
        MARKET_OVERVIEW: '市场概览 - {{app.name}}',
        ANALYSIS_PAGE: '{{route.params.type}}分析 - {{app.name}}',
        ADMIN_PAGE: '管理后台 - {{user.role}}权限'
    } as const

    // 预定义条件规则
    static readonly CONDITIONAL_RULES = {
        AUTHENTICATED_USER: [
            {
                condition: (ctx: TitleContext) => Boolean(ctx.user?.username),
                template: '{{user.username}}的工作台 - {{app.name}}'
            },
            {
                condition: () => true,
                template: '访客工作台 - {{app.name}}'
            }
        ],

        STOCK_PAGE: [
            {
                condition: (ctx: TitleContext) => Boolean(ctx.data?.name && ctx.data?.symbol),
                template: '{{data.name}} ({{data.symbol}}) - 股票信息'
            },
            {
                condition: (ctx: TitleContext) => Boolean(ctx.route?.params?.symbol),
                template: '{{route.params.symbol}} - 股票信息'
            },
            {
                condition: () => true,
                template: '股票信息 - {{app.name}}'
            }
        ]
    } as const
}

// 创建全局实例
export const titleGenerator = new TitleGenerator()

// 便捷函数
export const generateTitle = (template: string, context?: TitleContext) => titleGenerator.generate(template, context)
export const generateConditionalTitle = (rules: ConditionalTitleRule[], context?: TitleContext) =>
    titleGenerator.generateConditional(rules, context)
export const generateAdvancedTitle = (template: string, context?: TitleContext) =>
    titleGenerator.generateAdvanced(template, context)

export default titleGenerator
