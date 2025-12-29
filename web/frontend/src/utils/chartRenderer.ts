import type { KLineData } from '@/types/kline';

export interface RenderOptions {
  canvas: HTMLCanvasElement;
  data: KLineData[];
  width: number;
  height: number;
  padding?: { top: number; right: number; bottom: number; left: number };
  colors?: {
    upColor: string;
    downColor: string;
    upBorderColor: string;
    downBorderColor: string;
    upWickColor: string;
    downWickColor: string;
    gridColor: string;
    axisColor: string;
  };
}

export interface ChartMetrics {
  minPrice: number;
  maxPrice: number;
  priceRange: number;
  minVolume: number;
  maxVolume: number;
  volumeRange: number;
  candleWidth: number;
  candleSpacing: number;
}

export class ChartRenderer {
  private ctx: CanvasRenderingContext2D;
  private options: RenderOptions;
  private metrics: ChartMetrics | null = null;

  constructor(options: RenderOptions) {
    this.options = options;
    const canvas = options.canvas;
    this.ctx = canvas.getContext('2d')!;
    canvas.width = options.width;
    canvas.height = options.height;
  }

  calculateMetrics(): ChartMetrics {
    const { data, width, height, padding = { top: 20, right: 60, bottom: 30, left: 10 } } = this.options;

    if (data.length === 0) {
      throw new Error('No data to render');
    }

    const chartHeight = height - padding.top - padding.bottom;
    const chartWidth = width - padding.left - padding.right;

    let minPrice = Infinity;
    let maxPrice = -Infinity;
    let minVolume = Infinity;
    let maxVolume = -Infinity;

    for (const item of data) {
      if (item.low < minPrice) minPrice = item.low;
      if (item.high > maxPrice) maxPrice = item.high;
      if (item.volume < minVolume) minVolume = item.volume;
      if (item.volume > maxVolume) maxVolume = item.volume;
    }

    const pricePadding = (maxPrice - minPrice) * 0.1;
    minPrice -= pricePadding;
    maxPrice += pricePadding;

    const volumeHeight = chartHeight * 0.2;
    const volumeMax = maxVolume * 1.1;

    const candleSpacing = Math.max(1, Math.floor(chartWidth / data.length) - 1);
    const candleWidth = Math.max(1, candleSpacing - 2);

    this.metrics = {
      minPrice,
      maxPrice,
      priceRange: maxPrice - minPrice,
      minVolume,
      maxVolume: volumeMax,
      volumeRange: volumeMax - minVolume,
      candleWidth,
      candleSpacing
    };

    return this.metrics;
  }

  priceToY(price: number): number {
    if (!this.metrics) this.calculateMetrics();
    const { padding = { top: 20, right: 60, bottom: 30, left: 10 } } = this.options;
    const chartHeight = this.options.height - padding.top - padding.bottom;
    const ratio = (price - this.metrics!.minPrice) / this.metrics!.priceRange;
    return this.options.height - padding.bottom - ratio * chartHeight;
  }

  volumeToY(volume: number): number {
    if (!this.metrics) this.calculateMetrics();
    const { padding = { top: 20, right: 60, bottom: 30, left: 10 } } = this.options;
    const chartHeight = this.options.height - padding.top - padding.bottom;
    const volumeHeight = chartHeight * 0.2;
    const ratio = volume / this.metrics!.maxVolume;
    return this.options.height - padding.bottom - ratio * volumeHeight;
  }

  indexToX(index: number): number {
    if (!this.metrics) this.calculateMetrics();
    const { padding = { left: 10 } } = this.options;
    return padding.left + index * this.metrics!.candleSpacing + this.metrics!.candleWidth / 2;
  }

  render(): void {
    const { data, padding = { top: 20, right: 60, bottom: 30, left: 10 }, colors } = this.options;

    this.calculateMetrics();
    this.clear();
    this.drawGrid(padding);
    this.drawVolume(padding);
    this.drawCandles(padding, colors);
    this.drawAxes(padding);
  }

  clear(): void {
    const { width, height } = this.options;
    this.ctx.clearRect(0, 0, width, height);
  }

  drawGrid(padding: { top: number; right: number; bottom: number; left: number }): void {
    const { width, height, colors } = this.options;
    const gridColor = colors?.gridColor || '#333333';

    this.ctx.strokeStyle = gridColor;
    this.ctx.lineWidth = 0.5;

    const chartHeight = height - padding.top - padding.bottom;
    const chartWidth = width - padding.left - padding.right;

    const horizontalLines = 5;
    for (let i = 0; i <= horizontalLines; i++) {
      const y = padding.top + (chartHeight / horizontalLines) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(padding.left, y);
      this.ctx.lineTo(width - padding.right, y);
      this.ctx.stroke();
    }

    const verticalLines = 6;
    for (let i = 0; i <= verticalLines; i++) {
      const x = padding.left + (chartWidth / verticalLines) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(x, padding.top);
      this.ctx.lineTo(x, height - padding.bottom);
      this.ctx.stroke();
    }
  }

  drawVolume(padding: { top: number; right: number; bottom: number; left: number }, colors?: RenderOptions['colors']): void {
    const { data } = this.options;
    const upColor = colors?.upColor || '#26a69a';
    const downColor = colors?.downColor || '#ef5350';

    const chartHeight = this.options.height - padding.top - padding.bottom;
    const volumeHeight = chartHeight * 0.2;
    const volumeTop = this.options.height - padding.bottom - volumeHeight;

    this.ctx.fillStyle = upColor;

    for (let i = 0; i < data.length; i++) {
      const x = this.indexToX(i) - this.metrics!.candleWidth / 2;
      const y = this.volumeToY(data[i].volume);
      const barHeight = this.options.height - padding.bottom - y;

      this.ctx.fillStyle = data[i].close >= data[i].open ? upColor : downColor;
      this.ctx.fillRect(x, y, this.metrics!.candleWidth, barHeight);
    }
  }

  drawCandles(padding: { top: number; right: number; bottom: number; left: number }, colors?: RenderOptions['colors']): void {
    const { data } = this.options;
    const upColor = colors?.upColor || '#26a69a';
    const downColor = colors?.downColor || '#ef5350';
    const upBorderColor = colors?.upBorderColor || upColor;
    const downBorderColor = colors?.downBorderColor || downColor;
    const upWickColor = colors?.upWickColor || upColor;
    const downWickColor = colors?.downWickColor || downColor;

    for (let i = 0; i < data.length; i++) {
      const x = this.indexToX(i) - this.metrics!.candleWidth / 2;
      const openY = this.priceToY(data[i].open);
      const closeY = this.priceToY(data[i].close);
      const highY = this.priceToY(data[i].high);
      const lowY = this.priceToY(data[i].low);
      const isUp = data[i].close >= data[i].open;
      const color = isUp ? upColor : downColor;
      const borderColor = isUp ? upBorderColor : downBorderColor;
      const wickColor = isUp ? upWickColor : downWickColor;

      this.ctx.fillStyle = color;
      this.ctx.strokeStyle = borderColor;
      this.ctx.lineWidth = 1;

      const bodyHeight = Math.max(1, Math.abs(closeY - openY));
      this.ctx.fillRect(x, Math.min(openY, closeY), this.metrics!.candleWidth, bodyHeight);
      this.ctx.strokeRect(x, Math.min(openY, closeY), this.metrics!.candleWidth, bodyHeight);

      this.ctx.strokeStyle = wickColor;
      this.ctx.beginPath();
      this.ctx.moveTo(this.indexToX(i), highY);
      this.ctx.lineTo(this.indexToX(i), lowY);
      this.ctx.stroke();
    }
  }

  drawAxes(padding: { top: number; right: number; bottom: number; left: number }): void {
    const { width, height, colors } = this.options;
    const axisColor = colors?.axisColor || '#888888';

    this.ctx.fillStyle = axisColor;
    this.ctx.font = '10px monospace';
    this.ctx.textAlign = 'right';

    if (!this.metrics) this.calculateMetrics();

    const { minPrice, maxPrice } = this.metrics!;
    const priceStep = (maxPrice - minPrice) / 4;
    const chartHeight = height - padding.top - padding.bottom;

    for (let i = 0; i <= 4; i++) {
      const price = minPrice + priceStep * i;
      const y = padding.top + (chartHeight / 4) * i;
      this.ctx.fillText(price.toFixed(2), width - padding.right + 5, y + 3);
    }

    this.ctx.textAlign = 'center';
    const data = this.options.data;
    const step = Math.ceil(data.length / 6);

    for (let i = 0; i < data.length; i += step) {
      const x = this.indexToX(i);
      const date = new Date(data[i].timestamp);
      const dateStr = `${date.getMonth() + 1}/${date.getDate()}`;
      this.ctx.fillText(dateStr, x, height - padding.bottom + 15);
    }
  }

  resize(width: number, height: number): void {
    this.options.width = width;
    this.options.height = height;
    this.options.canvas.width = width;
    this.options.canvas.height = height;
    this.metrics = null;
  }
}

export default ChartRenderer;
