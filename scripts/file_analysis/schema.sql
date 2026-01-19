-- 文件分析系统数据库表结构
-- 创建时间: 2026-01-18
-- 用途: 存储项目中所有代码文件的分析信息

-- 删除已存在的表（按依赖顺序）
DROP TABLE IF EXISTS file_references CASCADE;
DROP TABLE IF EXISTS file_metadata CASCADE;
DROP TABLE IF EXISTS file_categories CASCADE;
DROP TABLE IF EXISTS analysis_runs CASCADE;

-- 1. 分析运行记录表
CREATE TABLE analysis_runs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(36) UNIQUE NOT NULL,
    start_time TIMESTAMP NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'running', -- running, completed, failed
    total_files INTEGER DEFAULT 0,
    python_files INTEGER DEFAULT 0,
    typescript_files INTEGER DEFAULT 0,
    javascript_files INTEGER DEFAULT 0,
    vue_files INTEGER DEFAULT 0,
    html_files INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. 文件分类表
CREATE TABLE file_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES file_categories(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 插入默认分类
INSERT INTO file_categories (category_name, category_code, description) VALUES
('Python后端', 'py_backend', 'Python后端服务文件'),
('Python测试', 'py_test', 'Python测试文件'),
('Python脚本', 'py_script', 'Python工具脚本'),
('Python核心', 'py_core', 'Python核心模块'),
('TypeScript前端', 'ts_frontend', 'TypeScript前端文件'),
('JavaScript工具', 'js_utility', 'JavaScript工具文件'),
('Vue组件', 'vue_component', 'Vue组件文件'),
('HTML页面', 'html_page', 'HTML页面文件'),
('配置文件', 'config', '配置相关文件'),
('文档文件', 'doc', '文档文件'),
('其他文件', 'other', '其他类型文件');

-- 3. 文件元数据表
CREATE TABLE file_metadata (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES analysis_runs(run_id),
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(20) NOT NULL, -- python, typescript, javascript, vue, html, other
    file_size BIGINT,
    line_count INTEGER,
    function_count INTEGER DEFAULT 0,
    class_count INTEGER DEFAULT 0,
    category_id INTEGER REFERENCES file_categories(id),
    file_function TEXT, -- 文件功能描述
    description TEXT, -- 详细描述
    module_name VARCHAR(255), -- 模块名（Python）
    package_name VARCHAR(255), -- 包名（Python）
    imports_count INTEGER DEFAULT 0,
    exports_count INTEGER DEFAULT 0,
    references_in_count INTEGER DEFAULT 0, -- 被引用次数
    references_out_count INTEGER DEFAULT 0, -- 引用次数
    complexity_score INTEGER DEFAULT 0, -- 复杂度评分
    quality_score INTEGER DEFAULT 0, -- 质量评分
    has_tests BOOLEAN DEFAULT FALSE,
    is_entry_point BOOLEAN DEFAULT FALSE,
    last_modified TIMESTAMP,
    file_created TIMESTAMP,
    analyzed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(run_id, file_path)
);

-- 4. 文件引用关系表
CREATE TABLE file_references (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES analysis_runs(run_id),
    source_file_id INTEGER NOT NULL REFERENCES file_metadata(id),
    target_file_id INTEGER NOT NULL REFERENCES file_metadata(id),
    reference_type VARCHAR(50) NOT NULL, -- import, require, export, extends, implements, etc.
    reference_line INTEGER,
    reference_code TEXT,
    is_external BOOLEAN DEFAULT FALSE,
    is_valid BOOLEAN DEFAULT TRUE, -- 引用是否有效
    validation_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 创建索引以提升查询性能
CREATE INDEX idx_file_metadata_run_id ON file_metadata(run_id);
CREATE INDEX idx_file_metadata_file_type ON file_metadata(file_type);
CREATE INDEX idx_file_metadata_category_id ON file_metadata(category_id);
CREATE INDEX idx_file_metadata_file_name ON file_metadata(file_name);
CREATE INDEX idx_file_metadata_file_path ON file_metadata(file_path);

CREATE INDEX idx_file_references_run_id ON file_references(run_id);
CREATE INDEX idx_file_references_source_file_id ON file_references(source_file_id);
CREATE INDEX idx_file_references_target_file_id ON file_references(target_file_id);
CREATE INDEX idx_file_references_reference_type ON file_references(reference_type);

CREATE INDEX idx_analysis_runs_status ON analysis_runs(status);
CREATE INDEX idx_analysis_runs_start_time ON analysis_runs(start_time);

-- 创建视图：文件统计概览
CREATE VIEW file_statistics AS
SELECT
    fm.category_id,
    fc.category_name,
    fm.file_type,
    COUNT(*) as file_count,
    SUM(fm.line_count) as total_lines,
    SUM(fm.function_count) as total_functions,
    SUM(fm.class_count) as total_classes,
    AVG(fm.complexity_score) as avg_complexity,
    AVG(fm.quality_score) as avg_quality,
    SUM(fm.references_in_count) as total_references_in,
    SUM(fm.references_out_count) as total_references_out
FROM file_metadata fm
LEFT JOIN file_categories fc ON fm.category_id = fc.id
GROUP BY fm.category_id, fc.category_name, fm.file_type
ORDER BY fc.category_name, fm.file_type;

-- 创建视图：引用关系概览
CREATE VIEW reference_summary AS
SELECT
    source.file_name as source_file,
    source.file_path as source_path,
    target.file_name as target_file,
    target.file_path as target_path,
    fr.reference_type,
    fr.is_valid,
    COUNT(*) as reference_count
FROM file_references fr
JOIN file_metadata source ON fr.source_file_id = source.id
JOIN file_metadata target ON fr.target_file_id = target.id
GROUP BY source.file_name, source.file_path, target.file_name, target.file_path, fr.reference_type, fr.is_valid
ORDER BY source.file_name, reference_count DESC;

-- 创建触发器：自动更新时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_analysis_runs_updated_at BEFORE UPDATE ON analysis_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_file_metadata_updated_at BEFORE UPDATE ON file_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_file_categories_updated_at BEFORE UPDATE ON file_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加注释
COMMENT ON TABLE analysis_runs IS '文件分析运行记录表';
COMMENT ON TABLE file_categories IS '文件分类表';
COMMENT ON TABLE file_metadata IS '文件元数据表';
COMMENT ON TABLE file_references IS '文件引用关系表';
COMMENT ON VIEW file_statistics IS '文件统计概览视图';
COMMENT ON VIEW reference_summary IS '引用关系概览视图';