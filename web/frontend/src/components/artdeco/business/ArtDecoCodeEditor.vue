<template>
    <div class="artdeco-code-editor" :class="{ 'is-focused': isFocused, 'is-readonly': readonly }">
        <!-- Header / Toolbar -->
        <div class="editor-header">
            <div class="editor-title">{{ title || 'CODE EDITOR' }}</div>
            <div class="editor-lang" v-if="language">{{ language }}</div>
        </div>

        <!-- Editor Body -->
        <div class="editor-body">
            <!-- Line Numbers -->
            <div class="line-numbers" ref="lineNumbersRef">
                <div v-for="n in lineCount" :key="n" class="line-number">{{ n }}</div>
            </div>

            <!-- Text Area -->
            <textarea
                ref="textareaRef"
                v-model="internalValue"
                class="code-textarea"
                :readonly="readonly"
                spellcheck="false"
                @input="handleInput"
                @scroll="handleScroll"
                @focus="isFocused = true"
                @blur="isFocused = false"
                @keydown.tab.prevent="insertTab"
            ></textarea>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed } from 'vue'

    interface Props {
        modelValue: string
        title?: string
        language?: string
        readonly?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        modelValue: '',
        title: '',
        language: 'PYTHON',
        readonly: false
    })

    const emit = defineEmits({
        'update:modelValue': (_value: string) => true
    })

    const textareaRef = ref<HTMLTextAreaElement>()
    const lineNumbersRef = ref<HTMLElement>()
    const isFocused = ref(false)

    // Use internal value to avoid cursor jumping issues on prop updates
    const internalValue = computed({
        get: () => props.modelValue,
        set: val => emit('update:modelValue', val)
    })

    const lineCount = computed(() => {
        return props.modelValue.split('\n').length
    })

    function handleInput() {
        // Auto-resize or logic if needed
    }

    function handleScroll() {
        if (textareaRef.value && lineNumbersRef.value) {
            lineNumbersRef.value.scrollTop = textareaRef.value.scrollTop
        }
    }

    function insertTab(_event: KeyboardEvent) {
        if (props.readonly) return

        const textarea = textareaRef.value
        if (!textarea) return

        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        const value = textarea.value

        // Insert 4 spaces
        const tab = '    '
        textarea.value = value.substring(0, start) + tab + value.substring(end)
        textarea.selectionStart = textarea.selectionEnd = start + tab.length

        emit('update:modelValue', textarea.value)
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens';

    .artdeco-code-editor {
      display: flex;
      flex-direction: column;
      background: var(--artdeco-bg-global);
      border: 1px solid var(--artdeco-gold-opacity-20);
      border-radius: var(--artdeco-radius-none);
      transition: all var(--artdeco-transition-base);
      height: 100%;
      min-height: calc(var(--artdeco-spacing-20) * 3 + var(--artdeco-spacing-12) + var(--artdeco-spacing-3));
    }

    .artdeco-code-editor.is-focused {
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
    }

    .editor-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
      background: var(--artdeco-bg-header);
      border-bottom: 1px solid var(--artdeco-gold-opacity-20);
    }

    .editor-title {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-sm);
      color: var(--artdeco-accent-gold);
      letter-spacing: 1px;
    }

    .editor-lang {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-sm);
      color: var(--artdeco-fg-muted);
    }

    .editor-body {
      flex: 1;
      display: flex;
      position: relative;
      overflow: hidden;
    }

    .line-numbers {
      width: var(--artdeco-spacing-10);
      background: var(--artdeco-bg-card);
      border-right: 1px solid var(--artdeco-gold-opacity-20);
      color: var(--artdeco-fg-muted);
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base);
      line-height: 1.5; /* Match textarea line-height */
      text-align: right;
      padding: calc(var(--artdeco-spacing-5) / 2) var(--artdeco-spacing-2) calc(var(--artdeco-spacing-5) / 2) 0;
      overflow: hidden;
      user-select: none;
      opacity: 50%;
    }

    .line-number {
      height: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-px));
    }

    .code-textarea {
      flex: 1;
      background: transparent;
      border: none;
      color: var(--artdeco-fg-secondary);
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base);
      line-height: 1.5;
      padding: calc(var(--artdeco-spacing-5) / 2);
      resize: none;
      outline: none;
      white-space: pre;
      overflow: auto;
      tab-size: 4;
    }

    .code-textarea::selection {
      background: var(--artdeco-gold-opacity-30);
      color: var(--artdeco-fg-primary);
    }

    /* Syntax Highlighting Simulation (Simple color overrides) */

    /* Since we are using a textarea, we can't do real highlighting without a parser and overlay.
       For now, we just ensure the text color is readable. */
</style>
