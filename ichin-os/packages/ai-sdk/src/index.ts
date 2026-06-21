import type {
  AgentDefinition, AgentReasoningStyle, MemoryType, WorkflowDefinition,
  WorkflowTrigger, WorkflowTriggerType, WorkflowAction, WorkflowActionType,
  WorkflowNode, WorkflowNodeType, WorkspaceType, RequestType,
  OrchestratorDecision, AgentName,
} from '@ichin/shared-types'

export class AgentBuilder {
  private id = ''
  private name = ''
  private role = ''
  private reasoningStyle: AgentReasoningStyle = 'analytical'
  private tools: string[] = []
  private memoryScope: MemoryType[] = ['working']
  private confidenceThreshold = 0.7
  private riskSensitivity = 0.5
  private enabled = true

  setId(id: string): this {
    this.id = id
    return this
  }

  setName(name: string): this {
    this.name = name
    return this
  }

  setRole(role: string): this {
    this.role = role
    return this
  }

  setReasoningStyle(style: AgentReasoningStyle): this {
    this.reasoningStyle = style
    return this
  }

  setTools(tools: string[]): this {
    this.tools = tools
    return this
  }

  setMemoryScope(scope: MemoryType[]): this {
    this.memoryScope = scope
    return this
  }

  setConfidenceThreshold(threshold: number): this {
    this.confidenceThreshold = threshold
    return this
  }

  setRiskSensitivity(sensitivity: number): this {
    this.riskSensitivity = sensitivity
    return this
  }

  setEnabled(enabled: boolean): this {
    this.enabled = enabled
    return this
  }

  build(): AgentDefinition {
    if (!this.id) throw new Error('AgentBuilder: id is required')
    if (!this.name) throw new Error('AgentBuilder: name is required')
    if (!this.role) throw new Error('AgentBuilder: role is required')

    return {
      id: this.id,
      name: this.name,
      role: this.role,
      reasoningStyle: this.reasoningStyle,
      allowedTools: this.tools,
      memoryScope: this.memoryScope,
      confidenceThreshold: this.confidenceThreshold,
      riskSensitivity: this.riskSensitivity,
      enabled: this.enabled,
    }
  }
}

export class WorkflowBuilder {
  private id = ''
  private name = ''
  private description = ''
  private trigger: WorkflowTrigger = { type: 'manual', config: {} }
  private actions: WorkflowAction[] = []
  private nodes: WorkflowNode[] = []
  private enabled = true

  setId(id: string): this {
    this.id = id
    return this
  }

  setName(name: string): this {
    this.name = name
    return this
  }

  setDescription(description: string): this {
    this.description = description
    return this
  }

  setEnabled(enabled: boolean): this {
    this.enabled = enabled
    return this
  }

  addTrigger(type: WorkflowTriggerType, config: Record<string, unknown> = {}): this {
    this.trigger = { type, config }
    return this
  }

  addCondition(config: Record<string, unknown>): this {
    this.nodes.push({
      id: `condition-${this.nodes.length + 1}`,
      type: 'condition',
      config,
      position: { x: 0, y: 0 },
      connections: [],
    })
    return this
  }

  addAIAction(config: Record<string, unknown>): this {
    this.nodes.push({
      id: `ai-${this.nodes.length + 1}`,
      type: 'ai',
      config,
      position: { x: 0, y: 0 },
      connections: [],
    })
    return this
  }

  addAction(type: WorkflowActionType, config: Record<string, unknown> = {}): this {
    const action: WorkflowAction = { type, config }
    this.actions.push(action)
    return this
  }

  addOutput(config: Record<string, unknown>): this {
    this.nodes.push({
      id: `output-${this.nodes.length + 1}`,
      type: 'output',
      config,
      position: { x: 0, y: 0 },
      connections: [],
    })
    return this
  }

  connect(fromId: string, toId: string): this {
    const from = this.nodes.find((n) => n.id === fromId)
    if (from) {
      from.connections.push(toId)
    }
    return this
  }

  build(): WorkflowDefinition {
    if (!this.id) throw new Error('WorkflowBuilder: id is required')
    if (!this.name) throw new Error('WorkflowBuilder: name is required')

    const now = Date.now()
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      trigger: this.trigger,
      actions: this.actions,
      enabled: this.enabled,
      createdAt: now,
      updatedAt: now,
    }
  }
}

export class MemoryQueryBuilder {
  private workspace?: WorkspaceType
  private memoryType?: MemoryType
  private relevanceThreshold = 0.5
  private limit = 50
  private context?: Record<string, unknown>

  setWorkspace(workspace: WorkspaceType): this {
    this.workspace = workspace
    return this
  }

  setMemoryType(type: MemoryType): this {
    this.memoryType = type
    return this
  }

  setRelevanceThreshold(threshold: number): this {
    this.relevanceThreshold = threshold
    return this
  }

  setLimit(limit: number): this {
    this.limit = limit
    return this
  }

  setContext(context: Record<string, unknown>): this {
    this.context = context
    return this
  }

  build(): Record<string, unknown> {
    const query: Record<string, unknown> = {
      relevanceThreshold: this.relevanceThreshold,
      limit: this.limit,
    }
    if (this.workspace) query.workspace = this.workspace
    if (this.memoryType) query.memoryType = this.memoryType
    if (this.context) query.context = this.context
    return query
  }
}

export class AIOrchestratorClient {
  private baseUrl: string

  constructor(baseUrl = 'http://localhost:8011') {
    this.baseUrl = baseUrl
  }

  async orchestrate(input: string): Promise<OrchestratorDecision> {
    const res = await fetch(`${this.baseUrl}/api/orchestrate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input }),
    })
    if (!res.ok) throw new Error(`Orchestrator request failed: ${res.status}`)
    return res.json()
  }

  async classify(input: string): Promise<{ requestType: RequestType; urgency: string }> {
    const res = await fetch(`${this.baseUrl}/api/classify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input }),
    })
    if (!res.ok) throw new Error(`Classification request failed: ${res.status}`)
    return res.json()
  }

  async getContext(workspace: WorkspaceType): Promise<Record<string, unknown>> {
    const res = await fetch(`${this.baseUrl}/api/context?workspace=${workspace}`)
    if (!res.ok) throw new Error(`Context request failed: ${res.status}`)
    return res.json()
  }

  async getAgentStatus(agent: AgentName): Promise<Record<string, unknown>> {
    const res = await fetch(`${this.baseUrl}/api/agents/${agent}`)
    if (!res.ok) throw new Error(`Agent status request failed: ${res.status}`)
    return res.json()
  }
}

export class PermissionsHelper {
  static REQUIRED_PERMISSIONS: Record<string, string[]> = {
    memory: ['MEMORY_READ'],
    network: ['NETWORK_ACCESS'],
    files: ['FILE_ACCESS'],
    calendar: ['CALENDAR_ACCESS'],
    notifications: ['NOTIFICATIONS_ACCESS'],
    workspace: ['WORKSPACE_INTEGRATION'],
    ai: ['AI_ACCESS'],
  }

  static checkPermission(
    required: string,
    granted: string[]
  ): { allowed: boolean; missing: string[] } {
    const needed = PermissionsHelper.REQUIRED_PERMISSIONS[required] || [required]
    const missing = needed.filter((p) => !granted.includes(p))
    return { allowed: missing.length === 0, missing }
  }

  static validateAppPermissions(
    requested: string[],
    sandboxLevel: number
  ): { valid: boolean; violations: string[] } {
    const levelPermissions: Record<number, string[]> = {
      1: ['AI_ACCESS', 'NOTIFICATIONS_ACCESS'],
      2: ['AI_ACCESS', 'NOTIFICATIONS_ACCESS', 'MEMORY_READ'],
      3: ['AI_ACCESS', 'NOTIFICATIONS_ACCESS', 'MEMORY_READ', 'FILE_ACCESS', 'WORKSPACE_INTEGRATION'],
      4: ['AI_ACCESS', 'NOTIFICATIONS_ACCESS', 'MEMORY_READ', 'FILE_ACCESS', 'WORKSPACE_INTEGRATION', 'NETWORK_ACCESS', 'CALENDAR_ACCESS'],
    }
    const allowed = levelPermissions[sandboxLevel] || levelPermissions[1]
    const violations = requested.filter((p) => !allowed.includes(p))
    return { valid: violations.length === 0, violations }
  }

  static permissionTypeToLevel(type: string): 'none' | 'read' | 'write' | 'admin' {
    const levels: Record<string, 'none' | 'read' | 'write' | 'admin'> = {
      AI_ACCESS: 'admin',
      MEMORY_READ: 'read',
      FILE_ACCESS: 'write',
      NETWORK_ACCESS: 'write',
      WORKSPACE_INTEGRATION: 'write',
      CALENDAR_ACCESS: 'read',
      NOTIFICATIONS_ACCESS: 'read',
    }
    return levels[type] || 'none'
  }
}
