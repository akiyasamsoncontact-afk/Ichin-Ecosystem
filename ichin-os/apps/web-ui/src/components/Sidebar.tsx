import type { WorkspaceType } from '../types'
import { useWorkspaceStore } from '../stores/workspaceStore'
import { WORKSPACE_COLORS, WORKSPACE_LABELS } from '../types'

const ICONS: Record<WorkspaceType, string> = {
  study: '📚',
  coding: '💻',
  learning: '🧠',
  personal: '👤',
}

const ORDER: WorkspaceType[] = ['study', 'coding', 'learning', 'personal']

export default function Sidebar() {
  const active = useWorkspaceStore((s) => s.active)
  const setActive = useWorkspaceStore((s) => s.setActive)

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 8,
      padding: '12px 6px',
      borderRight: '1px solid rgba(255,255,255,0.05)',
      background: 'rgba(255,255,255,0.02)',
    }}>
      {ORDER.map((ws) => {
        const isActive = ws === active
        return (
          <button
            key={ws}
            onClick={() => setActive(ws)}
            style={{
              position: 'relative',
              width: 40,
              height: 40,
              borderRadius: 12,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: isActive ? WORKSPACE_COLORS[ws] + '20' : 'transparent',
              border: isActive ? `1px solid ${WORKSPACE_COLORS[ws]}` : '1px solid transparent',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              fontSize: 16,
            }}
            title={WORKSPACE_LABELS[ws]}
          >
            {ICONS[ws]}
          </button>
        )
      })}
    </div>
  )
}
