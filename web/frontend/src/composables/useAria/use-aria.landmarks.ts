import { computed, type ComputedRef } from "vue";

import type { AriaProps } from "./unknown";

export function createDecorativeAria(): ComputedRef<AriaProps> {
  return computed(() => ({
    "aria-hidden": true,
    role: "presentation",
  }));
}

export function createNavigationAria(label: string): ComputedRef<AriaProps> {
  return computed(() => ({
    "aria-label": label,
    role: "navigation",
  }));
}

export function createMainAria(label: string): ComputedRef<AriaProps> {
  return computed(() => ({
    "aria-label": label,
    role: "main",
  }));
}

export function createSearchAria(label: string): ComputedRef<AriaProps> {
  return computed(() => ({
    "aria-label": label,
    role: "search",
  }));
}

export function createHintId(fieldName: string, hintType: "hint" | "error" | "description" = "hint"): string {
  const normalizedField = fieldName.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  return `${normalizedField || "field"}-${hintType}`;
}
