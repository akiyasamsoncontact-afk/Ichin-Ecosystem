export type WorkspaceType = 'study' | 'coding' | 'learning' | 'personal'

export type FocusMode = 'normal' | 'focus' | 'deep_focus' | 'lock'

export type OrbState = 'idle' | 'active' | 'critical'

export type AgentName =
  | 'orion' | 'nova' | 'sage' | 'pulse'
  | 'echo' | 'iris' | 'atlas' | 'aegis'

export interface AgentOutput {
  agent: AgentName
  recommendation: string
  confidence: number
  risk: number
  efficiency: number
  reasoning: string
}

export interface CouncilDecision {
  decision: string
  agentsUsed: AgentName[]
  confidence: number
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  reasoning: string
  outputs: AgentOutput[]
}

export interface OrbNotification {
  id: string
  message: string
  state: OrbState
  actions: { label: string; action: string }[]
  timestamp: number
  dismissed?: boolean
}

export interface MemoryItem {
  id: string
  content: string
  type: string
  importance: number
  decay: number
  lastAccessed: number
  context: Record<string, unknown>
}

export interface Task {
  id: string
  title: string
  description?: string
  completed: boolean
  workspace: WorkspaceType
  priority: number
  createdAt: number
  dueDate?: number
  tags: string[]
}

export interface AppManifest {
  id: string
  name: string
  description: string
  version: string
  author: string
  icon: string
  category: string
  permissions: Permission[]
  aiCompatibility: number
  workspaceIntegration: WorkspaceType[]
  rating: number
  aiTested: boolean
}

export interface Permission {
  id: string
  name: string
  description: string
  granted: boolean
}

export interface AppInstance {
  id: string
  manifest: AppManifest
  installed: boolean
  lastUsed?: number
  config: Record<string, unknown>
}

export interface WorkflowDefinition {
  id: string
  name: string
  description: string
  trigger: WorkflowTrigger
  actions: WorkflowAction[]
  enabled: boolean
  createdAt: number
}

export interface WorkflowTrigger {
  type: 'time' | 'event' | 'ai' | 'manual'
  config: Record<string, unknown>
}

export interface WorkflowAction {
  type: string
  config: Record<string, unknown>
}

export interface AgentDefinition {
  id: string
  name: string
  description: string
  baseModel: string
  capabilities: string[]
  temperature: number
  systemPrompt: string
  enabled: boolean
}

export interface UIState {
  activePanel: string | null
  spotlightOpen: boolean
  councilOpen: boolean
  missionControlOpen: boolean
  settingsOpen: boolean
  cheatsheetOpen: boolean
  ambientMode: 'calm' | 'neutral' | 'focus' | 'deep_focus'
  layout: LayoutConfig
  onboardingComplete: boolean
}

export interface LayoutConfig {
  sidebarExpanded: boolean
  panelPositions: Record<string, { x: number; y: number }>
  panelSizes: Record<string, number>
}

export interface FocusState {
  mode: FocusMode
  blockedProcesses: string[]
  sessionStart: number
  totalFocusTime: number
}
