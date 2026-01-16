<template>
    <span class="artdeco-roman-numeral" :class="sizeClass">
        {{ toRoman(number) }}
    </span>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    // ============================================
    //   COMPONENT: ArtDecoRomanNumeral
    //   Art Deco 风格罗马数字组件
    //
    //   Design Philosophy:
    //   - Classical elegance with Roman numerals
    //   - Display font for sophistication
    //   - Wide letter spacing for luxury feel
    //
    //   Usage:
    //   <ArtDecoRomanNumeral :number="1" />  // I
    //   <ArtDecoRomanNumeral :number="4" />  // IV
    //   <ArtDecoRomanNumeral :number="10" size="lg" />  // X (large)
    // ============================================

    // ============================================
    //   PROPS - 组件属性
    // ============================================

    interface Props {
        /// Number to convert to Roman numeral (1-3999)
        number: number

        /// Size variant
        /// - sm: Small (0.875rem)
        /// - md: Medium (1rem, default)
        /// - lg: Large (1.25rem)
        /// - xl: Extra large (1.5rem)
        size?: 'sm' | 'md' | 'lg' | 'xl'

        /// Additional CSS classes
        class?: string
    }

    const props = withDefaults(defineProps<Props>(), {
        number: 1,
        size: 'md',
        class: ''
    })

    // ============================================
    //   COMPUTED - 计算属性
    // ============================================

    const sizeClass = computed(() => `artdeco-roman-numeral--${props.size}`)

    /**
     * Convert a number to Roman numerals
     * 将数字转换为罗马数字
     * @param num - Number to convert (1-3999)
     * @returns Roman numeral string
     */
    const toRoman = (num: number): string => {
        if (num < 1 || num > 3999) {
            console.warn(`ArtDecoRomanNumeral: Number ${num} is out of range (1-3999)`)
            return '?'
        }

        const romanNumerals = [
            { value: 1000, symbol: 'M' },
            { value: 900, symbol: 'CM' },
            { value: 500, symbol: 'D' },
            { value: 400, symbol: 'CD' },
            { value: 100, symbol: 'C' },
            { value: 90, symbol: 'XC' },
            { value: 50, symbol: 'L' },
            { value: 40, symbol: 'XL' },
            { value: 10, symbol: 'X' },
            { value: 9, symbol: 'IX' },
            { value: 5, symbol: 'V' },
            { value: 4, symbol: 'IV' },
            { value: 1, symbol: 'I' }
        ]

        let result = ''
        let remaining = num

        for (const { value, symbol } of romanNumerals) {
            while (remaining >= value) {
                result += symbol
                remaining -= value
            }
        }

        return result
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-roman-numeral {
        font-family: var(--artdeco-font-display); // Marcellus - classic Roman
        color: var(--artdeco-accent-gold);
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;

        // Size variants
        &--sm {
            font-size: var(--artdeco-font-size-sm); // 0.875rem
            letter-spacing: var(--artdeco-tracking-wide); // 0.05em
        }

        &--md {
            font-size: var(--artdeco-font-size-base); // 1rem
            letter-spacing: var(--artdeco-tracking-wider); // 0.1em
        }

        &--lg {
            font-size: var(--artdeco-font-size-md); // 1.25rem
            letter-spacing: var(--artdeco-tracking-wider); // 0.1em
        }

        &--xl {
            font-size: var(--artdeco-font-size-lg); // 1.5rem
            letter-spacing: var(--artdeco-tracking-widest); // 0.2em
        }
    }
</style>
