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

/**
 * Validation trigger union used by frontend-only form schemas.
 */
export type FormValidationTrigger = 'blur' | 'change' | 'submit';

/**
 * Value categories supported by reusable validation rules.
 */
export type FormValidationValueType =
  | 'string'
  | 'number'
  | 'boolean'
  | 'array'
  | 'date'
  | 'enum';

/**
 * Selectable option metadata for enum-like form fields.
 */
export interface FormFieldOption<T = string | number | boolean> {
  label: string;
  value: T;
  disabled?: boolean;
  description?: string;
}

/**
 * Validation rule definition consumed by frontend form builders.
 */
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

/**
 * Field-to-rule mapping for a complete frontend form schema.
 */
export type FormValidationSchema = Record<string, FormValidationRule[]>;

/**
 * Runtime validation state tracked for a single form field.
 */
export interface FormValidationState {
  is_valid: boolean;
  is_dirty: boolean;
  is_touched: boolean;
  errors: string[];
  warnings?: string[];
}

/**
 * Frontend-only form field metadata used by shared form renderers.
 */
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
