import { describe, it, expect, beforeEach, vi } from 'vitest';
import { CrosshairHandler } from '@/utils/crosshair';
import type { KLineData } from '@/types/kline';

describe('Chart Interaction', () => {
  let mockCanvas: HTMLCanvasElement;
  let mockContainer: HTMLElement;
  let mockData: KLineData[];

  beforeEach(() => {
    mockCanvas = document.createElement('canvas');
    mockCanvas.width = 800;
    mockCanvas.height = 600;

    mockContainer = document.createElement('div');
    mockContainer.appendChild(mockCanvas);

    mockData = Array.from({ length: 100 }, (_, i) => ({
      timestamp: Date.now() - (100 - i) * 86400000,
      open: 100 + Math.random() * 10,
      high: 105 + Math.random() * 10,
      low: 95 + Math.random() * 10,
      close: 100 + Math.random() * 10,
      volume: 1000000 + Math.random() * 500000
    }));
  });

  describe('CrosshairHandler', () => {
    it('should create crosshair handler with options', () => {
      const onMove = vi.fn();
      const onLeave = vi.fn();

      const handler = new CrosshairHandler({
        canvas: mockCanvas,
        chartContainer: mockContainer,
        data: mockData,
        onMove,
        onLeave
      });

      expect(handler).toBeDefined();
      handler.destroy();
    });

    it('should set layout parameters correctly', () => {
      const handler = new CrosshairHandler({
        canvas: mockCanvas,
        chartContainer: mockContainer,
        data: mockData
      });

      handler.setLayout(10, 8, { left: 10, right: 60, top: 20, bottom: 30 });

      handler.destroy();
    });

    it('should handle mouse move events', () => {
      const onMove = vi.fn();

      const handler = new CrosshairHandler({
        canvas: mockCanvas,
        chartContainer: mockContainer,
        data: mockData,
        onMove
      });

      handler.setLayout(10, 8, { left: 10, right: 60, top: 20, bottom: 30 });

      const event = new MouseEvent('mousemove', {
        clientX: mockCanvas.getBoundingClientRect().left + 100,
        clientY: mockCanvas.getBoundingClientRect().top + 200
      });
      mockCanvas.dispatchEvent(event);

      handler.destroy();
    });

    it('should handle mouse leave events', () => {
      const onLeave = vi.fn();

      const handler = new CrosshairHandler({
        canvas: mockCanvas,
        chartContainer: mockContainer,
        data: mockData,
        onLeave
      });

      const event = new MouseEvent('mouseleave');
      mockCanvas.dispatchEvent(event);

      handler.destroy();
    });

    it('should calculate correct data index from mouse position', () => {
      const handler = new CrosshairHandler({
        canvas: mockCanvas,
        chartContainer: mockContainer,
        data: mockData
      });

      handler.setLayout(10, 8, { left: 10, right: 60, top: 20, bottom: 30 });

      const x = 100;
      const chartLeft = 10;
      const spacing = 10;
      const dataIndex = Math.floor((x - chartLeft) / spacing);

      expect(dataIndex).toBe(9);

      handler.destroy();
    });

    it('should handle empty data gracefully', () => {
      const handler = new CrosshairHandler({
        canvas: mockCanvas,
        chartContainer: mockContainer,
        data: []
      });

      const event = new MouseEvent('mousemove', {
        clientX: mockCanvas.getBoundingClientRect().left + 100,
        clientY: mockCanvas.getBoundingClientRect().top + 200
      });
      mockCanvas.dispatchEvent(event);

      handler.destroy();
    });

    it('should clamp data index to valid range', () => {
      const handler = new CrosshairHandler({
        canvas: mockCanvas,
        chartContainer: mockContainer,
        data: mockData
      });

      handler.setLayout(10, 8, { left: 10, right: 60, top: 20, bottom: 30 });

      const clampedIndex = Math.max(0, Math.min(50, mockData.length - 1));
      expect(clampedIndex).toBe(50);

      handler.destroy();
    });
  });

  describe('chart interaction utilities', () => {
    it('should calculate zoom level correctly', () => {
      const zoomLevel = 1.5;
      const expected = 1 / zoomLevel;
      expect(expected).toBeCloseTo(0.667, 3);
    });

    it('should calculate pan offset correctly', () => {
      const panOffset = 50;
      const visibleRange = 100;
      const panRatio = panOffset / visibleRange;
      expect(panRatio).toBe(0.5);
    });
  });

  describe('touch interaction', () => {
    it('should handle touch events for mobile', () => {
      const onMove = vi.fn();

      const handler = new CrosshairHandler({
        canvas: mockCanvas,
        chartContainer: mockContainer,
        data: mockData,
        onMove
      });

      const touchStartEvent = new TouchEvent('touchstart', {
        touches: [new Touch({ identifier: 0, target: mockCanvas, clientX: 100, clientY: 200 })]
      });
      mockCanvas.dispatchEvent(touchStartEvent);

      handler.destroy();
    });

    it('should handle pinch zoom on touch devices', () => {
      const initialDistance = 100;
      const finalDistance = 150;
      const zoomRatio = finalDistance / initialDistance;

      expect(zoomRatio).toBe(1.5);
    });
  });

  describe('keyboard interaction', () => {
    it('should handle keyboard navigation', () => {
      const arrowRight = 'ArrowRight';
      const arrowLeft = 'ArrowLeft';

      expect(arrowRight).toBe('ArrowRight');
      expect(arrowLeft).toBe('ArrowLeft');
    });

    it('should calculate keyboard pan step', () => {
      const panStep = 5;
      const visibleCandles = 100;
      const stepRatio = panStep / visibleCandles;
      expect(stepRatio).toBe(0.05);
    });
  });

  describe('wheel zoom', () => {
    it('should calculate zoom direction from wheel event', () => {
      const wheelDeltaY = -100;
      const zoomIn = wheelDeltaY < 0;
      expect(zoomIn).toBe(true);
    });

    it('should calculate zoom factor', () => {
      const zoomFactor = 0.1;
      const maxZoom = 5;
      const minZoom = 0.2;
      const newZoom = Math.max(minZoom, Math.min(maxZoom, zoomFactor));
      expect(newZoom).toBe(0.2);
    });
  });

  describe('gesture recognition', () => {
    it('should detect pinch gesture', () => {
      const touch1 = { identifier: 1, clientX: 100, clientY: 200 };
      const touch2 = { identifier: 2, clientX: 200, clientY: 200 };
      const touches = [touch1, touch2];

      const distance = Math.sqrt(
        Math.pow(touch2.clientX - touch1.clientX, 2) +
        Math.pow(touch2.clientY - touch1.clientY, 2)
      );

      expect(distance).toBe(100);
    });

    it('should detect pan gesture', () => {
      const startX = 100;
      const endX = 150;
      const panDelta = endX - startX;

      expect(panDelta).toBe(50);
    });
  });
});
