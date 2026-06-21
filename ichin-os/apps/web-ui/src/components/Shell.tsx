import { useWorkspaceStore } from '../stores/workspaceStore'
import { useFocusStore } from '../stores/focusStore'
import { useUIStore } from '../stores/uiStore'
import { WORKSPACE_TITLES } from '../types'

const FOCUS_LABELS: Record<string, string> = {
  normal: 'Normal',
  focus: 'Focus',
  deep_focus: 'Deep Focus',
  lock: 'Lock',
}

const FOCUS_COLORS: Record<string, string> = {
  normal: '#666',
  focus: '#00E676',
  deep_focus: '#FFB300',
  lock: '#FF5252',
}

export default function Shell() {
  const activeWorkspace = useWorkspaceStore((s) => s.active)
  const focusMode = useFocusStore((s) => s.mode)
  const { setSpotlightOpen, setMissionControlOpen, setSettingsOpen } = useUIStore()

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      height: 44,
      padding: '0 16px',
      background: 'rgba(255,255,255,0.05)',
      borderBottom: '1px solid rgba(255,255,255,0.05)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 13, fontWeight: 500, color: 'rgba(255,255,255,0.8)' }}>
          {WORKSPACE_TITLES[activeWorkspace]}
        </span>
        <span style={{
          fontSize: 10,
          padding: '2px 8px',
          borderRadius: 12,
          backgroundColor: FOCUS_COLORS[focusMode] + '20',
          color: FOCUS_COLORS[focusMode],
        }}>
          {FOCUS_LABELS[focusMode]}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <button
          onClick={() => setSpotlightOpen(true)}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '4px 12px', borderRadius: 8,
            fontSize: 11, color: 'rgba(255,255,255,0.4)',
            background: 'transparent', border: 'none', cursor: 'pointer',
          }}
        >
          ⌕ Search...
          <kbd style={{ fontSize: 9, padding: '1px 4px', borderRadius: 4, background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.3)' }}>
            ^Space
          </kbd>
        </button>
        <button
          onClick={() => setMissionControlOpen(true)}
          style={{
            padding: 6, borderRadius: 8,
            color: 'rgba(255,255,255,0.4)',
            background: 'transparent', border: 'none', cursor: 'pointer', fontSize: 14,
          }}
          title="Mission Control"
        >
          ⊞
        </button>
        <button
          onClick={() => setSettingsOpen(true)}
          style={{
            padding: 6, borderRadius: 8,
            color: 'rgba(255,255,255,0.4)',
            background: 'transparent', border: 'none', cursor: 'pointer', fontSize: 14,
          }}
          title="Settings"
        >
          ⚙
        </button>
      </div>
    </div>
  )
}
