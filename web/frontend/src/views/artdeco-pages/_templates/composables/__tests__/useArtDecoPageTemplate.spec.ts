import { flushPromises, mount } from "@vue/test-utils"
import { defineComponent, h, nextTick } from "vue"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { getDataMock, postDataMock, mockValues } = vi.hoisted(() => ({
  getDataMock: vi.fn(),
  postDataMock: vi.fn(),
  mockValues: {
    loading: false,
    error: null as unknown,
  },
}))

vi.mock("@/composables/useApiService", async () => {
  const { ref } = await import("vue")

  return {
    useApiService: () => ({
      loading: ref(mockValues.loading),
      error: ref(mockValues.error),
      getData: getDataMock,
      postData: postDataMock,
    }),
  }
})

import { useArtDecoPageTemplate } from "../useArtDecoPageTemplate"

const basePageConfig = {
  title: "风险管理中心",
  permission: "",
}

const baseTabs = [
  { key: "overview", label: "概览", icon: "activity" },
  { key: "detail", label: "详情", icon: "list" },
  { key: "alert", label: "预警", icon: "warning" },
]

const mountComposableHarness = (options?: {
  pageConfig?: Record<string, unknown>
  tabs?: Array<{ key: string; label: string; icon?: string }>
  defaultTab?: string
}) => {
  const component = defineComponent({
    props: {
      pageConfig: {
        type: Object,
        required: true,
      },
      tabs: {
        type: Array,
        required: true,
      },
      defaultTab: {
        type: String,
        default: "",
      },
    },
    emits: ["tab-change", "data-loaded", "data-error"],
    setup(props, { emit, slots }) {
      return useArtDecoPageTemplate(props, slots, emit)
    },
    render() {
      return h("div")
    },
  })

  return mount(component, {
    props: {
      pageConfig: {
        ...basePageConfig,
        ...(options?.pageConfig ?? {}),
      },
      tabs: options?.tabs ?? baseTabs,
      defaultTab: options?.defaultTab ?? "",
    },
  })
}

describe("useArtDecoPageTemplate", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
    vi.useRealTimers()
    mockValues.loading = false
    mockValues.error = null
    getDataMock.mockResolvedValue({
      success: true,
      request_id: "req-default",
      data: { ok: true },
    })
    postDataMock.mockResolvedValue({
      success: true,
      request_id: "req-post",
      data: { ok: true },
    })
  })

  it("falls back to the first tab when defaultTab is invalid", async () => {
    const wrapper = mountComposableHarness({
      pageConfig: {
        showTabs: true,
      },
      defaultTab: "missing",
    })

    await flushPromises()

    expect(wrapper.vm.activeTab).toBe("overview")
    expect(wrapper.vm.tabButtonId("detail")).toBe("artdeco-tab-detail")
    expect(wrapper.vm.tabPanelId("detail")).toBe("artdeco-panel-detail")
  })

  it("reconciles active tab when tab set changes and current tab disappears", async () => {
    const wrapper = mountComposableHarness({
      pageConfig: {
        showTabs: true,
      },
      defaultTab: "detail",
    })

    await flushPromises()
    expect(wrapper.vm.activeTab).toBe("detail")

    await wrapper.setProps({
      tabs: [{ key: "overview", label: "概览", icon: "activity" }],
    })
    await flushPromises()

    expect(wrapper.vm.activeTab).toBe("overview")
  })

  it("treats malformed auth-store payload as allow-by-default and supports wildcard permission", async () => {
    const wrapper = mountComposableHarness()
    await flushPromises()

    localStorage.setItem("auth-store", "{broken-json")
    expect(wrapper.vm.hasPermission("risk:admin")).toBe(true)

    localStorage.setItem("auth-store", JSON.stringify({ permissions: ["*"] }))
    expect(wrapper.vm.hasPermission("risk:admin")).toBe(true)

    localStorage.setItem("auth-store", JSON.stringify({ permissions: ["risk:view-basic"] }))
    expect(wrapper.vm.hasPermission("risk:admin")).toBe(false)
  })

  it("supports keyboard navigation across tabs and moves focus to the newly active button", async () => {
    const wrapper = mountComposableHarness({
      pageConfig: {
        showTabs: true,
      },
      defaultTab: "overview",
    })
    await flushPromises()

    const buttons = baseTabs.map((tab) => {
      const button = document.createElement("button")
      button.id = tab.key
      document.body.appendChild(button)
      return button
    })

    try {
      buttons.forEach((button, index) => {
        wrapper.vm.setTabButtonRef(button, index)
      })

      const event = new KeyboardEvent("keydown", { key: "ArrowRight" })
      const preventDefault = vi.spyOn(event, "preventDefault")

      await wrapper.vm.handleTabKeydown(event, 0)
      await nextTick()

      expect(preventDefault).toHaveBeenCalled()
      expect(wrapper.vm.activeTab).toBe("detail")
      expect(document.activeElement).toBe(buttons[1])
      expect(wrapper.emitted("tab-change")).toEqual([["detail"]])
    } finally {
      buttons.forEach((button) => button.remove())
    }
  })

  it("refetches when cache has expired and watched api params change", async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date("2026-01-01T00:00:00.000Z"))

    const wrapper = mountComposableHarness({
      pageConfig: {
        apiUrl: "/api/risk/cache",
        apiParams: { page: 1 },
        cacheTime: 10_000,
      },
    })

    await flushPromises()
    expect(getDataMock).toHaveBeenCalledTimes(1)

    vi.setSystemTime(new Date("2026-01-01T00:00:12.000Z"))
    await wrapper.setProps({
      pageConfig: {
        ...basePageConfig,
        apiUrl: "/api/risk/cache",
        apiParams: { page: 2 },
        cacheTime: 10_000,
      },
    })
    await flushPromises()

    expect(getDataMock).toHaveBeenCalledTimes(2)
    expect(getDataMock).toHaveBeenLastCalledWith("/api/risk/cache", { page: 2 })
  })

  it("marks the view as loaded immediately when no apiUrl is configured", async () => {
    const wrapper = mountComposableHarness()

    await flushPromises()

    expect(wrapper.vm.dataLoaded).toBe(true)
    expect(getDataMock).not.toHaveBeenCalled()
  })
})
