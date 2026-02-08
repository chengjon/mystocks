import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ArtDecoMarketData from '@/views/artdeco-pages/ArtDecoMarketData.vue'
import { createRouter, createWebHistory } from 'vue-router'

// Mock components to avoid deep rendering issues
vi.mock('@/components/artdeco', () => ({
    ArtDecoButton: { template: '<button><slot/></button>' },
    ArtDecoCard: { template: '<div><slot/></div>' },
    ArtDecoStatCard: { template: '<div></div>' }
}))

// Mock composable if needed, but integration testing is better
// Here we rely on the real composable which uses refs

const router = createRouter({
    history: createWebHistory(),
    routes: [{ path: '/', component: ArtDecoMarketData }]
})

describe('ArtDecoMarketData.vue', () => {
    it('renders the page title', () => {
        const wrapper = mount(ArtDecoMarketData, {
            global: {
                plugins: [router]
            }
        })
        expect(wrapper.text()).toContain('市场数据分析中心')
    })

    it('renders tabs', () => {
        const wrapper = mount(ArtDecoMarketData, {
            global: {
                plugins: [router]
            }
        })
        const tabs = wrapper.findAll('.main-tab')
        expect(tabs.length).toBeGreaterThan(0)
        expect(tabs[1].text()).toContain('资金流向')
    })

    it('switches tabs', async () => {
        const wrapper = mount(ArtDecoMarketData, {
            global: {
                plugins: [router]
            }
        })
        
        // Initial state
        expect(wrapper.findComponent({ name: 'MarketFundFlow' }).exists()).toBe(true)
        
        // Click second tab (ETF? concepts?)
        // Tabs: data-quality, fund-flow, etf...
        // Index 2 is ETF
        const tabs = wrapper.findAll('.main-tab')
        await tabs[2].trigger('click')
        
        expect(wrapper.findComponent({ name: 'MarketPlaceholder' }).exists()).toBe(true)
    })
})
