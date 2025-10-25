# SSE Client Examples
# Week 2 Day 3 - SSE Real-time Push

Complete examples showing how to consume SSE (Server-Sent Events) endpoints from MyStocks Web API.

---

## JavaScript/TypeScript Examples

### 1. Basic Connection Example

```javascript
// Connect to training progress stream
const eventSource = new EventSource('http://localhost:8000/api/v1/sse/training');

// Handle connection events
eventSource.addEventListener('connected', (event) => {
    const data = JSON.parse(event.data);
    console.log('✅ Connected:', data.data.message);
    console.log('Client ID:', data.data.client_id);
});

// Handle training progress events
eventSource.addEventListener('training_progress', (event) => {
    const data = JSON.parse(event.data);
    console.log('Training Progress:', data.data.progress + '%');
    console.log('Status:', data.data.status);
    console.log('Message:', data.data.message);

    if (data.data.metrics) {
        console.log('Loss:', data.data.metrics.loss);
        console.log('Accuracy:', data.data.metrics.accuracy);
    }
});

// Handle errors
eventSource.addEventListener('error', (event) => {
    console.error('SSE connection error');
    // Automatically reconnects with exponential backoff
});

// Close connection when done
// eventSource.close();
```

### 2. React Hook Example

```typescript
import { useEffect, useState } from 'react';

interface TrainingProgress {
    task_id: string;
    progress: number;
    status: string;
    message: string;
    metrics?: {
        loss: number;
        accuracy: number;
    };
}

export function useTrainingProgress(taskId: string) {
    const [progress, setProgress] = useState<TrainingProgress | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const eventSource = new EventSource(
            `http://localhost:8000/api/v1/sse/training?client_id=client-${taskId}`
        );

        eventSource.addEventListener('connected', () => {
            setIsConnected(true);
            setError(null);
        });

        eventSource.addEventListener('training_progress', (event) => {
            const data = JSON.parse(event.data);
            setProgress(data.data);
        });

        eventSource.addEventListener('error', () => {
            setIsConnected(false);
            setError(new Error('SSE connection failed'));
        });

        return () => {
            eventSource.close();
        };
    }, [taskId]);

    return { progress, isConnected, error };
}

// Usage in component:
function TrainingProgressBar({ taskId }) {
    const { progress, isConnected } = useTrainingProgress(taskId);

    if (!progress) return <div>Connecting...</div>;

    return (
        <div>
            <ProgressBar value={progress.progress} />
            <p>{progress.message}</p>
            {progress.metrics && (
                <div>
                    <p>Loss: {progress.metrics.loss}</p>
                    <p>Accuracy: {progress.metrics.accuracy}</p>
                </div>
            )}
        </div>
    );
}
```

### 3. Vue 3 Composition API Example

```typescript
import { ref, onMounted, onUnmounted } from 'vue';

export function useBacktestProgress(backtestId: string) {
    const progress = ref(0);
    const status = ref('');
    const currentDate = ref('');
    const results = ref<any>(null);
    const isConnected = ref(false);

    let eventSource: EventSource | null = null;

    onMounted(() => {
        eventSource = new EventSource(
            `http://localhost:8000/api/v1/sse/backtest?client_id=backtest-${backtestId}`
        );

        eventSource.addEventListener('connected', () => {
            isConnected.value = true;
        });

        eventSource.addEventListener('backtest_progress', (event) => {
            const data = JSON.parse(event.data);
            progress.value = data.data.progress;
            status.value = data.data.status;
            currentDate.value = data.data.current_date;

            if (data.data.results) {
                results.value = data.data.results;
            }
        });
    });

    onUnmounted(() => {
        if (eventSource) {
            eventSource.close();
        }
    });

    return {
        progress,
        status,
        currentDate,
        results,
        isConnected
    };
}
```

### 4. Multiple Channels Example

```javascript
class SSEManager {
    constructor() {
        this.connections = {};
        this.listeners = {};
    }

    connect(channel, handlers) {
        if (this.connections[channel]) {
            console.warn(`Already connected to ${channel}`);
            return;
        }

        const eventSource = new EventSource(
            `http://localhost:8000/api/v1/sse/${channel}`
        );

        eventSource.addEventListener('connected', (event) => {
            console.log(`✅ Connected to ${channel}`);
            if (handlers.onConnect) {
                handlers.onConnect(JSON.parse(event.data));
            }
        });

        // Register custom event handlers
        Object.keys(handlers).forEach(eventType => {
            if (eventType !== 'onConnect' && eventType !== 'onError') {
                eventSource.addEventListener(eventType, (event) => {
                    handlers[eventType](JSON.parse(event.data));
                });
            }
        });

        eventSource.addEventListener('error', () => {
            console.error(`❌ Error connecting to ${channel}`);
            if (handlers.onError) {
                handlers.onError();
            }
        });

        this.connections[channel] = eventSource;
    }

    disconnect(channel) {
        if (this.connections[channel]) {
            this.connections[channel].close();
            delete this.connections[channel];
            console.log(`🔌 Disconnected from ${channel}`);
        }
    }

    disconnectAll() {
        Object.keys(this.connections).forEach(channel => {
            this.disconnect(channel);
        });
    }
}

// Usage:
const sseManager = new SSEManager();

// Connect to training updates
sseManager.connect('training', {
    onConnect: (data) => console.log('Training channel connected', data),
    training_progress: (data) => updateTrainingUI(data),
    onError: () => console.error('Training channel error')
});

// Connect to risk alerts
sseManager.connect('alerts', {
    onConnect: (data) => console.log('Alerts channel connected', data),
    risk_alert: (data) => showRiskAlert(data),
    onError: () => console.error('Alerts channel error')
});

// Connect to dashboard updates
sseManager.connect('dashboard', {
    onConnect: (data) => console.log('Dashboard channel connected', data),
    dashboard_update: (data) => updateDashboard(data),
    onError: () => console.error('Dashboard channel error')
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    sseManager.disconnectAll();
});
```

---

## Python Client Example

```python
import sseclient
import requests
import json

class MyStocksSSEClient:
    """Python client for MyStocks SSE endpoints"""

    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url

    def listen_training(self, callback, client_id=None):
        """
        Listen to training progress updates

        Args:
            callback: Function to call with each event
            client_id: Optional client identifier
        """
        url = f'{self.base_url}/api/v1/sse/training'
        if client_id:
            url += f'?client_id={client_id}'

        response = requests.get(url, stream=True, headers={'Accept': 'text/event-stream'})
        client = sseclient.SSEClient(response)

        for event in client.events():
            try:
                data = json.loads(event.data)
                callback(data)
            except json.JSONDecodeError:
                print(f"Invalid JSON: {event.data}")
            except KeyboardInterrupt:
                break

    def listen_backtest(self, callback, client_id=None):
        """Listen to backtest progress updates"""
        url = f'{self.base_url}/api/v1/sse/backtest'
        if client_id:
            url += f'?client_id={client_id}'

        response = requests.get(url, stream=True, headers={'Accept': 'text/event-stream'})
        client = sseclient.SSEClient(response)

        for event in client.events():
            try:
                data = json.loads(event.data)
                callback(data)
            except json.JSONDecodeError:
                pass
            except KeyboardInterrupt:
                break

    def listen_alerts(self, callback, client_id=None):
        """Listen to risk alerts"""
        url = f'{self.base_url}/api/v1/sse/alerts'
        if client_id:
            url += f'?client_id={client_id}'

        response = requests.get(url, stream=True, headers={'Accept': 'text/event-stream'})
        client = sseclient.SSEClient(response)

        for event in client.events():
            try:
                data = json.loads(event.data)
                if data['event'] == 'risk_alert':
                    callback(data)
            except json.JSONDecodeError:
                pass
            except KeyboardInterrupt:
                break

# Usage example:
def handle_training_progress(data):
    if data['event'] == 'training_progress':
        progress_data = data['data']
        print(f"Progress: {progress_data['progress']}%")
        print(f"Status: {progress_data['status']}")
        print(f"Message: {progress_data['message']}")

        if 'metrics' in progress_data:
            print(f"Loss: {progress_data['metrics'].get('loss')}")
            print(f"Accuracy: {progress_data['metrics'].get('accuracy')}")

def handle_risk_alert(data):
    alert = data['data']
    print(f"🚨 RISK ALERT: {alert['message']}")
    print(f"Severity: {alert['severity']}")
    print(f"Metric: {alert['metric_name']} = {alert['metric_value']} (threshold: {alert['threshold']})")

# Start listening
client = MyStocksSSEClient()
client.listen_training(handle_training_progress, client_id='python-client-001')
# Or
# client.listen_alerts(handle_risk_alert)
```

---

## cURL Example

```bash
# Connect to training progress stream
curl -N -H "Accept: text/event-stream" \
    http://localhost:8000/api/v1/sse/training

# Output:
# data: {"event": "connected", "data": {"client_id": "...", "channel": "training", "message": "Connected to training channel"}, "timestamp": "2025-10-24T15:30:00Z"}
#
# data: {"event": "ping", "data": {"timestamp": "2025-10-24T15:30:30Z"}}
#
# data: {"event": "training_progress", "data": {"task_id": "...", "progress": 45.5, "status": "running", ...}, "timestamp": "2025-10-24T15:30:35Z"}

# Connect to backtest stream
curl -N -H "Accept: text/event-stream" \
    http://localhost:8000/api/v1/sse/backtest?client_id=curl-client-001

# Connect to alerts stream
curl -N -H "Accept: text/event-stream" \
    http://localhost:8000/api/v1/sse/alerts

# Check SSE server status
curl http://localhost:8000/api/v1/sse/status

# Output:
# {
#   "status": "active",
#   "total_connections": 5,
#   "channels": {
#     "training": {"connection_count": 2, "clients": ["client-1", "client-2"]},
#     "backtest": {"connection_count": 1, "clients": ["client-3"]},
#     "alerts": {"connection_count": 2, "clients": ["client-4", "client-5"]}
#   }
# }
```

---

## Broadcasting Events from Backend

### From Strategy API (Training Progress)

```python
from app.core.sse_manager import get_sse_broadcaster

async def train_model(model_data):
    broadcaster = get_sse_broadcaster()

    # Start training
    task_id = "training-" + str(uuid.uuid4())

    # Send initial progress
    await broadcaster.send_training_progress(
        task_id=task_id,
        progress=0.0,
        status="started",
        message="Training started",
        metrics={}
    )

    # Training loop
    for epoch in range(100):
        # Train...
        loss, accuracy = train_epoch()

        # Broadcast progress every epoch
        await broadcaster.send_training_progress(
            task_id=task_id,
            progress=(epoch + 1) / 100 * 100,
            status="running",
            message=f"Training epoch {epoch + 1}/100",
            metrics={"loss": loss, "accuracy": accuracy}
        )

    # Send completion
    await broadcaster.send_training_progress(
        task_id=task_id,
        progress=100.0,
        status="completed",
        message="Training completed successfully",
        metrics={"final_loss": loss, "final_accuracy": accuracy}
    )
```

### From Backtest API (Backtest Progress)

```python
from app.core.sse_manager import get_sse_broadcaster

async def run_backtest(backtest_config):
    broadcaster = get_sse_broadcaster()
    backtest_id = "backtest-" + str(uuid.uuid4())

    dates = pd.date_range(start_date, end_date)
    total_days = len(dates)

    for i, current_date in enumerate(dates):
        # Run backtest for this date
        results = simulate_trading(current_date)

        # Broadcast progress
        await broadcaster.send_backtest_progress(
            backtest_id=backtest_id,
            progress=(i + 1) / total_days * 100,
            status="running",
            message=f"Simulating {current_date}",
            current_date=str(current_date.date()),
            results={
                "total_return": results.total_return,
                "sharpe_ratio": results.sharpe_ratio,
                "max_drawdown": results.max_drawdown
            }
        )

    # Send completion
    await broadcaster.send_backtest_progress(
        backtest_id=backtest_id,
        progress=100.0,
        status="completed",
        message="Backtest completed",
        results=final_results
    )
```

### From Risk API (Alerts)

```python
from app.core.sse_manager import get_sse_broadcaster

async def check_risk_limits(portfolio):
    broadcaster = get_sse_broadcaster()

    # Calculate VaR
    var_95 = calculate_var(portfolio, confidence=0.95)
    threshold = 0.05

    if var_95 > threshold:
        # Send risk alert
        await broadcaster.send_risk_alert(
            alert_type="var_exceeded",
            severity="high",
            message=f"VaR exceeded threshold: {var_95:.4f} > {threshold:.4f}",
            metric_name="var_95",
            metric_value=var_95,
            threshold=threshold,
            entity_type="portfolio",
            entity_id=portfolio.id
        )
```

---

## Best Practices

### 1. Connection Management

```javascript
// ✅ Good: Reconnect with exponential backoff
class ReconnectingSSE {
    constructor(url) {
        this.url = url;
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        this.connect();
    }

    connect() {
        this.eventSource = new EventSource(this.url);

        this.eventSource.addEventListener('connected', () => {
            this.reconnectDelay = 1000; // Reset delay on successful connection
        });

        this.eventSource.addEventListener('error', () => {
            this.eventSource.close();

            // Reconnect with exponential backoff
            setTimeout(() => {
                this.reconnectDelay = Math.min(
                    this.reconnectDelay * 2,
                    this.maxReconnectDelay
                );
                this.connect();
            }, this.reconnectDelay);
        });
    }
}
```

### 2. Memory Management

```javascript
// ✅ Good: Clean up event listeners
useEffect(() => {
    const eventSource = new EventSource(url);

    const handlers = {
        connected: handleConnected,
        training_progress: handleProgress
    };

    Object.entries(handlers).forEach(([event, handler]) => {
        eventSource.addEventListener(event, handler);
    });

    return () => {
        // Clean up: remove listeners and close connection
        Object.entries(handlers).forEach(([event, handler]) => {
            eventSource.removeEventListener(event, handler);
        });
        eventSource.close();
    };
}, [url]);
```

### 3. Error Handling

```typescript
// ✅ Good: Handle all error scenarios
function useSSE(url: string) {
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const eventSource = new EventSource(url);
        let retryCount = 0;
        const maxRetries = 5;

        eventSource.addEventListener('error', (e) => {
            retryCount++;

            if (retryCount >= maxRetries) {
                setError(new Error('Max retries reached'));
                eventSource.close();
            } else {
                console.log(`Retry ${retryCount}/${maxRetries}`);
            }
        });

        return () => eventSource.close();
    }, [url]);

    return { error };
}
```

---

## Installation Requirements

### JavaScript/TypeScript
```bash
# No additional packages needed - EventSource is native
```

### Python
```bash
pip install sseclient-py requests
```

---

## Troubleshooting

### Issue: Connection Immediately Closes

**Solution**: Check CORS settings in backend

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: No Events Received

**Solution**: Ensure proper Accept header

```javascript
// ❌ Wrong
fetch('http://localhost:8000/api/v1/sse/training')

// ✅ Correct
const eventSource = new EventSource('http://localhost:8000/api/v1/sse/training');
```

### Issue: Connection Timeout

**Solution**: SSE sends ping events every 30 seconds to keep connection alive. No action needed on client side.

---

## Performance Considerations

1. **Connection Limit**: Browsers limit ~6 concurrent SSE connections per domain
2. **Buffering**: Disable nginx buffering with `X-Accel-Buffering: no` header
3. **Keep-Alive**: Server sends ping events every 30 seconds to prevent timeout
4. **Memory**: Each connection consumes ~100KB of memory on server

---

## Security Considerations

1. **Authentication**: Pass tokens via URL query parameter:
   ```javascript
   const eventSource = new EventSource(`/api/v1/sse/training?token=${authToken}`);
   ```

2. **Rate Limiting**: Server limits to 100 connections per IP

3. **HTTPS**: Always use HTTPS in production

4. **CORS**: Configure allowed origins appropriately

---

For more information, see:
- [MDN: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [HTML5 SSE Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [FastAPI SSE Documentation](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
