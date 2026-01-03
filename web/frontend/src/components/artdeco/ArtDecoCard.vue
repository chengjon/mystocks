<template>
  <div class="artdeco-card" :class="cardClasses">
    <!-- Corner decorations -->
    <div class="artdeco-corner-tl"></div>
    <div class="artdeco-corner-br"></div>

    <!-- Card Header (Optional) -->
    <div v-if="$slots.header || title" class="artdeco-card-header">
      <slot name="header">
        <h3>{{ title }}</h3>
        <p v-if="subtitle" class="artdeco-card-subtitle">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- Card Content -->
    <div class="artdeco-card-body">
      <slot></slot>
    </div>

    <!-- Card Footer (Optional) -->
    <div v-if="$slots.footer" class="artdeco-card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  subtitle?: string
  hoverable?: boolean
  clickable?: boolean
  variant?: 'default' | 'stat' | 'bordered'
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  subtitle: '',
  hoverable: true,
  clickable: false,
  variant: 'default'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const cardClasses = computed(() => ({
  'artdeco-card-clickable': props.clickable,
  'artdeco-card-hoverable': props.hoverable,
  [`artdeco-card-${props.variant}`]: true
}))

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-card {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  padding: var(--artdeco-space-lg);
  position: relative;
  overflow: hidden;
  transition: all var(--artdeco-transition-base);
}

/* Double-frame effect */
.artdeco-card::before {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  right: 4px;
  bottom: 4px;
  border: 1px solid var(--artdeco-gold-dim);
  pointer-events: none;
  opacity: 0.3;
  transition: opacity var(--artdeco-transition-base);
}

/* Corner decorations */
.artdeco-corner-tl,
.artdeco-corner-br {
  position: absolute;
  width: 16px;
  height: 16px;
  pointer-events: none;
  opacity: 0.4;
  transition: opacity var(--artdeco-transition-base);
}

.artdeco-corner-tl {
  top: 8px;
  left: 8px;
  border-top: 2px solid var(--artdeco-gold-primary);
  border-left: 2px solid var(--artdeco-gold-primary);
}

.artdeco-corner-br {
  bottom: 8px;
  right: 8px;
  border-bottom: 2px solid var(--artdeco-gold-primary);
  border-right: 2px solid var(--artdeco-gold-primary);
}

/* Card header */
.artdeco-card-header {
  margin-bottom: var(--artdeco-space-md);
  padding-bottom: var(--artdeco-space-md);
  border-bottom: 1px solid rgba(212, 175, 55, 0.2);
}

.artdeco-card-header h3 {
  font-family: var(--artdeco-font-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-display);
  margin: 0 0 var(--artdeco-space-sm) 0;
}

.artdeco-card-subtitle {
  font-family: var(--artdeco-font-body);
  font-size: 0.875rem;
  color: var(--artdeco-silver-muted);
  margin: 0;
}

/* Card body */
.artdeco-card-body {
  font-family: var(--artdeco-font-body);
  color: var(--artdeco-silver-text);
  line-height: 1.6;
}

/* Card footer */
.artdeco-card-footer {
  margin-top: var(--artdeco-space-md);
  padding-top: var(--artdeco-space-md);
  border-top: 1px solid rgba(212, 175, 55, 0.2);
  color: var(--artdeco-silver-muted);
  font-size: 0.875rem;
}

/* Hoverable variant */
.artdeco-card-hoverable:hover {
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
  transform: translateY(-2px);
}

.artdeco-card-hoverable:hover::before {
  opacity: 0.6;
}

.artdeco-card-hoverable:hover .artdeco-corner-tl,
.artdeco-card-hoverable:hover .artdeco-corner-br {
  opacity: 1;
}

/* Clickable variant */
.artdeco-card-clickable {
  cursor: pointer;
}

.artdeco-card-clickable:active {
  transform: translateY(0);
}

/* Stat variant */
.artdeco-card-stat {
  padding: var(--artdeco-space-xl);
  text-align: center;
}

/* Bordered variant */
.artdeco-card-bordered {
  border-width: 2px;
}
</style>
