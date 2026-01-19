-- 迁移脚本：添加CSS和JSON文件统计列
-- 创建时间: 2026-01-19
-- 用途：为analysis_runs表添加css_files和json_files列

-- 添加CSS文件统计列
ALTER TABLE analysis_runs ADD COLUMN IF NOT EXISTS css_files INTEGER DEFAULT 0;

-- 添加JSON文件统计列
ALTER TABLE analysis_runs ADD COLUMN IF NOT EXISTS json_files INTEGER DEFAULT 0;

-- 添加注释
COMMENT ON COLUMN analysis_runs.css_files IS 'CSS文件数量';
COMMENT ON COLUMN analysis_runs.json_files IS 'JSON文件数量';

-- 验证列是否添加成功
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'analysis_runs'
  AND column_name IN ('css_files', 'json_files');