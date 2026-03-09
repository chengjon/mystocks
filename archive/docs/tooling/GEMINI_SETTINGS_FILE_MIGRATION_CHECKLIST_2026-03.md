# GEMINI 设置相关文件迁移清单

> 说明：该文档保留为一次性迁移记录，已自仓库根目录归档到 `archive/docs/tooling/`。

## 1. 结果说明
- 根目录：`/opt/mydoc/cliproxyapi/gemini`
- `.gemini` 目标目录：`/opt/mydoc/cliproxyapi/gemini/.gemini`
- 脚本目标子目录：`/opt/mydoc/cliproxyapi/gemini/scripts`
- 本次自动迁移尝试失败（权限限制）：
  - `mkdir: cannot create directory '/opt/mydoc/cliproxyapi/gemini/.gemini': Permission denied`
  - `mkdir: cannot create directory '/opt/mydoc/cliproxyapi/gemini/scripts/gemini_proxy_regression': Permission denied`

## 2. 需迁移文件（源 -> 目标）
1. `/opt/claude/mystocks_spec/.gemini/.env`  
   -> `/opt/mydoc/cliproxyapi/gemini/.gemini/.env`
2. `/opt/claude/mystocks_spec/.gemini/settings.json`  
   -> `/opt/mydoc/cliproxyapi/gemini/.gemini/settings.json`
3. `/opt/claude/mystocks_spec/.gemini/GEMINI.md`  
   -> `/opt/mydoc/cliproxyapi/gemini/.gemini/GEMINI.md`
4. `/opt/claude/mystocks_spec/.gemini/policies/tool-guard.toml`  
   -> `/opt/mydoc/cliproxyapi/gemini/.gemini/policies/tool-guard.toml`
5. `/opt/claude/mystocks_spec/scripts/gemini_clean_start.sh`  
   -> `/opt/mydoc/cliproxyapi/gemini/scripts/gemini_clean_start.sh`
6. `/opt/claude/mystocks_spec/scripts/gemini_proxy_regression/01_single_tool_roundtrip.sh`  
   -> `/opt/mydoc/cliproxyapi/gemini/scripts/gemini_proxy_regression/01_single_tool_roundtrip.sh`
7. `/opt/claude/mystocks_spec/scripts/gemini_proxy_regression/02_empty_function_name_guard.sh`  
   -> `/opt/mydoc/cliproxyapi/gemini/scripts/gemini_proxy_regression/02_empty_function_name_guard.sh`
8. `/opt/claude/mystocks_spec/scripts/gemini_proxy_regression/03_two_tool_serial_roundtrip.sh`  
   -> `/opt/mydoc/cliproxyapi/gemini/scripts/gemini_proxy_regression/03_two_tool_serial_roundtrip.sh`
9. `/opt/claude/mystocks_spec/scripts/gemini_proxy_regression/04_stream_vs_nonstream_consistency.sh`  
   -> `/opt/mydoc/cliproxyapi/gemini/scripts/gemini_proxy_regression/04_stream_vs_nonstream_consistency.sh`
10. `/opt/claude/mystocks_spec/Gemini代理配置成功经验与固化指南.updated.md`  
    -> `/opt/mydoc/cliproxyapi/gemini/scripts/Gemini代理配置成功经验与固化指南.updated.md`

## 3. 目标目录 tree 结构
```text
/opt/mydoc/cliproxyapi/gemini
├── .gemini
│   ├── .env
│   ├── GEMINI.md
│   ├── settings.json
│   └── policies
│       └── tool-guard.toml
├── docs
│   └── ...（现有文档）
└── scripts
    ├── gemini_clean_start.sh
    ├── gemini_proxy_regression
    │   ├── 01_single_tool_roundtrip.sh
    │   ├── 02_empty_function_name_guard.sh
    │   ├── 03_two_tool_serial_roundtrip.sh
    │   └── 04_stream_vs_nonstream_consistency.sh
    └── Gemini代理配置成功经验与固化指南.updated.md
```

## 4. 手动迁移命令（可直接执行）
```bash
mkdir -p /opt/mydoc/cliproxyapi/gemini/.gemini/policies
mkdir -p /opt/mydoc/cliproxyapi/gemini/scripts/gemini_proxy_regression

cp -f /opt/claude/mystocks_spec/.gemini/.env \
  /opt/mydoc/cliproxyapi/gemini/.gemini/.env
cp -f /opt/claude/mystocks_spec/.gemini/settings.json \
  /opt/mydoc/cliproxyapi/gemini/.gemini/settings.json
cp -f /opt/claude/mystocks_spec/.gemini/GEMINI.md \
  /opt/mydoc/cliproxyapi/gemini/.gemini/GEMINI.md
cp -f /opt/claude/mystocks_spec/.gemini/policies/tool-guard.toml \
  /opt/mydoc/cliproxyapi/gemini/.gemini/policies/tool-guard.toml

cp -f /opt/claude/mystocks_spec/scripts/gemini_clean_start.sh \
  /opt/mydoc/cliproxyapi/gemini/scripts/gemini_clean_start.sh
cp -f /opt/claude/mystocks_spec/scripts/gemini_proxy_regression/*.sh \
  /opt/mydoc/cliproxyapi/gemini/scripts/gemini_proxy_regression/

cp -f /opt/claude/mystocks_spec/Gemini代理配置成功经验与固化指南.updated.md \
  /opt/mydoc/cliproxyapi/gemini/scripts/Gemini代理配置成功经验与固化指南.updated.md
```

## 5. 迁移后验证
```bash
find /opt/mydoc/cliproxyapi/gemini -maxdepth 5 -type f | sort
```
