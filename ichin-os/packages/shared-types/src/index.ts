export type WorkspaceType = 'study' | 'coding' | 'learning' | 'personal'
export type FocusMode = 'normal' | 'focus' | 'deep_focus' | 'lock'
export type OrbState = 'idle' | 'active' | 'critical'
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'
export type RequestType = 'task' | 'question' | 'system_action' | 'chat' | 'automation'
export type UrgencyLevel = 'low' | 'medium' | 'high' | 'critical'
export type ExecutionStatus = 'approved' | 'requires_confirmation' | 'denied' | 'escalated'

export type AgentName =
  | 'orion' | 'nova' | 'sage' | 'pulse'
  | 'echo' | 'iris' | 'atlas' | 'aegis'

export type MemoryType = 'ephemeral' | 'working' | 'long_term' | 'structured'
export type AppType = 'native' | 'web' | 'external'
export type AppStatus = 'running' | 'suspended' | 'terminated'
export type AgentReasoningStyle = 'analytical' | 'creative' | 'structured' | 'hybrid'
export type EventType = 'AI_REQUEST' | 'AGENT_RESPONSE' | 'MEMORY_UPDATE' | 'APP_EVENT' | 'WORKFLOW_TRIGGER' | 'SECURITY_ALERT' | 'UI_STATE_CHANGE'
export type SandboxLevel = 1 | 2 | 3 | 4

export type PermissionType = 'AI_ACCESS' | 'MEMORY_READ' | 'FILE_ACCESS' | 'NETWORK_ACCESS' | 'WORKSPACE_INTEGRATION' | 'CALENDAR_ACCESS' | 'NOTIFICATIONS_ACCESS'

export type WorkflowTriggerType = 'time' | 'event' | 'ai' | 'manual'
export type WorkflowActionType = 'create_task' | 'send_message' | 'schedule_event' | 'summarize' | 'run_agent' | 'modify_ui' | 'trigger_orb'
export type WorkflowNodeType = 'trigger' | 'condition' | 'ai' | 'action' | 'output'

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
  riskLevel: RiskLevel
  reasoning: string
  outputs: AgentOutput[]
}

export interface AgentDefinition {
  id: string
  name: string
  role: string
  reasoningStyle: AgentReasoningStyle
  allowedTools: string[]
  memoryScope: MemoryType[]
  confidenceThreshold: number
  riskSensitivity: number
  enabled: boolean
}

export interface FocusState {
  mode: FocusMode
  blockedProcesses: string[]
  sessionStart: number
  totalFocusTime: number
  workspaces: WorkspaceConfig[]
}

export interface UIState {
  activePanel: string | null
  spotlightOpen: boolean
  councilOpen: boolean
  missionControlOpen: boolean
  settingsOpen: boolean
  cheatsheetOpen: boolean
  ambientMode: boolean
  layout: LayoutConfig
  onboardingComplete: boolean
}

export interface LayoutConfig {
  sidebarExpanded: boolean
  panelPositions: Record<string, { x: number; y: number }>
  panelSizes: Record<string, number>
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
  type: MemoryType
  importance: number
  decay: number
  lastAccessed: number
  context: Record<string, unknown>
  workspace: WorkspaceType
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

export interface Permission {
  id: string
  name: string
  description: string
  granted: boolean
  permissionType: PermissionType
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
  appType: AppType
}

export interface AppInstance {
  id: string
  manifest: AppManifest
  installed: boolean
  lastUsed?: number
  config: Record<string, unknown>
  status: AppStatus
}

export interface WorkflowTrigger {
  type: WorkflowTriggerType
  config: Record<string, unknown>
}

export interface WorkflowAction {
  type: WorkflowActionType
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
  updatedAt: number
}

export interface WorkflowNode {
  id: string
  type: WorkflowNodeType
  config: Record<string, unknown>
  position: { x: number; y: number }
  connections: string[]
}

export interface WorkspaceConfig {
  id: string
  name: string
  type: WorkspaceType
  accentColor: string
  icon: string
  layout: LayoutConfig
}

export interface SystemEvent {
  id: string
  type: EventType
  source: string
  payload: Record<string, unknown>
  timestamp: number
  severity: RiskLevel
}

export interface ProcessInfo {
  id: string
  name: string
  type: string
  pid: number
  status: AppStatus
  priority: number
  cpu: number
  memory: number
  sandboxLevel: SandboxLevel
  startTime: number
}

export interface AuditLog {
  id: string
  processId: string
  permission: string
  action: string
  impact: RiskLevel
  rollbackAvailable: boolean
  timestamp: number
}

export interface RollbackSnapshot {
  id: string
  timestamp: number
  reason: string
  services: string[]
  status: 'pending' | 'completed' | 'failed'
}

export interface UserProfile {
  id: string
  name: string
  workspaces: WorkspaceType[]
  preferences: Record<string, unknown>
  createdAt: number
}

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export interface OrchestratorDecision {
  requestId: string
  requestType: RequestType
  urgency: UrgencyLevel
  execution: ExecutionStatus
  assignedAgents: AgentName[]
  combinedConfidence: number
  riskAssessment: RiskLevel
  reasoning: string
  timestamp: number
}
