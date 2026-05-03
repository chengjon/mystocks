/**
 * Type extension compatibility smoke fixture.
 *
 * This file exists only to keep `npm run type-check` honest about the
 * coexistence of legacy root exports and the newer extension surface.
 */

import type { APIResponse, PaginationParams, UnifiedResponse } from "@/api/types";
import type { FormField, StrategyVM } from "@/api/types/extensions";

export interface TypeExtensionCompatibilitySmoke {
  root_response: APIResponse | null;
  root_pagination: PaginationParams;
  root_unified: UnifiedResponse<StrategyVM[]>;
  extension_strategy: StrategyVM | null;
  extension_form_field: FormField | null;
}

export type TypeExtensionCompatibilityRecord = Record<string, TypeExtensionCompatibilitySmoke>;
