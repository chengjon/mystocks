<template>
    <div class="artdeco-language-switcher">
        <el-dropdown trigger="click" @command="handleLanguageChange" @visible-change="handleDropdownToggle">
            <button
                class="language-button"
                :aria-label="$t('accessibility.changeLanguage')"
                :aria-expanded="isDropdownOpen"
                aria-haspopup="listbox"
                role="button"
                tabindex="0"
            >
                <span class="language-flag">{{ currentLocale.flag }}</span>
                <span class="language-code">{{ currentLocale.code.split('-')[1] }}</span>
                <span class="language-icon" aria-hidden="true">▼</span>
            </button>

            <template #dropdown>
                <el-dropdown-menu role="listbox" :aria-label="$t('settings.language')">
                    <el-dropdown-item
                        v-for="localeItem in supportedLocales"
                        :key="localeItem.code"
                        :command="localeItem.code"
                        :class="{ 'is-active': localeItem.code === locale }"
                        role="option"
                        :aria-selected="localeItem.code === locale"
                    >
                        <span class="locale-flag">{{ localeItem.flag }}</span>
                        <span class="locale-name">{{ localeItem.name }}</span>
                        <span v-if="localeItem.code === locale" class="locale-check" aria-hidden="true">✓</span>
                    </el-dropdown-item>
                </el-dropdown-menu>
            </template>
        </el-dropdown>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed } from 'vue'
    import { useI18n } from '@/composables/useI18n'
    import type { SupportedLocale } from '@/i18n'

    /**
     * ArtDecoLanguageSwitcher - 语言切换器组件
     *
     * 特性:
     * - ArtDeco 风格设计
     * - 下拉菜单选择语言
     * - ARIA 无障碍标签
     * - LocalStorage 持久化
     * - 支持键盘导航
     *
     * 示例:
     * <ArtDecoLanguageSwitcher />
     */

    // Composables
    const { locale, localeInfo, supportedLocales, setLocale } = useI18n()

    // State
    const isDropdownOpen = ref(false)

    // Computed
    const currentLocale = computed(() => localeInfo.value || { code: 'zh-CN', name: '简体中文', flag: '🇨🇳' })

    // Methods
    const handleLanguageChange = (newLocale: SupportedLocale) => {
        setLocale(newLocale)
        isDropdownOpen.value = false
    }

    const handleDropdownToggle = (visible: boolean) => {
        isDropdownOpen.value = visible
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-language-switcher {
        display: inline-block;

        .language-button {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-2);
            padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
            background: var(--artdeco-bg-elevated);
            border: 1px solid var(--artdeco-border-default);
            border-radius: var(--artdeco-radius-sm);
            color: var(--artdeco-fg-primary);
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            cursor: pointer;
            transition: all var(--artdeco-transition-base);

            &:hover {
                border-color: var(--artdeco-gold-primary);
                background: rgba(212, 175, 55, 0.05);
                box-shadow: 0 0 10px rgba(212, 175, 55, 0.2);
            }

            &:active {
                transform: translateY(1px);
            }

            // 焦点状态（键盘导航）
            &:focus-visible {
                outline: 2px solid var(--artdeco-gold-primary);
                outline-offset: 2px;
                box-shadow:
                    0 0 0 2px var(--artdeco-bg-global),
                    0 0 0 4px var(--artdeco-gold-primary),
                    0 0 12px rgba(212, 175, 55, 0.4);
            }

            .language-flag {
                font-size: var(--artdeco-text-lg);
                line-height: 1;
            }

            .language-code {
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            .language-icon {
                font-size: 10px;
                color: var(--artdeco-gold-primary);
                transition: transform var(--artdeco-transition-base);
            }
        }

        // Element Plus 下拉菜单样式覆盖
        :deep(.el-dropdown-menu) {
            background: var(--artdeco-bg-elevated);
            border: 1px solid var(--artdeco-border-default);
            border-radius: var(--artdeco-radius-md);
            padding: var(--artdeco-spacing-2);
            box-shadow: var(--artdeco-shadow-xl);
            min-width: 180px;

            // ArtDeco 几何角落装饰
            @include artdeco-geometric-corners;
        }

        :deep(.el-dropdown-menu__item) {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-3);
            padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
            color: var(--artdeco-fg-primary);
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            border-radius: var(--artdeco-radius-sm);
            transition: all var(--artdeco-transition-fast);

            &:hover {
                background: rgba(212, 175, 55, 0.1);
                color: var(--artdeco-gold-primary);
            }

            &.is-active {
                background: rgba(212, 175, 55, 0.15);
                color: var(--artdeco-gold-primary);
                font-weight: 600;
            }

            // 焦点状态
            &:focus-visible {
                outline: 2px solid var(--artdeco-gold-primary);
                outline-offset: -2px;
            }

            .locale-flag {
                font-size: var(--artdeco-text-lg);
                line-height: 1;
            }

            .locale-name {
                flex: 1;
            }

            .locale-check {
                color: var(--artdeco-gold-primary);
                font-weight: bold;
            }
        }
    }

    // 减少动画支持（无障碍性）
    @media (prefers-reduced-motion: reduce) {
        .artdeco-language-switcher {
            .language-button,
            .language-icon,
            :deep(.el-dropdown-menu__item) {
                transition: none !important;
            }
        }
    }
</style>
