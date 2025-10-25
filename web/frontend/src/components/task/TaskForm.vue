<template>
  <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
    <el-form-item label="任务ID" prop="task_id">
      <el-input v-model="formData.task_id" placeholder="唯一标识符，如：daily_sync" />
    </el-form-item>

    <el-form-item label="任务名称" prop="task_name">
      <el-input v-model="formData.task_name" placeholder="任务的显示名称" />
    </el-form-item>

    <el-form-item label="任务类型" prop="task_type">
      <el-select v-model="formData.task_type" style="width: 100%">
        <el-option label="定时任务" value="cron" />
        <el-option label="进程管理" value="supervisor" />
        <el-option label="手动任务" value="manual" />
        <el-option label="数据同步" value="data_sync" />
        <el-option label="指标计算" value="indicator_calc" />
        <el-option label="市场数据获取" value="market_fetch" />
      </el-select>
    </el-form-item>

    <el-form-item label="任务模块" prop="task_module">
      <el-input v-model="formData.task_module" placeholder="Python模块路径，如：app.tasks.data_sync" />
    </el-form-item>

    <el-form-item label="任务函数" prop="task_function">
      <el-input v-model="formData.task_function" placeholder="函数名称，如：sync_daily_data" />
    </el-form-item>

    <el-form-item label="描述">
      <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="任务的详细说明" />
    </el-form-item>

    <el-form-item label="优先级" prop="priority">
      <el-select v-model="formData.priority" style="width: 100%">
        <el-option label="关键 (100)" :value="100" />
        <el-option label="高 (200)" :value="200" />
        <el-option label="普通 (500)" :value="500" />
        <el-option label="低 (800)" :value="800" />
        <el-option label="批处理 (900)" :value="900" />
      </el-select>
    </el-form-item>

    <el-divider content-position="left">调度配置</el-divider>

    <el-form-item label="调度类型">
      <el-select v-model="scheduleType" style="width: 100%" @change="handleScheduleTypeChange">
        <el-option label="无调度（手动）" value="none" />
        <el-option label="Cron表达式" value="cron" />
        <el-option label="固定间隔" value="interval" />
        <el-option label="一次性" value="once" />
      </el-select>
    </el-form-item>

    <el-form-item label="Cron表达式" v-if="scheduleType === 'cron'">
      <el-input v-model="formData.schedule.cron_expression" placeholder="如：0 0 * * *（每天零点）" />
      <div style="margin-top: 8px; color: #909399; font-size: 12px">
        示例: 0 0 * * * (每天零点) | 0 * * * * (每小时) | */5 * * * * (每5分钟)
      </div>
    </el-form-item>

    <el-form-item label="执行间隔(秒)" v-if="scheduleType === 'interval'">
      <el-input-number v-model="formData.schedule.interval_seconds" :min="1" :max="86400" />
    </el-form-item>

    <el-form-item label="开始时间" v-if="scheduleType !== 'none'">
      <el-date-picker
        v-model="formData.schedule.start_time"
        type="datetime"
        placeholder="选择开始时间"
        style="width: 100%"
      />
    </el-form-item>

    <el-divider content-position="left">高级配置</el-divider>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="超时时间(秒)">
          <el-input-number v-model="formData.timeout" :min="1" :max="86400" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="重试次数">
          <el-input-number v-model="formData.retry_count" :min="0" :max="10" style="width: 100%" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="重试延迟(秒)">
          <el-input-number v-model="formData.retry_delay" :min="1" :max="3600" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="自动重启">
          <el-switch v-model="formData.auto_restart" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="任务标签">
      <el-select v-model="formData.tags" multiple filterable allow-create style="width: 100%">
        <el-option label="每日" value="daily" />
        <el-option label="实时" value="realtime" />
        <el-option label="批处理" value="batch" />
        <el-option label="重要" value="important" />
      </el-select>
    </el-form-item>

    <el-form-item label="任务参数">
      <el-input
        v-model="paramsJson"
        type="textarea"
        :rows="4"
        placeholder='JSON格式，如：{"symbol": "000001", "period": "daily"}'
      />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit">提交</el-button>
      <el-button @click="$emit('cancel')">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  task: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref(null)
const scheduleType = ref('none')
const paramsJson = ref('{}')

const formData = ref({
  task_id: '',
  task_name: '',
  task_type: 'manual',
  task_module: '',
  task_function: '',
  description: '',
  priority: 500,
  schedule: {
    schedule_type: 'none',
    cron_expression: '',
    interval_seconds: 3600,
    start_time: null,
    end_time: null,
    enabled: true
  },
  params: {},
  timeout: 3600,
  retry_count: 0,
  retry_delay: 60,
  dependencies: [],
  tags: [],
  auto_restart: false,
  stop_on_error: true
})

const rules = {
  task_id: [{ required: true, message: '请输入任务ID', trigger: 'blur' }],
  task_name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  task_type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  task_module: [{ required: true, message: '请输入任务模块', trigger: 'blur' }],
  task_function: [{ required: true, message: '请输入任务函数', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

watch(
  () => props.task,
  (newTask) => {
    if (newTask) {
      formData.value = { ...newTask }
      if (newTask.schedule) {
        scheduleType.value = newTask.schedule.schedule_type
      }
      if (newTask.params) {
        paramsJson.value = JSON.stringify(newTask.params, null, 2)
      }
    }
  },
  { immediate: true }
)

const handleScheduleTypeChange = (type) => {
  formData.value.schedule.schedule_type = type
  if (type === 'none') {
    formData.value.schedule = null
  } else if (!formData.value.schedule) {
    formData.value.schedule = {
      schedule_type: type,
      cron_expression: '',
      interval_seconds: 3600,
      start_time: null,
      end_time: null,
      enabled: true
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    // 解析参数JSON
    try {
      formData.value.params = JSON.parse(paramsJson.value)
    } catch (e) {
      ElMessage.error('任务参数JSON格式错误')
      return
    }

    // 如果没有调度配置，移除schedule字段
    if (scheduleType.value === 'none') {
      formData.value.schedule = null
    }

    emit('submit', formData.value)
  } catch (error) {
    ElMessage.error('请填写完整的表单信息')
  }
}
</script>

<style scoped lang="scss">
:deep(.el-divider__text) {
  font-weight: 600;
  color: #409eff;
}
</style>
