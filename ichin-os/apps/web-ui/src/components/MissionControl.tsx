import { useEffect } from 'react'
import { useUIStore } from '../stores/uiStore'

const STATS = [
  { label: 'System Health', value: '98%', icon: '⚡', color: '#00E676' },
  { label: 'Focus Time', value: '4h 32m', icon: '🕐', color: '#4A9EFF' },
  { label: 'Tasks Done', value: '12/18', icon: '✓', color: '#B388FF' },
  { label: 'AI Decisions', value: '147', icon: '🧠', color: '#FFB300' },
]

const RECENT_ACTIONS = [
  { time: '2m ago', text: 'AI Council resolved query about project structure' },
  { time: '15m ago', text: 'Focus Mode activated for coding session' },
  { time: '32m ago', text: 'Memory consolidation completed (142 items)' },
  { time: '1h ago', text: 'New workflow created: Daily Standup Report' },
  { time: '2h ago', text: 'App installed: Advanced Markdown Editor' },
]

const AI_DECISIONS = [
  { agent: 'Orion', action: 'Schedule optimization', confidence: 87, risk: 'low' },
  { agent: 'Nova', action: 'Creative task routing', confidence: 73, risk: 'med' },
  { agent: 'Aegis', action: 'Security audit passed', confidence: 95, risk: 'low' },
]

export default function MissionControl() {
  const isOpen = useUIStore((s) => s.missionControlOpen)
  const setOpen = useUIStore((s) => s.setMissionControlOpen)
  const close = () => setOpen(false)

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close()
    }
    if (isOpen) window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 999 }}>
      <div onClick={close} style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(16px)' }} />
      <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'auto', padding: 24 }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 20, color: 'rgba(255,255,255,0.4)' }}>⊞</span>
              <h1 style={{ fontSize: 20, fontWeight: 300, color: 'rgba(255,255,255,0.8)' }}>Mission Control</h1>
            </div>
            <button onClick={close} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.3)', cursor: 'pointer', fontSize: 16, padding: 6 }}>
              ✕
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }}>
            {STATS.map((stat) => (
              <div key={stat.label} style={{
                background: 'rgba(255,255,255,0.05)',
                borderRadius: 16,
                padding: 16,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                  <span style={{ fontSize: 12, color: stat.color }}>{stat.icon}</span>
                  <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)' }}>{stat.label}</span>
                </div>
                <div style={{ fontSize: 26, fontWeight: 300, color: stat.color }}>{stat.value}</div>
              </div>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 12 }}>
            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 16 }}>
              <h3 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>
                Recent Actions
              </h3>
              {RECENT_ACTIONS.map((a, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, fontSize: 12 }}>
                  <span style={{ fontSize: 9, color: 'rgba(255,255,255,0.2)', width: 50 }}>{a.time}</span>
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'rgba(255,255,255,0.1)' }} />
                  <span style={{ color: 'rgba(255,255,255,0.5)' }}>{a.text}</span>
                </div>
              ))}
            </div>

            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 16 }}>
              <h3 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>
                AI Decisions Log
              </h3>
              {AI_DECISIONS.map((d, i) => (
                <div key={i} style={{ padding: '8px 10px', borderRadius: 10, background: 'rgba(255,255,255,0.03)', marginBottom: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                    <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.7)' }}>{d.agent}</span>
                    <span style={{
                      fontSize: 9,
                      padding: '1px 6px',
                      borderRadius: 6,
                      background: d.risk === 'low' ? 'rgba(0,230,118,0.15)' : 'rgba(255,179,0,0.15)',
                      color: d.risk === 'low' ? '#00E676' : '#FFB300',
                    }}>
                      {d.risk}
                    </span>
                  </div>
                  <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', marginBottom: 4 }}>{d.action}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ flex: 1, height: 3, background: 'rgba(255,255,255,0.05)', borderRadius: 2 }}>
                      <div style={{ height: '100%', width: `${d.confidence}%`, background: 'rgba(0,230,118,0.5)', borderRadius: 2 }} />
                    </div>
                    <span style={{ fontSize: 9, color: 'rgba(255,255,255,0.3)' }}>{d.confidence}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
