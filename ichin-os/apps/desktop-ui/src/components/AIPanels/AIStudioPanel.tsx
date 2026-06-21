import { useState } from 'react'
import { motion } from 'framer-motion'
import { Workflow, Bot, BarChart3, Play, Save } from 'lucide-react'

const WORKFLOWS = [
  { id: 'w1', name: 'Daily Standup Report', enabled: true, actions: 4 },
  { id: 'w2', name: 'Code Review Trigger', enabled: true, actions: 3 },
  { id: 'w3', name: 'Study Session Prep', enabled: false, actions: 5 },
]

const TRAINING_FEEDBACK = [
  { metric: 'Accuracy', value: 87, trend: 'up' },
  { metric: 'Response Time', value: 320, trend: 'down', unit: 'ms' },
  { metric: 'User Satisfaction', value: 92, trend: 'up' },
]

export default function AIStudioPanel() {
  const [tab, setTab] = useState<'workflows' | 'agents' | 'training'>('workflows')

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
        {(['workflows', 'agents', 'training'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-3 py-1.5 rounded-lg text-xs transition-all ${
              tab === t ? 'bg-white/10 text-white/80' : 'text-white/30 hover:text-white/50'
            }`}
          >
            {t === 'workflows' && <Workflow size={12} className="inline mr-1" />}
            {t === 'agents' && <Bot size={12} className="inline mr-1" />}
            {t === 'training' && <BarChart3 size={12} className="inline mr-1" />}
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-auto p-4">
        {tab === 'workflows' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs uppercase text-white/30">Active Workflows</h3>
              <button className="p-1.5 rounded-lg bg-white/10 text-white/60 hover:bg-white/15">
                <Save size={14} />
              </button>
            </div>
            {WORKFLOWS.map((wf) => (
              <div key={wf.id} className="glass rounded-xl p-3 flex items-center justify-between">
                <div>
                  <div className="text-sm text-white/70">{wf.name}</div>
                  <div className="text-xs text-white/30">{wf.actions} actions</div>
                </div>
                <div className={`w-2 h-2 rounded-full ${wf.enabled ? 'bg-accent-coding' : 'bg-white/10'}`} />
              </div>
            ))}
          </div>
        )}

        {tab === 'agents' && (
          <div className="space-y-2">
            <p className="text-xs text-white/30 mb-3">Agent Design Canvas</p>
            <div className="glass rounded-2xl p-8 flex items-center justify-center min-h-[200px]">
              <div className="text-center text-white/20">
                <Bot size={32} className="mx-auto mb-2" />
                <p className="text-xs">Agent designer workspace</p>
                <p className="text-[10px] mt-1">Drag components to build custom agents</p>
              </div>
            </div>
          </div>
        )}

        {tab === 'training' && (
          <div className="space-y-4">
            {TRAINING_FEEDBACK.map((f) => (
              <div key={f.metric} className="glass rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-white/50">{f.metric}</span>
                  <span className="text-sm text-white/80">
                    {f.value}{f.unit || '%'}
                    <span className={`text-[10px] ml-1 ${f.trend === 'up' ? 'text-accent-coding' : 'text-red-400'}`}>
                      {f.trend === 'up' ? '↑' : '↓'}
                    </span>
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-white/5">
                  <div className="h-full rounded-full bg-accent-coding/50" style={{ width: `${f.value}%` }} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
