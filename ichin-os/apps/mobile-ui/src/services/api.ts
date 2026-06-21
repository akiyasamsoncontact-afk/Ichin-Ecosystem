import axios from 'axios'
import type {
  AgentName, AgentOutput, CouncilDecision, OrbNotification,
  MemoryItem, Task, AppManifest, AppInstance, WorkflowDefinition,
  AgentDefinition, UIState, FocusState,
} from '../types'

const BASE = {
  ORCHESTRATOR: 'http://localhost:8011',
  AGENTS: 'http://localhost:8012',
  MEMORY: 'http://localhost:8013',
  UI: 'http://localhost:8014',
  APPS: 'http://localhost:8015',
  STUDIO: 'http://localhost:8016',
  SECURITY: 'http://localhost:8017',
}

const client = axios.create({ timeout: 10000 })

export const orchestratorApi = {
  orchestrate: (input: string) =>
    client.post<{ decision: CouncilDecision }>(`${BASE.ORCHESTRATOR}/orchestrate`, { input }).then(r => r.data),
  classify: (text: string) =>
    client.post<{ category: string; confidence: number }>(`${BASE.ORCHESTRATOR}/classify`, { text }).then(r => r.data),
  context: (query: string) =>
    client.post<{ context: Record<string, unknown> }>(`${BASE.ORCHESTRATOR}/context`, { query }).then(r => r.data),
}

export const agentsApi = {
  reason: (name: AgentName, input: string) =>
    client.post<AgentOutput>(`${BASE.AGENTS}/agents/${name}/reason`, { input }).then(r => r.data),
  orchestrate: (input: string) =>
    client.post<{ outputs: AgentOutput[] }>(`${BASE.AGENTS}/agents/orchestrate`, { input }).then(r => r.data),
}

export const memoryApi = {
  store: (item: Partial<MemoryItem>) =>
    client.post<MemoryItem>(`${BASE.MEMORY}/memory/store`, item).then(r => r.data),
  query: (query: string) =>
    client.post<{ results: MemoryItem[] }>(`${BASE.MEMORY}/memory/query`, { query }).then(r => r.data),
  promote: (id: string) =>
    client.post<MemoryItem>(`${BASE.MEMORY}/memory/promote`, { id }).then(r => r.data),
}

export const uiApi = {
  getState: () => client.get<UIState>(`${BASE.UI}/ui/state`).then(r => r.data),
  sendIntent: (intent: string, payload?: Record<string, unknown>) =>
    client.post<{ ok: boolean }>(`${BASE.UI}/ui/intent`, { intent, ...payload }).then(r => r.data),
  orb: {
    setState: (state: string) =>
      client.post<{ ok: boolean }>(`${BASE.UI}/ui/orb/state`, { state }).then(r => r.data),
    notify: (notification: Partial<OrbNotification>) =>
      client.post<OrbNotification>(`${BASE.UI}/ui/orb/notify`, notification).then(r => r.data),
    dismiss: (id: string) =>
      client.post<{ ok: boolean }>(`${BASE.UI}/ui/orb/dismiss`, { id }).then(r => r.data),
  },
  focus: {
    setMode: (mode: string) =>
      client.post<{ ok: boolean }>(`${BASE.UI}/ui/focus/mode`, { mode }).then(r => r.data),
    getState: () => client.get<FocusState>(`${BASE.UI}/ui/focus/state`).then(r => r.data),
    block: (process: string) =>
      client.post<{ ok: boolean }>(`${BASE.UI}/ui/focus/block`, { process }).then(r => r.data),
  },
}

export const appsApi = {
  listInstalled: () => client.get<AppInstance[]>(`${BASE.APPS}/apps`).then(r => r.data),
  getApp: (id: string) => client.get<AppInstance>(`${BASE.APPS}/apps/${id}`).then(r => r.data),
  install: (id: string) => client.post<{ ok: boolean }>(`${BASE.APPS}/apps/${id}/install`).then(r => r.data),
  uninstall: (id: string) => client.post<{ ok: boolean }>(`${BASE.APPS}/apps/${id}/uninstall`).then(r => r.data),
  storeList: () => client.get<{ apps: AppManifest[] }>(`${BASE.APPS}/store`).then(r => r.data),
}

export const studioApi = {
  listWorkflows: () => client.get<WorkflowDefinition[]>(`${BASE.STUDIO}/workflow`).then(r => r.data),
  createWorkflow: (wf: Partial<WorkflowDefinition>) =>
    client.post<WorkflowDefinition>(`${BASE.STUDIO}/workflow`, wf).then(r => r.data),
  listAgents: () => client.get<AgentDefinition[]>(`${BASE.STUDIO}/agent`).then(r => r.data),
  createAgent: (agent: Partial<AgentDefinition>) =>
    client.post<AgentDefinition>(`${BASE.STUDIO}/agent`, agent).then(r => r.data),
  train: (config: Record<string, unknown>) =>
    client.post<{ ok: boolean }>(`${BASE.STUDIO}/training`, config).then(r => r.data),
}

export const securityApi = {
  listProcesses: () => client.get<unknown[]>(`${BASE.SECURITY}/processes`).then(r => r.data),
  securityCheck: (action: string) =>
    client.post<{ allowed: boolean }>(`${BASE.SECURITY}/security/check`, { action }).then(r => r.data),
  createSnapshot: (label: string) =>
    client.post<{ id: string }>(`${BASE.SECURITY}/snapshots`, { label }).then(r => r.data),
  listSnapshots: () => client.get<unknown[]>(`${BASE.SECURITY}/snapshots`).then(r => r.data),
}
