import { useState, useEffect } from 'react'
import { useUIStore } from '../stores/uiStore'

const SECTIONS = [
  { id: 'behavior', label: 'AI Behavior', icon: '⚙' },
  { id: 'focus', label: 'Focus Mode', icon: '◎' },
  { id: 'themes', label: 'Workspace Themes', icon: '🎨' },
  { id: 'permissions', label: 'Agent Permissions', icon: '🛡' },
  { id: 'shortcuts', label: 'Shortcuts', icon: '⌨' },
  { id: 'privacy', label: 'Privacy Controls', icon: '🔒' },
]

const SHORTCUTS = [
  { keys: 'Ctrl + Space', action: 'Open Spotlight' },
  { keys: 'Ctrl + A', action: 'Open AI Council' },
  { keys: 'Ctrl + F', action: 'Cycle Focus Mode' },
  { keys: 'Ctrl + Tab', action: 'Cycle Workspace' },
  { keys: 'Ctrl + Shift + W', action: 'Mission Control' },
  { keys: 'Ctrl + ,', action: 'Open Settings' },
  { keys: 'Esc', action: 'Close panel / Go back' },
]

export default function Settings() {
  const isOpen = useUIStore((s) => s.settingsOpen)
  const setOpen = useUIStore((s) => s.setSettingsOpen)
  const [section, setSection] = useState('behavior')

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    if (isOpen) window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 999, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div onClick={() => setOpen(false)} style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(12px)' }} />
      <div style={{
        position: 'relative',
        width: '100%',
        maxWidth: 600,
        maxHeight: '80vh',
        background: 'rgba(255,255,255,0.08)',
        backdropFilter: 'blur(20px)',
        borderRadius: 16,
        border: '1px solid rgba(255,255,255,0.12)',
        overflow: 'hidden',
        display: 'flex',
      }}>
        <div style={{ width: 160, borderRight: '1px solid rgba(255,255,255,0.05)', padding: 12 }}>
          {SECTIONS.map((s) => (
            <button
              key={s.id}
              onClick={() => setSection(s.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '8px 12px',
                borderRadius: 8,
                border: 'none',
                background: section === s.id ? 'rgba(255,255,255,0.1)' : 'transparent',
                color: section === s.id ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.3)',
                fontSize: 11,
                cursor: 'pointer',
                textAlign: 'left',
                marginBottom: 2,
              }}
            >
              <span style={{ fontSize: 12 }}>{s.icon}</span>
              {s.label}
            </button>
          ))}
        </div>

        <div style={{ flex: 1, padding: 20, overflow: 'auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <h2 style={{ fontSize: 13, fontWeight: 500, color: 'rgba(255,255,255,0.8)' }}>
              {SECTIONS.find((s) => s.id === section)?.label}
            </h2>
            <button onClick={() => setOpen(false)} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.3)', cursor: 'pointer', fontSize: 14 }}>
              ✕
            </button>
          </div>

          {section === 'behavior' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 6, display: 'block' }}>AI Aggression Level</label>
                <input type="range" min="0" max="100" defaultValue={50}
                  style={{ width: '100%' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, color: 'rgba(255,255,255,0.2)' }}>
                  <span>Passive</span><span>Balanced</span><span>Aggressive</span>
                </div>
              </div>
              <div>
                <label style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 6, display: 'block' }}>Suggestion Frequency</label>
                <input type="range" min="0" max="100" defaultValue={40}
                  style={{ width: '100%' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, color: 'rgba(255,255,255,0.2)' }}>
                  <span>Rarely</span><span>Normal</span><span>Often</span>
                </div>
              </div>
            </div>
          )}

          {section === 'focus' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {['Normal', 'Focus', 'Deep Focus', 'Lock'].map((m) => (
                <div key={m} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 12px',
                  borderRadius: 10,
                  background: 'rgba(255,255,255,0.05)',
                }}>
                  <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)' }}>{m}</span>
                  <div style={{ display: 'flex', gap: 8, fontSize: 10, color: 'rgba(255,255,255,0.3)' }}>
                    {['block', 'notify', 'allow'].map((a) => (
                      <label key={a} style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                        <input type="checkbox" defaultChecked={a === 'allow'} />
                        {a}
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {section === 'themes' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {['Study', 'Coding', 'Learning', 'Personal'].map((ws) => (
                <div key={ws} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 12px',
                  borderRadius: 10,
                  background: 'rgba(255,255,255,0.05)',
                }}>
                  <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)' }}>{ws}</span>
                  <input type="color" defaultValue={
                    ws === 'Study' ? '#4A9EFF' : ws === 'Coding' ? '#00E676' : ws === 'Learning' ? '#B388FF' : '#9E9E9E'
                  } style={{ width: 32, height: 32, borderRadius: '50%', cursor: 'pointer', background: 'transparent', border: 'none' }} />
                </div>
              ))}
            </div>
          )}

          {section === 'permissions' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {['orion', 'nova', 'sage', 'pulse', 'echo', 'iris', 'atlas', 'aegis'].map((agent) => (
                <div key={agent} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 12px',
                  borderRadius: 10,
                  background: 'rgba(255,255,255,0.05)',
                }}>
                  <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)', textTransform: 'capitalize' }}>{agent}</span>
                  <label style={{ position: 'relative', display: 'inline-block', width: 36, height: 20, cursor: 'pointer' }}>
                    <input type="checkbox" defaultChecked style={{ display: 'none' }} />
                    <div style={{
                      width: 36,
                      height: 20,
                      borderRadius: 10,
                      background: 'rgba(255,255,255,0.1)',
                      transition: 'background 0.2s',
                    }} />
                  </label>
                </div>
              ))}
            </div>
          )}

          {section === 'shortcuts' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {SHORTCUTS.map((s) => (
                <div key={s.action} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 10px',
                  borderRadius: 8,
                }}>
                  <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>{s.action}</span>
                  <kbd style={{
                    fontSize: 10,
                    padding: '3px 8px',
                    borderRadius: 4,
                    background: 'rgba(255,255,255,0.05)',
                    color: 'rgba(255,255,255,0.3)',
                    fontFamily: 'monospace',
                  }}>
                    {s.keys}
                  </kbd>
                </div>
              ))}
            </div>
          )}

          {section === 'privacy' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ padding: 14, borderRadius: 12, background: 'rgba(255,255,255,0.05)' }}>
                <h3 style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', marginBottom: 6 }}>Memory Management</h3>
                <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', marginBottom: 10 }}>Total stored memories: 1,432 items (45 MB)</p>
                <div style={{ display: 'flex', gap: 6 }}>
                  <button style={{ padding: '6px 14px', borderRadius: 8, background: 'rgba(255,255,255,0.1)', border: 'none', color: 'rgba(255,255,255,0.6)', fontSize: 11, cursor: 'pointer' }}>
                    Clear Session
                  </button>
                  <button style={{ padding: '6px 14px', borderRadius: 8, background: 'rgba(255,82,82,0.1)', border: 'none', color: 'rgba(255,82,82,0.6)', fontSize: 11, cursor: 'pointer' }}>
                    Delete All
                  </button>
                </div>
              </div>
              <div style={{ padding: 14, borderRadius: 12, background: 'rgba(255,255,255,0.05)' }}>
                <h3 style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', marginBottom: 6 }}>Data Deletion</h3>
                <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', marginBottom: 10 }}>Permanently remove all stored data</p>
                <button style={{ padding: '6px 14px', borderRadius: 8, background: 'rgba(255,82,82,0.1)', border: 'none', color: 'rgba(255,82,82,0.6)', fontSize: 11, cursor: 'pointer' }}>
                  Factory Reset
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
