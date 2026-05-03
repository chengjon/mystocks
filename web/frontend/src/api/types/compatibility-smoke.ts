/**
 * Type extension compatibility smoke fixture.
 *
 * This file exists only to keep `npm run type-check` honest about the
 * coexistence of legacy root exports and the newer extension surface.
 */

import type { APIResponse, PaginationParams, UnifiedResponse } from "@/api/types";
import type {
  APIErrorVM,
  AsyncFunction,
  CurrencyCode,
  FormField,
  FormValidationSchema,
  FormValidationState,
  FilterParamsVM,
  HttpMethod,
  KeysOfType,
  LanguageCode,
  LoadingState,
  PaginatedResponseVM,
  PaginationParamsVM,
  SearchParams,
  SearchParamsVM,
  SortParamsVM,
  StrategyComparisonDataVM,
  StrategyOptimizationRequestVM,
  StrategyOptimizationResultVM,
  StrategyVM,
  TimeoutOptions,
  UploadResult,
  UploadProgressVM,
  UploadResultVM,
  ValidationResultVM,
  WSDataMessage,
  WSDataMessageVM,
  WSErrorMessageVM,
  WSSubscription,
  WSSubscriptionVM,
} from "@/api/types/extensions";

type TypeExtensionUploadStringKey = KeysOfType<UploadResult, string>;
type TypeExtensionSearchLoader = AsyncFunction<
  PaginatedResponseVM<StrategyVM>,
  [SearchParams, TimeoutOptions?]
>;

export interface TypeExtensionCompatibilitySmoke {
  root_response: APIResponse | null;
  root_pagination: PaginationParams;
  root_unified: UnifiedResponse<StrategyVM[]>;
  extension_strategy: StrategyVM | null;
  extension_form_field: FormField | null;
  extension_form_schema: FormValidationSchema;
  extension_form_state: FormValidationState | null;
  extension_strategy_comparison: StrategyComparisonDataVM | null;
  extension_strategy_optimization_request: StrategyOptimizationRequestVM | null;
  extension_strategy_optimization_result: StrategyOptimizationResultVM | null;
  extension_paginated_response: PaginatedResponseVM<StrategyVM> | null;
  extension_api_error: APIErrorVM | null;
  extension_pagination_params: PaginationParamsVM;
  extension_search_params: SearchParamsVM;
  extension_filter_params: FilterParamsVM;
  extension_sort_params: SortParamsVM | null;
  extension_validation_result: ValidationResultVM | null;
  extension_upload_result: UploadResultVM | null;
  extension_upload_progress: UploadProgressVM | null;
  extension_ws_subscription_vm: WSSubscriptionVM | null;
  extension_ws_data_message_vm: WSDataMessageVM<StrategyVM[]> | null;
  extension_ws_error_message_vm: WSErrorMessageVM | null;
  extension_ws_subscription: WSSubscription | null;
  extension_ws_data_message: WSDataMessage<StrategyVM[]> | null;
  extension_search_params_legacy: SearchParams;
  extension_upload_result_legacy: UploadResult | null;
  extension_upload_string_key: TypeExtensionUploadStringKey | null;
  extension_search_loader: TypeExtensionSearchLoader | null;
  extension_timeout_options: TimeoutOptions;
  extension_http_method: HttpMethod;
  extension_loading_state: LoadingState;
  extension_language_code: LanguageCode;
  extension_currency_code: CurrencyCode;
}

export type TypeExtensionCompatibilityRecord = Record<string, TypeExtensionCompatibilitySmoke>;
