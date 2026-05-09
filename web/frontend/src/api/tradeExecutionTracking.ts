import { request } from '@/utils/request.ts'

type ApiEnvelope<T> = {
  data?: T
  request_id?: string
}

export type ExecutionChannel = 'miniqmt' | 'tdxquant' | 'external'
export type ExecutionSubmissionStatus = 'bridge_task_accepted' | 'broker_acknowledged' | 'submission_failed'
export type ExecutionBrokerState = 'review_required' | 'broker_acknowledged'

export interface ExecutionBridgeEvidence {
  bridgeTaskId: string | null
  receiptStatus: string | null
  resultStatus: string | null
  sourceName: string | null
}

export interface ExecutionBrokerCorrelation {
  externalOrderId: string | null
  brokerEventType: string | null
  identityStatus: string
}

export interface ExecutionTrackingItem {
  trackingId: string
  accountId: string
  orderId: string
  symbol: string
  direction: string
  quantity: number
  price: number
  requestedAt: string
  channel: ExecutionChannel
  submissionStatus: ExecutionSubmissionStatus
  brokerState: ExecutionBrokerState
  reconciliationStatus: string
  bridgeEvidence: ExecutionBridgeEvidence
  brokerCorrelation: ExecutionBrokerCorrelation
}

export interface ExecutionTrackingSummary {
  totalCount: number
  bridgeAcceptedCount: number
  brokerAcknowledgedCount: number
  reviewRequiredCount: number
  reconciledCount: number
}

export interface ExecutionTrackingPayload {
  status: string
  endpoint: string
  resource: string
  requestId: string
  verifiedAt: string
  items: ExecutionTrackingItem[]
  summary: ExecutionTrackingSummary
  totalCount: number
  page: number
  pageSize: number
}

export interface ExecutionEvidenceEvent {
  eventType: string
  occurredAt: string
  summary: string
  evidence: Record<string, unknown>
}

export interface ExecutionTrackingDetailPayload {
  status: string
  endpoint: string
  resource: string
  requestId: string
  verifiedAt: string
  item: ExecutionTrackingItem
  evidenceTimeline: ExecutionEvidenceEvent[]
}

export interface ExternalExecutionTriggerRequest {
  accountId: string
  channel?: ExecutionChannel
  symbol: string
  direction: 'buy' | 'sell'
  quantity: number
  price: number
  requestedBy?: string
  clientRequestId?: string
}

export interface ExternalExecutionTriggerPayload {
  status: string
  endpoint: string
  resource: string
  requestId: string
  verifiedAt: string
  trackingId: string
  accepted: boolean
  channel: ExecutionChannel
  submissionStatus: ExecutionSubmissionStatus
  brokerState: ExecutionBrokerState
  bridgeReceipt: ExecutionBridgeEvidence
}

const EXECUTION_BASE_URL = '/trade/execution-tracking'

const asRecord = (value: unknown): Record<string, unknown> =>
  typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}

const asArray = <T = unknown>(value: unknown): T[] => (Array.isArray(value) ? (value as T[]) : [])

const asNumber = (value: unknown, fallback = 0): number =>
  typeof value === 'number' && Number.isFinite(value)
    ? value
    : typeof value === 'string' && value.trim() !== '' && Number.isFinite(Number(value))
      ? Number(value)
      : fallback

const asString = (value: unknown, fallback = ''): string =>
  typeof value === 'string' ? value : value == null ? fallback : String(value)

const asNullableString = (value: unknown): string | null => (value == null ? null : asString(value))

const unwrapResponseData = <T>(raw: unknown): T => {
  let payload = raw

  if (raw && typeof raw === 'object' && 'data' in (raw as Record<string, unknown>)) {
    const outer = raw as ApiEnvelope<unknown>
    if (outer.data !== undefined) {
      payload = outer.data
    }
  }

  if (payload && typeof payload === 'object' && 'data' in (payload as Record<string, unknown>)) {
    const envelope = payload as ApiEnvelope<T>
    if (envelope.data !== undefined) {
      return envelope.data
    }
  }

  return payload as T
}

const extractEnvelopeRequestId = (raw: unknown): string => {
  if (raw && typeof raw === 'object' && 'request_id' in (raw as Record<string, unknown>)) {
    return asString((raw as Record<string, unknown>).request_id)
  }
  if (raw && typeof raw === 'object' && 'data' in (raw as Record<string, unknown>)) {
    const data = (raw as ApiEnvelope<unknown>).data
    if (data && typeof data === 'object' && 'request_id' in (data as Record<string, unknown>)) {
      return asString((data as Record<string, unknown>).request_id)
    }
  }
  return ''
}

const normalizeBridgeEvidence = (raw: unknown): ExecutionBridgeEvidence => {
  const record = asRecord(raw)
  return {
    bridgeTaskId: asNullableString(record.bridge_task_id),
    receiptStatus: asNullableString(record.receipt_status),
    resultStatus: asNullableString(record.result_status),
    sourceName: asNullableString(record.source_name),
  }
}

const normalizeBrokerCorrelation = (raw: unknown): ExecutionBrokerCorrelation => {
  const record = asRecord(raw)
  return {
    externalOrderId: asNullableString(record.external_order_id),
    brokerEventType: asNullableString(record.broker_event_type),
    identityStatus: asString(record.identity_status, 'missing_broker_identity'),
  }
}

const normalizeExecutionItem = (raw: unknown): ExecutionTrackingItem => {
  const record = asRecord(raw)
  return {
    trackingId: asString(record.tracking_id),
    accountId: asString(record.account_id),
    orderId: asString(record.order_id),
    symbol: asString(record.symbol),
    direction: asString(record.direction),
    quantity: asNumber(record.quantity),
    price: asNumber(record.price),
    requestedAt: asString(record.requested_at),
    channel: asString(record.channel, 'external') as ExecutionChannel,
    submissionStatus: asString(record.submission_status, 'submission_failed') as ExecutionSubmissionStatus,
    brokerState: asString(record.broker_state, 'review_required') as ExecutionBrokerState,
    reconciliationStatus: asString(record.reconciliation_status, 'not_imported'),
    bridgeEvidence: normalizeBridgeEvidence(record.bridge_evidence),
    brokerCorrelation: normalizeBrokerCorrelation(record.broker_correlation),
  }
}

const normalizeExecutionSummary = (raw: unknown): ExecutionTrackingSummary => {
  const record = asRecord(raw)
  return {
    totalCount: asNumber(record.total_count),
    bridgeAcceptedCount: asNumber(record.bridge_accepted_count),
    brokerAcknowledgedCount: asNumber(record.broker_acknowledged_count),
    reviewRequiredCount: asNumber(record.review_required_count),
    reconciledCount: asNumber(record.reconciled_count),
  }
}

const normalizeExecutionTracking = (raw: unknown): ExecutionTrackingPayload => {
  const payload = unwrapResponseData<Record<string, unknown>>(raw)
  const requestId = extractEnvelopeRequestId(raw)
  return {
    status: asString(payload.status, 'available'),
    endpoint: asString(payload.endpoint, 'trade'),
    resource: asString(payload.resource, 'execution_tracking'),
    requestId,
    verifiedAt: requestId ? new Date().toISOString() : '',
    items: asArray(payload.items).map(normalizeExecutionItem),
    summary: normalizeExecutionSummary(payload.summary),
    totalCount: asNumber(payload.total_count),
    page: asNumber(payload.page, 1),
    pageSize: asNumber(payload.page_size, 20),
  }
}

const normalizeExecutionDetail = (raw: unknown): ExecutionTrackingDetailPayload => {
  const payload = unwrapResponseData<Record<string, unknown>>(raw)
  const requestId = extractEnvelopeRequestId(raw)
  return {
    status: asString(payload.status, 'available'),
    endpoint: asString(payload.endpoint, 'trade'),
    resource: asString(payload.resource, 'execution_tracking_detail'),
    requestId,
    verifiedAt: requestId ? new Date().toISOString() : '',
    item: normalizeExecutionItem(payload.item),
    evidenceTimeline: asArray(payload.evidence_timeline).map((event) => {
      const record = asRecord(event)
      return {
        eventType: asString(record.event_type),
        occurredAt: asString(record.occurred_at),
        summary: asString(record.summary),
        evidence: asRecord(record.evidence),
      }
    }),
  }
}

const normalizeTriggerPayload = (raw: unknown): ExternalExecutionTriggerPayload => {
  const payload = unwrapResponseData<Record<string, unknown>>(raw)
  const requestId = extractEnvelopeRequestId(raw)
  return {
    status: asString(payload.status, 'available'),
    endpoint: asString(payload.endpoint, 'trade'),
    resource: asString(payload.resource, 'execution_trigger'),
    requestId,
    verifiedAt: requestId ? new Date().toISOString() : '',
    trackingId: asString(payload.tracking_id),
    accepted: Boolean(payload.accepted),
    channel: asString(payload.channel, 'miniqmt') as ExecutionChannel,
    submissionStatus: asString(payload.submission_status, 'bridge_task_accepted') as ExecutionSubmissionStatus,
    brokerState: asString(payload.broker_state, 'review_required') as ExecutionBrokerState,
    bridgeReceipt: normalizeBridgeEvidence(payload.bridge_receipt),
  }
}

export const fetchExecutionTracking = async (params?: {
  accountId?: string
  orderId?: string
  bridgeTaskId?: string
  page?: number
  pageSize?: number
}): Promise<ExecutionTrackingPayload> => {
  const rawData = await request.get(EXECUTION_BASE_URL, {
    params: {
      account_id: params?.accountId,
      order_id: params?.orderId,
      bridge_task_id: params?.bridgeTaskId,
      page: params?.page,
      page_size: params?.pageSize,
    },
  })
  return normalizeExecutionTracking(rawData)
}

export const fetchExecutionTrackingDetail = async (
  trackingId: string,
): Promise<ExecutionTrackingDetailPayload> => {
  const rawData = await request.get(`${EXECUTION_BASE_URL}/${trackingId}`)
  return normalizeExecutionDetail(rawData)
}

export const postExternalExecutionTrigger = async (
  params: ExternalExecutionTriggerRequest,
): Promise<ExternalExecutionTriggerPayload> => {
  const rawData = await request.post(`${EXECUTION_BASE_URL}/trigger`, {
    account_id: params.accountId,
    channel: params.channel || 'miniqmt',
    symbol: params.symbol,
    direction: params.direction,
    quantity: params.quantity,
    price: params.price,
    requested_by: params.requestedBy,
    client_request_id: params.clientRequestId,
  })
  return normalizeTriggerPayload(rawData)
}
