# 📊 Avila Pulse - API Documentation

## Base URL
```
https://pulse.avila.inc/api/v1
```

## Authentication
All API requests require authentication via JWT token:
```bash
Authorization: Bearer {your_jwt_token}
```

---

## Endpoints

### 🔍 Status & Health

#### GET `/health`
Check API health status

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T10:30:00Z",
  "version": "1.0.0",
  "uptime": 3600
}
```

#### GET `/status`
Get current system status

**Response:**
```json
{
  "status": "operational",
  "services": {
    "api": "operational",
    "websocket": "operational",
    "database": "operational",
    "cache": "operational"
  },
  "metrics": {
    "requests_per_second": 1247,
    "active_connections": 3542,
    "avg_response_time_ms": 45
  }
}
```

---

### 📊 Metrics

#### GET `/metrics`
Get all available metrics

**Query Parameters:**
- `period` (optional): `1h`, `24h`, `7d`, `30d` (default: `24h`)
- `type` (optional): `performance`, `users`, `errors`, `all` (default: `all`)
- `start_date` (optional): ISO 8601 timestamp
- `end_date` (optional): ISO 8601 timestamp

**Response:**
```json
{
  "period": "24h",
  "metrics": {
    "total_events": 125847,
    "active_users": 3542,
    "avg_latency_ms": 45,
    "error_rate": 0.03,
    "requests_per_second": 1247
  },
  "timestamp": "2025-11-19T10:30:00Z"
}
```

#### POST `/metrics`
Send custom metric

**Request Body:**
```json
{
  "name": "custom.metric.name",
  "value": 123.45,
  "timestamp": "2025-11-19T10:30:00Z",
  "tags": {
    "environment": "production",
    "service": "api",
    "region": "us-east"
  }
}
```

**Response:**
```json
{
  "success": true,
  "metric_id": "met_abc123xyz",
  "timestamp": "2025-11-19T10:30:00Z"
}
```

---

### ⚡ Events

#### POST `/events`
Send event to stream

**Request Body:**
```json
{
  "event_type": "user.action",
  "data": {
    "user_id": "usr_123",
    "action": "page_view",
    "page": "/dashboard"
  },
  "timestamp": "2025-11-19T10:30:00Z",
  "metadata": {
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Response:**
```json
{
  "success": true,
  "event_id": "evt_abc123xyz",
  "queued_at": "2025-11-19T10:30:00.123Z"
}
```

#### GET `/events`
Get event stream history

**Query Parameters:**
- `limit` (optional): Number of events (default: 100, max: 1000)
- `offset` (optional): Pagination offset
- `event_type` (optional): Filter by event type
- `since` (optional): ISO 8601 timestamp

**Response:**
```json
{
  "events": [
    {
      "event_id": "evt_abc123",
      "event_type": "user.action",
      "timestamp": "2025-11-19T10:30:00Z",
      "data": {...}
    }
  ],
  "total": 1000,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

---

### 👥 Users

#### GET `/users/active`
Get currently active users

**Response:**
```json
{
  "active_users": 3542,
  "timestamp": "2025-11-19T10:30:00Z",
  "breakdown": {
    "web": 2100,
    "mobile": 1200,
    "api": 242
  }
}
```

#### GET `/users/stats`
Get user statistics

**Query Parameters:**
- `period` (optional): `1h`, `24h`, `7d`, `30d`

**Response:**
```json
{
  "period": "24h",
  "total_users": 15420,
  "new_users": 342,
  "returning_users": 15078,
  "avg_session_duration_sec": 1247,
  "sessions": 28940
}
```

---

### 🚨 Alerts

#### GET `/alerts`
Get current alerts

**Query Parameters:**
- `status` (optional): `active`, `resolved`, `all` (default: `active`)
- `severity` (optional): `critical`, `warning`, `info`

**Response:**
```json
{
  "alerts": [
    {
      "alert_id": "alt_abc123",
      "severity": "warning",
      "title": "High CPU Usage",
      "message": "CPU usage above 80% for 5 minutes",
      "status": "active",
      "created_at": "2025-11-19T10:25:00Z",
      "metadata": {
        "cpu_usage": 85.4,
        "threshold": 80,
        "server": "api-server-01"
      }
    }
  ],
  "total": 1
}
```

#### POST `/alerts`
Create custom alert

**Request Body:**
```json
{
  "severity": "warning",
  "title": "Custom Alert",
  "message": "Something needs attention",
  "metadata": {
    "custom_field": "value"
  }
}
```

**Response:**
```json
{
  "success": true,
  "alert_id": "alt_abc123",
  "created_at": "2025-11-19T10:30:00Z"
}
```

#### PATCH `/alerts/{alert_id}`
Update alert status

**Request Body:**
```json
{
  "status": "resolved",
  "resolved_by": "usr_123",
  "resolution_notes": "Fixed server configuration"
}
```

---

### 📈 Analytics

#### GET `/analytics/performance`
Get performance analytics

**Response:**
```json
{
  "period": "24h",
  "latency": {
    "avg_ms": 45,
    "p50_ms": 38,
    "p95_ms": 120,
    "p99_ms": 250
  },
  "throughput": {
    "requests_per_second": 1247,
    "bytes_per_second": 15728640
  },
  "errors": {
    "total": 42,
    "rate": 0.03,
    "by_type": {
      "4xx": 35,
      "5xx": 7
    }
  }
}
```

#### GET `/analytics/trends`
Get trend analysis

**Query Parameters:**
- `metric` (required): Metric name
- `period` (optional): `7d`, `30d`, `90d`

**Response:**
```json
{
  "metric": "active_users",
  "period": "7d",
  "trend": "increasing",
  "change_percent": 12.5,
  "forecast": {
    "next_7d": 4100,
    "confidence": 0.85
  },
  "data_points": [...]
}
```

---

### 🔗 Integrations

#### GET `/integrations`
List active integrations

**Response:**
```json
{
  "integrations": [
    {
      "integration_id": "int_portal",
      "name": "Portal Avila",
      "type": "webhook",
      "status": "active",
      "last_sync": "2025-11-19T10:29:00Z"
    },
    {
      "integration_id": "int_vault",
      "name": "Avila Vault",
      "type": "api",
      "status": "active",
      "last_sync": "2025-11-19T10:30:00Z"
    }
  ]
}
```

#### POST `/integrations`
Create new integration

**Request Body:**
```json
{
  "name": "Custom Integration",
  "type": "webhook",
  "config": {
    "url": "https://example.com/webhook",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer token"
    }
  }
}
```

---

### 🤖 AI Agents

#### GET `/agents`
List AI agents status

**Response:**
```json
{
  "agents": [
    {
      "agent_id": "agt_analytics",
      "name": "Analytics AI",
      "status": "active",
      "last_run": "2025-11-19T10:30:00Z",
      "insights_generated": 127
    },
    {
      "agent_id": "agt_forecast",
      "name": "Forecasting AI",
      "status": "active",
      "last_run": "2025-11-19T10:28:00Z",
      "predictions_made": 45
    }
  ]
}
```

#### POST `/agents/{agent_id}/run`
Trigger agent execution

**Response:**
```json
{
  "success": true,
  "execution_id": "exe_abc123",
  "status": "running",
  "estimated_duration_sec": 30
}
```

#### GET `/agents/{agent_id}/insights`
Get agent insights

**Response:**
```json
{
  "agent_id": "agt_analytics",
  "insights": [
    {
      "insight_id": "ins_abc123",
      "type": "anomaly",
      "title": "Unusual traffic spike detected",
      "description": "Traffic increased 45% compared to baseline",
      "confidence": 0.92,
      "created_at": "2025-11-19T10:25:00Z",
      "metadata": {...}
    }
  ]
}
```

---

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('wss://pulse.avila.inc/ws');
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your_jwt_token'
  }));
};
```

### Subscribe to metrics
```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['metrics', 'events', 'alerts']
}));
```

### Receive real-time updates
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  // {
  //   type: 'metric_update',
  //   data: { ... }
  // }
};
```

---

## Rate Limits

- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Enterprise**: 10000 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1637325600
```

---

## Error Codes

| Code | Description                             |
| ---- | --------------------------------------- |
| 400  | Bad Request - Invalid parameters        |
| 401  | Unauthorized - Invalid or missing token |
| 403  | Forbidden - Insufficient permissions    |
| 404  | Not Found - Resource not found          |
| 429  | Too Many Requests - Rate limit exceeded |
| 500  | Internal Server Error                   |
| 503  | Service Unavailable                     |

**Error Response Format:**
```json
{
  "error": {
    "code": "invalid_parameter",
    "message": "The 'period' parameter must be one of: 1h, 24h, 7d, 30d",
    "details": {...}
  }
}
```

---

## SDKs

### JavaScript/Node.js
```bash
npm install @avila/pulse-client
```

```javascript
import PulseClient from '@avila/pulse-client';

const client = new PulseClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://pulse.avila.inc/api/v1'
});

// Send metric
await client.metrics.send({
  name: 'custom.metric',
  value: 123
});

// Get metrics
const metrics = await client.metrics.get({ period: '24h' });
```

### Python
```bash
pip install avila-pulse
```

```python
from avila_pulse import PulseClient

client = PulseClient(api_key='your_api_key')

# Send event
client.events.send({
    'event_type': 'user.action',
    'data': {'action': 'click'}
})

# Get alerts
alerts = client.alerts.get(status='active')
```

---

## Support

- **Documentation**: https://pulse.avila.inc/docs
- **Status Page**: https://status.avila.inc
- **Email**: support@avila.inc
- **GitHub**: https://github.com/avilaops/Pulse

---

*Last updated: November 19, 2025*
