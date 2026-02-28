<template>
    <nav class="artdeco-sidebar">
        <!-- Decorative background pattern -->
        <div class="artdeco-sidebar-pattern"></div>

        <!-- Header Section -->
        <div class="artdeco-sidebar-header">
            <!-- Decorative corner ornaments -->
            <div class="artdeco-corner-tl"></div>
            <div class="artdeco-corner-tr"></div>

            <!-- Logo with ArtDeco style -->
            <router-link to="/artdeco/dashboard" class="artdeco-logo">
                <div class="artdeco-logo-frame">
                    <span class="artdeco-logo-text">MYSTOCKS</span>
                    <span class="artdeco-logo-subtitle">ArtDeco Edition</span>
                </div>
            </router-link>

            <!-- Decorative divider line with ornament -->
            <div class="artdeco-header-divider">
                <div class="artdeco-divider-ornament"></div>
            </div>
        </div>

        <!-- Navigation Menu -->
        <div class="artdeco-nav">
            <!-- Section 1: Market Data -->
            <div class="artdeco-nav-section artdeco-fade-in" style="animation-delay: 0.1s">
                <div class="artdeco-nav-section-header">
                    <div class="artdeco-nav-section-icon">◈</div>
                    <div class="artdeco-nav-section-title">MARKET DATA</div>
                    <div class="artdeco-nav-section-line"></div>
                </div>

                <router-link to="/artdeco/dashboard" class="artdeco-nav-item" active-class="active">
                    <div class="artdeco-nav-number">Ⅰ</div>
                    <div class="artdeco-nav-content">
                        <div class="artdeco-nav-label">主控仪表盘</div>
                        <div class="artdeco-nav-subtitle">Dashboard</div>
                    </div>
                </router-link>

                <router-link to="/artdeco/market-center" class="artdeco-nav-item" active-class="active">
                    <div class="artdeco-nav-number">Ⅱ</div>
                    <div class="artdeco-nav-content">
                        <div class="artdeco-nav-label">市场行情中心</div>
                        <div class="artdeco-nav-subtitle">Market Center</div>
                    </div>
                </router-link>

                <router-link to="/artdeco/stock-screener" class="artdeco-nav-item" active-class="active">
                    <div class="artdeco-nav-number">Ⅲ</div>
                    <div class="artdeco-nav-content">
                        <div class="artdeco-nav-label">智能选股池</div>
                        <div class="artdeco-nav-subtitle">Stock Screener</div>
                    </div>
                </router-link>
            </div>

            <!-- Section 2: Analysis Tools -->
            <div class="artdeco-nav-section artdeco-fade-in" style="animation-delay: 0.2s">
                <div class="artdeco-nav-section-header">
                    <div class="artdeco-nav-section-icon">◇</div>
                    <div class="artdeco-nav-section-title">ANALYSIS TOOLS</div>
                    <div class="artdeco-nav-section-line"></div>
                </div>

                <router-link to="/artdeco/data-analysis" class="artdeco-nav-item" active-class="active">
                    <div class="artdeco-nav-number">Ⅳ</div>
                    <div class="artdeco-nav-content">
                        <div class="artdeco-nav-label">数据分析</div>
                        <div class="artdeco-nav-subtitle">Data Analysis</div>
                    </div>
                </router-link>

                <router-link to="/artdeco/strategy-lab" class="artdeco-nav-item" active-class="active">
                    <div class="artdeco-nav-number">Ⅴ</div>
                    <div class="artdeco-nav-content">
                        <div class="artdeco-nav-label">策略实验室</div>
                        <div class="artdeco-nav-subtitle">Strategy Lab</div>
                    </div>
                </router-link>

                <router-link to="/artdeco/backtest-arena" class="artdeco-nav-item" active-class="active">
                    <div class="artdeco-nav-number">Ⅵ</div>
                    <div class="artdeco-nav-content">
                        <div class="artdeco-nav-label">回测竞技场</div>
                        <div class="artdeco-nav-subtitle">Backtest Arena</div>
                    </div>
                </router-link>
            </div>

            <!-- Section 3: Trade Management -->
            <div class="artdeco-nav-section artdeco-fade-in" style="animation-delay: 0.3s">
                <div class="artdeco-nav-section-header">
                    <div class="artdeco-nav-section-icon">◆</div>
                    <div class="artdeco-nav-section-title">TRADE MANAGEMENT</div>
                    <div class="artdeco-nav-section-line"></div>
                </div>

                <router-link to="/artdeco/trade-station" class="artdeco-nav-item" active-class="active">
                    <div class="artdeco-nav-number">Ⅶ</div>
                    <div class="artdeco-nav-content">
                        <div class="artdeco-nav-label">交易工作站</div>
                        <div class="artdeco-nav-subtitle">Trade Station</div>
                    </div>
                </router-link>

                <router-link to="/artdeco/risk-center" class="artdeco-nav-item" active-class="active">
                    <div class="artdeco-nav-number">Ⅷ</div>
                    <div class="artdeco-nav-content">
                        <div class="artdeco-nav-label">风控中心</div>
                        <div class="artdeco-nav-subtitle">Risk Center</div>
                    </div>
                </router-link>
            </div>

            <!-- Section 4: System -->
            <div class="artdeco-nav-section artdeco-fade-in" style="animation-delay: 0.4s">
                <div class="artdeco-nav-section-header">
                    <div class="artdeco-nav-section-icon">◈</div>
                    <div class="artdeco-nav-section-title">SYSTEM</div>
                    <div class="artdeco-nav-section-line"></div>
                </div>

                <router-link to="/artdeco/system-settings" class="artdeco-nav-item" active-class="active">
                    <div class="artdeco-nav-number">Ⅸ</div>
                    <div class="artdeco-nav-content">
                        <div class="artdeco-nav-label">系统设置</div>
                        <div class="artdeco-nav-subtitle">System Settings</div>
                    </div>
                </router-link>
            </div>
        </div>

        <!-- Footer with decorative element -->
        <div class="artdeco-sidebar-footer">
            <div class="artdeco-footer-ornament">❧</div>
            <div class="artdeco-footer-text">EST. 2025</div>
        </div>
    </nav>
</template>

<script setup lang="ts"></script>

<style scoped lang="scss">
@import "./styles/ArtDecoSidebar";
</style>
