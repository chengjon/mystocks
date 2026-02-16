import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createWebHistory } from 'vue-router';
import { createPinia, setActivePinia } from 'pinia';
import SidebarMenu from '@/components/layout/SidebarMenu.vue';
import * as ElementPlus from 'element-plus';
import menuConfig from '@/config/menu.config.js';

// Use vi.hoisted to create variables that can be accessed inside vi.mock
const { mockAuthStore } = vi.hoisted(() => {
  return { 
    mockAuthStore: vi.fn(() => ({
      user: {
        roles: ['admin'],
      },
    }))
  }
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: mockAuthStore,
}));

// Mock router
const routes = menuConfig.flatMap(item => item.children ? [item, ...item.children] : [item])
  .filter(item => item.path)
  .map(item => ({ path: item.path, component: { template: '<div>Mock Page</div>' } }));

const router = createRouter({
  history: createWebHistory(),
  routes,
});

describe('SidebarMenu.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    // Reset mock to default 'admin' before each test
    mockAuthStore.mockReturnValue({
      user: {
        roles: ['admin'],
      },
    });
  });

  it('renders menu items based on menu.config.js', async () => {
    const wrapper = mount(SidebarMenu, {
      global: {
        plugins: [router, ElementPlus],
        stubs: {
          SidebarMenuItem: true, // Stub the child component for isolation
        }
      },
    });

    await router.isReady();

    const renderedItems = wrapper.findAllComponents({ name: 'SidebarMenuItem' });
    
    // Filter out disabled menus from the config to get the expected count
    const expectedCount = menuConfig.filter(item => !item.disabled).length;
    
    expect(renderedItems.length).toBe(expectedCount);
  });

  it('filters menu items based on user roles', async () => {
    // Override mock for this specific test
    mockAuthStore.mockReturnValue({
        user: {
            roles: ['user'] 
        }
    });

    const wrapper = mount(SidebarMenu, {
        global: {
          plugins: [router, ElementPlus],
          stubs: {
            SidebarMenuItem: true,
          }
        },
      });
  
      await router.isReady();

      const renderedItems = wrapper.findAllComponents({ name: 'SidebarMenuItem' });
      
      const expectedCountForUser = menuConfig.filter(menu => {
        if (!menu.roles || menu.roles.length === 0) return true;
        return menu.roles.includes('user');
      }).length;
      
      expect(renderedItems.length).toBe(expectedCountForUser);
  });
});

describe('SidebarMenuItem.vue', () => {
    beforeEach(() => {
        setActivePinia(createPinia());
      });

    it('renders a simple menu item', async () => {
        const item = { id: 'dashboard', title: 'Dashboard', path: '/dashboard', icon: 'Monitor' };
        const wrapper = mount(SidebarMenu, { // Mount the parent to provide context
            global: {
              plugins: [router, ElementPlus],
            },
          });
        
        await router.isReady();

        const menuItem = wrapper.find(`[index="${item.path}"]`);
        expect(menuItem.exists()).toBe(true);
        expect(menuItem.text()).toContain(item.title);
    });

    it('renders a submenu with children', async () => {
        const item = menuConfig.find(m => m.id === 'market');
        const wrapper = mount(SidebarMenu, {
            global: {
              plugins: [router, ElementPlus],
            },
          });
    
        await router.isReady();
    
        const subMenu = wrapper.find(`[index="${item.id}"]`);
        expect(subMenu.exists()).toBe(true);
        expect(subMenu.text()).toContain(item.title);
        
        // Check for children within the submenu
        const childItems = subMenu.findAllComponents({ name: 'ElMenuItem' });
        expect(childItems.length).toBe(item.children.length);
        expect(childItems[0].text()).toContain(item.children[0].title);
    });

    it('navigates on menu item click', async () => {
        const push = vi.spyOn(router, 'push');
        const wrapper = mount(SidebarMenu, {
          global: {
            plugins: [router, ElementPlus],
          },
        });
    
        await router.isReady();
    
        const dashboardItem = wrapper.find('[index="/dashboard"]');
        await dashboardItem.trigger('click');
    
        expect(push).toHaveBeenCalledWith('/dashboard');
    });
});
