/**
 * Navigation System Unit Tests
 *
 * Tests for ArtDecoBaseLayout navigation functionality
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import ArtDecoBaseLayout from '@/layouts/ArtDecoBaseLayout.vue'

// Mock router
const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', name: 'home', meta: { title: 'Home' } },
        { path: '/dashboard', name: 'dashboard', meta: { title: 'Dashboard' } },
        { path: '/trading', name: 'trading', meta: { title: 'Trading' } }
    ]
})

describe('ArtDecoBaseLayout Navigation', () => {
    const mockMenuItems = [
        { path: '/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/trading', label: 'Trading', icon: '💼' }
    ]

    beforeEach(() => {
        vi.clearAllMocks()
    })

    describe('Breadcrumb Navigation', () => {
        it('generates breadcrumbs from route path', async () => {
            router.push('/trading/orders')
            await router.isReady()

            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Trading Center'
                },
                global: {
                    plugins: [router]
                }
            })

            // Check if breadcrumb component exists
            const breadcrumbNav = wrapper.findComponent({ name: 'BreadcrumbNav' })
            expect(breadcrumbNav.exists()).toBe(true)
        })

        it('handles route meta breadcrumb labels', async () => {
            router.push('/dashboard')
            await router.isReady()

            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Dashboard'
                },
                global: {
                    plugins: [router]
                }
            })

            // Verify breadcrumb generation doesn't throw errors
            expect(wrapper.vm.breadcrumbItems).toBeDefined()
        })

        it('handles breadcrumb generation errors gracefully', () => {
            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test'
                }
            })

            // Should return fallback breadcrumbs on error
            expect(wrapper.vm.breadcrumbItems.length).toBeGreaterThan(0)
        })
    })

    describe('Sidebar State Management', () => {
        it('toggles sidebar collapsed state', async () => {
            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test'
                }
            })

            // Initially not collapsed
            expect(wrapper.vm.sidebarCollapsed).toBe(false)

            // Toggle sidebar
            await wrapper.vm.toggleSidebar()
            expect(wrapper.vm.sidebarCollapsed).toBe(true)

            // Toggle again
            await wrapper.vm.toggleSidebar()
            expect(wrapper.vm.sidebarCollapsed).toBe(false)
        })

        it('closes mobile sidebar on overlay click', async () => {
            // Mock mobile viewport
            Object.defineProperty(window, 'innerWidth', { value: 800 })

            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test'
                }
            })

            // Open sidebar (not collapsed)
            wrapper.vm.sidebarCollapsed = false
            await wrapper.vm.$nextTick()

            // Click overlay should close sidebar on mobile
            const overlay = wrapper.find('.mobile-overlay')
            if (overlay.exists()) {
                await overlay.trigger('click')
                expect(wrapper.vm.sidebarCollapsed).toBe(true)
            }
        })
    })

    describe('Command Palette Integration', () => {
        it('generates command items from menu items', () => {
            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test Page'
                }
            })

            const commandItems = wrapper.vm.commandItems
            expect(commandItems).toHaveLength(2)
            expect(commandItems[0]).toMatchObject({
                path: '/dashboard',
                label: 'Dashboard',
                category: 'Test Page'
            })
        })

        it('opens command palette', async () => {
            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test'
                }
            })

            const mockCommandPalette = {
                open: vi.fn()
            }

            wrapper.vm.commandPaletteRef = mockCommandPalette as any
            wrapper.vm.openCommandPalette()

            expect(mockCommandPalette.open).toHaveBeenCalled()
        })
    })

    describe('Keyboard Navigation', () => {
        it('toggles sidebar with Ctrl+B', () => {
            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test'
                }
            })

            // Initially not collapsed
            expect(wrapper.vm.sidebarCollapsed).toBe(false)

            // Simulate Ctrl+B keydown
            const event = new KeyboardEvent('keydown', {
                key: 'b',
                ctrlKey: true
            })
            document.dispatchEvent(event)

            // Should toggle sidebar
            expect(wrapper.vm.sidebarCollapsed).toBe(true)
        })

        it('closes mobile sidebar with Escape', () => {
            // Mock mobile
            Object.defineProperty(window, 'innerWidth', { value: 800 })

            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test'
                }
            })

            // Open sidebar
            wrapper.vm.sidebarCollapsed = false

            // Simulate Escape keydown
            const event = new KeyboardEvent('keydown', {
                key: 'Escape'
            })
            document.dispatchEvent(event)

            // Should close sidebar on mobile
            expect(wrapper.vm.sidebarCollapsed).toBe(true)
        })
    })

    describe('Responsive Behavior', () => {
        it('detects mobile viewport', () => {
            // Mock mobile viewport
            Object.defineProperty(window, 'innerWidth', { value: 800 })

            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test'
                }
            })

            // Trigger mobile check
            wrapper.vm.checkMobile()
            expect(wrapper.vm.isMobile).toBe(true)
        })

        it('detects desktop viewport', () => {
            // Mock desktop viewport
            Object.defineProperty(window, 'innerWidth', { value: 1200 })

            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test'
                }
            })

            // Trigger mobile check
            wrapper.vm.checkMobile()
            expect(wrapper.vm.isMobile).toBe(false)
        })
    })

    describe('Analytics Integration', () => {
        it('tracks command palette events', () => {
            // Mock gtag
            ;(window as any).gtag = vi.fn()

            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test Page'
                }
            })

            wrapper.vm.onCommandPaletteOpen()

            expect((window as any).gtag).toHaveBeenCalledWith('event', 'command_palette_open', {
                event_category: 'navigation',
                event_label: 'Test Page'
            })
        })

        it('handles analytics errors gracefully', () => {
            // Mock gtag that throws
            ;(window as any).gtag = vi.fn(() => {
                throw new Error('Analytics error')
            })

            const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

            const wrapper = mount(ArtDecoBaseLayout, {
                props: {
                    menuItems: mockMenuItems,
                    pageTitle: 'Test'
                }
            })

            // Should not throw
            expect(() => wrapper.vm.onCommandPaletteOpen()).not.toThrow()

            // Should log warning
            expect(consoleSpy).toHaveBeenCalledWith('Analytics error:', expect.any(Error))

            consoleSpy.mockRestore()
        })
    })
})
