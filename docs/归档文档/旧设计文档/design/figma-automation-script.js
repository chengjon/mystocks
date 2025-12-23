/**
 * MyStocks Figma 自动化脚本
 *
 * 功能:
 * 1. 批量创建颜色样式
 * 2. 批量创建文本样式
 * 3. 自动生成基础组件
 *
 * 使用方法:
 * 1. 在 Figma 中打开任意文件
 * 2. 菜单栏 → Plugins → Development → New Plugin
 * 3. 选择 "Run once" (运行一次)
 * 4. 将本脚本全部代码复制粘贴到编辑器
 * 5. 点击 "Run" 运行
 * 6. 等待完成提示
 */

// ============================================================================
// 第一部分: 颜色样式创建
// ============================================================================

// 从 design-tokens.json 导入的颜色定义
const COLORS = {
  // 主色调
  primary: { name: "Primary/Blue", value: "#409EFF", description: "主品牌色" },
  success: { name: "Success/Green", value: "#67C23A", description: "成功状态、下跌数据" },
  warning: { name: "Warning/Orange", value: "#E6A23C", description: "警告" },
  danger: { name: "Danger/Red", value: "#F56C6C", description: "错误状态、上涨数据" },
  info: { name: "Info/Gray", value: "#909399", description: "信息色" },

  // 金融专用色
  "financial-up-limit": { name: "Financial/Up Limit", value: "#FF3333", description: "涨停红" },
  "financial-up": { name: "Financial/Up", value: "#F56C6C", description: "上涨红" },
  "financial-flat": { name: "Financial/Flat", value: "#909399", description: "平盘灰" },
  "financial-down": { name: "Financial/Down", value: "#67C23A", description: "下跌绿" },
  "financial-down-limit": { name: "Financial/Down Limit", value: "#00CC00", description: "跌停绿" },

  // 背景色
  "bg-page": { name: "Background/Page", value: "#F5F7FA", description: "页面底色" },
  "bg-card": { name: "Background/Card", value: "#FFFFFF", description: "卡片背景" },
  "bg-table-stripe": { name: "Background/Table Stripe", value: "#FAFAFA", description: "表格斑马纹" },
  "bg-hover": { name: "Background/Hover", value: "#F5F7FA", description: "悬停背景" },
  "bg-selected": { name: "Background/Selected", value: "#ECF5FF", description: "选中背景" },

  // 边框色
  "border-default": { name: "Border/Default", value: "#DCDFE6", description: "默认边框" },
  "border-light": { name: "Border/Light", value: "#E4E7ED", description: "浅色边框" },
  "border-focus": { name: "Border/Focus", value: "#409EFF", description: "焦点边框" },

  // 文本色
  "text-primary": { name: "Text/Primary", value: "#303133", description: "主要文本" },
  "text-regular": { name: "Text/Regular", value: "#606266", description: "常规文本" },
  "text-secondary": { name: "Text/Secondary", value: "#909399", description: "次要文本" },
  "text-placeholder": { name: "Text/Placeholder", value: "#C0C4CC", description: "占位文本" },
};

// 文本样式定义
const TEXT_STYLES = {
  "heading-xl": {
    name: "Heading/XL",
    fontSize: 28,
    lineHeight: 36,
    fontWeight: 600,
    color: "#303133",
    description: "超大标题"
  },
  "heading-lg": {
    name: "Heading/L",
    fontSize: 24,
    lineHeight: 32,
    fontWeight: 600,
    color: "#303133",
    description: "大标题"
  },
  "heading-md": {
    name: "Heading/M",
    fontSize: 20,
    lineHeight: 28,
    fontWeight: 500,
    color: "#303133",
    description: "中标题"
  },
  "heading-sm": {
    name: "Heading/S",
    fontSize: 18,
    lineHeight: 26,
    fontWeight: 500,
    color: "#303133",
    description: "小标题"
  },
  "body-regular": {
    name: "Body/Regular",
    fontSize: 14,
    lineHeight: 22,
    fontWeight: 400,
    color: "#606266",
    description: "正文"
  },
  "body-secondary": {
    name: "Body/Secondary",
    fontSize: 14,
    lineHeight: 22,
    fontWeight: 400,
    color: "#909399",
    description: "次要正文"
  },
  "caption": {
    name: "Caption",
    fontSize: 13,
    lineHeight: 20,
    fontWeight: 400,
    color: "#909399",
    description: "辅助文本"
  },
  "small": {
    name: "Small",
    fontSize: 12,
    lineHeight: 18,
    fontWeight: 400,
    color: "#C0C4CC",
    description: "小字"
  },
  "number-lg": {
    name: "Number/Large",
    fontSize: 32,
    lineHeight: 40,
    fontWeight: 500,
    color: "#303133",
    fontFamily: "SF Mono",
    description: "数字大号"
  },
  "number-md": {
    name: "Number/Medium",
    fontSize: 20,
    lineHeight: 28,
    fontWeight: 500,
    color: "#303133",
    fontFamily: "SF Mono",
    description: "数字中号"
  },
  "number-sm": {
    name: "Number/Small",
    fontSize: 14,
    lineHeight: 22,
    fontWeight: 400,
    color: "#303133",
    fontFamily: "SF Mono",
    description: "数字小号"
  },
};

// ============================================================================
// 辅助函数: 颜色转换
// ============================================================================

/**
 * 将 Hex 颜色转换为 RGB 对象
 * @param {string} hex - Hex 颜色值 (如 "#409EFF")
 * @returns {{r: number, g: number, b: number}} RGB 对象 (0-1 范围)
 */
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16) / 255,
    g: parseInt(result[2], 16) / 255,
    b: parseInt(result[3], 16) / 255
  } : { r: 0, g: 0, b: 0 };
}

// ============================================================================
// 主函数: 创建颜色样式
// ============================================================================

/**
 * 批量创建颜色样式
 */
function createColorStyles() {
  console.log("开始创建颜色样式...");

  let successCount = 0;
  let errorCount = 0;

  for (const [key, colorData] of Object.entries(COLORS)) {
    try {
      const rgb = hexToRgb(colorData.value);

      // 创建 Paint Style
      const style = figma.createPaintStyle();
      style.name = colorData.name;
      style.description = colorData.description || "";

      // 设置颜色
      style.paints = [{
        type: 'SOLID',
        color: rgb
      }];

      console.log(`✓ 创建颜色样式: ${colorData.name} (${colorData.value})`);
      successCount++;

    } catch (error) {
      console.error(`✗ 创建颜色样式失败: ${colorData.name}`, error);
      errorCount++;
    }
  }

  console.log(`颜色样式创建完成: 成功 ${successCount} 个, 失败 ${errorCount} 个`);
  return { successCount, errorCount };
}

// ============================================================================
// 主函数: 创建文本样式
// ============================================================================

/**
 * 批量创建文本样式
 */
async function createTextStyles() {
  console.log("开始创建文本样式...");

  // 加载字体 (必须先加载才能使用)
  const fontsToLoad = [
    { family: "Inter", style: "Regular" },
    { family: "Inter", style: "Medium" },
    { family: "Inter", style: "Semi Bold" },
    { family: "SF Mono", style: "Regular" },
    { family: "SF Mono", style: "Medium" },
  ];

  console.log("加载字体...");
  for (const font of fontsToLoad) {
    try {
      await figma.loadFontAsync(font);
      console.log(`✓ 加载字体: ${font.family} ${font.style}`);
    } catch (error) {
      console.warn(`⚠ 字体加载失败 (将使用默认字体): ${font.family} ${font.style}`);
    }
  }

  let successCount = 0;
  let errorCount = 0;

  for (const [key, textData] of Object.entries(TEXT_STYLES)) {
    try {
      // 创建 Text Style
      const style = figma.createTextStyle();
      style.name = textData.name;
      style.description = textData.description || "";

      // 设置字体
      const fontFamily = textData.fontFamily || "Inter";
      let fontStyle = "Regular";

      if (textData.fontWeight === 600) fontStyle = "Semi Bold";
      else if (textData.fontWeight === 500) fontStyle = "Medium";

      style.fontName = { family: fontFamily, style: fontStyle };
      style.fontSize = textData.fontSize;
      style.lineHeight = { value: textData.lineHeight, unit: "PIXELS" };

      console.log(`✓ 创建文本样式: ${textData.name} (${textData.fontSize}px)`);
      successCount++;

    } catch (error) {
      console.error(`✗ 创建文本样式失败: ${textData.name}`, error);
      errorCount++;
    }
  }

  console.log(`文本样式创建完成: 成功 ${successCount} 个, 失败 ${errorCount} 个`);
  return { successCount, errorCount };
}

// ============================================================================
// 主函数: 创建基础组件
// ============================================================================

/**
 * 创建按钮组件
 */
function createButtonComponent() {
  console.log("创建按钮组件...");

  const frame = figma.createFrame();
  frame.name = "Button Components";
  frame.x = 0;
  frame.y = 0;
  frame.resize(800, 400);
  frame.layoutMode = "HORIZONTAL";
  frame.itemSpacing = 20;
  frame.paddingLeft = 20;
  frame.paddingTop = 20;

  const buttonTypes = [
    { name: "Primary", color: "#409EFF" },
    { name: "Success", color: "#67C23A" },
    { name: "Warning", color: "#E6A23C" },
    { name: "Danger", color: "#F56C6C" },
    { name: "Info", color: "#909399" },
  ];

  for (const btnType of buttonTypes) {
    try {
      // 创建按钮矩形
      const button = figma.createRectangle();
      button.name = `Button/${btnType.name}/Default`;
      button.resize(120, 32);
      button.cornerRadius = 4;

      // 设置背景色
      const rgb = hexToRgb(btnType.color);
      button.fills = [{
        type: 'SOLID',
        color: rgb
      }];

      // 创建文本
      const text = figma.createText();
      text.characters = "按钮";
      text.fontSize = 14;
      text.fills = [{
        type: 'SOLID',
        color: { r: 1, g: 1, b: 1 } // 白色
      }];

      // 组合成 Frame
      const btnFrame = figma.createFrame();
      btnFrame.name = `Button/${btnType.name}`;
      btnFrame.resize(120, 32);
      btnFrame.layoutMode = "HORIZONTAL";
      btnFrame.primaryAxisAlignItems = "CENTER";
      btnFrame.counterAxisAlignItems = "CENTER";
      btnFrame.paddingLeft = 20;
      btnFrame.paddingRight = 20;
      btnFrame.fills = [{
        type: 'SOLID',
        color: rgb
      }];
      btnFrame.cornerRadius = 4;

      btnFrame.appendChild(text);
      frame.appendChild(btnFrame);

      // 创建组件
      const component = figma.createComponentFromNode(btnFrame);

      console.log(`✓ 创建按钮组件: ${btnType.name}`);

    } catch (error) {
      console.error(`✗ 创建按钮组件失败: ${btnType.name}`, error);
    }
  }

  console.log("按钮组件创建完成");
  return frame;
}

/**
 * 创建 PriceCell 组件
 */
async function createPriceCellComponent() {
  console.log("创建 PriceCell 组件...");

  // 加载字体
  await figma.loadFontAsync({ family: "SF Mono", style: "Medium" });

  const frame = figma.createFrame();
  frame.name = "PriceCell Components";
  frame.x = 0;
  frame.y = 450;
  frame.resize(600, 200);
  frame.layoutMode = "HORIZONTAL";
  frame.itemSpacing = 30;
  frame.paddingLeft = 20;
  frame.paddingTop = 20;

  const cellTypes = [
    { name: "Up", color: "#F56C6C", icon: "▲", value: "+12.34", change: "+2.50%" },
    { name: "Down", color: "#67C23A", icon: "▼", value: "-8.90", change: "-1.20%" },
    { name: "Flat", color: "#909399", icon: "—", value: "15.67", change: "0.00%" },
  ];

  for (const cellType of cellTypes) {
    try {
      // 创建容器
      const cellFrame = figma.createFrame();
      cellFrame.name = `PriceCell/${cellType.name}`;
      cellFrame.layoutMode = "HORIZONTAL";
      cellFrame.itemSpacing = 4;
      cellFrame.primaryAxisAlignItems = "CENTER";
      cellFrame.counterAxisAlignItems = "CENTER";

      const rgb = hexToRgb(cellType.color);

      // 图标文本
      const icon = figma.createText();
      icon.characters = cellType.icon;
      icon.fontSize = 12;
      icon.fills = [{ type: 'SOLID', color: rgb }];

      // 数值文本
      const value = figma.createText();
      value.characters = cellType.value;
      value.fontSize = 14;
      value.fontName = { family: "SF Mono", style: "Medium" };
      value.fills = [{ type: 'SOLID', color: rgb }];

      // 涨跌幅文本
      const change = figma.createText();
      change.characters = `(${cellType.change})`;
      change.fontSize = 12;
      change.fills = [{ type: 'SOLID', color: rgb }];
      change.opacity = 0.8;

      cellFrame.appendChild(icon);
      cellFrame.appendChild(value);
      cellFrame.appendChild(change);
      frame.appendChild(cellFrame);

      // 创建组件
      const component = figma.createComponentFromNode(cellFrame);

      console.log(`✓ 创建 PriceCell 组件: ${cellType.name}`);

    } catch (error) {
      console.error(`✗ 创建 PriceCell 组件失败: ${cellType.name}`, error);
    }
  }

  console.log("PriceCell 组件创建完成");
  return frame;
}

// ============================================================================
// 主程序入口
// ============================================================================

/**
 * 主函数: 执行所有自动化任务
 */
async function main() {
  console.log("========================================");
  console.log("MyStocks Figma 自动化脚本");
  console.log("========================================");
  console.log("");

  try {
    // 步骤 1: 创建颜色样式
    console.log("【步骤 1/4】创建颜色样式");
    console.log("----------------------------------------");
    const colorResult = createColorStyles();
    console.log("");

    // 步骤 2: 创建文本样式
    console.log("【步骤 2/4】创建文本样式");
    console.log("----------------------------------------");
    const textResult = await createTextStyles();
    console.log("");

    // 步骤 3: 创建按钮组件
    console.log("【步骤 3/4】创建按钮组件");
    console.log("----------------------------------------");
    createButtonComponent();
    console.log("");

    // 步骤 4: 创建 PriceCell 组件
    console.log("【步骤 4/4】创建 PriceCell 组件");
    console.log("----------------------------------------");
    await createPriceCellComponent();
    console.log("");

    // 总结
    console.log("========================================");
    console.log("✅ 自动化脚本执行完成!");
    console.log("========================================");
    console.log(`颜色样式: ${colorResult.successCount} 个`);
    console.log(`文本样式: ${textResult.successCount} 个`);
    console.log("按钮组件: 5 种类型");
    console.log("PriceCell 组件: 3 种变体");
    console.log("");
    console.log("请检查左侧面板:");
    console.log("- Assets → Local styles → 查看样式");
    console.log("- Layers → 查看组件");
    console.log("");

    // 显示完成通知
    figma.notify("✅ MyStocks 组件创建完成! 请查看左侧面板。", { timeout: 5000 });

  } catch (error) {
    console.error("❌ 脚本执行失败:", error);
    figma.notify("❌ 脚本执行失败，请查看控制台错误信息", { error: true });
  }

  // 关闭插件 (可选 - 如果想查看结果请注释掉此行)
  // figma.closePlugin();
}

// 执行主函数
main();
