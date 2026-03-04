import { describe, expect, it } from "vitest"
import { mount } from "@vue/test-utils"

import FundFlowAnalysis from "../FundFlowAnalysis.vue"

describe("FundFlowAnalysis", () => {
  it("does not crash when mounted without parent-provided props", () => {
    expect(() =>
      mount(FundFlowAnalysis as never, {
        global: {
          stubs: {
            ArtDecoStatCard: { template: "<div><slot /></div>" },
            ArtDecoCard: { template: "<div><slot /></div>" },
            ArtDecoSelect: { template: "<div />" },
            ArtDecoTable: { template: "<div />" },
            ArtDecoChart: { template: "<div />" }
          }
        }
      })
    ).not.toThrow()
  })
})
