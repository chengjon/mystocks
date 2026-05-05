import ElementPlus from "element-plus";
import { flushPromises, mount } from "@vue/test-utils";
import { init } from "klinecharts";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { getPatternsMock } = vi.hoisted(() => ({
  getPatternsMock: vi.fn(),
}));

vi.mock("@/api", () => ({
  technicalApi: {
    getPatterns: getPatternsMock,
  },
}));

import KLineChart from "@/components/technical/KLineChart.vue";

const baseProps = {
  symbol: "600519.SH",
  ohlcvData: {
    dates: ["2026-01-01", "2026-01-02", "2026-01-03"],
    open: [10, 11, 10.5],
    high: [11, 11.5, 10.8],
    low: [9.8, 10.4, 10],
    close: [10.8, 10.5, 10.1],
    volume: [100, 120, 130],
  },
  indicators: [],
  loading: false,
};

function mountKLineChart(overrides: Record<string, unknown> = {}) {
  return mount(KLineChart, {
    props: {
      ...baseProps,
      ...overrides,
    },
    global: {
      plugins: [ElementPlus],
      config: {
        warnHandler: () => {},
      },
    },
  });
}

function createDeferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((innerResolve, innerReject) => {
    resolve = innerResolve;
    reject = innerReject;
  });

  return { promise, resolve, reject };
}

describe("KLineChart overlays", () => {
  beforeEach(() => {
    getPatternsMock.mockReset();
    vi.mocked(init).mockClear();
  });

  it("requests automatic patterns and keeps manual tools available", async () => {
    getPatternsMock.mockResolvedValue({
      success: true,
      data: {
        status: "available",
        symbol: "600519.SH",
        period: "daily",
        patterns: [
          {
            pattern_name: "double_top",
            direction: "bearish",
            confidence: 0.82,
            gap_side: null,
            gap_fill_status: null,
            gap_zone: null,
            anchor_points: [
              { role: "left_peak", timestamp: 1, value: 10.5 },
              { role: "neckline", timestamp: 2, value: 9.8 },
              { role: "right_peak", timestamp: 3, value: 10.4 },
            ],
          },
        ],
      },
    });

    const wrapper = mountKLineChart();

    await flushPromises();

    expect(getPatternsMock).toHaveBeenCalledWith("600519.SH", "daily");
    expect(wrapper.text()).toContain("趋势线");
    expect(wrapper.text()).toContain("水平线");
    expect(wrapper.text()).toContain("矩形");
    expect(wrapper.text()).toContain("清空画线");
    expect(wrapper.text()).toContain("重置");

    const chartInstance = vi.mocked(init).mock.results.at(-1)?.value;
    expect(chartInstance?.createOverlay).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        name: "segment",
        extendData: expect.objectContaining({
          source: "AUTO",
          patternName: "double_top",
          confidence: 0.82,
          segmentIndex: 0,
          segmentCount: 2,
        }),
        points: [{ timestamp: 1, value: 10.5 }, { timestamp: 2, value: 9.8 }],
      }),
      "candle_pane",
    );
    expect(chartInstance?.createOverlay).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        name: "segment",
        extendData: expect.objectContaining({
          source: "AUTO",
          patternName: "double_top",
          confidence: 0.82,
          segmentIndex: 1,
          segmentCount: 2,
        }),
        points: [{ timestamp: 2, value: 9.8 }, { timestamp: 3, value: 10.4 }],
      }),
      "candle_pane",
    );
  });

  it("renders reviewed automatic gap zones once supported while keeping manual tools available", async () => {
    getPatternsMock.mockResolvedValue({
      success: true,
      data: {
        status: "available",
        symbol: "600519.SH",
        period: "daily",
        patterns: [
          {
            pattern_name: "breakaway_gap",
            direction: "bullish",
            confidence: 0.74,
            anchor_points: [],
            gap_side: "up",
            gap_fill_status: "open",
            gap_zone: {
              start_timestamp: 1767225600000,
              end_timestamp: 1767312000000,
              upper_value: 10.8,
              lower_value: 10.25,
              filled_at: null,
            },
          },
        ],
      },
    });

    const wrapper = mountKLineChart();

    await flushPromises();

    expect(getPatternsMock).toHaveBeenCalledWith("600519.SH", "daily");
    expect(wrapper.text()).toContain("趋势线");
    expect(wrapper.text()).toContain("水平线");
    expect(wrapper.text()).toContain("矩形");
    expect(wrapper.text()).toContain("清空画线");

    const chartInstance = vi.mocked(init).mock.results.at(-1)?.value;
    expect(chartInstance?.createOverlay).toHaveBeenCalledWith(
      expect.objectContaining({
        name: "mvpGapZone",
        points: [
          { timestamp: 1767225600000, value: 10.8 },
          { timestamp: 1767312000000, value: 10.25 },
        ],
        extendData: expect.objectContaining({
          source: "AUTO",
          patternName: "breakaway_gap",
          gapSide: "up",
          gapFillStatus: "open",
          upperValue: 10.8,
          lowerValue: 10.25,
        }),
      }),
      "candle_pane",
    );
  });

  it("surfaces a user-facing warning when automatic pattern loading fails without hiding manual tools", async () => {
    getPatternsMock.mockRejectedValue(new Error("pattern backend unavailable"));
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    const wrapper = mountKLineChart();

    await flushPromises();

    expect(getPatternsMock).toHaveBeenCalledWith("600519.SH", "daily");
    expect(consoleErrorSpy).toHaveBeenCalled();
    expect(wrapper.text()).toContain("自动形态暂不可用");
    expect(wrapper.text()).toContain("趋势线");
    expect(wrapper.text()).toContain("水平线");
    expect(wrapper.text()).toContain("矩形");

    consoleErrorSpy.mockRestore();
  });

  it("ignores stale automatic-pattern responses after the symbol changes", async () => {
    const deferredInitial = createDeferred<{
      success: boolean
      data: {
        status: "available"
        symbol: string
        period: "daily"
        patterns: Array<{
          pattern_name: string
          direction: string
          confidence: number
          anchor_points: Array<{ role: string; timestamp: number; value: number }>
        }>
      }
    }>();

    getPatternsMock
      .mockImplementationOnce(() => deferredInitial.promise)
      .mockResolvedValueOnce({
        success: true,
        data: {
          status: "available",
          symbol: "000001.SZ",
          period: "daily",
          patterns: [
            {
              pattern_name: "double_bottom",
              direction: "bullish",
              confidence: 0.77,
              gap_side: null,
              gap_fill_status: null,
              gap_zone: null,
              anchor_points: [
                { role: "left_bottom", timestamp: 11, value: 9.5 },
                { role: "neckline", timestamp: 12, value: 10.1 },
                { role: "right_bottom", timestamp: 13, value: 9.6 },
              ],
            },
          ],
        },
      });

    const wrapper = mountKLineChart();
    await flushPromises();

    expect(getPatternsMock).toHaveBeenNthCalledWith(1, "600519.SH", "daily");

    await wrapper.setProps({ symbol: "000001.SZ" });
    await flushPromises();

    const chartInstance = vi.mocked(init).mock.results.at(-1)?.value;
    expect(chartInstance?.createOverlay).toHaveBeenCalledTimes(2);
    expect(chartInstance?.createOverlay).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        extendData: expect.objectContaining({ patternName: "double_bottom" }),
      }),
      "candle_pane",
    );

    deferredInitial.resolve({
      success: true,
      data: {
        status: "available",
        symbol: "600519.SH",
        period: "daily",
        patterns: [
          {
            pattern_name: "double_top",
            direction: "bearish",
            confidence: 0.82,
            gap_side: null,
            gap_fill_status: null,
            gap_zone: null,
            anchor_points: [
              { role: "left_peak", timestamp: 1, value: 10.5 },
              { role: "neckline", timestamp: 2, value: 9.8 },
              { role: "right_peak", timestamp: 3, value: 10.4 },
            ],
          },
        ],
      },
    });
    await flushPromises();

    expect(chartInstance?.createOverlay).toHaveBeenCalledTimes(2);
  });

  it("clears automatic overlays for unsupported non-daily periods while keeping manual tools available", async () => {
    getPatternsMock.mockResolvedValue({
      success: true,
      data: {
        status: "available",
        symbol: "600519.SH",
        period: "daily",
        patterns: [
          {
            pattern_name: "double_top",
            direction: "bearish",
            confidence: 0.82,
            gap_side: null,
            gap_fill_status: null,
            gap_zone: null,
            anchor_points: [
              { role: "left_peak", timestamp: 1, value: 10.5 },
              { role: "neckline", timestamp: 2, value: 9.8 },
              { role: "right_peak", timestamp: 3, value: 10.4 },
            ],
          },
        ],
      },
    });

    const wrapper = mountKLineChart();
    await flushPromises();

    const chartInstance = vi.mocked(init).mock.results.at(-1)?.value;
    const setupState = wrapper.vm.$.setupState as {
      currentPeriod: string
      handlePeriodChange: (period: string) => void
    };

    setupState.currentPeriod = "5min";
    setupState.handlePeriodChange("5min");
    await flushPromises();

    expect(wrapper.text()).toContain("自动形态当前仅支持日线视图");
    expect(chartInstance?.removeOverlay).toHaveBeenCalledWith("overlay-1");
    expect(chartInstance?.removeOverlay).toHaveBeenCalledWith("overlay-2");
    expect(wrapper.text()).toContain("趋势线");
    expect(wrapper.text()).toContain("水平线");
    expect(wrapper.text()).toContain("矩形");
  });
});
