import type { KLineData } from '@/types/kline';

export interface CrosshairPosition {
  x: number;
  y: number;
  dataIndex: number;
  data?: KLineData;
}

export interface CrosshairCallbacks {
  onMove?: (position: CrosshairPosition) => void;
  onLeave?: () => void;
}

export interface CrosshairOptions {
  canvas: HTMLCanvasElement;
  chartContainer: HTMLElement;
  data: KLineData[];
  onMove?: (position: CrosshairPosition) => void;
  onLeave?: () => void;
}

export class CrosshairHandler {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private chartContainer: HTMLElement;
  private data: KLineData[];
  private callbacks: Required<CrosshairCallbacks>;
  private isActive: boolean = false;
  private currentPosition: CrosshairPosition | null = null;
  private candleSpacing: number = 0;
  private candleWidth: number = 0;
  private padding: { left: number; top: number; right: number; bottom: number } = { left: 10, top: 20, right: 60, bottom: 30 };

  constructor(options: CrosshairOptions) {
    this.canvas = options.canvas;
    this.ctx = this.canvas.getContext('2d')!;
    this.chartContainer = options.chartContainer;
    this.data = options.data;
    this.callbacks = {
      onMove: options.onMove || (() => {}),
      onLeave: options.onLeave || (() => {})
    };
    this.bindEvents();
  }

  setLayout(spacing: number, width: number, padding: { left: number; top: number; right: number; bottom: number }): void {
    this.candleSpacing = spacing;
    this.candleWidth = width;
    this.padding = padding;
  }

  bindEvents(): void {
    this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
    this.canvas.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
    this.canvas.addEventListener('mouseenter', this.handleMouseEnter.bind(this));
  }

  private handleMouseMove(event: MouseEvent): void {
    const rect = this.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const chartLeft = this.padding.left;
    const chartRight = this.canvas.width - this.padding.right;
    const chartTop = this.padding.top;
    const chartBottom = this.canvas.height - this.padding.bottom;

    if (x < chartLeft || x > chartRight || y < chartTop || y > chartBottom) {
      this.handleMouseLeave();
      return;
    }

    const dataIndex = Math.floor((x - chartLeft) / this.candleSpacing);
    const clampedIndex = Math.max(0, Math.min(dataIndex, this.data.length - 1));
    const data = this.data[clampedIndex];

    this.currentPosition = {
      x,
      y,
      dataIndex: clampedIndex,
      data
    };

    this.callbacks.onMove(this.currentPosition);
    this.draw(x, y);
  }

  private handleMouseEnter(event: MouseEvent): void {
    this.isActive = true;
  }

  private handleMouseLeave(): void {
    this.isActive = false;
    this.currentPosition = null;
    this.callbacks.onLeave();
    this.clear();
  }

  private clear(): void {
    const width = this.canvas.width;
    const height = this.canvas.height;
    this.ctx.clearRect(0, 0, width, height);
  }

  draw(mouseX: number, mouseY: number): void {
    if (!this.isActive || !this.currentPosition) return;

    this.clear();

    const { x, y, data } = this.currentPosition;
    const { width, height } = this.canvas;

    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
    this.ctx.lineWidth = 1;
    this.ctx.setLineDash([4, 4]);

    this.ctx.beginPath();
    this.ctx.moveTo(x, this.padding.top);
    this.ctx.lineTo(x, height - this.padding.bottom);
    this.ctx.stroke();

    this.ctx.beginPath();
    this.ctx.moveTo(this.padding.left, y);
    this.ctx.lineTo(width - this.padding.right, y);
    this.ctx.stroke();

    this.ctx.setLineDash([]);

    if (data) {
      this.drawTooltip(x, y, data);
    }
  }

  private drawTooltip(x: number, y: number, data: KLineData): void {
    const tooltipWidth = 140;
    const tooltipHeight = 120;
    const padding = 10;

    let tooltipX = x + 15;
    let tooltipY = y - tooltipHeight / 2;

    if (tooltipX + tooltipWidth > this.canvas.width - this.padding.right) {
      tooltipX = x - tooltipWidth - 15;
    }

    if (tooltipY < this.padding.top) {
      tooltipY = this.padding.top;
    }
    if (tooltipY + tooltipHeight > this.canvas.height - this.padding.bottom) {
      tooltipY = this.canvas.height - this.padding.bottom - tooltipHeight;
    }

    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    this.ctx.lineWidth = 1;

    this.ctx.beginPath();
    this.ctx.roundRect(tooltipX, tooltipY, tooltipWidth, tooltipHeight, 4);
    this.ctx.fill();
    this.ctx.stroke();

    this.ctx.fillStyle = '#ffffff';
    this.ctx.font = '12px monospace';

    const date = new Date(data.timestamp);
    const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;

    this.ctx.fillText(dateStr, tooltipX + padding, tooltipY + 20);

    this.ctx.fillStyle = '#aaaaaa';
    this.ctx.fillText(`O: ${data.open.toFixed(2)}`, tooltipX + padding, tooltipY + 38);
    this.ctx.fillText(`H: ${data.high.toFixed(2)}`, tooltipX + padding, tooltipY + 54);
    this.ctx.fillText(`L: ${data.low.toFixed(2)}`, tooltipX + padding, tooltipY + 70);
    this.ctx.fillText(`C: ${data.close.toFixed(2)}`, tooltipX + padding, tooltipY + 86);
    this.ctx.fillText(`V: ${(data.volume / 10000).toFixed(2)}万`, tooltipX + padding, tooltipY + 102);

    const change = ((data.close - data.open) / data.open * 100);
    this.ctx.fillStyle = change >= 0 ? '#26a69a' : '#ef5350';
    this.ctx.fillText(`${change >= 0 ? '+' : ''}${change.toFixed(2)}%`, tooltipX + padding + 70, tooltipY + 86);
  }

  destroy(): void {
    this.canvas.removeEventListener('mousemove', this.handleMouseMove.bind(this));
    this.canvas.removeEventListener('mouseleave', this.handleMouseLeave.bind(this));
    this.canvas.removeEventListener('mouseenter', this.handleMouseEnter.bind(this));
    this.clear();
  }
}

export default CrosshairHandler;
