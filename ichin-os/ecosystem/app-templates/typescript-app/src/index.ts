import type { AppManifest, WorkspaceType } from '@ichin/shared-types'
import { readFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8011'
const MEMORY_URL = process.env.MEMORY_URL || 'http://localhost:8013'
const UI_URL = process.env.UI_URL || 'http://localhost:8014'

interface IchinAppConfig {
  manifest: AppManifest
  context?: Record<string, unknown>
}

class IchinApp {
  public readonly manifest: AppManifest
  private context: Record<string, unknown> = {}
  private memory = new Map<string, unknown>()

  constructor(config: IchinAppConfig) {
    this.manifest = config.manifest
    this.context = config.context ?? {}
  }

  async activate(workspace: WorkspaceType): Promise<void> {
    console.log(`[${this.manifest.name}] Activated in workspace: ${workspace}`)
    this.context['workspace'] = workspace
  }

  async deactivate(): Promise<void> {
    console.log(`[${this.manifest.name}] Deactivated`)
  }

  async aiQuery(prompt: string): Promise<string> {
    const payload = {
      request: prompt,
      mode: 'normal',
      workspace: (this.context['workspace'] as string) || 'system',
    }
    try {
      const resp = await fetch(`${ORCHESTRATOR_URL}/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (resp.ok) {
        const data = await resp.json()
        return data.result || data.FINAL_RESULT || ''
      }
    } catch (e) {
      console.error(`[${this.manifest.name}] Orchestrator error:`, e)
    }
    return ''
  }

  async memorySet(key: string, value: unknown): Promise<void> {
    this.memory.set(key, value)
    try {
      await fetch(`${MEMORY_URL}/memory/store`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, value, type: 'pattern', workspace: this.context['workspace'] || 'system' }),
      })
    } catch (e) {
      console.error(`[${this.manifest.name}] Memory store error:`, e)
    }
  }

  async memoryGet<T>(key: string): Promise<T | undefined> {
    if (this.memory.has(key)) return this.memory.get(key) as T
    try {
      const resp = await fetch(`${MEMORY_URL}/memory/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: key, workspace: this.context['workspace'] || 'system' }),
      })
      if (resp.ok) {
        const data = await resp.json()
        return data as T
      }
    } catch { /* ignore */ }
    return undefined
  }

  async notify(message: string, state: 'idle' | 'active' | 'critical' = 'active'): Promise<void> {
    console.log(`[${this.manifest.name}] Orb [${state}]: ${message}`)
    try {
      await fetch(`${UI_URL}/orb/notify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, state, source: this.manifest.name }),
      })
    } catch { /* ignore */ }
  }
}

function loadManifest(): AppManifest {
  const path = join(__dirname, '..', 'manifest.json')
  return JSON.parse(readFileSync(path, 'utf-8'))
}

async function main() {
  const manifest = loadManifest()
  const app = new IchinApp({ manifest })

  await app.activate('coding')

  console.log(`\n${manifest.name} v${manifest.version}`)
  console.log(`Author: ${manifest.author}`)
  console.log(`Permissions: ${manifest.permissions.map(p => p.id).join(', ')}`)
  console.log(`AI Compatibility: ${(manifest.aiCompatibility * 100).toFixed(0)}%`)

  const result = await app.aiQuery('Hello ICHIN OS')
  console.log(`\nAI says: ${result}`)

  await app.notify(`${manifest.name} is ready`)
  await app.deactivate()
}

main().catch(console.error)
