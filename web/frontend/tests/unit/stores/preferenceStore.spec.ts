import { beforeEach, describe, expect, it, vi } from "vitest"
import { createPinia, setActivePinia } from "pinia"
import { nextTick } from "vue"
import { usePreferenceStore } from "@/stores/preferenceStore"

describe("preferenceStore persistence", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute("data-theme")
    vi.stubGlobal(
      "matchMedia",
      vi.fn().mockReturnValue({
        matches: false,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })
    )
  })

  it("loads persisted sidebar state from localStorage", () => {
    localStorage.setItem(
      "artdeco-preferences",
      JSON.stringify({
        theme: "light",
        sidebarCollapsed: true,
        reducedMotion: true,
        showPerformance: true,
        chartRefreshRate: 5000,
      })
    )

    const store = usePreferenceStore()

    expect(store.theme).toBe("light")
    expect(store.sidebarCollapsed).toBe(true)
    expect(store.reducedMotion).toBe(true)
    expect(store.showPerformance).toBe(true)
    expect(store.chartRefreshRate).toBe(5000)
    expect(document.documentElement.getAttribute("data-theme")).toBe("light")
  })

  it("persists sidebar toggle updates back to localStorage", async () => {
    const store = usePreferenceStore()

    expect(store.sidebarCollapsed).toBe(false)

    store.toggleSidebar()
    await nextTick()

    expect(store.sidebarCollapsed).toBe(true)
    expect(JSON.parse(localStorage.getItem("artdeco-preferences") || "{}")).toMatchObject({
      sidebarCollapsed: true,
    })
  })
})
