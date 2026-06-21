import type { AppManifest, Permission } from '@ichin/shared-types'

export interface AppListItem {
  id: string
  name: string
  description: string
  icon: string
  category: string
  rating: number
  version: string
  author: string
  aiCompatibility: number
  aiTested: boolean
  installs: number
}

export interface AppDetail {
  manifest: AppManifest
  screenshots: string[]
  reviews: AppReview[]
  ratings: { average: number; count: number }
  installs: number
}

export interface AppReview {
  id: string
  appId: string
  status: string
  securityScore: number
  sandboxScore: number
  performanceScore: number
  aiScore: number
  overallScore: number
  issues: string[]
  timestamp: number
}

export interface AppRating {
  id: string
  appId: string
  userId: string
  score: number
  comment: string
  timestamp: number
}

export interface InstallRecord {
  id: string
  appId: string
  installedAt: number
  status: string
  config: Record<string, unknown>
  lastUsed: number | null
}

export interface InstalledApp {
  installRecord: InstallRecord
  manifest: AppManifest
}

export interface Category {
  id: string
  name: string
  description: string
  icon: string
}

export interface AppSubmission {
  name: string
  description: string
  version: string
  author: string
  icon: string
  category: string
  permissions: Permission[]
  aiCompatibility: number
  workspaceIntegration: string[]
  appType: string
  manifestUrl: string
}
