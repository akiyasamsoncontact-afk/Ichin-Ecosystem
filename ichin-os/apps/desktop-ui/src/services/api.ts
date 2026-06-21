import type { AgentName, AgentOutput, CouncilDecision, OrbNotification, MemoryItem, Task, AppManifest, AppInstance, WorkflowDefinition, AgentDefinition, UIState, FocusState } from '../types'

const BASE = {
  ORCHESTRATOR: 'http://localhost:8011',
  AGENTS: 'http://localhost:8012',
  MEMORY: 'http://localhost:8013',
  UI: 'http://localhost:8014',
  APPS: 'http://localhost:8015',
  STUDIO: 'http://localhost:8016',
  SECURITY: 'http://localhost:8017',
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(url, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options?.headers },
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return (await res.json()) as T
  } catch {
    throw new Error(`API unavailable: ${url}`)
  }
}

export const orchestratorApi = {
  orchestrate: (input: string) =>
    request<{ decision: CouncilDecision }>(`${BASE.ORCHESTRATOR}/orchestrate`, { method: 'POST', body: JSON.stringify({ input }) }),
  classify: (text: string) =>
    request<{ category: string; confidence: number }>(`${BASE.ORCHESTRATOR}/classify`, { method: 'POST', body: JSON.stringify({ text }) }),
  context: (query: string) =>
    request<{ context: Record<string, unknown> }>(`${BASE.ORCHESTRATOR}/context`, { method: 'POST', body: JSON.stringify({ query }) }),
}

export const agentsApi = {
  reason: (name: AgentName, input: string) =>
    request<AgentOutput>(`${BASE.AGENTS}/agents/${name}/reason`, { method: 'POST', body: JSON.stringify({ input }) }),
  orchestrate: (input: string) =>
    request<{ outputs: AgentOutput[] }>(`${BASE.AGENTS}/agents/orchestrate`, { method: 'POST', body: JSON.stringify({ input }) }),
}

export const memoryApi = {
  store: (item: Partial<MemoryItem>) =>
    request<MemoryItem>(`${BASE.MEMORY}/memory/store`, { method: 'POST', body: JSON.stringify(item) }),
  query: (query: string) =>
    request<{ results: MemoryItem[] }>(`${BASE.MEMORY}/memory/query`, { method: 'POST', body: JSON.stringify({ query }) }),
  promote: (id: string) =>
    request<MemoryItem>(`${BASE.MEMORY}/memory/promote`, { method: 'POST', body: JSON.stringify({ id }) }),
}

export const uiApi = {
  getState: () => request<UIState>(`${BASE.UI}/ui/state`),
  sendIntent: (intent: string, payload?: Record<string, unknown>) =>
    request<{ ok: boolean }>(`${BASE.UI}/ui/intent`, { method: 'POST', body: JSON.stringify({ intent, ...payload }) }),
  orb: {
    setState: (state: string) => request<{ ok: boolean }>(`${BASE.UI}/ui/orb/state`, { method: 'POST', body: JSON.stringify({ state }) }),
    notify: (notification: Partial<OrbNotification>) =>
      request<OrbNotification>(`${BASE.UI}/ui/orb/notify`, { method: 'POST', body: JSON.stringify(notification) }),
    dismiss: (id: string) => request<{ ok: boolean }>(`${BASE.UI}/ui/orb/dismiss`, { method: 'POST', body: JSON.stringify({ id }) }),
  },
  focus: {
    setMode: (mode: string) => request<{ ok: boolean }>(`${BASE.UI}/ui/focus/mode`, { method: 'POST', body: JSON.stringify({ mode }) }),
    getState: () => request<FocusState>(`${BASE.UI}/ui/focus/state`),
    block: (process: string) => request<{ ok: boolean }>(`${BASE.UI}/ui/focus/block`, { method: 'POST', body: JSON.stringify({ process }) }),
  },
}

export const appsApi = {
  listInstalled: () => request<AppInstance[]>(`${BASE.APPS}/apps`),
  getApp: (id: string) => request<AppInstance>(`${BASE.APPS}/apps/${id}`),
  install: (id: string) => request<{ ok: boolean }>(`${BASE.APPS}/apps/${id}/install`, { method: 'POST' }),
  uninstall: (id: string) => request<{ ok: boolean }>(`${BASE.APPS}/apps/${id}/uninstall`, { method: 'POST' }),
  storeList: () => request<{ apps: AppManifest[] }>(`${BASE.APPS}/store`),
}

export const studioApi = {
  listWorkflows: () => request<WorkflowDefinition[]>(`${BASE.STUDIO}/workflow`),
  createWorkflow: (wf: Partial<WorkflowDefinition>) =>
    request<WorkflowDefinition>(`${BASE.STUDIO}/workflow`, { method: 'POST', body: JSON.stringify(wf) }),
  listAgents: () => request<AgentDefinition[]>(`${BASE.STUDIO}/agent`),
  createAgent: (agent: Partial<AgentDefinition>) =>
    request<AgentDefinition>(`${BASE.STUDIO}/agent`, { method: 'POST', body: JSON.stringify(agent) }),
  train: (config: Record<string, unknown>) =>
    request<{ ok: boolean }>(`${BASE.STUDIO}/training`, { method: 'POST', body: JSON.stringify(config) }),
}

export const securityApi = {
  listProcesses: () => request<unknown[]>(`${BASE.SECURITY}/processes`),
  securityCheck: (action: string) =>
    request<{ allowed: boolean }>(`${BASE.SECURITY}/security/check`, { method: 'POST', body: JSON.stringify({ action }) }),
  createSnapshot: (label: string) =>
    request<{ id: string }>(`${BASE.SECURITY}/snapshots`, { method: 'POST', body: JSON.stringify({ label }) }),
  listSnapshots: () => request<unknown[]>(`${BASE.SECURITY}/snapshots`),
}

export const aiRouterApi = {
  complete: (prompt: string, model?: string, strategy?: string) =>
    request<{ response: string; model_used: string; strategy: string }>(`http://localhost:8020/complete`, { method: 'POST', body: JSON.stringify({ prompt, model, strategy }) }),
  health: () => request<{ status: string }>(`http://localhost:8020/health`),
  models: () => request<{ providers: string[] }>(`http://localhost:8020/models`),
}

export const voiceEngineApi = {
  speak: (text: string, personality?: string) =>
    request<{ text: string; audio: string; personality: string }>(`http://localhost:8030/api/tts`, { method: 'POST', body: JSON.stringify({ text, personality }) }),
  transcribe: (audioData: string) =>
    request<{ text: string }>(`http://localhost:8030/api/stt`, { method: 'POST', body: JSON.stringify({ audio_data: audioData }) }),
  personalities: () => request<{ personalities: string[] }>(`http://localhost:8030/api/personalities`),
}

export const browserEngineApi = {
  navigate: (url: string) =>
    request<{ status: string; session_id: string }>(`http://localhost:8040/api/navigate`, { method: 'POST', body: JSON.stringify({ url }) }),
  extract: () =>
    request<{ content: Record<string, unknown> }>(`http://localhost:8040/api/extract`, { method: 'POST' }),
  research: (query: string) =>
    request<{ findings: Record<string, unknown> }>(`http://localhost:8040/api/research`, { method: 'POST', body: JSON.stringify({ query }) }),
}

export const metasearchApi = {
  search: (query: string, engines?: string[]) =>
    request<{ results: unknown[]; total: number }>(`http://localhost:8050/api/search`, { method: 'POST', body: JSON.stringify({ query, engines }) }),
  spotlight: (query: string) =>
    request<{ results: unknown[] }>(`http://localhost:8050/api/spotlight`, { method: 'POST', body: JSON.stringify({ query }) }),
}

export const mailAiApi = {
  process: (email: Record<string, unknown>) =>
    request<{ category: string; priority: string; summary: string }>(`http://localhost:8060/api/process`, { method: 'POST', body: JSON.stringify(email) }),
}

export const knowledgeGraphApi = {
  query: (query: string, workspace?: string) =>
    request<{ nodes: unknown[]; edges: unknown[] }>(`http://localhost:8070/api/query`, { method: 'POST', body: JSON.stringify({ query, workspace }) }),
  workspace: (workspace: string) =>
    request<{ nodes: unknown[]; edges: unknown[] }>(`http://localhost:8070/api/workspace`, { method: 'POST', body: JSON.stringify({ workspace }) }),
}
