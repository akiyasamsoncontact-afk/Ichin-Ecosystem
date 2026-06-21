import { useFocusStore } from '../stores/focusStore'

const FOCUS_CONFIG: Record<string, { label: string; description: string; color: string }> = {
  normal: { label: 'Normal Mode', description: 'All processes allowed. Full system access.', color: '#666' },
  focus: { label: 'Focus Mode', description: 'Non-essential notifications suppressed. Distractions minimized.', color: '#00E676' },
  deep_focus: { label: 'Deep Focus Mode', description: 'Only critical notifications. All social/entertainment blocked.', color: '#FFB300' },
  lock: { label: 'Lock Mode', description: 'Maximum restriction. Only essential apps allowed.', color: '#FF5252' },
}

export default function FocusOverlay() {
  const mode = useFocusStore((s) => s.mode)
  const blockedProcesses = useFocusStore((s) => s.blockedProcesses)
  const config = FOCUS_CONFIG[mode]

  if (mode === 'normal') return null

  return (
    <div style={{
      position: 'fixed',
      top: 44,
      left: 0,
      right: 0,
      zIndex: 30,
      pointerEvents: 'none',
      display: 'flex',
      justifyContent: 'center',
    }}>
      <div style={{
        maxWidth: 480,
        width: '100%',
        background: config.color + '08',
        borderLeft: `1px solid ${config.color}30`,
        borderRight: `1px solid ${config.color}30`,
        borderBottom: `1px solid ${config.color}30`,
        borderRadius: '0 0 16px 16px',
        padding: '10px 24px',
        textAlign: 'center',
      }}>
        <span style={{ fontSize: 13, fontWeight: 500, color: config.color }}>{config.label}</span>
        <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginTop: 2 }}>{config.description}</p>
        {blockedProcesses.length > 0 && (
          <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 6 }}>
            {blockedProcesses.map((p) => (
              <span key={p} style={{
                fontSize: 9,
                padding: '2px 8px',
                borderRadius: 8,
                background: 'rgba(255,255,255,0.05)',
                color: 'rgba(255,255,255,0.3)',
              }}>
                Blocked: {p}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
