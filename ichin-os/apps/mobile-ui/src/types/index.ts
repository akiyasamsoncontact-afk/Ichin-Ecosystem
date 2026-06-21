import type {
  WorkspaceType, FocusMode, OrbState, AgentName,
  AgentOutput, CouncilDecision, OrbNotification, MemoryItem,
  Task, AppManifest, AppInstance, WorkflowDefinition,
  AgentDefinition, FocusState, UIState,
} from '@ichin/shared-types'

export type {
  WorkspaceType, FocusMode, OrbState, AgentName,
  AgentOutput, CouncilDecision, OrbNotification, MemoryItem,
  Task, AppManifest, AppInstance, WorkflowDefinition,
  AgentDefinition, FocusState, UIState,
}

export const WORKSPACE_COLORS: Record<WorkspaceType, string> = {
  study: '#4A9EFF',
  coding: '#00E676',
  learning: '#B388FF',
  personal: '#9E9E9E',
}

export const ORB_COLORS: Record<OrbState, { main: string; glow: string }> = {
  idle: { main: '#4A9EFF', glow: 'rgba(74, 158, 255, 0.3)' },
  active: { main: '#00E676', glow: 'rgba(0, 230, 118, 0.3)' },
  critical: { main: '#FF5252', glow: 'rgba(255, 82, 82, 0.4)' },
}

export const WORKSPACE_LABELS: Record<WorkspaceType, string> = {
  study: 'Study',
  coding: 'Coding',
  learning: 'Learning',
  personal: 'Personal',
}

export const WORKSPACE_TITLES: Record<WorkspaceType, string> = {
  study: 'Study Space',
  coding: 'Coding Space',
  learning: 'Learning Path',
  personal: 'Personal Space',
}
