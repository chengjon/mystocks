#!/usr/bin/env python3
"""
MyStocks前端综合测试脚本
使用Chrome DevTools CDP协议进行全面测试
"""

import json
import asyncio
import websockets
import subprocess
import sys


def get_dashboard_page():
    """获取仪表盘页面的WebSocket URL"""
    curl_output = subprocess.run(["curl", "-s", "http://localhost:9222/json"], capture_output=True, text=True).stdout
    pages = json.loads(curl_output)

    target_page = None
    for p in pages:
        if "/dashboard" in p.get("url", ""):
            target_page = p
            break

    if not target_page:
        print("❌ 未找到仪表盘页面")
        sys.exit(1)

    return target_page


async def test_console_errors(ws):
    """测试1: Console错误和警告"""
    print("\n" + "=" * 80)
    print("【测试1】Console错误和警告")
    print("=" * 80)

    await ws.send(
        json.dumps(
            {
                "id": 10,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """
        (() => {
            const errors = [];
            const warnings = [];
            
            // 获取控制台消息
            const logs = window.__console_logs || [];
            logs.filter(l => l.type === 'error').forEach(l => errors.push(l.message));
            logs.filter(l => l.type === 'warning').forEach(l => warnings.push(l.message));
            
            // 检查Vue运行时错误
            if (window.__vue_errors) {
                errors.push(...window.__vue_errors);
            }
            
            // 检查Service Worker错误
            if (window.__sw_errors) {
                errors.push(...window.__sw_errors);
            }
            
            return { errors, warnings, logCount: logs.length };
        })();
    """,
                    "returnByValue": True,
                },
            }
        )
    )
    response = await ws.recv()
    data = json.loads(response)
    result = data.get("result", {}).get("result", {}).get("value", {})

    errors = result.get("errors", [])
    warnings = result.get("warnings", [])

    print(f"发现错误: {len(errors)} 个")
    for i, e in enumerate(errors[:10], 1):
        print(f"  [{i}] {str(e)[:200]}")

    print(f"\n发现警告: {len(warnings)} 个")
    for i, w in enumerate(warnings[:10], 1):
        print(f"  [{i}] {str(w)[:200]}")

    if not errors and not warnings:
        print("  ✅ 无错误和警告")

    return errors, warnings


async def test_pinia_init(ws):
    """测试2: Pinia初始化和路由守卫"""
    print("\n" + "=" * 80)
    print("【测试2】Pinia初始化和路由守卫")
    print("=" * 80)

    await ws.send(
        json.dumps(
            {
                "id": 20,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """
        (() => {
            const result = {
                piniaExists: false,
                authStoreExists: false,
                routerExists: false,
                piniaVersion: 'N/A',
                stores: [],
                appMounted: false
            };
            
            // 检查Pinia
            if (window.Pinia) {
                result.piniaExists = true;
                result.piniaVersion = window.Pinia.version || 'unknown';
            }
            
            // 检查Vue Router
            if (window.VueRouter || (document.__vue_app__ && document.__vue_app__.config && document.__vue_app__.config.globalProperties.$router)) {
                result.routerExists = true;
            }
            
            // 获取所有Pinia stores
            try {
                const app = document.__vue_app__;
                if (app && app.config && app.config.globalProperties && app.config.globalProperties.$pinia) {
                    const stores = app.config.globalProperties.$pinia.state.value;
                    result.stores = Object.keys(stores);
                }
            } catch (e) {
                result.storesError = e.message;
            }
            
            // 检查app是否挂载
            result.appMounted = !!document.querySelector('[data-v-app]') || !!document.getElementById('app');
            
            return result;
        })();
    """,
                    "returnByValue": True,
                },
            }
        )
    )
    response = await ws.recv()
    data = json.loads(response)
    result = data.get("result", {}).get("result", {}).get("value", {})

    print(f"  Pinia存在: {'✅' if result.get('piniaExists') else '❌'}")
    print(f"  Pinia版本: {result.get('piniaVersion', 'N/A')}")
    print(f"  Router存在: {'✅' if result.get('routerExists') else '❌'}")
    print(f"  App已挂载: {'✅' if result.get('appMounted') else '❌'}")
    print(f"  已注册Stores: {result.get('stores', [])}")

    if not result.get("piniaExists"):
        print("  ❌ Pinia未加载 - 这会导致状态管理失败")

    if not result.get("routerExists"):
        print("  ❌ Vue Router未加载 - 这会导致路由守卫失败")

    return result


async def test_service_worker(ws):
    """测试3: Service Worker缓存逻辑"""
    print("\n" + "=" * 80)
    print("【测试3】Service Worker缓存逻辑")
    print("=" * 80)

    await ws.send(
        json.dumps(
            {
                "id": 30,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """
        (async () => {
            const result = {
                swRegistered: false,
                swVersion: 'N/A',
                cacheNames: [],
                cacheKeys: [],
                swContent: null,
                cleanupLogic: []
            };
            
            // 检查Service Worker注册状态
            if (navigator.serviceWorker && navigator.serviceWorker.controller) {
                result.swRegistered = true;
                result.swVersion = navigator.serviceWorker.controller.scriptURL || 'N/A';
            }
            
            // 检查缓存
            if (window.caches) {
                result.cacheNames = await caches.keys();
                
                for (const name of result.cacheNames) {
                    const cache = await caches.open(name);
                    const keys = await cache.keys();
                    result.cacheKeys.push({ name, count: keys.length });
                }
            }
            
            // 获取Service Worker内容
            try {
                const swResponse = await fetch('/sw.js');
                if (swResponse.ok) {
                    result.swContent = await swResponse.text();
                    
                    // 分析缓存清理逻辑
                    const lines = result.swContent.split('\\n');
                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i];
                        if (line.includes('delete') || line.includes('cleanup') || line.includes('mystocks-v1')) {
                            result.cleanupLogic.push({ line: i + 1, content: line.trim().substring(0, 150) });
                        }
                    }
                }
            } catch (e) {
                result.swError = e.message;
            }
            
            return result;
        })();
    """,
                    "returnByValue": True,
                },
            }
        )
    )
    response = await ws.recv()
    data = json.loads(response)
    result = data.get("result", {}).get("result", {}).get("value", {})

    print(f"  SW已注册: {'✅' if result.get('swRegistered') else '❌'}")
    print(f"  SW版本: {result.get('swVersion', 'N/A')[:80]}...")
    print(f"  缓存列表: {result.get('cacheNames', [])}")

    if result.get("cacheKeys"):
        print(f"  缓存详情:")
        for ck in result.get("cacheKeys", []):
            print(f"    - {ck['name']}: {ck['count']} 条")

    # 分析缓存清理逻辑
    cleanup = result.get("cleanupLogic", [])
    if cleanup:
        print(f"\n  ⚠️  检测到缓存清理逻辑 ({len(cleanup)} 处):")
        for cl in cleanup[:15]:
            print(f"    Line {cl['line']}: {cl['content']}")

    # 检查是否有mystocks-v1.0.0相关逻辑
    if any("mystocks-v1.0.0" in str(cl) for cl in cleanup):
        print("  ⚠️  检测到mystocks-v1.0.0缓存清理逻辑 - 可能导致无限循环")

    return result


async def test_api_endpoints(ws):
    """测试4: 后端API可用性"""
    print("\n" + "=" * 80)
    print("【测试4】后端API可用性（/api/contracts/*）")
    print("=" * 80)

    await ws.send(
        json.dumps(
            {
                "id": 40,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """
        (async () => {
            const endpoints = [
                '/api/contracts/default-api/active',
                '/api/contracts/auth-api/active',
                '/api/contracts/market-api/active',
                '/api/health',
                '/api/auth/login'
            ];
            
            const results = [];
            for (const endpoint of endpoints) {
                try {
                    const start = Date.now();
                    const response = await fetch(endpoint, { method: 'GET' });
                    const duration = Date.now() - start;
                    const text = await response.text().substring(0, 300);
                    results.push({
                        endpoint,
                        status: response.status,
                        ok: response.ok,
                        duration: duration,
                        text: text
                    });
                } catch (e) {
                    results.push({
                        endpoint,
                        error: e.message
                    });
                }
            }
            return results;
        })();
    """,
                    "returnByValue": True,
                },
            }
        )
    )
    response = await ws.recv()
    data = json.loads(response)
    results = data.get("result", {}).get("result", {}).get("value", [])

    api_503_count = 0
    for r in results:
        if r.get("error"):
            print(f"  ❌ {r['endpoint']}: ERROR - {r['error']}")
        elif r.get("status"):
            status_icon = "✅" if r["ok"] else "❌"
            print(f"  {status_icon} {r['endpoint']}: HTTP {r['status']} ({r['duration']}ms)")
            if r["status"] == 503:
                api_503_count += 1
                # 显示响应内容（通常是HTML错误页）
                if "503" in r["text"] or "Service" in r["text"]:
                    print(f"      -> Service Unavailable: 契约验证服务未运行")
            elif r["status"] == 404:
                print(f"      -> 端点不存在 - 这是预期的，因为契约验证可能未启用")
            elif r["status"] == 200:
                print(f"      -> 正常响应")

    return results, api_503_count


async def test_websocket(ws):
    """测试5: WebSocket连接状态"""
    print("\n" + "=" * 80)
    print("【测试5】WebSocket连接状态")
    print("=" * 80)

    await ws.send(
        json.dumps(
            {
                "id": 50,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """
        (() => {
            const result = {
                wsManagerExists: false,
                realtimeIntegrationLoaded: false,
                wsConnections: [],
                wsErrors: []
            };
            
            // 检查WebSocket管理器
            if (window.marketDataWebSocket || window.tradingWebSocket || window.riskWebSocket) {
                result.wsManagerExists = true;
            }
            
            // 检查realtimeIntegration.js是否加载
            const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
            result.realtimeIntegrationLoaded = scripts.some(s => s.includes('realtimeIntegration'));
            
            // 获取WebSocket URL
            if (navigator.serviceWorker && navigator.serviceWorker.controller) {
                // WebSocket通过Service Worker可能已代理
            }
            
            // 检查"Receiving end does not exist"错误
            const logs = window.__console_logs || [];
            result.wsErrors = logs.filter(l => 
                l.message && l.message.includes('Receiving end does not exist')
            ).map(l => l.message);
            
            return result;
        })();
    """,
                    "returnByValue": True,
                },
            }
        )
    )
    response = await ws.recv()
    data = json.loads(response)
    result = data.get("result", {}).get("result", {}).get("value", {})

    print(f"  Realtime Integration已加载: {'✅' if result.get('realtimeIntegrationLoaded') else '❌'}")
    print(f"  WS管理器存在: {'✅' if result.get('wsManagerExists') else '❌'}")

    ws_errors = result.get("wsErrors", [])
    if ws_errors:
        print(f"\n  ⚠️  发现 {len(ws_errors)} 个'Receiving end does not exist'错误:")
        for e in ws_errors[:5]:
            print(f"    - {e[:150]}...")
        print("  根因: WebSocket消息处理器未正确注册")
    else:
        print("  ✅ 未发现WebSocket通信错误")

    return result


async def test_resources(ws):
    """测试6: 资源加载（icons, manifest）"""
    print("\n" + "=" * 80)
    print("【测试6】资源加载（icons, manifest）")
    print("=" * 80)

    await ws.send(
        json.dumps(
            {
                "id": 60,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """
        (async () => {
            const result = {
                manifestLoaded: false,
                manifestContent: null,
                iconStatus: [],
                downloadErrors: []
            };
            
            // 加载manifest
            try {
                const manifestResponse = await fetch('/manifest.json');
                if (manifestResponse.ok) {
                    result.manifestLoaded = true;
                    result.manifestContent = await manifestResponse.json();
                }
            } catch (e) {
                result.manifestError = e.message;
            }
            
            // 检查图标
            const icons = [
                '/icons/icon-144.png',
                '/icons/icon-192.png',
                '/icons/icon-512.png'
            ];
            
            for (const icon of icons) {
                try {
                    const imgResponse = await fetch(icon);
                    const blob = await imgResponse.blob();
                    if (blob.type === 'image/png') {
                        result.iconStatus.push({ url: icon, valid: true, size: blob.size });
                    } else {
                        result.iconStatus.push({ url: icon, valid: false, type: blob.type });
                    }
                } catch (e) {
                    result.downloadErrors.push({ url: icon, error: e.message });
                }
            }
            
            return result;
        })();
    """,
                    "returnByValue": True,
                },
            }
        )
    )
    response = await ws.recv()
    data = json.loads(response)
    result = data.get("result", {}).get("result", {}).get("value", {})

    print(f"  Manifest加载: {'✅' if result.get('manifestLoaded') else '❌'}")

    if result.get("manifestContent"):
        icons = result["manifestContent"].get("icons", [])
        print(f"  Manifest中定义icons: {len(icons)} 个")
        for icon in icons:
            print(f"    - {icon.get('src', 'N/A')}")

    valid_icons = [i for i in result.get("iconStatus", []) if i.get("valid")]
    if valid_icons:
        print(f"  有效图标: {len(valid_icons)} 个")
        for icon in valid_icons:
            print(f"    ✅ {icon['url']}: {icon['size']} bytes")

    errors = result.get("downloadErrors", [])
    if errors:
        print(f"\n  ❌ 下载错误 ({len(errors)} 个):")
        for e in errors:
            print(f"    - {e['url']}: {e['error']}")

    return result


async def test_vue_warnings(ws):
    """测试7: Vue兼容性和运行时警告"""
    print("\n" + "=" * 80)
    print("【测试7】Vue兼容性和运行时警告")
    print("=" * 80)

    await ws.send(
        json.dumps(
            {
                "id": 70,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """
        (() => {
            const result = {
                vueVersion: 'N/A',
                vueWarnings: [],
                deprecatedWarnings: [],
                resolveComponentIssues: [],
                appMounted: false
            };
            
            // Vue版本
            if (window.Vue) {
                result.vueVersion = window.Vue.version || 'unknown';
            }
            
            // Vue应用状态
            const app = document.__vue_app__;
            result.appMounted = !!app;
            
            // apple-mobile-web-app-capable (iOS已废弃)
            const metaTags = document.querySelectorAll('meta[name]');
            for (const meta of metaTags) {
                if (meta.getAttribute('name') === 'apple-mobile-web-app-capable') {
                    result.deprecatedWarnings.push('apple-mobile-web-app-capable标签存在（iOS 13+已废弃）');
                }
            }
            
            // 获取Vue警告
            const consoleWarnings = window.__console_logs || [];
            result.vueWarnings = consoleWarnings.filter(l => 
                l.type === 'warning' && 
                (l.message.includes('resolveComponent') || 
                 l.message.includes('Vue') ||
                 l.message.includes('Compat') ||
                 l.message.includes('component'))
            ).map(l => l.message);
            
            return result;
        })();
    """,
                    "returnByValue": True,
                },
            }
        )
    )
    response = await ws.recv()
    data = json.loads(response)
    result = data.get("result", {}).get("result", {}).get("value", {})

    print(f"  Vue版本: {result.get('vueVersion', 'N/A')}")
    print(f"  App已挂载: {'✅' if result.get('appMounted') else '❌'}")

    for warn in result.get("deprecatedWarnings", []):
        print(f"  ⚠️  兼容性警告: {warn}")

    vue_warnings = result.get("vueWarnings", [])
    if vue_warnings:
        print(f"\n  发现 {len(vue_warnings)} 个Vue警告:")
        for w in vue_warnings[:5]:
            print(f"    - {w[:150]}...")
    else:
        print("  ✅ 无Vue兼容性问题")

    return result


async def test_page_functionality(ws):
    """测试8: 页面功能验证"""
    print("\n" + "=" * 80)
    print("【测试8】页面功能验证")
    print("=" * 80)

    await ws.send(
        json.dumps(
            {
                "id": 80,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """
        (() => {
            const result = {
                userLoggedIn: false,
                userInfo: null,
                dashboardElements: [],
                apiCallsWorking: false,
                pageTitle: document.title
            };
            
            // 检查登录状态
            const token = localStorage.getItem('auth_token');
            const user = localStorage.getItem('auth_user');
            result.userLoggedIn = !!token;
            if (user) {
                try {
                    result.userInfo = JSON.parse(user);
                } catch (e) {}
            }
            
            // 检查仪表盘元素
            const dashboardSelectors = [
                '.dashboard', '.dashboard-header', '.dashboard-content',
                '.stats-card', '.chart-container', '.data-table', 'h1'
            ];
            for (const selector of dashboardSelectors) {
                const el = document.querySelector(selector);
                if (el) {
                    result.dashboardElements.push(selector);
                }
            }
            
            // 测试API调用
            try {
                const response = await fetch('/api/health');
                result.apiCallsWorking = response.ok;
            } catch (e) {
                result.apiCallsWorking = false;
            }
            
            return result;
        })();
    """,
                    "returnByValue": True,
                },
            }
        )
    )
    response = await ws.recv()
    data = json.loads(response)
    result = data.get("result", {}).get("result", {}).get("value", {})

    user = result.get("userInfo", {})
    print(f"  页面标题: {result.get('pageTitle', 'N/A')}")
    print(f"  用户登录: {'✅' if result.get('userLoggedIn') else '❌'}")
    if user:
        print(f"    用户: {user.get('username')} ({user.get('role')})")

    print(f"  API调用正常: {'✅' if result.get('apiCallsWorking') else '❌'}")

    elements = result.get("dashboardElements", [])
    print(f"  仪表盘元素: {len(elements)} 个")
    for el in elements:
        print(f"    - {el}")

    return result


async def main():
    """主测试函数"""
    print("=" * 80)
    print("MyStocks前端综合测试报告")
    print("=" * 80)

    # 获取目标页面
    target_page = get_dashboard_page()
    page_id = target_page["id"]
    uri = target_page["webSocketDebuggerUrl"]

    print(f"测试页面: {target_page['title']}")
    print(f"URL: {target_page['url']}")
    print(f"Page ID: {page_id}")

    async with websockets.connect(uri) as ws:
        # 启用必要的域
        await ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
        await ws.recv()
        await ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))
        await ws.recv()

        # 执行测试
        errors, warnings = await test_console_errors(ws)
        pinia_result = await test_pinia_init(ws)
        sw_result = await test_service_worker(ws)
        api_results, api_503_count = await test_api_endpoints(ws)
        ws_result = await test_websocket(ws)
        resource_result = await test_resources(ws)
        vue_result = await test_vue_warnings(ws)
        func_result = await test_page_functionality(ws)

        # 测试总结
        print("\n" + "=" * 80)
        print("【测试总结】")
        print("=" * 80)

        total_errors = len(errors)
        total_warnings = len(warnings)
        ws_errors_count = len(ws_result.get("wsErrors", []))
        icon_errors = len(resource_result.get("downloadErrors", []))

        print(f"  Console错误: {total_errors}")
        print(f"  Console警告: {total_warnings}")
        print(f"  API 503错误: {api_503_count}")
        print(f"  WebSocket错误: {ws_errors_count}")
        print(f"  图标下载错误: {icon_errors}")
        print(f"  用户已登录: {'✅' if func_result.get('userLoggedIn') else '❌'}")
        print(
            f"  页面功能正常: {'✅' if func_result.get('dashboardElements') and func_result.get('apiCallsWorking') else '❌'}"
        )

        issues = []
        if total_errors > 0:
            issues.append(f"{total_errors}个Console错误")
        if api_503_count > 0:
            issues.append(f"{api_503_count}个503 API错误")
        if ws_errors_count > 0:
            issues.append(f"{ws_errors_count}个WebSocket错误")
        if icon_errors > 0:
            issues.append(f"{icon_errors}个图标下载错误")

        if not issues:
            print("\n  🎉 所有测试通过！")
        else:
            print(f"\n  ⚠️  发现 {len(issues)} 类问题: {', '.join(issues)}")
            print("\n  需要修复的问题:")
            if api_503_count > 0:
                print("    1. 后端契约验证服务未运行 (503)")
            if ws_errors_count > 0:
                print("    2. WebSocket消息处理器未注册")
            if icon_errors > 0:
                print("    3. 图标资源下载失败")
            if not pinia_result.get("piniaExists"):
                print("    4. Pinia未正确加载")

        print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
