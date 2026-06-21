import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, Clock, CheckCircle2, Brain, X, Shield, Zap } from 'lucide-react'
import { useUIStore } from '../../stores/uiStore'

const STATS = [
  { label: 'System Health', value: '98%', icon: Activity, color: '#00E676' },
  { label: 'Focus Time', value: '4h 32m', icon: Clock, color: '#4A9EFF' },
  { label: 'Tasks Done', value: '12/18', icon: CheckCircle2, color: '#B388FF' },
  { label: 'AI Decisions', value: '147', icon: Brain, color: '#FFB300' },
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

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="absolute inset-0 bg-black/70 backdrop-blur-xl" onClick={close} />
          <motion.div
            className="relative w-full h-full overflow-auto p-6"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 20, opacity: 0 }}
          >
            <div className="max-w-5xl mx-auto space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Shield size={24} className="text-white/40" />
                  <h1 className="text-lg font-light text-white/80">Mission Control</h1>
                </div>
                <button onClick={close} className="p-2 rounded-lg hover:bg-white/10 text-white/30">
                  <X size={18} />
                </button>
              </div>

              <div className="grid grid-cols-4 gap-4">
                {STATS.map((stat) => (
                  <div key={stat.label} className="glass rounded-2xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <stat.icon size={16} style={{ color: stat.color }} />
                      <span className="text-xs text-white/40">{stat.label}</span>
                    </div>
                    <div className="text-2xl font-light" style={{ color: stat.color }}>{stat.value}</div>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="glass rounded-2xl p-4 col-span-2">
                  <h3 className="text-xs uppercase tracking-wider text-white/30 mb-3">Recent Actions</h3>
                  <div className="space-y-2">
                    {RECENT_ACTIONS.map((a, i) => (
                      <div key={i} className="flex items-center gap-3 text-sm">
                        <span className="text-[10px] text-white/20 w-14">{a.time}</span>
                        <div className="w-1.5 h-1.5 rounded-full bg-white/10" />
                        <span className="text-xs text-white/50">{a.text}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="glass rounded-2xl p-4">
                  <h3 className="text-xs uppercase tracking-wider text-white/30 mb-3">AI Decisions Log</h3>
                  <div className="space-y-3">
                    {AI_DECISIONS.map((d, i) => (
                      <div key={i} className="p-3 rounded-xl bg-white/5">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-white/70">{d.agent}</span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded-full" style={{
                            backgroundColor: d.risk === 'low' ? 'rgba(0,230,118,0.15)' : 'rgba(255,179,0,0.15)',
                            color: d.risk === 'low' ? '#00E676' : '#FFB300',
                          }}>
                            {d.risk}
                          </span>
                        </div>
                        <div className="text-xs text-white/40">{d.action}</div>
                        <div className="mt-1">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1 rounded-full bg-white/5">
                              <div className="h-full rounded-full bg-accent-coding/50" style={{ width: `${d.confidence}%` }} />
                            </div>
                            <span className="text-[10px] text-white/30">{d.confidence}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
