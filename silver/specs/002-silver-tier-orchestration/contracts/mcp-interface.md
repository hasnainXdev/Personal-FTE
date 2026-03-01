# MCP Server Interface Contract

**Version**: 1.0.0
**Created**: 2026-02-20
**Status**: Draft

---

## Overview

The MCP (Model Context Protocol) Server provides a centralized boundary for all external actions. No agent skill may directly call external APIs - all external execution MUST pass through MCP.

**Server Location**: `localhost:8765`
**Transport**: HTTP/1.1
**Content Type**: `application/json`

---

## Endpoints

### POST /execute

Execute an external action.

**Request**:
```json
{
  "action": "string (required)",
  "parameters": "object (required)",
  "timeout_ms": "number (optional, default: 30000)",
  "request_id": "string (optional, for tracing)"
}
```

**Response**:
```json
{
  "success": "boolean",
  "result": "object (if success)",
  "error": "string (if !success)",
  "error_code": "string (if !success)",
  "duration_ms": "number",
  "request_id": "string (echoed back)"
}
```

**Actions**:

#### send_email

Send an email via configured SMTP provider.

**Parameters**:
```json
{
  "to": "string (email address)",
  "subject": "string",
  "body": "string",
  "cc": "string[] (optional)",
  "attachments": "string[] (optional, file paths)"
}
```

**Response (success)**:
```json
{
  "message_id": "string",
  "sent_timestamp": "ISO8601"
}
```

**Error Codes**:
- `SMTP_AUTH_FAILED`: Authentication with SMTP server failed
- `INVALID_RECIPIENT`: Recipient email address invalid
- `SEND_TIMEOUT`: Email send timed out

---

#### post_linkedin

Publish a post to LinkedIn.

**Parameters**:
```json
{
  "content": "string (post text, max 3000 chars)",
  "draft_url": "string (optional, reference to draft file)",
  "visibility": "string (optional: public | connections | private, default: public)"
}
```

**Response (success)**:
```json
{
  "post_url": "string",
  "post_id": "string",
  "published_timestamp": "ISO8601"
}
```

**Error Codes**:
- `LINKEDIN_AUTH_FAILED`: LinkedIn OAuth token invalid/expired
- `CONTENT_TOO_LONG`: Content exceeds LinkedIn character limit
- `RATE_LIMITED`: LinkedIn API rate limit exceeded
- `NETWORK_ERROR`: Network connectivity issue

---

#### fetch_url

Fetch content from a URL.

**Parameters**:
```json
{
  "url": "string (required)",
  "method": "string (optional: GET | POST, default: GET)",
  "headers": "object (optional)",
  "body": "object (optional, for POST)",
  "timeout_ms": "number (optional, overrides request timeout)"
}
```

**Response (success)**:
```json
{
  "status_code": "number",
  "headers": "object",
  "body": "string",
  "content_type": "string"
}
```

**Error Codes**:
- `HTTP_ERROR`: Non-2xx response status
- `INVALID_URL`: URL format invalid
- `FETCH_TIMEOUT`: Request timed out
- `SSL_ERROR`: SSL certificate validation failed

---

#### trigger_webhook

Send payload to a webhook endpoint.

**Parameters**:
```json
{
  "webhook_url": "string (required)",
  "payload": "object (required)",
  "secret": "string (optional, for HMAC signature)"
}
```

**Response (success)**:
```json
{
  "status_code": "number",
  "response_body": "object",
  "delivered_timestamp": "ISO8601"
}
```

**Error Codes**:
- `WEBHOOK_TIMEOUT`: Webhook endpoint did not respond
- `INVALID_RESPONSE`: Webhook returned invalid JSON
- `SIGNATURE_FAILED`: HMAC signature generation failed

---

### GET /health

Check MCP server health status.

**Request**: No body required.

**Response**:
```json
{
  "status": "string (healthy | degraded | unhealthy)",
  "uptime_seconds": "number",
  "version": "string",
  "actions_available": "string[]",
  "last_action_timestamp": "ISO8601 | null"
}
```

**Status Definitions**:
- `healthy`: All action handlers operational
- `degraded`: Some actions unavailable (see logs)
- `unhealthy`: Server unable to process actions

---

### GET /logs

Retrieve recent action logs (for debugging).

**Request**:
```json
{
  "limit": "number (optional, default: 50, max: 200)",
  "action_type": "string (optional, filter by action)",
  "status": "string (optional: success | failure)"
}
```

**Response**:
```json
{
  "logs": [
    {
      "timestamp": "ISO8601",
      "action_type": "string",
      "request_id": "string",
      "status": "string",
      "duration_ms": "number",
      "error": "string (if failure)"
    }
  ],
  "total_count": "number"
}
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "error_details": {
    "field": "specific detail (optional)"
  },
  "duration_ms": 123,
  "request_id": "req_abc123"
}
```

### Error Code Taxonomy

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Request format invalid |
| `ACTION_NOT_FOUND` | 404 | Action type not implemented |
| `AUTH_FAILED` | 401 | External service authentication failed |
| `TIMEOUT` | 408 | Action execution timed out |
| `RATE_LIMITED` | 429 | External service rate limit hit |
| `INTERNAL_ERROR` | 500 | MCP server internal error |
| `SERVICE_UNAVAILABLE` | 503 | External service unavailable |

---

## Security Requirements

1. **No Direct API Calls**: Agent skills MUST NOT bypass MCP server
2. **Credential Storage**: All API tokens stored in environment variables or secure vault
3. **Request Logging**: All requests/responses logged (sensitive data redacted)
4. **Timeout Enforcement**: All actions have maximum timeout (default 30s)
5. **Rate Limiting**: MCP server enforces per-service rate limits

---

## Testing

### Health Check Test

```bash
curl http://localhost:8765/health
```

Expected: `{"status": "healthy", ...}`

### Action Execution Test

```bash
curl -X POST http://localhost:8765/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "fetch_url",
    "parameters": {"url": "https://httpbin.org/get"},
    "timeout_ms": 5000
  }'
```

Expected: `{"success": true, "result": {...}}`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-20 | Initial contract: send_email, post_linkedin, fetch_url, trigger_webhook |

---

## Next Steps

1. ✅ MCP interface contract complete
2. Create watcher-contract.md
3. Implement MCP server (mcp_server/server.py)
4. Add action handlers (mcp_server/actions/*.py)
