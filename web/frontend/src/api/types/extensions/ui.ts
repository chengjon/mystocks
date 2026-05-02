/**
 * UI Form Types
 *
 * Frontend-only form field metadata and validation contracts used by
 * Element Plus-style form builders and reusable form helpers.
 */

export type FormFieldComponent =
  | 'input'
  | 'textarea'
  | 'input-number'
  | 'select'
  | 'switch'
  | 'radio'
  | 'checkbox'
  | 'date'
  | 'date-range';

export type FormValidationTrigger = 'blur' | 'change' | 'submit';

export type FormValidationValueType =
  | 'string'
  | 'number'
  | 'boolean'
  | 'array'
  | 'date'
  | 'enum';

export interface FormFieldOption<T = string | number | boolean> {
  label: string;
  value: T;
  disabled?: boolean;
  description?: string;
}

export interface FormValidationRule {
  required?: boolean;
  type?: FormValidationValueType;
  min?: number;
  max?: number;
  pattern?: string | RegExp;
  message: string;
  trigger?: FormValidationTrigger | FormValidationTrigger[];
  validator_name?: string;
}

export type FormValidationSchema = Record<string, FormValidationRule[]>;

export interface FormValidationState {
  is_valid: boolean;
  is_dirty: boolean;
  is_touched: boolean;
  errors: string[];
  warnings?: string[];
}

export interface FormField<T = unknown> {
  key: string;
  label: string;
  component: FormFieldComponent;
  required?: boolean;
  placeholder?: string;
  default_value?: T;
  help_text?: string;
  props?: Record<string, unknown>;
  options?: FormFieldOption[];
  rules?: FormValidationRule[];
}
