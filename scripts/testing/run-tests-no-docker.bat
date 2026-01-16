@echo off
:: MyStocks 无Docker E2E测试启动脚本 (Windows版本)
:: 为Vue 3 + FastAPI架构优化的端到端测试执行器
::
:: 功能:
:: 1. 环境检查和准备
:: 2. 依赖安装验证
:: 3. 测试服务启动管理
:: 4. E2E测试执行
:: 5. 结果报告生成
::
:: 作者: Claude Code
:: 生成时间: 2025-11-14

setlocal enabledelayedexpansion

:: 脚本配置
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..\..
set LOG_DIR=%PROJECT_ROOT%\test-results\logs
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=%LOG_DIR%\test_execution_%TIMESTAMP%.log

:: 配置参数
set SKIP_ENV_CHECK=false
set SKIP_DEPENDENCIES=false
set SKIP_FRONTEND_INSTALL=false
set SKIP_BACKEND_INSTALL=false
set SKIP_PLAYWRIGHT_INSTALL=false
set SKIP_FRONTEND_SERVER=false
set SKIP_BACKEND_SERVER=false
set PARALLEL_WORKERS=1
set BROWSERS=chromium
set TEST_PATTERN=
set HEADLESS=true
set VERBOSE=false
set GENERATE_REPORT=true
set CLEANUP=true

:: 创建日志目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: 日志函数
call :log_info "MyStocks 无Docker E2E测试启动 (Windows)"
call :log_info "项目根目录: %PROJECT_ROOT%"
call :log_info "日志文件: %LOG_FILE%"
echo.

:: 解析命令行参数
call :parse_args %*

:: 显示启动信息
call :show_startup_info

:: 主执行流程
call :main

goto :eof

:: 日志函数
:log
set timestamp=%date% %time%
echo [%timestamp%] [%~1] %~2 >> "%LOG_FILE%"
goto :eof

:log_info
call :log "INFO" "%~1"
echo %~1
goto :eof

:log_success
call :log "SUCCESS" "%~1"
echo %~1
goto :eof

:log_warning
call :log "WARNING" "%~1"
echo %~1
goto :eof

:log_error
call :log "ERROR" "%~1"
echo %~1
goto :eof

:: 解析命令行参数
:parse_args
if "%~1"=="" goto :eof

if "%~1"=="--skip-env-check" (
    set SKIP_ENV_CHECK=true
    shift
    goto :parse_args
)

if "%~1"=="--skip-dependencies" (
    set SKIP_DEPENDENCIES=true
    shift
    goto :parse_args
)

if "%~1"=="--skip-frontend-install" (
    set SKIP_FRONTEND_INSTALL=true
    shift
    goto :parse_args
)

if "%~1"=="--skip-backend-install" (
    set SKIP_BACKEND_INSTALL=true
    shift
    goto :parse_args
)

if "%~1"=="--skip-playwright-install" (
    set SKIP_PLAYWRIGHT_INSTALL=true
    shift
    goto :parse_args
)

if "%~1"=="--skip-frontend-server" (
    set SKIP_FRONTEND_SERVER=true
    shift
    goto :parse_args
)

if "%~1"=="--skip-backend-server" (
    set SKIP_BACKEND_SERVER=true
    shift
    goto :parse_args
)

if "%~1"=="--workers" (
    set PARALLEL_WORKERS=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--browsers" (
    set BROWSERS=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--pattern" (
    set TEST_PATTERN=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--headed" (
    set HEADLESS=false
    shift
    goto :parse_args
)

if "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto :parse_args
)

if "%~1"=="--no-report" (
    set GENERATE_REPORT=false
    shift
    goto :parse_args
)

if "%~1"=="--no-cleanup" (
    set CLEANUP=false
    shift
    goto :parse_args
)

if "%~1"=="--help" goto :show_help
if "%~1"=="-h" goto :show_help

echo 未知参数: %~1
call :show_help
exit /b 1

:: 显示帮助信息
:show_help
echo MyStocks 无Docker E2E测试启动脚本
echo.
echo 用法: %0 [选项]
echo.
echo 环境控制选项:
echo   --skip-env-check           跳过环境检查
echo   --skip-dependencies        跳过依赖安装检查
echo   --skip-frontend-install    跳过前端依赖安装
echo   --skip-backend-install     跳过后端依赖安装
echo   --skip-playwright-install  跳过Playwright浏览器安装
echo.
echo 服务控制选项:
echo   --skip-frontend-server     跳过前端服务器启动
echo   --skip-backend-server      跳过后端服务器启动
echo.
echo 测试执行选项:
echo   --workers NUM              并行工作进程数 (默认: 1)
echo   --browsers BROWSERS        浏览器列表，用逗号分隔 (默认: chromium)
echo                              可选值: chromium,firefox,webkit
echo   --pattern PATTERN          测试文件匹配模式 (默认: 所有测试)
echo   --headed                   非无头模式运行测试
echo   --verbose                  显示详细输出
echo   --no-report                不生成测试报告
echo   --no-cleanup               测试完成后不清理进程
echo.
echo 帮助选项:
echo   --help, -h                 显示此帮助信息
echo.
echo 示例:
echo   %0                                    # 运行所有测试
echo   %0 --pattern auth.spec.ts            # 只运行认证测试
echo   %0 --workers 3 --browsers chromium,firefox  # 多进程多浏览器测试
echo   %0 --headed --verbose                # 可视化调试模式
echo.
exit /b 0

:: 显示启动信息
:show_startup_info
call :log_info "启动参数:"
call :log_info "  跳过环境检查: %SKIP_ENV_CHECK%"
call :log_info "  跳过依赖安装: %SKIP_DEPENDENCIES%"
call :log_info "  跳过前端安装: %SKIP_FRONTEND_INSTALL%"
call :log_info "  跳过后端安装: %SKIP_BACKEND_INSTALL%"
call :log_info "  跳过Playwright安装: %SKIP_PLAYWRIGHT_INSTALL%"
call :log_info "  跳过前端服务器: %SKIP_FRONTEND_SERVER%"
call :log_info "  跳过后端服务器: %SKIP_BACKEND_SERVER%"
call :log_info "  并行进程数: %PARALLEL_WORKERS%"
call :log_info "  浏览器: %BROWSERS%"
if "%TEST_PATTERN%"=="" (
    call :log_info "  测试模式: 所有测试"
) else (
    call :log_info "  测试模式: %TEST_PATTERN%"
)
call :log_info "  无头模式: %HEADLESS%"
call :log_info "  详细输出: %VERBOSE%"
call :log_info "  生成报告: %GENERATE_REPORT%"
call :log_info "  清理进程: %CLEANUP%"
echo.
goto :eof

:: 检查系统要求
:check_system_requirements
call :log_info "检查系统要求..."

:: 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Node.js 未安装"
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
call :log_success "Node.js: !NODE_VERSION!"

:: 检查npm
npm --version >nul 2>&1
if errorlevel 1 (
    call :log_error "npm 未安装"
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
call :log_success "npm: !NPM_VERSION!"

:: 检查Python3
python --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Python 未安装"
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
call :log_success "!PYTHON_VERSION!"

:: 检查pip
pip --version >nul 2>&1
if errorlevel 1 (
    call :log_error "pip 未安装"
    exit /b 1
)

exit /b 0

:: 安装前端依赖
:install_frontend_dependencies
if "%SKIP_FRONTEND_INSTALL%"=="true" (
    call :log_info "跳过前端依赖安装"
    exit /b 0
)

call :log_info "安装前端依赖..."

set "frontend_dir=%PROJECT_ROOT%\web\frontend"

if not exist "!frontend_dir!" (
    call :log_error "前端目录不存在: !frontend_dir!"
    exit /b 1
)

pushd "!frontend_dir!"

if not exist "package.json" (
    call :log_error "package.json 文件不存在"
    popd
    exit /b 1
)

:: 安装依赖
call :log_info "执行 npm install..."
npm install --silent
if errorlevel 1 (
    call :log_error "前端依赖安装失败"
    popd
    exit /b 1
)

popd
call :log_success "前端依赖安装完成"
exit /b 0

:: 安装后端依赖
:install_backend_dependencies
if "%SKIP_BACKEND_INSTALL%"=="true" (
    call :log_info "跳过后端依赖安装"
    exit /b 0
)

call :log_info "安装后端依赖..."

set "backend_dir=%PROJECT_ROOT%\web\backend"

if not exist "!backend_dir!" (
    call :log_error "后端目录不存在: !backend_dir!"
    exit /b 1
)

pushd "!backend_dir!"

if not exist "requirements.txt" (
    call :log_error "requirements.txt 文件不存在"
    popd
    exit /b 1
)

:: 安装依赖
call :log_info "执行 pip install -r requirements.txt..."
pip install -r requirements.txt --quiet
if errorlevel 1 (
    call :log_error "后端依赖安装失败"
    popd
    exit /b 1
)

popd
call :log_success "后端依赖安装完成"
exit /b 0

:: 安装Playwright浏览器
:install_playwright_browsers
if "%SKIP_PLAYWRIGHT_INSTALL%"=="true" (
    call :log_info "跳过Playwright浏览器安装"
    exit /b 0
)

call :log_info "安装Playwright浏览器..."

pushd "%PROJECT_ROOT%"

:: 安装Playwright浏览器
call :log_info "安装Playwright浏览器: %BROWSERS%"
npx playwright install %BROWSERS% --with-deps
if errorlevel 1 (
    call :log_error "Playwright浏览器安装失败"
    popd
    exit /b 1
)

popd
call :log_success "Playwright浏览器安装完成"
exit /b 0

:: 启动前端服务器
:start_frontend_server
if "%SKIP_FRONTEND_SERVER%"=="true" (
    call :log_info "跳过前端服务器启动"
    exit /b 0
)

call :log_info "启动前端开发服务器..."

set "frontend_dir=%PROJECT_ROOT%\web\frontend"

if not exist "!frontend_dir!" (
    call :log_error "前端目录不存在"
    exit /b 1
)

:: 检查端口
netstat -an | find "0.0.0.0:5173" | find "LISTENING" >nul
if not errorlevel 1 (
    call :log_error "前端端口 5173 被占用，无法启动前端服务器"
    exit /b 1
) else (
    call :log_success "前端端口 5173 可用"
)

pushd "!frontend_dir!"

:: 启动开发服务器
set NODE_ENV=test
set PLAYWRIGHT_BASE_URL=http://localhost:5173

start /B npm run dev > "%LOG_DIR%\frontend_%TIMESTAMP%.log" 2>&1

:: 等待服务器启动
call :log_info "等待前端服务器启动..."
for /l %%i in (1,1,30) do (
    curl -s http://localhost:5173 >nul 2>&1
    if not errorlevel 1 (
        call :log_success "前端服务器启动成功"
        popd
        exit /b 0
    )
    timeout /t 2 >nul
)

call :log_error "前端服务器启动超时"
popd
exit /b 1

:: 启动后端服务器
:start_backend_server
if "%SKIP_BACKEND_SERVER%"=="true" (
    call :log_info "跳过后端服务器启动"
    exit /b 0
)

call :log_info "启动后端API服务器..."

set "backend_dir=%PROJECT_ROOT%\web\backend"

if not exist "!backend_dir!" (
    call :log_error "后端目录不存在"
    exit /b 1
)

:: 检查端口
netstat -an | find "0.0.0.0:8000" | find "LISTENING" >nul
if not errorlevel 1 (
    call :log_error "后端端口 8000 被占用，无法启动后端服务器"
    exit /b 1
) else (
    call :log_success "后端端口 8000 可用"
)

pushd "!backend_dir!"

:: 启动API服务器
set TESTING=1
set USE_MOCK_DATA=1
set PLAYWRIGHT_API_URL=http://localhost:8000

start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "%LOG_DIR%\backend_%TIMESTAMP%.log" 2>&1

:: 等待服务器启动
call :log_info "等待后端服务器启动..."
for /l %%i in (1,1,30) do (
    curl -s http://localhost:8000/docs >nul 2>&1
    if not errorlevel 1 (
        call :log_success "后端服务器启动成功"
        popd
        exit /b 0
    )
    timeout /t 2 >nul
)

call :log_error "后端服务器启动超时"
popd
exit /b 1

:: 停止测试服务器
:stop_test_servers
if "%CLEANUP%"=="false" (
    call :log_info "跳过服务器清理"
    exit /b 0
)

call :log_info "停止测试服务器..."

taskkill /f /im node.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1

call :log_success "测试服务器已停止"
exit /b 0

:: 运行E2E测试
:run_e2e_tests
call :log_info "开始运行E2E测试..."

pushd "%PROJECT_ROOT%"

:: 创建测试结果目录
if not exist "test-results\screenshots" mkdir "test-results\screenshots"
if not exist "test-results\videos" mkdir "test-results\videos"
if not exist "test-results\traces" mkdir "test-results\traces"
if not exist "test-results\reports" mkdir "test-results\reports"

:: 设置环境变量
if "%PLAYWRIGHT_BASE_URL%"=="" set PLAYWRIGHT_BASE_URL=http://localhost:5173
if "%PLAYWRIGHT_API_URL%"=="" set PLAYWRIGHT_API_URL=http://localhost:8000
if "%PLAYWRIGHT_TIMEOUT%"=="" set PLAYWRIGHT_TIMEOUT=30000

:: 构建测试命令
set test_cmd=npx playwright test

if not "%TEST_PATTERN%"=="" (
    set test_cmd=!test_cmd! %TEST_PATTERN%
) else (
    set test_cmd=!test_cmd! tests/e2e/specs/
)

set test_cmd=!test_cmd! --workers=%PARALLEL_WORKERS%
set test_cmd=!test_cmd! --project=%BROWSERS%
set test_cmd=!test_cmd! --output=test-results
set test_cmd=!test_cmd! --reporter=html,json,junit

if "%HEADLESS%"=="false" (
    set test_cmd=!test_cmd! --headed
)

if "%VERBOSE%"=="true" (
    set test_cmd=!test_cmd! --verbose
)

call :log_info "执行测试命令: !test_cmd!"

:: 执行测试
!test_cmd!
if errorlevel 1 (
    call :log_error "E2E测试执行失败"
    popd
    exit /b 1
)

popd
call :log_success "E2E测试执行成功"
exit /b 0

:: 生成测试报告
:generate_test_report
if "%GENERATE_REPORT%"=="false" (
    call :log_info "跳过测试报告生成"
    exit /b 0
)

call :log_info "生成测试报告..."

set "report_dir=%PROJECT_ROOT%\test-results\reports"
set "report_file=%report_dir%\test_execution_report_%TIMESTAMP%.md"

if not exist "%report_dir%" mkdir "%report_dir%"

:: 创建Markdown报告
(
echo # E2E测试执行报告
echo.
echo **生成时间**: %date% %time%
echo **项目**: MyStocks
echo **执行模式**: 无Docker测试环境
echo.
echo ## 测试配置
echo.
echo - **并行进程数**: %PARALLEL_WORKERS%
echo - **浏览器**: %BROWSERS%
if "%TEST_PATTERN%"=="" (
    echo - **测试模式**: 所有测试
) else (
    echo - **测试模式**: %TEST_PATTERN%
)
echo - **无头模式**: %HEADLESS%
echo - **详细输出**: %VERBOSE%
echo.
echo ## 环境信息
echo.
echo - **前端URL**: %PLAYWRIGHT_BASE_URL%
echo - **后端URL**: %PLAYWRIGHT_API_URL%
echo - **超时设置**: %PLAYWRIGHT_TIMEOUT%ms
echo.
echo ## 文件输出
echo.
echo - **截图目录**: test-results/screenshots/
echo - **视频目录**: test-results/videos/
echo - **追踪目录**: test-results/traces/
echo - **HTML报告**: test-results/index.html
echo - **JSON报告**: test-results/results.json
echo - **JUnit报告**: test-results/junit.xml
echo.
echo ## 执行日志
echo.
echo 详细执行日志请查看: %LOG_FILE%
) > "%report_file%"

call :log_success "测试报告已生成: %report_file"

:: 如果HTML报告存在，显示路径
if exist "%PROJECT_ROOT%\test-results\index.html" (
    call :log_info "HTML测试报告: %PROJECT_ROOT%\test-results\index.html"
)

exit /b 0

:: 主函数
:main
set start_time=%time%

call :log_info "=== 步骤 1: 环境检查 ==="
if "%SKIP_ENV_CHECK%"=="true" (
    call :log_info "跳过环境检查"
) else (
    call :check_system_requirements
    if errorlevel 1 exit /b 1
)
echo.

call :log_info "=== 步骤 2: 依赖安装 ==="
if "%SKIP_DEPENDENCIES%"=="true" (
    call :log_info "跳过依赖安装"
) else (
    call :install_frontend_dependencies
    if errorlevel 1 exit /b 1

    call :install_backend_dependencies
    if errorlevel 1 exit /b 1

    call :install_playwright_browsers
    if errorlevel 1 exit /b 1
)
echo.

call :log_info "=== 步骤 3: 启动测试服务 ==="
call :start_frontend_server
if errorlevel 1 exit /b 1

call :start_backend_server
if errorlevel 1 exit /b 1
echo.

call :log_info "=== 步骤 4: 等待服务稳定 ==="
timeout /t 5 >nul
echo.

call :log_info "=== 步骤 5: 运行E2E测试 ==="
call :run_e2e_tests
set test_success=!errorlevel!
echo.

call :log_info "=== 步骤 6: 生成测试报告 ==="
call :generate_test_report
echo.

call :log_info "=== 执行完成 ==="
call :log_success "测试执行完成"

:: 返回适当的退出码
if %test_success% equ 0 (
    call :log_success "测试执行成功"
    exit /b 0
) else (
    call :log_error "测试执行失败"
    exit /b 1
)
