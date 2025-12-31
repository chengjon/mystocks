/**
 * ECharts Type Declarations
 *
 * Extended type declarations for ECharts to handle missing type definitions.
 */

declare module 'echarts' {
  export interface EChartsOption {
    [key: string]: any;
  }

  export interface ECharts {
    dispose: () => void;
    resize: () => void;
    setOption: (option: EChartsOption, notMerge?: boolean, lazyUpdate?: boolean) => void;
    getOption: () => EChartsOption;
    showLoading: (type?: string, opts?: object) => void;
    hideLoading: () => void;
    getDataURL: (opts: { type?: string; pixelRatio?: number; backgroundColor?: string }) => string;
    getConnectedDataURL: (opts: object) => string;
    convertToPixel: (finder: object, value: any) => any;
    convertFromPixel: (finder: object, value: any) => any;
    containPixel: (finder: object, value: any) => boolean;
    focus: (action: string, name: string) => void;
    dispatch: (action: object) => void;
    on: (event: string, handler: Function, context?: object) => void;
    off: (event: string, handler?: Function) => void;
  }

  export interface EChartsInitOpts {
    renderer?: 'canvas' | 'svg';
    width?: number | string;
    height?: number | string;
    locale?: string;
    renderer?: string;
  }

  export function init(
    dom: HTMLElement,
    theme?: string | object,
    opts?: EChartsInitOpts
  ): ECharts;

  export function dispose(dom: HTMLElement | string | ECharts): void;

  export function connect(group: string | object): void;

  export function disconnect(group: string): void;

  export function registerMap(mapName: string, geoJson: object, opt?: object): void;

  export function registerTheme(name: string, theme: object): void;

  export function getInstanceByDom(dom: HTMLElement): ECharts | null;

  export function use(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    deps: any[],
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    fn: (...args: any[]) => void
  ): void;
}

// ============================================
// Element Plus Type Extensions
// ============================================

declare module 'element-plus/es' {
  import type { DefineComponent } from 'vue';

  export const ElTag: DefineComponent<{
    type?: 'success' | 'info' | 'warning' | 'danger' | 'primary';
    closable?: boolean;
    disableTransitions?: boolean;
    hit?: boolean;
    effect?: 'dark' | 'light' | 'plain';
    size?: 'large' | 'default' | 'small';
  }>;

  export const ElButton: DefineComponent<{
    type?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default';
    size?: 'large' | 'default' | 'small';
    plain?: boolean;
    round?: boolean;
    circle?: boolean;
    loading?: boolean;
    disabled?: boolean;
    icon?: string;
    autofocus?: boolean;
    nativeType?: 'button' | 'submit' | 'reset';
  }>;

  export const ElCard: DefineComponent<{
    bodyStyle?: object;
    header?: string | object;
    shadow?: 'always' | 'hover' | 'never';
  }>;

  export const ElTable: DefineComponent<{
    data?: any[];
    size?: 'large' | 'default' | 'small';
    width?: number | string;
    height?: number | string;
    maxHeight?: number | string;
    fit?: boolean;
    stripe?: boolean;
    border?: boolean;
    rowKey?: string | ((row: any) => string);
    showHeader?: boolean;
    showSummary?: boolean;
    summaryMethod?: (param: { columns: any[]; data: any[] }) => any[];
    rowClassName?: string | ((param: { row: any; rowIndex: number }) => string);
    rowStyle?: object | ((param: { row: any; rowIndex: number }) => object);
    cellClassName?: string | ((param: { row: any; column: any; rowIndex: number; columnIndex: number }) => string);
    cellStyle?: object | ((param: { row: any; column: any; rowIndex: number; columnIndex: number }) => object);
    headerRowClassName?: string | ((param: { row: any; rowIndex: number }) => string);
    headerRowStyle?: object | ((param: { row: any; rowIndex: number }) => object);
    headerCellClassName?: string | ((param: { row: any; column: any; rowIndex: number; columnIndex: number }) => string);
    headerCellStyle?: object | ((param: { row: any; column: any; rowIndex: number; columnIndex: number }) => object);
    highlightCurrentRow?: boolean;
    currentRowKey?: string | number;
    emptyText?: string;
    expandRowKeys?: any[];
    defaultExpandAll?: boolean;
    defaultSort?: { prop: string; order: string };
    tooltipEffect?: string;
    spanMethod?: (param: { row: any; column: any; rowIndex: number; columnIndex: number }) => object;
    selectOnIndeterminate?: boolean;
    indent?: number;
    lazy?: boolean;
    load?: (row: any, resolve: (children: any[]) => void) => void;
    treeProps?: { hasChildren?: string; children?: string };
  }>;

  export const ElTableColumn: DefineComponent<{
    type?: 'index' | 'selection' | 'expand' | 'html';
    index?: number | ((index: number) => number);
    label?: string;
    columnKey?: string;
    prop?: string;
    width?: number | string;
    minWidth?: number | string;
    fixed?: boolean | 'left' | 'right';
    renderHeader?: (param: { column: any; $index: number }) => VNode;
    sortable?: boolean | 'custom';
    sortMethod?: (a: any, b: any) => number;
    sortBy?: string | string[] | ((row: any, index: number) => string);
    resizable?: boolean;
    formatter?: (row: any, column: any, cellValue: any, index: number) => any;
    showOverflowTooltip?: boolean;
    align?: 'left' | 'center' | 'right';
    headerAlign?: 'left' | 'center' | 'right';
    className?: string;
    labelClassName?: string;
    selectable?: (row: any, index: number) => boolean;
    reserveSelection?: boolean;
    filterMethod?: (value: any, row: any, column: any) => boolean;
    filteredValue?: string[];
    filterPlacement?: string;
    filterClassName?: string;
  }>;

  export const ElDialog: DefineComponent<{
    title?: string;
    modal?: boolean;
    modalAppendToBody?: boolean;
    appendToBody?: boolean;
    lockScroll?: boolean;
    closeOnClickModal?: boolean;
    closeOnPressEscape?: boolean;
    showClose?: boolean;
    beforeClose?: (done: () => void) => void;
    center?: boolean;
    destroyOnClose?: boolean;
    width?: string | number;
    fullscreen?: boolean;
    top?: string;
    draggable?: boolean;
    overflow?: boolean;
  }>;

  export const ElInput: DefineComponent<{
    type?: 'text' | 'textarea' | 'password' | 'number' | 'email' | 'url' | 'date' | 'tel';
    modelValue?: string | number;
    maxlength?: number;
    minlength?: number;
    showWordLimit?: boolean;
    placeholder?: string;
    clearable?: boolean;
    showPassword?: boolean;
    disabled?: boolean;
    size?: 'large' | 'default' | 'small';
    prefixIcon?: string;
    suffixIcon?: string;
    rows?: number;
    autosize?: boolean | { minRows: number; maxRows: number };
    autocomplete?: string;
    name?: string;
    readonly?: boolean;
    max?: number;
    min?: number;
    step?: number;
    resize?: 'none' | 'both' | 'horizontal' | 'vertical';
    autofocus?: boolean;
    form?: string;
    label?: string;
    tabindex?: string | number;
  }>;

  export const ElSelect: DefineComponent<{
    modelValue?: string | number | string[] | number[];
    multiple?: boolean;
    disabled?: boolean;
    valueKey?: string;
    size?: 'large' | 'default' | 'small';
    clearable?: boolean;
    filterable?: boolean;
    allowCreate?: boolean;
    remote?: boolean;
    loading?: boolean;
    filterMethod?: (query: string) => void;
    remoteMethod?: (query: string) => void;
    remoteShowSuffix?: boolean;
    loadingText?: string;
    noMatchText?: string;
    noDataText?: string;
    popperClass?: string;
    defaultFirstOption?: boolean;
    reserveKeyword?: boolean;
    placeholder?: string;
    prefixIcon?: string;
    clearIcon?: string;
    fitInputWidth?: boolean;
  }>;

  export const ElOption: DefineComponent<{
    value: string | number;
    label?: string;
    disabled?: boolean;
  }>;

  export const ElInputNumber: DefineComponent<{
    modelValue?: number;
    min?: number;
    max?: number;
    step?: number;
    stepStrictly?: boolean;
    precision?: number;
    size?: 'large' | 'default' | 'small';
    disabled?: boolean;
    controls?: boolean;
    controlsPosition?: 'right' | '';
    name?: string;
    placeholder?: string;
  }>;

  export const ElDatePicker: DefineComponent<{
    modelValue?: string | Date | (string | Date)[];
    type?: 'year' | 'month' | 'date' | 'dates' | 'week' | 'datetime' | 'datetimerange' | 'daterange' | 'monthrange';
    disabledDate?: (date: Date) => boolean;
    startPlaceholder?: string;
    endPlaceholder?: string;
    defaultValue?: Date | (Date | null)[];
    defaultTime?: Date | (Date | null)[];
    valueFormat?: string;
    dateFormat?: string;
    size?: 'large' | 'default' | 'small';
    format?: string;
    popperClass?: string;
    pickerOptions?: object;
    rangeSeparator?: string;
    unlinkPanels?: boolean;
    clearable?: boolean;
  }>;

  export const ElTabs: DefineComponent<{
    modelValue?: string;
    type?: 'card' | 'border-card';
    closable?: boolean;
    addable?: boolean;
    editable?: boolean;
    tabPosition?: 'top' | 'right' | 'bottom' | 'left';
    stretch?: boolean;
    beforeLeave?: (activeName: string, oldActiveName: string) => boolean | Promise<boolean>;
  }>;

  export const ElTabPane: DefineComponent<{
    name: string;
    label?: string;
    disabled?: boolean;
    closable?: boolean;
    lazy?: boolean;
  }>;

  export const ElMenu: DefineComponent<{
    mode?: 'horizontal' | 'vertical';
    defaultActive?: string;
    defaultOpeneds?: string[];
    uniqueOpened?: boolean;
    router?: boolean;
    menuTrigger?: 'hover' | 'click';
    collapse?: boolean;
    backgroundColor?: string;
    textColor?: string;
    activeTextColor?: string;
    collapseTransition?: boolean;
  }>;

  export const ElMenuItem: DefineComponent<{
    index?: string;
    route?: object;
    disabled?: boolean;
  }>;

  export const ElRow: DefineComponent<{
    gutter?: number;
    justify?: 'start' | 'center' | 'end' | 'space-between' | 'space-around';
    align?: 'top' | 'middle' | 'bottom';
    tag?: string;
  }>;

  export const ElCol: DefineComponent<{
    span?: number;
    offset?: number;
    pull?: number;
    push?: number;
    xs?: number | object;
    sm?: number | object;
    md?: number | object;
    lg?: number | object;
    xl?: number | object;
    tag?: string;
  }>;

  export const ElContainer: DefineComponent<{
    direction?: 'horizontal' | 'vertical';
  }>;

  export const ElHeader: DefineComponent<{
    height?: string;
  }>;

  export const ElAside: DefineComponent<{
    width?: string;
  }>;

  export const ElMain: DefineComponent;

  export const ElScrollbar: DefineComponent<{
    height?: string;
    maxHeight?: string;
    native?: boolean;
    wrapStyle?: object;
    wrapClass?: string;
    viewClass?: string;
    viewStyle?: object;
    noresize?: boolean;
    tag?: string;
  }>;

  export const ElSpace: DefineComponent<{
    size?: 'small' | 'medium' | 'large' | number;
    direction?: 'horizontal' | 'vertical';
    alignment?: string;
    wrap?: boolean;
    spacer?: string | VNode;
  }>;

  export const ElEmpty: DefineComponent<{
    description?: string;
    image?: string;
  }>;

  export const ElRadioGroup: DefineComponent<{
    modelValue?: string | number;
    size?: 'large' | 'default' | 'small';
    disabled?: boolean;
    textColor?: string;
    fill?: string;
  }>;

  export const ElRadioButton: DefineComponent;

  export const ElDivider: DefineComponent<{
    direction?: 'horizontal' | 'vertical';
    contentPosition?: 'left' | 'center' | 'right';
    borderType?: 'solid' | 'dashed' | 'dotted';
  }>;

  export const ElDrawer: DefineComponent<{
    modelValue?: boolean;
    title?: string;
    direction?: 'ltr' | 'rtl' | 'ttb' | 'btt';
    size?: string;
    modal?: boolean;
    modalClass?: string;
    appendToBody?: boolean;
    lockScroll?: boolean;
    closeOnClickModal?: boolean;
    closeOnPressEscape?: boolean;
    showClose?: boolean;
    beforeClose?: (done: () => void) => void;
    destroyOnClose?: boolean;
  }>;

  export const ElDropdown: DefineComponent<{
    type?: string;
    size?: 'large' | 'default' | 'small';
    splitButton?: boolean;
    disabled?: boolean;
    trigger?: 'click' | 'hover' | 'contextmenu';
    hideOnClick?: boolean;
    tabindex?: number;
    popperClass?: string;
  }>;

  export const ElDropdownItem: DefineComponent<{
    command?: string | number;
    disabled?: boolean;
    divided?: boolean;
  }>;

  export const ElDropdownMenu: DefineComponent;

  export const ElAutocomplete: DefineComponent<{
    modelValue?: string;
    valueKey?: string;
    debounce?: number;
    placeholder?: string;
    clearable?: boolean;
    disabled?: boolean;
    valueIcon?: string;
    popperClass?: string;
    popperOptions?: object;
    triggerOnFocus?: boolean;
    selectWhenUnmatched?: boolean;
    name?: string;
    label?: string;
    prefixIcon?: string;
    suffixIcon?: string;
    fetchSuggestions?: (queryString: string, cb: (data: any[]) => void) => void;
  }>;
}
