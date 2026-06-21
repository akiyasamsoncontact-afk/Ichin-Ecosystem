import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, Save, Clock, Zap, User, Terminal, GitBranch, Plus, X } from 'lucide-react'

type NodeType = 'trigger' | 'action' | 'condition'

interface FlowNode {
  id: string
  type: NodeType
  label: string
  config: Record<string, string>
}

const TRIGGER_TYPES = [
  { id: 'time', label: 'Time', icon: Clock },
  { id: 'event', label: 'Event', icon: Zap },
  { id: 'ai', label: 'AI Decision', icon: GitBranch },
  { id: 'manual', label: 'Manual', icon: User },
]

export default function WorkflowBuilder() {
  const [nodes, setNodes] = useState<FlowNode[]>([
    { id: 't1', type: 'trigger', label: 'Time Trigger', config: { schedule: '09:00' } },
    { id: 'a1', type: 'action', label: 'Create Task', config: { task: 'Daily standup' } },
  ])

  const addNode = (type: NodeType) => {
    const id = `${type[0]}${Date.now()}`
    const label = type === 'trigger' ? 'New Trigger' : type === 'action' ? 'New Action' : 'Condition'
    setNodes([...nodes, { id, type, label, config: {} }])
  }

  const removeNode = (id: string) => {
    setNodes(nodes.filter((n) => n.id !== id))
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
        <span className="text-sm text-white/70">Workflow Builder</span>
        <div className="flex-1" />
        <button className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-accent-coding/10 text-accent-coding text-xs hover:bg-accent-coding/20">
          <Play size={12} /> Run
        </button>
        <button className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/10 text-white/60 text-xs hover:bg-white/15">
          <Save size={12} /> Save
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4">
        <div className="space-y-3">
          {nodes.map((node, i) => (
            <motion.div
              key={node.id}
              className="glass rounded-xl p-4 relative"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {i > 0 && (
                <div className="absolute -top-3 left-6 w-px h-3 bg-white/10" />
              )}
              <div className="flex items-start gap-3">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                  node.type === 'trigger' ? 'bg-accent-study/10 text-accent-study' :
                  node.type === 'action' ? 'bg-accent-coding/10 text-accent-coding' :
                  'bg-accent-learning/10 text-accent-learning'
                }`}>
                  <Terminal size={14} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-white/70">{node.label}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      node.type === 'trigger' ? 'bg-accent-study/10 text-accent-study' :
                      node.type === 'action' ? 'bg-accent-coding/10 text-accent-coding' :
                      'bg-accent-learning/10 text-accent-learning'
                    }`}>
                      {node.type}
                    </span>
                  </div>
                  {Object.entries(node.config).map(([k, v]) => (
                    <div key={k} className="text-xs text-white/30 mt-1">
                      {k}: {v}
                    </div>
                  ))}
                </div>
                <button onClick={() => removeNode(node.id)} className="p-1 rounded hover:bg-white/10 text-white/20">
                  <X size={12} />
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="flex gap-2 mt-4">
          <button
            onClick={() => addNode('trigger')}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-accent-study/10 text-accent-study text-xs hover:bg-accent-study/20"
          >
            <Plus size={12} /> Add Trigger
          </button>
          <button
            onClick={() => addNode('action')}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-accent-coding/10 text-accent-coding text-xs hover:bg-accent-coding/20"
          >
            <Plus size={12} /> Add Action
          </button>
          <button
            onClick={() => addNode('condition')}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-accent-learning/10 text-accent-learning text-xs hover:bg-accent-learning/20"
          >
            <GitBranch size={12} /> Add Condition
          </button>
        </div>
      </div>
    </div>
  )
}
