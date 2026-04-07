# PWA Icons Setup

> **参考指南说明**:
> 本文件用于提供 Web 子系统的使用方法、操作指引、接口接入说明、排障提示或结构参考，帮助理解局部实现与协作方式。
> 其中的步骤、示例、端口、目录和操作建议应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为仓库共享规则或当前状态的唯一事实来源。


## Required Icon Sizes

The following icon files need to be created with MyStocks branding:

### Core Icons (Required)
- `icon-192.png` (192x192px) - Primary app icon
- `icon-512.png` (512x512px) - High-res app icon
- `icon-72.png` (72x72px) - Small icon
- `icon-96.png` (96x96px) - Medium icon
- `icon-128.png` (128x128px) - Large icon
- `icon-144.png` (144x144px) - iOS icon

### Shortcut Icons (Optional)
- `shortcut-dashboard.png` (96x96px) - Dashboard shortcut
- `shortcut-market.png` (96x96px) - Market shortcut
- `shortcut-trading.png` (96x96px) - Trading shortcut

## Icon Specifications

### Design Requirements
- **Background**: Obsidian black (#0A0A0A)
- **Accent**: Metallic gold (#D4AF37)
- **Style**: ArtDeco geometric patterns
- **Format**: PNG with transparency
- **Safe Zone**: 80% of icon area for important elements

### Icon Content
- **Primary Icon**: "MS" monogram with ArtDeco border
- **Shortcut Icons**: Relevant symbols (📊 for dashboard, 📈 for market, 💼 for trading)

## Generation Command

To generate proper icons, run:
```bash
# Using a design tool or icon generator
# Example with ImageMagick (if available):
# convert -size 192x192 xc:"#0A0A0A" \
#         -fill "#D4AF37" -pointsize 72 -gravity center \
#         -annotate +0+0 "MS" \
#         -bordercolor "#D4AF37" -border 4 \
#         icon-192.png
```

## Placeholder Files

For now, placeholder files are created. Replace with actual PNG icons before production deployment.