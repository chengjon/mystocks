export const createChannelConnectedLogger = (channelLabel, channelName) => (data) => {
  console.log(`[${channelLabel}] Connected to ${channelName} channel:`, data)
}

export const createKeepaliveLogger = (channelLabel) => (_data) => {
  console.log(`[${channelLabel}] Keepalive ping received`)
}

export const unwrapSSEPayload = (data) => data.data || data

export const createRiskAlertRecord = (data) => ({
  ...unwrapSSEPayload(data),
  id: `alert-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
  timestamp: new Date().toISOString(),
  read: false
})

export const appendBoundedAlert = (alerts, alert, maxAlerts) => {
  alerts.value.unshift(alert)

  if (alerts.value.length > maxAlerts) {
    alerts.value = alerts.value.slice(0, maxAlerts)
  }
}

export const markAlertAsReadById = (alerts, unreadCount, alertId) => {
  const alert = alerts.value.find(item => item.id === alertId)
  if (alert && !alert.read) {
    alert.read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }
}

export const markAllAlertsAsRead = (alerts, unreadCount) => {
  alerts.value.forEach((alert) => {
    alert.read = true
  })
  unreadCount.value = 0
}

export const clearAlertState = (alerts, latestAlert, unreadCount) => {
  alerts.value = []
  latestAlert.value = null
  unreadCount.value = 0
}
