import { ref } from 'vue'
import { request, monitoringApi } from '@/api/index'
import { ElMessage } from 'element-plus'

/**
 * API服务组合函数
 * 提供常用的API调用方法，包括健康检查
 */
export function useApiService() {
  const loading = ref(false)
  const error = ref(null)

  /**
   * 获取健康检查数据
   * 调用后端健康检查API端点
   */
  const getHealthData = async () => {
    try {
      loading.value = true
      error.value = null

      // 调用系统健康检查API
      const response = await monitoringApi.getSystemHealth()

      // 将API响应转换为前端需要的格式
      const healthData = {
        timestamp: new Date(response.timestamp).getTime(),
        frontend: response.services.frontend?.status === 'normal' ? 200 : 500,
        frontendResponseTime: response.services.frontend?.response_time || 0,
        api: response.services.api?.status === 'normal' ? 200 : 500,
        postgresql: response.services.postgresql?.status === 'normal' ? '正常' : '异常',
        tdengine: response.services.tdengine?.status === 'normal' ? '可访问' : '不可访问',
        disk: response.services.disk?.status === 'normal' ? '正常' : '异常',
        system: response.services.system?.status === 'normal' ? '正常' : '异常',
        overallStatus: response.overall_status
      }

      return healthData
    } catch (err) {
      console.error('获取健康检查数据失败:', err)
      error.value = err

      // 返回默认状态
      return {
        timestamp: Date.now(),
        frontend: 500,
        frontendResponseTime: 0,
        api: 500,
        postgresql: '异常',
        tdengine: '不可访问',
        disk: '未知',
        system: '未知',
        overallStatus: 'error'
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * 执行详细健康检查
   */
  const getDetailedHealthData = async () => {
    try {
      loading.value = true
      error.value = null

      const response = await monitoringApi.getDetailedSystemHealth()
      return response
    } catch (err) {
      console.error('执行详细健康检查失败:', err)
      error.value = err
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 通用GET请求方法
   */
  const getData = async (url, params = {}) => {
    try {
      loading.value = true
      error.value = null
      return await request.get(url, { params })
    } catch (err) {
      console.error(`GET请求失败: ${url}`, err)
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 通用POST请求方法
   */
  const postData = async (url, data = {}) => {
    try {
      loading.value = true
      error.value = null
      return await request.post(url, data)
    } catch (err) {
      console.error(`POST请求失败: ${url}`, err)
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    loading,
    error,

    // 健康检查方法
    getHealthData,
    getDetailedHealthData,

    // 通用请求方法
    getData,
    postData
  }
}

export default useApiService
