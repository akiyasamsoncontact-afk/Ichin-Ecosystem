import { useState } from 'react'
import { useUIStore } from '../stores/uiStore'

const AGENT_INFO: { name: string; role: string; color: string }[] = [
  { name: 'orion', role: 'Strategic Planner', color: '#4A9EFF' },
  { name: 'nova', role: 'Creative Innovator', color: '#FF6B6B' },
  { name: 'sage', role: 'Knowledge Expert', color: '#B388FF' },
  { name: 'pulse', role: 'System Monitor', color: '#00E676' },
  { name: 'echo', role: 'Communication', color: '#FFB300' },
  { name: 'iris', role: 'Visual Analyst', color: '#FF80AB' },
  { name: 'atlas', role: 'Data Navigator', color: '#40C4FF' },
  { name: 'aegis', role: 'Security Guard', color: '#FF5252' },
]

interface AgentOutput {
  agent: string
  recommendation: string
  confidence: number
  risk: number
}

export default function AICouncil() {
  const isOpen = useUIStore((s) => s.councilOpen)
  const setOpen = useUIStore((s) => s.setCouncilOpen)
  const close = () => setOpen(false)
  const [input, setInput] = useState('')
  const [outputs, setOutputs] = useState<AgentOutput[]>([])
  const [loading, setLoading] = useState(false)

  const handleOrchestrate = async () => {
    if (!input.trim()) return
    setLoading(true)
    setOutputs([])
    const fallback: AgentOutput[] = AGENT_INFO.map((a) => ({
      agent: a.name,
      recommendation: `Analysis from ${a.name}`,
      confidence: 0.5 + Math.random() * 0.4,
      risk: Math.random() * 0.5,
    }))
    await new Promise((r) => setTimeout(r, 800))
    setOutputs(fallback)
    setLoading(false)
  }

  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 999,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <div onClick={close} style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(12px)' }} />
      <div style={{
        position: 'relative',
        width: '100%',
        maxWidth: 560,
        maxHeight: '80vh',
        background: 'rgba(255,255,255,0.08)',
        backdropFilter: 'blur(20px)',
        borderRadius: 16,
        border: '1px solid rgba(255,255,255,0.12)',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 20px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 14, color: 'rgba(255,255,255,0.6)' }}>◎</span>
            <h2 style={{ fontSize: 13, fontWeight: 500, color: 'rgba(255,255,255,0.8)' }}>AI Council</h2>
          </div>
          <button onClick={close} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.3)', cursor: 'pointer', fontSize: 14, padding: 4 }}>
            ✕
          </button>
        </div>

        <div style={{ padding: 16, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleOrchestrate()}
              placeholder="What would you like the council to decide?"
              style={{
                flex: 1,
                padding: '8px 14px',
                borderRadius: 10,
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
                color: '#fff',
                fontSize: 13,
                outline: 'none',
              }}
            />
            <button
              onClick={handleOrchestrate}
              disabled={loading || !input.trim()}
              style={{
                padding: '8px 16px',
                borderRadius: 10,
                background: 'rgba(255,255,255,0.1)',
                border: 'none',
                color: 'rgba(255,255,255,0.8)',
                fontSize: 12,
                cursor: 'pointer',
                opacity: loading || !input.trim() ? 0.3 : 1,
              }}
            >
              {loading ? 'Consulting...' : 'Orchestrate'}
            </button>
          </div>

          {loading && (
            <div style={{ textAlign: 'center', padding: 24 }}>
              <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.3)' }}>Consulting all agents...</span>
            </div>
          )}

          {outputs.length > 0 && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
              {outputs.map((o) => {
                const info = AGENT_INFO.find((a) => a.name === o.agent)
                return (
                  <div key={o.agent} style={{
                    padding: 10,
                    borderRadius: 10,
                    background: 'rgba(255,255,255,0.05)',
                    borderLeft: `2px solid ${info?.color || '#666'}`,
                  }}>
                    <div style={{ display: 'flex', gap: 6, marginBottom: 4 }}>
                      <span style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.8)', textTransform: 'capitalize' }}>{o.agent}</span>
                      <span style={{ fontSize: 9, color: 'rgba(255,255,255,0.3)' }}>{info?.role}</span>
                    </div>
                    <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', marginBottom: 6, lineHeight: 1.4 }}>{o.recommendation}</div>
                    <div style={{ display: 'flex', gap: 10 }}>
                      <span style={{ fontSize: 9, color: o.confidence > 0.7 ? '#00E676' : '#FFB300' }}>
                        {(o.confidence * 100).toFixed(0)}%
                      </span>
                      <span style={{ fontSize: 9, color: o.risk > 0.5 ? '#FF5252' : '#B0B0B0' }}>
                        Risk: {(o.risk * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
