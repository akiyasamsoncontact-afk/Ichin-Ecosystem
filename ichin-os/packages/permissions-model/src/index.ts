import type { Permission, PermissionType, SandboxLevel } from '@ichin/shared-types'

export type PermissionLevel = 'none' | 'read' | 'write' | 'admin'

export interface PermissionCheckResult {
  granted: boolean
  reason: string
  requiredLevel: PermissionLevel
}

export class PermissionRegistry {
  private static instance: PermissionRegistry
  private permissions: Map<string, Permission> = new Map()

  private constructor() {}

  static getInstance(): PermissionRegistry {
    if (!PermissionRegistry.instance) {
      PermissionRegistry.instance = new PermissionRegistry()
    }
    return PermissionRegistry.instance
  }

  register(permission: Permission): void {
    this.permissions.set(permission.id, permission)
  }

  registerMany(permissions: Permission[]): void {
    permissions.forEach((p) => this.permissions.set(p.id, p))
  }

  get(id: string): Permission | undefined {
    return this.permissions.get(id)
  }

  getAll(): Permission[] {
    return Array.from(this.permissions.values())
  }

  getByType(type: PermissionType): Permission[] {
    return Array.from(this.permissions.values()).filter((p) => p.permissionType === type)
  }

  getGranted(): Permission[] {
    return Array.from(this.permissions.values()).filter((p) => p.granted)
  }

  revoke(id: string): void {
    const perm = this.permissions.get(id)
    if (perm) {
      perm.granted = false
    }
  }

  grant(id: string): void {
    const perm = this.permissions.get(id)
    if (perm) {
      perm.granted = true
    }
  }

  clear(): void {
    this.permissions.clear()
  }

  get size(): number {
    return this.permissions.size
  }
}

export class PermissionValidator {
  private readonly hierarchy: Record<PermissionLevel, number> = {
    none: 0,
    read: 1,
    write: 2,
    admin: 3,
  }

  private readonly typeLevelMap: Record<PermissionType, PermissionLevel> = {
    AI_ACCESS: 'admin',
    MEMORY_READ: 'read',
    FILE_ACCESS: 'write',
    NETWORK_ACCESS: 'write',
    WORKSPACE_INTEGRATION: 'write',
    CALENDAR_ACCESS: 'read',
    NOTIFICATIONS_ACCESS: 'read',
  }

  validatePermission(requested: string, granted: string[]): PermissionCheckResult {
    const granted_set = new Set(granted)
    if (granted_set.has(requested)) {
      return { granted: true, reason: 'Permission granted', requiredLevel: 'none' }
    }
    return { granted: false, reason: `Missing permission: ${requested}`, requiredLevel: 'none' }
  }

  checkHierarchy(required: PermissionLevel, actual: PermissionLevel): boolean {
    return this.hierarchy[actual] >= this.hierarchy[required]
  }

  evaluateRisk(permissionType: PermissionType): number {
    const riskMap: Record<PermissionType, number> = {
      AI_ACCESS: 0.8,
      MEMORY_READ: 0.5,
      FILE_ACCESS: 0.7,
      NETWORK_ACCESS: 0.9,
      WORKSPACE_INTEGRATION: 0.4,
      CALENDAR_ACCESS: 0.3,
      NOTIFICATIONS_ACCESS: 0.2,
    }
    return riskMap[permissionType] ?? 0.5
  }

  validateBatch(requests: string[], granted: string[]): PermissionCheckResult[] {
    return requests.map((r) => this.validatePermission(r, granted))
  }

  getRequiredLevel(type: PermissionType): PermissionLevel {
    return this.typeLevelMap[type] || 'none'
  }

  isSufficientLevel(required: PermissionLevel, actual: PermissionLevel): boolean {
    return this.checkHierarchy(required, actual)
  }
}

export class SandboxLevelMapper {
  private static readonly levelConfig: Record<SandboxLevel, {
    label: string
    allowedPermissions: PermissionType[]
    maxProcesses: number
    networkAccess: boolean
    memoryAccess: boolean
  }> = {
    1: {
      label: 'Restricted',
      allowedPermissions: ['AI_ACCESS', 'NOTIFICATIONS_ACCESS'],
      maxProcesses: 2,
      networkAccess: false,
      memoryAccess: false,
    },
    2: {
      label: 'Standard',
      allowedPermissions: ['AI_ACCESS', 'NOTIFICATIONS_ACCESS', 'MEMORY_READ'],
      maxProcesses: 5,
      networkAccess: false,
      memoryAccess: true,
    },
    3: {
      label: 'Expanded',
      allowedPermissions: [
        'AI_ACCESS', 'NOTIFICATIONS_ACCESS', 'MEMORY_READ',
        'FILE_ACCESS', 'WORKSPACE_INTEGRATION',
      ],
      maxProcesses: 10,
      networkAccess: false,
      memoryAccess: true,
    },
    4: {
      label: 'Full',
      allowedPermissions: [
        'AI_ACCESS', 'NOTIFICATIONS_ACCESS', 'MEMORY_READ',
        'FILE_ACCESS', 'WORKSPACE_INTEGRATION',
        'NETWORK_ACCESS', 'CALENDAR_ACCESS',
      ],
      maxProcesses: 25,
      networkAccess: true,
      memoryAccess: true,
    },
  }

  static getAllowedPermissions(level: SandboxLevel): PermissionType[] {
    const config = SandboxLevelMapper.levelConfig[level]
    return config ? [...config.allowedPermissions] : []
  }

  static getLabel(level: SandboxLevel): string {
    return SandboxLevelMapper.levelConfig[level]?.label ?? 'Unknown'
  }

  static canAccessNetwork(level: SandboxLevel): boolean {
    return SandboxLevelMapper.levelConfig[level]?.networkAccess ?? false
  }

  static canAccessMemory(level: SandboxLevel): boolean {
    return SandboxLevelMapper.levelConfig[level]?.memoryAccess ?? false
  }

  static getMaxProcesses(level: SandboxLevel): number {
    return SandboxLevelMapper.levelConfig[level]?.maxProcesses ?? 0
  }

  static validatePermissionForLevel(type: PermissionType, level: SandboxLevel): boolean {
    const allowed = SandboxLevelMapper.getAllowedPermissions(level)
    return allowed.includes(type)
  }

  static getAllLevels(): SandboxLevel[] {
    return [1, 2, 3, 4]
  }

  static getConfig(level: SandboxLevel) {
    return SandboxLevelMapper.levelConfig[level] ?? null
  }
}

export class DefaultPermissions {
  static readonly AI_ACCESS: Permission = {
    id: 'perm-ai-access',
    name: 'AI Access',
    description: 'Access to AI inference and agent communication',
    granted: false,
    permissionType: 'AI_ACCESS',
  }

  static readonly MEMORY_READ: Permission = {
    id: 'perm-memory-read',
    name: 'Memory Read',
    description: 'Read access to the memory store',
    granted: false,
    permissionType: 'MEMORY_READ',
  }

  static readonly FILE_ACCESS: Permission = {
    id: 'perm-file-access',
    name: 'File Access',
    description: 'Read and write access to the file system',
    granted: false,
    permissionType: 'FILE_ACCESS',
  }

  static readonly NETWORK_ACCESS: Permission = {
    id: 'perm-network-access',
    name: 'Network Access',
    description: 'Access to external network resources',
    granted: false,
    permissionType: 'NETWORK_ACCESS',
  }

  static readonly WORKSPACE_INTEGRATION: Permission = {
    id: 'perm-workspace-integration',
    name: 'Workspace Integration',
    description: 'Integration with workspace context and data',
    granted: false,
    permissionType: 'WORKSPACE_INTEGRATION',
  }

  static readonly CALENDAR_ACCESS: Permission = {
    id: 'perm-calendar-access',
    name: 'Calendar Access',
    description: 'Read and write access to calendar events',
    granted: false,
    permissionType: 'CALENDAR_ACCESS',
  }

  static readonly NOTIFICATIONS_ACCESS: Permission = {
    id: 'perm-notifications-access',
    name: 'Notifications Access',
    description: 'Ability to send and manage system notifications',
    granted: false,
    permissionType: 'NOTIFICATIONS_ACCESS',
  }

  static getAll(): Permission[] {
    return [
      DefaultPermissions.AI_ACCESS,
      DefaultPermissions.MEMORY_READ,
      DefaultPermissions.FILE_ACCESS,
      DefaultPermissions.NETWORK_ACCESS,
      DefaultPermissions.WORKSPACE_INTEGRATION,
      DefaultPermissions.CALENDAR_ACCESS,
      DefaultPermissions.NOTIFICATIONS_ACCESS,
    ]
  }

  static getForSandboxLevel(level: SandboxLevel): Permission[] {
    const allowed = SandboxLevelMapper.getAllowedPermissions(level)
    return DefaultPermissions.getAll().filter((p) => allowed.includes(p.permissionType))
  }
}

export { PermissionRegistry as PermRegistry }
