import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Users, Shield, AlertTriangle, Activity, X } from 'lucide-react'
import { useCouncilStore } from '../../stores/councilStore'
import type { AgentName } from '../../types'

const AGENT_INFO: { name: AgentName; role: string; color: string }[] = [
  { name: 'orion', role: 'Strategic Planner', color: '#4A9EFF' },
  { name: 'nova', role: 'Creative Innovator', color: '#FF6B6B' },
  { name: 'sage', role: 'Knowledge Expert', color: '#B388FF' },
  { name: 'pulse', role: 'System Monitor', color: '#00E676' },
  { name: 'echo', role: 'Communication', color: '#FFB300' },
  { name: 'iris', role: 'Visual Analyst', color: '#FF80AB' },
  { name: 'atlas', role: 'Data Navigator', color: '#40C4FF' },
  { name: 'aegis', role: 'Security Guard', color: '#FF5252' },
]

export default function AICouncil() {
  const isOpen = useCouncilStore((s) => s.isOpen)
  const close = useCouncilStore((s) => s.close)
  const outputs = useCouncilStore((s) => s.outputs)
  const decision = useCouncilStore((s) => s.decision)
  const loading = useCouncilStore((s) => s.loading)
  const orchestrate = useCouncilStore((s) => s.orchestrate)
  const [input, setInput] = useState('')

  const handleOrchestrate = () => {
    if (!input.trim()) return
    orchestrate(input)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="absolute inset-0 bg-black/60 backdrop-blur-lg" onClick={close} />
          <motion.div
            className="relative w-full max-w-2xl max-h-[80vh] glass-strong rounded-2xl overflow-hidden flex flex-col"
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
              <div className="flex items-center gap-2">
                <Users size={18} className="text-white/60" />
                <h2 className="text-sm font-medium text-white/80">AI Council</h2>
              </div>
              <button onClick={close} className="p-1.5 rounded-lg hover:bg-white/10 text-white/30">
                <X size={16} />
              </button>
            </div>

            <div className="p-5 overflow-y-auto space-y-4">
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleOrchestrate()}
                  placeholder="What would you like the council to decide?"
                  className="flex-1 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-white/30"
                />
                <button
                  onClick={handleOrchestrate}
                  disabled={loading || !input.trim()}
                  className="px-4 py-2.5 rounded-xl bg-white/10 text-white/80 text-sm hover:bg-white/15 disabled:opacity-30 transition-all"
                >
                  {loading ? 'Consulting...' : 'Orchestrate'}
                </button>
              </div>

              {loading && (
                <div className="flex items-center justify-center py-8">
                  <div className="flex gap-2">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        className="w-2 h-2 rounded-full bg-white/30"
                        animate={{ y: [0, -8, 0] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
                      />
                    ))}
                  </div>
                </div>
              )}

              {outputs.length > 0 && (
                <div className="grid grid-cols-2 gap-2">
                  {outputs.map((o) => {
                    const info = AGENT_INFO.find((a) => a.name === o.agent)
                    return (
                      <div
                        key={o.agent}
                        className="p-3 rounded-xl bg-white/5"
                        style={{ borderLeft: `2px solid ${info?.color || '#666'}` }}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium text-white/80">{o.agent}</span>
                          <span className="text-[10px] text-white/30">{info?.role}</span>
                        </div>
                        <div className="text-xs text-white/50 line-clamp-2">{o.recommendation}</div>
                        <div className="flex gap-3 mt-2">
                          <span className="text-[10px]" style={{ color: o.confidence > 0.7 ? '#00E676' : '#FFB300' }}>
                            {(o.confidence * 100).toFixed(0)}%
                          </span>
                          <span className="text-[10px]" style={{ color: o.risk > 0.5 ? '#FF5252' : '#B0B0B0' }}>
                            Risk: {(o.risk * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}

              {decision && (
                <div className="glass rounded-xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Shield size={16} className="text-accent-coding" />
                      <span className="text-sm font-medium text-white/80">Council Decision</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-white/40">
                        Confidence: <span className="text-accent-coding">{(decision.confidence * 100).toFixed(0)}%</span>
                      </span>
                      <span className="flex items-center gap-1 text-xs" style={{
                        color: decision.riskLevel === 'critical' ? '#FF5252' :
                               decision.riskLevel === 'high' ? '#FFB300' :
                               decision.riskLevel === 'medium' ? '#FFA726' : '#00E676'
                      }}>
                        <AlertTriangle size={12} />
                        {decision.riskLevel}
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-white/40">{decision.reasoning.slice(0, 200)}</p>
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
