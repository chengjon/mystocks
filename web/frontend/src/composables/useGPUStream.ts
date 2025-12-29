import { ref, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';

export function useGPUStream(deviceId: number) {
  const metrics = ref<any>({});
  const connected = ref(false);
  let eventSource: EventSource | null = null;

  const connect = () => {
    try {
      eventSource = new EventSource(`/api/gpu/stream/${deviceId}`);

      eventSource.onopen = () => {
        connected.value = true;
        ElMessage.success('GPU实时监控已连接');
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          metrics.value = data;
        } catch (e) {
          console.error('解析GPU数据失败:', e);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE连接错误:', error);
        connected.value = false;
        eventSource?.close();
        setTimeout(() => {
          ElMessage.warning('GPU监控连接断开,5秒后重连');
          connect();
        }, 5000);
      };
    } catch (error) {
      console.error('创建SSE连接失败:', error);
      ElMessage.error('无法连接GPU监控服务');
    }
  };

  const disconnect = () => {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
      connected.value = false;
    }
  };

  onMounted(() => {
    connect();
  });

  onUnmounted(() => {
    disconnect();
  });

  return {
    metrics,
    connected,
    connect,
    disconnect
  };
}
