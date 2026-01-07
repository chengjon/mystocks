作为量化管理系统的开发人员，你已具备完整的技术底座（Web 页面、209 个 API、API 契约管理、指标体系、数据库、Playwright 等工具链），当前核心目标是标准化 API 契约与路由、实现 209 个 API 全量功能测试、打通 Web 端与真实 API 数据。以下是结合你现有环境的分步实施方案，充分发挥 PM2+tmux+lnav+Playwright 的优势，兼顾效率与稳定性：
一、 第一步：梳理路由 + 标准化 API 契约，建立统一 API 目录（基础支撑）
API 契约与路由的混乱是后续测试和联调的最大障碍，先完成这一步，为后续打通数据和测试奠定基础，核心是「批量梳理 + 标准化定义 + 自动注册 + 可视化目录」。
1. 批量梳理web/backend/app/api/路由模块，按业务分层归类
先按量化系统的业务属性，对 API 路由进行模块化拆分（与 Web 页面功能模块一一对应），避免零散无序，同时统计 209 个 API 的分布情况，确保无遗漏。
（1） 路由梳理规则（贴合量化业务）
业务模块	路由目录示例	API 功能范围（示例）	接口数量预估
行情数据模块	api/market/	K 线查询、实时价格、标的列表、指标原始数据	40+
策略管理模块	api/strategy/	策略 CRUD、参数配置、回测触发、回测结果查询	50+
交易委托模块	api/trade/	限价 / 市价委托、撤单、委托列表、仓位查询	30+
用户账户模块	api/user/	账号信息、资产查询、交易历史、权限验证	25+
指标管理模块	api/indicator/	指标配置、自定义指标、指标计算结果查询	35+
系统配置模块	api/system/	全局设置、日志查询、版本信息、缓存清理	29+
合计	-	209 个 API	209
（2） 实操方法：批量扫描路由（减少手动工作量）
根据你的后端框架（如 Python-Flask/Django、Node.js-Express），编写简易脚本（Python/Shell）扫描api/目录下的所有路由文件，自动提取「路由路径、请求方式、接口名称」，生成初始路由清单，再手动补充业务模块归类。
示例（Python-Flask 路由扫描脚本，可按需调整）：
python
运行
# scan_routes.py
import os
import importlib.util

# 路由存放根目录
API_ROOT_DIR = "web/backend/app/api"
# 存储路由清单
route_list = []

# 递归扫描所有.py路由文件
for root, dirs, files in os.walk(API_ROOT_DIR):
    for file in files:
        if file.endswith(".py") and not file.startswith("__"):
            file_path = os.path.join(root, file)
            # 导入模块
            spec = importlib.util.spec_from_file_location("route_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # 提取Flask路由（假设使用Blueprint注册路由）
            if hasattr(module, "bp"):
                for rule in module.bp.url_map.iter_rules():
                    # 排除静态路由
                    if "static" not in rule.rule:
                        route_info = {
                            "path": rule.rule,
                            "methods": list(rule.methods - {"OPTIONS", "HEAD"}),
                            "file_path": file_path,
                            "module": os.path.relpath(root, API_ROOT_DIR)
                        }
                        route_list.append(route_info)

# 导出路由清单到CSV（便于后续整理）
import csv
with open("api_route_list.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["path", "methods", "module", "file_path"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(route_list)

print(f"已扫描到 {len(route_list)} 个API路由，导出至 api_route_list.csv")
2. API 契约标准化：基于现有契约管理，统一字段定义
你已实现 API 契约管理，现在需要基于量化业务特性，统一契约核心字段，确保 209 个 API 契约格式一致，便于自动化注册和测试。
（1） 量化 API 契约核心字段（必选 + 业务专属）
字段名	类型	说明（贴合量化业务）	示例
api_id	字符串	唯一标识（模块_功能_版本）	market_kline_v1、strategy_backtest_v1
module	字符串	业务模块（与路由梳理一致）	market、strategy、trade
path	字符串	接口路由路径	/api/data/stocks/kline
method	字符串	请求方式（GET/POST/PUT/DELETE）	GET
request_params	数组	请求参数（含量化专属参数：标的、周期、时间范围）	[{name: "symbol", type: "string", required: true, desc: "股票代码/BTC"}]
response_code	字典	响应码（关联你的指标错误码体系）	{200: "成功", 20101: "标的不存在", 10001: "系统异常"}
response_data	结构体	响应数据格式（量化专属：K 线、指标、策略数据）	{kline: [], sma: [], timestamp: []}
contract_version	字符串	契约版本（用于迭代兼容）	v1.0
is_core	布尔值	是否核心 API（P0 优先级，优先测试 / 打通）	True（行情 K 线）、False（系统日志）
（2） 契约对齐：路由与契约一致性校验
利用第一步生成的路由清单，与现有 API 契约进行比对，自动找出不一致项（如路由路径变更、请求方式不匹配、参数缺失），避免契约与实际接口脱节。
实操：编写校验脚本，读取api_route_list.csv和 API 契约注册表（数据库 / JSON 文件），批量比对，生成不一致报告（用 lnav 格式化查看）。
3. API 契约注册与统一目录建立
（1） 自动化契约注册
方式 1：若契约存储在数据库，编写脚本批量导入标准化后的契约（基于路由清单 + 手动补充的业务信息），完成 209 个 API 的自动注册；
方式 2：若使用配置文件（YAML/JSON），在api/目录下为每个模块创建契约文件（如market_contract.yaml），统一存放至api/contracts/目录，形成契约仓库。
（2） 建立可视化 API 目录
基于注册后的契约，搭建简易可视化目录（无需复杂工具，快速落地）：
轻量方案：用 Markdown 生成API目录.md，按业务模块分类展示所有 API 的核心信息（路径、参数、响应格式），便于开发 / 测试查阅；
进阶方案：集成 Swagger/OpenAPI（利用标准化契约自动生成接口文档），支持在线调试 API（直接调用真实接口，验证返回数据），后续可对接 Playwright 测试。
二、 第二步：利用现有工具链，搭建 API 自动化测试体系（先测 API，再测 Web）
量化 Web 端依赖 API 数据，先确保 209 个 API 功能正常，再打通 Web 端，可大幅减少联调问题。充分发挥 PM2+tmux+lnav+Playwright 的优势，无需额外引入第三方 API 测试工具。
1. 工具分工：最大化利用现有配置
工具	核心作用（量化 API 测试场景）	实操要点
PM2	管理后端 API 服务进程，保障测试期间服务稳定	1. 启动 API 服务：pm2 start web/backend/app.py --name mystocks-api；
2. 监控服务状态：pm2 monit；
3. 日志收集：pm2 logs mystocks-api --out api_out.log --err api_err.log（为 lnav 提供日志源）；
4. 自动重启：服务异常时自动重启，避免测试中断。
tmux	分窗口管理多进程，无需切换终端，提升效率	1. 新建会话：tmux new -s mystocks-test；
2. 分窗口布局：
- 窗口 1：PM2 启动 / 监控 API 服务（pm2 monit）；
- 窗口 2：执行 Playwright API 测试用例；
- 窗口 3：lnav 查看聚合日志（API 日志 + 测试日志）；
- 窗口 4：手动调试异常 API（curl/Swagger）；
3. 会话保存：tmux detach（保留会话，后续重新连接：tmux attach -t mystocks-test）。
lnav	聚合 / 格式化 / 分析日志，快速定位 API 问题	1. 加载日志文件：lnav api_out.log api_err.log playwright_test.log；
2. 筛选错误：按级别（ERROR/WARN）筛选，快速定位 API 报错（如数据库查询失败、指标计算错误）；
3. 关联请求：通过requestId（你的 API 响应中已包含）关联请求与日志，排查单个 API 的异常。
Playwright	编写 API 自动化测试用例，复用现有配置	1. 利用 Playwright 内置request功能，无需额外引入pytest-requests；
2. 复用现有 Playwright 项目结构（tests/、utils/），编写 API 测试用例；
3. 与 Web 测试共享测试数据（标的、账号、策略参数），减少冗余。
2. Playwright 编写 API 自动化测试用例（核心实操）
复用你已配置的 Playwright 环境，编写 API 测试用例，优先覆盖 209 个 API 中的 P0 核心接口（行情、策略、交易），确保核心功能可用。
（1） 单个 API 测试示例（量化行情 K 线接口）
python
运行
# tests/test_api_market.py
import pytest
from playwright.sync_api import sync_playwright
from utils.test_data import TEST_SYMBOLS, TEST_TIME_RANGES
from utils.common_func import verify_indicator_value

# 复用Playwright，发起API请求
def test_market_kline_api():
    with sync_playwright() as p:
        # 无需启动浏览器，直接创建API请求上下文
        api_context = p.request.new_context(base_url="http://localhost:8000")  # 你的API服务地址
        symbol = TEST_SYMBOLS["BTC"]
        period = "1d"
        start_ts = TEST_TIME_RANGES["7d"]["start"]
        end_ts = TEST_TIME_RANGES["7d"]["end"]

        # 发起GET请求（量化K线接口）
        response = api_context.get(
            "/api/data/stocks/kline",
            params={
                "symbol": symbol,
                "period": period,
                "start_ts": start_ts,
                "end_ts": end_ts
            }
        )

        # 断言1：接口响应状态码200
        assert response.ok, f"K线API请求失败，状态码：{response.status}"
        response_data = response.json()

        # 断言2：响应数据格式正确（含量化核心字段）
        assert "requestId" in response_data, "响应缺少requestId"
        assert "kline" in response_data, "响应缺少kline数据"
        assert "timestamp" in response_data["kline"][0], "K线缺少时间戳"
        assert all(key in response_data["kline"][0] for key in ["open", "high", "low", "close", "volume"]), "K线字段不完整"

        # 断言3：指标数据正确性（如SMA，关联你的指标管理体系）
        if "sma" in response_data:
            actual_sma = response_data["sma"][-1]  # 最后一个时间点的SMA值
            expected_sma = calculate_expected_sma(response_data["kline"], period)  # 本地计算预期值
            verify_indicator_value(actual_sma, expected_sma)

        # 关闭API上下文
        api_context.dispose()
        print(f"[{symbol}-{period}] K线API测试通过")

# 批量测试多个标的+周期
@pytest.mark.parametrize("symbol,period", [
    (TEST_SYMBOLS["BTC"], "1d"),
    (TEST_SYMBOLS["600036"], "1h"),
    (TEST_SYMBOLS["ETH"], "15m")
])
def test_market_kline_batch_api(symbol, period):
    with sync_playwright() as p:
        api_context = p.request.new_context(base_url="http://localhost:8000")
        response = api_context.get(
            "/api/data/stocks/kline",
            params={"symbol": symbol, "period": period, "start_ts": 1735689600000, "end_ts": 1736294400000}
        )
        assert response.ok, f"[{symbol}-{period}] K线API请求失败"
        api_context.dispose()
（2） 批量执行 API 测试
bash
运行
# 在tmux窗口2中执行
playwright test tests/test_api_* --reporter html:reports/api_test_report.html
# 生成的日志重定向到文件，供lnav分析
playwright test tests/test_api_* > playwright_api_test.log 2>&1
3. API 测试结果分析与问题修复
用 lnav 打开api_err.log和playwright_api_test.log，筛选所有 ERROR 级别的日志；
按模块归类问题（如market模块 API 报错集中在标的不存在，strategy模块报错集中在参数非法）；
优先修复 P0 核心 API 的问题，确保核心功能可用，为后续 Web 端打通提供保障；
修复后重新执行对应 API 测试用例，直至通过。
三、 第三步：Web 端与真实 API 数据打通（替换 MOCK，分步推进）
避免一次性替换所有 MOCK 数据导致问题扎堆，采用「局部试点→数据适配→异常处理→全量切换」的策略，平稳打通 Web 与真实 API。
1. 局部试点：优先打通核心业务模块（最小可用）
选择 1-2 个核心模块（如行情展示模块），先替换该模块的 MOCK 数据为真实 API 请求，验证可行性，降低风险。
（1） 实操步骤
前端修改：在行情页的代码中，注释 MOCK 数据导入，新增真实 API 请求逻辑（使用fetch/axios调用对应的 API 接口，如/api/data/stocks/kline）；
数据映射：因 MOCK 数据与真实 API 响应格式可能不一致，需编写数据适配函数，将 API 返回数据转换为前端组件所需格式（与你的StandardKLine标准结构对齐）；
本地验证：启动 Web 服务（如npm run dev）和 API 服务（PM2 管理），在 Chrome 中访问行情页，验证：
K 线是否正常渲染（时间轴、价格区间是否正确）；
技术指标（SMA/RSI 等）是否正常展示（与 API 返回数据一致）；
标的切换、时间粒度切换功能是否可用。
2. 关键保障：数据适配与异常处理
（1） 数据适配：统一前后端数据格式
基于你已设计的指标管理体系和标准 K 线结构，前端定义统一的数据接口，确保与 API 返回数据无缝对接：
typescript
运行
// 前端 src/types/kline.ts（与后端StandardKLine一致）
export interface StandardKLine {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// 数据适配函数：API返回数据 → 前端组件数据
export function adaptKlineData(apiData: any): StandardKLine[] {
  if (!apiData || !apiData.kline) return [];
  return apiData.kline.map((item: any) => ({
    timestamp: item.timestamp,
    open: Number(item.open),
    high: Number(item.high),
    low: Number(item.low),
    close: Number(item.close),
    volume: Number(item.volume)
  }));
}
（2） 异常处理：避免 Web 页面崩溃
添加 API 请求的异常处理逻辑，覆盖网络错误、接口报错、数据为空等场景：
typescript
运行
// 前端 src/api/marketApi.ts
export async function getKlineData(symbol: string, period: string) {
  try {
    const response = await fetch(`/api/data/stocks/kline?symbol=${symbol}&period=${period}`);
    const data = await response.json();
    // 业务错误码处理（关联你的错误码体系）
    if (data.code !== 10000) {
      ElMessage.error(`获取K线失败：${data.message}`); // Element UI提示
      return { kline: [], sma: [] };
    }
    // 数据适配
    const adaptedKline = adaptKlineData(data);
    return { kline: adaptedKline, sma: data.sma };
  } catch (error) {
    ElMessage.error("网络异常，无法获取K线数据");
    return { kline: [], sma: [] };
  }
}
3. 全量切换：逐步替换所有模块 MOCK 数据
局部试点通过后，按业务模块优先级（P0→P1→P2），逐步替换其他模块的 MOCK 数据，每个模块替换后都进行手动验证和 Playwright 自动化测试，确保功能正常。
切换顺序：行情模块 → 策略管理模块 → 交易委托模块 → 用户账户模块 → 系统配置模块；
验证方式：手动验证核心功能 + Playwright 自动化测试关键场景。
四、 第四步：Web 端功能自动化测试（基于真实 API 数据）
在 API 测试通过、Web 端与真实数据打通后，复用现有 Playwright 配置，编写 Web 功能测试用例，覆盖多页面、多功能，确保 Web 端展示和操作的正确性。
1. 复用现有 Playwright 环境，编写 Web 测试用例
基于你已搭建的 Playwright 测试项目（tests/、utils/），编写 Web 测试用例，与 API 测试共享测试数据（标的、账号、策略参数），减少冗余。
（1） Web 功能测试示例（行情页 K 线展示 + 指标切换）
python
运行
# tests/test_web_market.py
import pytest
from playwright.sync_api import expect
from utils.element_locator import MARKET_ELEMENTS
from utils.test_data import TEST_SYMBOLS
from utils.common_func import login, take_screenshot

def test_web_market_kline_display(page):
    case_name = "test_web_market_kline_display"
    try:
        # Given：访问行情详情页（已自动登录，通过conftest.py夹具）
        target_symbol = TEST_SYMBOLS["BTC"]
        page.goto(f"http://localhost:3000/market/detail/{target_symbol}")
        expect(page.locator(MARKET_ELEMENTS["symbol_search_input"])).to_have_value(target_symbol)

        # When：验证K线容器可见，切换时间粒度
        expect(page.locator(MARKET_ELEMENTS["kline_container"])).to_be_visible(timeout=10000)
        page.locator(MARKET_ELEMENTS["time_granularity_select"]).select_option("1d")
        page.wait_for_selector(f'data-testid="kline-1d"')

        # Then：1. 断言K线渲染成功
        expect(page.locator(MARKET_ELEMENTS["kline_container"])).to_contain_text(target_symbol)
        # Then：2. 断言实时价格展示（与API返回数据一致）
        actual_price = float(page.locator(MARKET_ELEMENTS["real_time_price"]).inner_text())
        # 从API测试的缓存中获取预期价格，或重新调用API获取
        expected_price = get_expected_price_from_api(target_symbol)
        assert abs(actual_price - expected_price) <= 0.01, "实时价格展示异常"

        # Then：3. 断言SMA指标切换成功
        page.locator(MARKET_ELEMENTS["sma_indicator_btn"]).click()
        expect(page.locator(f'data-testid="indicator-SMA"')).to_be_visible()

    except Exception as e:
        take_screenshot(page, case_name)
        raise e
2. 利用 tmux+PM2+lnav 提升 Web 测试效率
tmux 分窗口：窗口 1（PM2 管理 API 服务）、窗口 2（Web 服务）、窗口 3（Playwright Web 测试）、窗口 4（lnav 查看聚合日志）；
日志聚合：lnav 同时加载 API 日志、Web 服务日志、Playwright Web 测试日志，快速定位问题（如 Web 页面展示异常，是 API 数据错误还是前端渲染错误）；
并行执行：Playwright 默认支持并行执行 Web 测试用例，提升全量测试效率。
五、 第五步：持续优化与维护（保障长期稳定性）
契约与路由同步更新：新增 / 修改 API 时，同步更新路由清单、API 契约和 API 目录，避免契约滞后；
测试用例迭代：Web/API 功能迭代时，同步新增 / 修改对应的测试用例，保持测试覆盖率；
工具链复用：将 tmux 会话配置、PM2 启动脚本、lnav 日志筛选规则整理成文档，便于团队复用；
定时执行测试：（可选）利用 crontab+tmux，定时执行全量 API+Web 测试，生成测试报告，及时发现线上问题。
总结
结合你的现有环境，实现 API 契约标准化、全量 API 测试、Web 与真实数据打通的核心要点：
先规范后落地：先梳理路由、标准化 API 契约、建立目录，为后续测试和联调奠定基础；
工具最大化复用：PM2 保障服务稳定，tmux 简化多进程管理，lnav 快速分析日志，Playwright 兼顾 API+Web 测试，无需额外引入第三方工具；
分步推进降风险：先测 API 再测 Web，先局部打通再全量切换，避免问题扎堆；
业务贴合量化特性：所有步骤围绕量化业务（K 线、指标、策略、交易）展开，确保核心功能的正确性和稳定性。
这套方案无需额外增加成本，可直接基于你的现有配置落地，既能完成 209 个 API 的全面测试，又能平稳实现 Web 与真实数据的打通，提升开发和测试效率。
