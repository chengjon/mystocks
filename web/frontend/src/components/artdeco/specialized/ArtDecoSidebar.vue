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
    @import '@/styles/artdeco-tokens.scss';

    /* ====================
   SIDEBAR CONTAINER
   ==================== */
    .artdeco-sidebar {
        width: 280px;
        background: var(--artdeco-bg-header);
        border-right: 2px solid var(--artdeco-gold-dim);
        position: fixed;
        height: 100vh;
        overflow-y: auto;
        overflow-x: hidden;
        z-index: var(--artdeco-z-fixed);
        transition: transform var(--artdeco-transition-slow);
    }

    /* Decorative background pattern */
    .artdeco-sidebar-pattern {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(212, 175, 55, 0.02) 10px,
            rgba(212, 175, 55, 0.02) 20px
        );
        pointer-events: none;
        z-index: 0;
    }

    /* ====================
   HEADER SECTION
   ==================== */
    .artdeco-sidebar-header {
        padding: var(--artdeco-spacing-5) var(--artdeco-spacing-4); // 40px 32px
        border-bottom: 2px solid rgba(212, 175, 55, 0.2);
        text-align: center;
        position: relative;
        background: var(--artdeco-bg-header);
        z-index: 1;
    }

    /* Decorative corner ornaments */
    .artdeco-corner-tl,
    .artdeco-corner-tr {
        position: absolute;
        width: 30px;
        height: 30px;
        border: 2px solid rgba(212, 175, 55, 0.2);
        pointer-events: none;
    }

    .artdeco-corner-tl {
        top: 10px;
        left: 10px;
        border-right: none;
        border-bottom: none;
    }

    .artdeco-corner-tr {
        top: 10px;
        right: 10px;
        border-left: none;
        border-bottom: none;
    }

    /* Logo with frame */
    .artdeco-logo {
        display: inline-block;
        text-decoration: none;
        position: relative;
        z-index: 1;
        margin-top: var(--artdeco-spacing-2); // 16px
    }

    .artdeco-logo-frame {
        border: 2px solid var(--artdeco-accent-gold);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4); // 24px 32px
        background: var(--artdeco-bg-card);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.1);
        transition: all var(--artdeco-transition-slow);
    }

    .artdeco-logo:hover .artdeco-logo-frame {
        border-color: var(--artdeco-accent-gold);
        box-shadow: var(--artdeco-glow-subtle);
        transform: scale(1.02);
    }

    .artdeco-logo-text {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-md); // 18px - 紧凑设计（原28px，-36%）
        font-weight: 700;
        color: var(--artdeco-accent-gold);
        letter-spacing: 0.25em; /* Changed from 6px to relative unit */
        text-transform: uppercase;
        display: block;
        margin-bottom: 4px;
        transition: color var(--artdeco-transition-slow);
        line-height: 1.2; /* Better vertical spacing */
    }

    .artdeco-logo:hover .artdeco-logo-text {
        color: var(--artdeco-accent-gold);
    }

    .artdeco-logo-subtitle {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-font-size-sm); // 12px - 紧凑设计（保持不变）
        font-weight: 500;
        color: var(--artdeco-fg-muted); /* Use theme variable */
        letter-spacing: 0.15em; /* Changed from 3px to relative unit */
        text-transform: uppercase;
        display: block;
    }

    /* Decorative divider with ornament */
    .artdeco-header-divider {
        height: 1px;
        background: linear-gradient(
            to right,
            transparent,
            var(--artdeco-accent-gold) 40%,
            var(--artdeco-accent-gold) 60%,
            transparent
        );
        margin: var(--artdeco-spacing-3) auto 0; // 24px
        position: relative;
        opacity: 0.6;
    }

    .artdeco-divider-ornament {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 8px;
        height: 8px;
        background: var(--artdeco-accent-gold);
        transform: translate(-50%, -50%) rotate(45deg);
        box-shadow: 0 0 8px var(--artdeco-accent-gold);
    }

    /* ====================
   NAVIGATION MENU
   ==================== */
    .artdeco-nav {
        padding: var(--artdeco-spacing-4); // 32px
        position: relative;
        z-index: 1;
    }

    /* Navigation Section */
    .artdeco-nav-section {
        margin-bottom: var(--artdeco-spacing-6); // 48px
    }

    /* Section Header with Icon */
    .artdeco-nav-section-header {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-2); // 16px
        margin-bottom: var(--artdeco-spacing-3); // 24px
        padding-bottom: var(--artdeco-spacing-2); // 16px
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }

    .artdeco-nav-section-icon {
        font-size: var(--artdeco-font-size-base); // 14px - 紧凑设计（原16px，-12.5%）
        color: var(--artdeco-accent-gold);
        text-shadow: 0 0 8px rgba(212, 175, 55, 0.3);
    }

    .artdeco-nav-section-title {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-sm); // 12px - 紧凑设计（保持不变）
        font-weight: 600;
        color: var(--artdeco-accent-gold); /* Changed to gold for better contrast */
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide); // 0.05em
        flex: 1;
        opacity: 0.8; /* Slightly muted for hierarchy */
    }

    .artdeco-nav-section-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(to right, rgba(212, 175, 55, 0.2), transparent);
    }

    /* Navigation Item - IMPROVED: Better spacing and visibility */
    .artdeco-nav-item {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-3); // 24px
        padding: 18px var(--artdeco-spacing-3); /* Increased from 16px for better touch targets */
        color: var(--artdeco-fg-primary); /* Champagne cream - excellent contrast */
        text-decoration: none;
        border-left: 3px solid transparent;
        background: transparent;
        transition: all var(--artdeco-transition-slow);
        margin-bottom: var(--artdeco-spacing-2); /* Increased from xs for better spacing */
        position: relative;
        overflow: hidden;
        min-height: 60px; /* Ensure consistent height */
    }

    .artdeco-nav-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        width: 0;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.05));
        transition: width var(--artdeco-transition-slow);
    }

    .artdeco-nav-number {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-md); // 18px - 紧凑设计（原20px，-10%）
        font-weight: 700;
        color: rgba(212, 175, 55, 0.2);
        min-width: 32px;
        text-align: center;
        transition: all var(--artdeco-transition-slow);
    }

    .artdeco-nav-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    /* IMPROVED: Better readability and contrast */
    .artdeco-nav-label {
        font-family: var(--artdeco-font-body);
        font-weight: 600;
        font-size: var(--artdeco-font-size-base); // 14px - 紧凑设计（原16px，-12.5%）
        color: var(--artdeco-fg-primary); /* Champagne cream */
        letter-spacing: 0.05em; /* Slightly wider for readability */
        transition: all var(--artdeco-transition-slow);
        line-height: 1.3; /* Better vertical spacing */
    }

    /* IMPROVED: Better contrast and visibility */
    .artdeco-nav-subtitle {
        font-family: var(--artdeco-font-body);
        font-weight: 400;
        font-size: var(--artdeco-font-size-sm); // 12px - 紧凑设计（保持不变）
        color: var(--artdeco-fg-muted); /* Pewter - defined in theme */
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all var(--artdeco-transition-slow);
        line-height: 1.2;
    }

    /* Hover State - IMPROVED: Better visual feedback */
    .artdeco-nav-item:hover {
        background: rgba(212, 175, 55, 0.08); /* Subtle gold tint */
        border-left-color: var(--artdeco-accent-gold); /* Full gold for visibility */
        padding-left: calc(var(--artdeco-spacing-3) + 4px); // 24px + 4px
    }

    .artdeco-nav-item:hover::before {
        width: 100%;
    }

    .artdeco-nav-item:hover .artdeco-nav-number {
        color: var(--artdeco-accent-gold);
        transform: scale(1.1);
        text-shadow: 0 0 12px rgba(212, 175, 55, 0.5);
    }

    .artdeco-nav-item:hover .artdeco-nav-label {
        color: var(--artdeco-accent-gold); /* Gold on hover */
        text-shadow: 0 0 8px rgba(212, 175, 55, 0.2); /* Subtle glow */
    }

    .artdeco-nav-item:hover .artdeco-nav-subtitle {
        color: var(--artdeco-fg-primary); /* Full brightness on hover */
    }

    /* Active State - IMPROVED: Better visibility and contrast */
    .artdeco-nav-item.active {
        background: linear-gradient(
            90deg,
            rgba(212, 175, 55, 0.2),
            /* Increased opacity for better visibility */ rgba(212, 175, 55, 0.08)
        );
        border-left-color: var(--artdeco-accent-gold);
        border-left-width: 4px; /* Thicker for emphasis */
        box-shadow: inset 0 0 30px rgba(212, 175, 55, 0.15); /* More intense glow */
    }

    .artdeco-nav-item.active .artdeco-nav-number {
        color: var(--artdeco-accent-gold);
        text-shadow: var(--artdeco-glow-subtle);
        transform: scale(1.15);
    }

    .artdeco-nav-item.active .artdeco-nav-label {
        color: var(--artdeco-accent-gold); /* Full gold for maximum visibility */
        font-weight: 700;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.3); /* Add glow for emphasis */
    }

    .artdeco-nav-item.active .artdeco-nav-subtitle {
        color: var(--artdeco-fg-secondary); /* Secondary text - better contrast */
    }

    /* ====================
   FOOTER SECTION
   ==================== */
    .artdeco-sidebar-footer {
        padding: var(--artdeco-spacing-4); // 32px
        text-align: center;
        border-top: 1px solid rgba(212, 175, 55, 0.2);
        background: var(--artdeco-bg-header);
        position: relative;
        z-index: 1;
    }

    .artdeco-footer-ornament {
        font-size: var(--artdeco-font-size-lg); // 24px - 紧凑设计（保持不变）
        color: rgba(212, 175, 55, 0.2);
        margin-bottom: var(--artdeco-spacing-1); // 8px
        text-shadow: 0 0 8px rgba(212, 175, 55, 0.2);
    }

    .artdeco-footer-text {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-xs); // 10px - 紧凑设计（原10.4px，-4%）
        font-weight: 600;
        color: var(--artdeco-fg-muted);
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ====================
   ANIMATIONS
   ==================== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .artdeco-fade-in {
        animation: fadeInUp 0.6s ease-out backwards;
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
