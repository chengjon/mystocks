// Global type declarations for auto-generated types
// This file provides type definitions for types that are referenced but not defined
// in the auto-generated type files (generated-types.ts, common.ts, etc.)

declare global {
  // Generic dictionary type used throughout the codebase
  type Dict = Record<string, any>;

  // Generic list type used throughout the codebase
  type List<T = any> = T[];

  // Generic type parameter (used in generic type definitions)
  type T = any;

  // Market overview (reference to market.ts)
  type MarketOverview = import('./market').MarketOverview;

  // HMM (Hidden Markov Model) configuration
  interface HMMConfig {
    states: number;
    emissions: string;
    iterations: number;
    tolerance: number;
  }

  // Neural Network configuration
  interface NeuralNetworkConfig {
    layers: number[];
    activation: string;
    optimizer: string;
    learningRate: number;
    epochs: number;
    batchSize: number;
  }

  // Generic list function (for compatibility)
  function list<T>(items: T[]): T[];
}

export {};
