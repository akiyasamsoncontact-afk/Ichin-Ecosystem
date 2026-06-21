import { create } from 'zustand'
import type { Task, MemoryItem, WorkflowDefinition, AgentDefinition, AppInstance } from '../types'
import { memoryApi, appsApi, studioApi, securityApi } from '../services/api'

interface AppStore {
  tasks: Task[]
  memories: MemoryItem[]
  workflows: WorkflowDefinition[]
  agents: AgentDefinition[]
  processes: unknown[]
  apps: AppInstance[]
  loadTasks: () => Promise<void>
  loadMemories: () => Promise<void>
  loadWorkflows: () => Promise<void>
  loadAgents: () => Promise<void>
  loadProcesses: () => Promise<void>
  loadApps: () => Promise<void>
  addTask: (task: Task) => void
  toggleTask: (id: string) => void
  removeTask: (id: string) => void
}

export const useAppStore = create<AppStore>((set, get) => ({
  tasks: [],
  memories: [],
  workflows: [],
  agents: [],
  processes: [],
  apps: [],

  loadTasks: async () => {
    try {
      const { results } = await memoryApi.query('tasks')
      const tasks: Task[] = (results || [])
        .filter((m) => m.type === 'task')
        .map((m) => JSON.parse(m.content))
      set({ tasks })
    } catch { /* offline */ }
  },

  loadMemories: async () => {
    try {
      const { results } = await memoryApi.query('recent')
      set({ memories: results || [] })
    } catch { /* offline */ }
  },

  loadWorkflows: async () => {
    try {
      const wfs = await studioApi.listWorkflows()
      set({ workflows: wfs || [] })
    } catch { /* offline */ }
  },

  loadAgents: async () => {
    try {
      const agents = await studioApi.listAgents()
      set({ agents: agents || [] })
    } catch { /* offline */ }
  },

  loadProcesses: async () => {
    try {
      const processes = await securityApi.listProcesses()
      set({ processes: processes || [] })
    } catch { /* offline */ }
  },

  loadApps: async () => {
    try {
      const apps = await appsApi.listInstalled()
      set({ apps: apps || [] })
    } catch { /* offline */ }
  },

  addTask: (task) => set((s) => ({ tasks: [...s.tasks, task] })),
  toggleTask: (id) =>
    set((s) => ({
      tasks: s.tasks.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t)),
    })),
  removeTask: (id) =>
    set((s) => ({ tasks: s.tasks.filter((t) => t.id !== id) })),
}))
