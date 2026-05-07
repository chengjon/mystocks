import { beforeEach, describe, expect, it } from "vitest"
import { createPinia, setActivePinia } from "pinia"
import { nextTick } from "vue"
import { useMenuStore } from "@/stores/menuStore"

describe("menuStore persistence", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it("loads persisted expanded keys from localStorage", () => {
    localStorage.setItem("artdeco-menu-expanded", JSON.stringify(["/market", "/strategy"]))

    const store = useMenuStore()

    expect(store.expandedKeys).toEqual(["/market", "/strategy"])
  })

  it("persists expanded keys when domains are toggled", async () => {
    const store = useMenuStore()

    store.toggleExpand("/market")
    await nextTick()

    expect(store.expandedKeys).toEqual(["/market"])
    expect(JSON.parse(localStorage.getItem("artdeco-menu-expanded") || "[]")).toEqual(["/market"])

    store.toggleExpand("/market")
    await nextTick()

    expect(store.expandedKeys).toEqual([])
    expect(JSON.parse(localStorage.getItem("artdeco-menu-expanded") || "[]")).toEqual([])
  })
})
