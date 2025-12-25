<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click.self="handleCancel">
        <div class="modal-container">
          <div class="modal-header">
            <h2>{{ isEditing ? '编辑策略' : '创建策略' }}</h2>
            <button @click="handleCancel" class="btn-close">✕</button>
          </div>

          <div class="modal-body">
            <form @submit.prevent="handleSubmit">
              <!-- 策略名称 -->
              <div class="form-group">
                <label for="name">策略名称 *</label>
                <input
                  id="name"
                  v-model="formData.name"
                  type="text"
                  required
                  placeholder="请输入策略名称"
                  class="form-input"
                />
              </div>

              <!-- 策略类型 -->
              <div class="form-group">
                <label for="type">策略类型 *</label>
                <select id="type" v-model="formData.type" required class="form-select">
                  <option value="trend_following">趋势跟踪</option>
                  <option value="mean_reversion">均值回归</option>
                  <option value="momentum">动量策略</option>
                </select>
              </div>

              <!-- 策略描述 -->
              <div class="form-group">
                <label for="description">策略描述 *</label>
                <textarea
                  id="description"
                  v-model="formData.description"
                  required
                  rows="3"
                  placeholder="请描述策略的核心逻辑和适用场景"
                  class="form-textarea"
                ></textarea>
              </div>

              <!-- 策略参数 -->
              <div class="form-group">
                <label>策略参数</label>
                <div class="parameters">
                  <div v-for="(value, key) in formData.parameters" :key="key" class="parameter-row">
                    <input
                      :value="key"
                      type="text"
                      disabled
                      class="form-input param-key"
                    />
                    <input
                      :value="value"
                      type="text"
                      @input="updateParameter(key, $event.target.value)"
                      class="form-input param-value"
                    />
                  </div>
                  <button
                    type="button"
                    @click="addParameter"
                    class="btn-add-param"
                  >
                    ➕ 添加参数
                  </button>
                </div>
              </div>

              <div class="modal-footer">
                <button type="button" @click="handleCancel" class="btn-cancel">
                  取消
                </button>
                <button type="submit" :disabled="isSubmitting" class="btn-submit">
                  {{ isSubmitting ? '保存中...' : isEditing ? '更新' : '创建' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { Strategy, CreateStrategyRequest, UpdateStrategyRequest } from '@/api/types/strategy';

const props = defineProps<{
  strategy?: Strategy | null;
}>();

const emit = defineEmits<{
  save: [data: CreateStrategyRequest | UpdateStrategyRequest];
  cancel: [];
}>();

const show = computed(() => !!props.strategy);

const isEditing = computed(() => !!props.strategy);

const isSubmitting = ref(false);

const formData = ref<{
  name: string;
  description: string;
  type: Strategy['type'];
  parameters: Record<string, any>;
}>({
  name: '',
  description: '',
  type: 'trend_following',
  parameters: {},
});

// Initialize form when strategy prop changes
watch(
  () => props.strategy,
  (strategy) => {
    if (strategy) {
      formData.value = {
        name: strategy.name,
        description: strategy.description,
        type: strategy.type,
        parameters: { ...strategy.parameters },
      };
    } else {
      formData.value = {
        name: '',
        description: '',
        type: 'trend_following',
        parameters: {},
      };
    }
  },
  { immediate: true }
);

const updateParameter = (key: string, value: string) => {
  formData.value.parameters[key] = value;
};

const addParameter = () => {
  const newKey = `param_${Object.keys(formData.value.parameters).length + 1}`;
  formData.value.parameters[newKey] = '';
};

const handleSubmit = () => {
  if (isEditing.value && props.strategy) {
    const data: UpdateStrategyRequest = {
      name: formData.value.name,
      description: formData.value.description,
      type: formData.value.type,
      parameters: formData.value.parameters,
    };
    emit('save', data);
  } else {
    const data: CreateStrategyRequest = {
      name: formData.value.name,
      description: formData.value.description,
      type: formData.value.type,
      parameters: formData.value.parameters,
    };
    emit('save', data);
  }
};

const handleCancel = () => {
  emit('cancel');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #737373;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-close:hover {
  background-color: #f3f4f6;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  max-height: calc(90vh - 140px);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.parameters {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
}

.parameter-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.param-key {
  flex: 1;
  min-width: 0;
  background-color: #f9fafb;
}

.param-value {
  flex: 1;
  min-width: 0;
}

.btn-add-param {
  width: 100%;
  padding: 8px;
  background-color: #f3f4f6;
  border: 1px dashed #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #6b7280;
}

.btn-add-param:hover {
  background-color: #e5e7eb;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel,
.btn-submit {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background-color: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-cancel:hover {
  background-color: #f9fafb;
}

.btn-submit {
  background-color: #3b82f6;
  border: none;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
}
</style>
