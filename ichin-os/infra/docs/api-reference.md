# ICHIN OS — Full API Reference

Base URL: `https://api.ichin.ai` (production) | `http://localhost:{port}` (dev)

---

## 1. Orchestrator (Port 8011)

Responsible for workflow orchestration, task routing, and system coordination.

### `GET /health`
Health check endpoint.

### `POST /ai/query`
Single entry point for AI queries (proxied through AI Gateway).
- **Body**: `{ query: string, session_id?: string, mode?: "fast"|"balanced"|"deep" }`
- **Response**: `{ response_id, text, sources[], model_used, processing_time_ms, follow_up_actions[] }`

### `POST /workflows`
Create a new multi-step workflow.
- **Body**: `{ type: string, steps: object[], context: object }`
- **Response**: `{ workflow_id, status, created_at }`

### `GET /workflows/{id}`
Get workflow status and results.

### `POST /workflows/{id}/cancel`
Cancel a running workflow.

### `GET /tasks`
List all tasks with optional filters (status, type, agent_id).

### `GET /tasks/{id}`
Get task details.

### `POST /tasks/{id}/retry`
Retry a failed task.

### `GET /services`
List all registered microservices and their health status.

### `GET /metrics`
Prometheus metrics endpoint.

---

## 2. Agents (Port 8012)

Manages agent lifecycle, tool execution, and agent-to-agent communication.

### `GET /health`

### `POST /agents`
Register a new agent.
- **Body**: `{ name: string, type: string, capabilities: string[], config: object }`
- **Response**: `{ agent_id, status }`

### `GET /agents`
List all agents.

### `GET /agents/{id}`
Get agent details and status.

### `PUT /agents/{id}`
Update agent configuration.
- **Body**: `{ config: object, capabilities?: string[] }`

### `DELETE /agents/{id}`
Decommission an agent.

### `POST /agents/{id}/execute`
Execute an agent task.
- **Body**: `{ task: string, input: object, context?: object }`
- **Response**: `{ task_id, status, output }`

### `GET /agents/{id}/tasks`
List tasks assigned to an agent.

### `POST /agents/{id}/pause`
Pause agent operations.

### `POST /agents/{id}/resume`
Resume agent operations.

### `GET /tools`
List available tools for agents.

### `POST /tools/execute`
Execute a specific tool.
- **Body**: `{ tool: string, parameters: object }`

---

## 3. Memory Engine (Port 8013)

Handles short-term and long-term memory, vector embeddings, and semantic search.

### `GET /health`

### `POST /memory/store`
Store a memory entry.
- **Body**: `{ user_id: string, content: object, type: "chat"|"fact"|"preference", metadata?: object, ttl?: number }`
- **Response**: `{ memory_id, embedding_id }`

### `POST /memory/query`
Query memories using semantic search.
- **Body**: `{ query: string, user_id?: string, limit?: number, threshold?: float, filters?: object }`
- **Response**: `{ results: [{ memory_id, content, score, metadata }], query_embedding }`

### `PUT /memory/{id}`
Update a memory entry.

### `DELETE /memory/{id}`
Delete a memory entry.

### `GET /memory/{id}`
Get a specific memory entry.

### `POST /memory/batch`
Batch store multiple memory entries.

### `POST /memory/search`
Full-text search across memories (non-semantic).
- **Body**: `{ query: string, fields: string[], limit?: number }`

### `POST /memory/summarize`
Summarize related memories.
- **Body**: `{ user_id: string, topic: string, max_sources?: number }`

### `DELETE /memory/user/{id}`
Purge all memories for a user.

### `GET /memory/stats`
Get memory storage statistics.

### `POST /embeddings`
Generate embeddings for arbitrary text.
- **Body**: `{ text: string | string[], model?: string }`

---

## 4. UI System (Port 8014)

Manages WebSocket connections, real-time UI updates, and session state.

### `GET /health`

### `GET /ws`
WebSocket upgrade endpoint for real-time communication.
- **Messages**: `{ type: "state_update"|"notification"|"agent_progress"|"workflow_update", payload: object }`

### `POST /sessions`
Create a new UI session.
- **Body**: `{ user_id: string, device: "desktop"|"mobile"|"web", preferences?: object }`

### `GET /sessions/{id}`
Get session state.

### `PUT /sessions/{id}`
Update session state.

### `DELETE /sessions/{id}`
Destroy a session.

### `GET /sessions/{id}/history`
Get session event history.

### `POST /notifications`
Send a notification to a user.
- **Body**: `{ user_id: string, type: "info"|"warning"|"error"|"success", title: string, message: string, action?: object }`

### `GET /notifications/{user_id}`
Get pending notifications for a user.

### `PUT /notifications/{id}/read`
Mark notification as read.

### `POST /state/broadcast`
Broadcast state to all connected clients.
- **Body**: `{ component: string, action: string, state: object }`

### `GET /state/{session_id}`
Get full state for a session.

---

## 5. App Runtime (Port 8015)

Manages application lifecycle, sandboxed execution, and resource allocation.

### `GET /health`

### `POST /apps/install`
Install an application.
- **Body**: `{ app_id: string, source: "store"|"url"|"local", manifest: object }`
- **Response**: `{ app_id, status, sandbox_id }`

### `GET /apps`
List installed applications.

### `GET /apps/{id}`
Get application details and permissions.

### `DELETE /apps/{id}/uninstall`
Uninstall an application.

### `POST /apps/{id}/launch`
Launch an application in a sandbox.
- **Body**: `{ args?: string[], env?: object, resources?: object }`
- **Response**: `{ process_id, sandbox_id, port }`

### `POST /apps/{id}/stop`
Stop a running application.

### `GET /apps/{id}/logs`
Get application logs.
- **Query**: `{ tail?: number, follow?: boolean }`

### `GET /processes`
List running processes.

### `GET /processes/{id}`
Get process details and resource usage.

### `POST /processes/{id}/signal`
Send a signal to a process.
- **Body**: `{ signal: "SIGTERM"|"SIGKILL"|"SIGINT" }`

### `GET /apps/{id}/permissions`
Get app permission manifest.

### `PUT /apps/{id}/permissions`
Update app permissions.
- **Body**: `{ permissions: object }`

### `GET /sandboxes`
List active sandboxes.

### `GET /resources`
Get resource usage statistics (CPU, memory, disk).

---

## 6. AI Studio (Port 8016)

Model fine-tuning, prompt engineering, and AI experimentation.

### `GET /health`

### `POST /models/fine-tune`
Start a fine-tuning job.
- **Body**: `{ base_model: string, training_data: object[], hyperparameters: object }`
- **Response**: `{ job_id, status }`

### `GET /models/fine-tune/{id}`
Get fine-tuning job status.

### `POST /models/fine-tune/{id}/cancel`
Cancel a fine-tuning job.

### `POST /prompts/test`
Test a prompt template.
- **Body**: `{ prompt: string, model: string, variables: object, parameters?: object }`
- **Response**: `{ output, tokens_used, latency_ms }`

### `POST /prompts/optimize`
Optimize a prompt for better results.
- **Body**: `{ prompt: string, target_model: string, criteria?: object }`

### `POST /evaluations/run`
Run an evaluation suite.
- **Body**: `{ test_cases: object[], model: string, metrics: string[] }`

### `GET /evaluations/{id}`
Get evaluation results.

### `GET /models`
List available models and their status.

### `GET /models/{id}`
Get model metadata and capabilities.

### `POST /models/{id}/deploy`
Deploy a custom model.
- **Body**: `{ model_id: string, endpoint: string, config: object }`

### `DELETE /models/{id}`
Undeploy a model.

### `GET /models/{id}/usage`
Get model usage statistics and costs.

---

## 7. Security Core (Port 8017)

Zero-trust authentication, authorization, audit logging, and sandbox enforcement.

### `GET /health`

### `POST /auth/login`
Authenticate a user.
- **Body**: `{ method: "password"|"oauth"|"key", credentials: object }`
- **Response**: `{ token, refresh_token, expires_in, user }`

### `POST /auth/refresh`
Refresh authentication token.
- **Body**: `{ refresh_token: string }`

### `POST /auth/logout`
Invalidate current session.

### `GET /auth/verify`
Verify a token's validity.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ valid, user, permissions[] }`

### `POST /auth/mfa/setup`
Configure MFA for a user.
- **Body**: `{ method: "totp"|"sms"|"email" }`

### `POST /auth/mfa/verify`
Verify MFA code.

### `POST /auth/oauth/{provider}`
OAuth2 login gateway.
- **Providers**: `google`, `github`, `microsoft`

### `GET /policies`
List all security policies.

### `POST /policies`
Create a security policy.
- **Body**: `{ name: string, rules: object[], effect: "allow"|"deny", priority: int }`

### `PUT /policies/{id}`
Update a security policy.

### `DELETE /policies/{id}`
Delete a security policy.

### `POST /sandbox/validate`
Validate a sandbox configuration.
- **Body**: `{ sandbox_id: string, config: object }`
- **Response**: `{ valid, violations[], score }`

### `GET /audit`
Query audit logs.
- **Query**: `{ user_id?, service?, action?, from?, to?, limit?, offset? }`
- **Response**: `{ logs: object[], total, page }`

### `POST /audit/export`
Export audit logs.
- **Body**: `{ format: "json"|"csv", date_range: object, filters?: object }`

### `POST /permissions/check`
Check if an action is permitted.
- **Body**: `{ user_id: string, resource: string, action: string, context?: object }`

### `GET /permissions/{user_id}`
Get all permissions for a user.

### `PUT /permissions/{user_id}`
Update user permissions.
- **Body**: `{ permissions: object, roles: string[] }`

### `GET /threats`
Get current threat intelligence feed.

### `POST /threats/report`
Report a security threat.
- **Body**: `{ type: string, severity: string, details: object }`

### `GET /rate-limits`
Get current rate limit status.

### `POST /encryption/encrypt`
Encrypt data with the system key.
- **Body**: `{ data: object, context?: string }`

### `POST /encryption/decrypt`
Decrypt data.
- **Body**: `{ encrypted_data: string, context?: string }`

---

## Common Response Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not found |
| 409  | Conflict |
| 422  | Unprocessable entity |
| 429  | Rate limited |
| 500  | Internal server error |
| 503  | Service unavailable |

All endpoints accept `Content-Type: application/json` and require
`Authorization: Bearer <token>` unless otherwise noted.
