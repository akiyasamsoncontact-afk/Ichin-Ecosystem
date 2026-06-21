import { useState } from 'react'
import { motion } from 'framer-motion'
import { Book, Lightbulb, Layers, Brain, Sparkles, ChevronRight } from 'lucide-react'
import { useAppStore } from '../../stores/appStore'

const TOPICS = [
  { id: 't1', name: 'Quantum Mechanics', progress: 65, cards: 42 },
  { id: 't2', name: 'Linear Algebra', progress: 80, cards: 28 },
  { id: 't3', name: 'Data Structures', progress: 45, cards: 56 },
  { id: 't4', name: 'Machine Learning', progress: 30, cards: 71 },
]

export default function StudyWorkspace() {
  const memories = useAppStore((s) => s.memories)
  const [selectedTopic, setSelectedTopic] = useState(TOPICS[0])

  return (
    <div className="h-full grid grid-cols-[240px_1fr_280px] gap-4 p-4" style={{ backgroundColor: 'rgba(74, 158, 255, 0.02)' }}>
      <div className="flex flex-col gap-3">
        <h2 className="text-xs uppercase tracking-wider text-white/30 px-2 mb-1">Topics</h2>
        {TOPICS.map((t) => (
          <motion.button
            key={t.id}
            onClick={() => setSelectedTopic(t)}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all ${
              selectedTopic.id === t.id ? 'glass' : 'hover:bg-white/5'
            }`}
            whileHover={{ x: 4 }}
            style={selectedTopic.id === t.id ? { borderColor: 'rgba(74, 158, 255, 0.3)' } : {}}
          >
            <Book size={16} style={{ color: '#4A9EFF' }} />
            <div className="flex-1 min-w-0">
              <div className="text-sm text-white/80 truncate">{t.name}</div>
              <div className="flex items-center gap-2 mt-1">
                <div className="flex-1 h-1 rounded-full bg-white/5">
                  <div className="h-full rounded-full bg-accent-study/50" style={{ width: `${t.progress}%` }} />
                </div>
                <span className="text-[10px] text-white/30">{t.progress}%</span>
              </div>
            </div>
          </motion.button>
        ))}
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex-1 glass rounded-2xl p-6 flex flex-col items-center justify-center gap-4">
          <Layers size={48} className="text-accent-study/30" />
          <p className="text-sm text-white/40 text-center max-w-xs">
            {selectedTopic.name} — Flashcard generation, quizzes, and notes available.
          </p>
          <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent-study/10 text-accent-study text-sm hover:bg-accent-study/20 transition-all">
            <Sparkles size={14} />
            Generate Flashcards
            <ChevronRight size={14} />
          </button>
        </div>

        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Flashcards', value: selectedTopic.cards, color: '#4A9EFF' },
            { label: 'Quizzes', value: Math.floor(selectedTopic.cards * 0.3), color: '#4A9EFF' },
            { label: 'Progress', value: `${selectedTopic.progress}%`, color: '#4A9EFF' },
          ].map((stat) => (
            <div key={stat.label} className="glass rounded-xl p-3 text-center">
              <div className="text-lg font-medium" style={{ color: stat.color }}>{stat.value}</div>
              <div className="text-[10px] text-white/30 uppercase tracking-wider">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <h2 className="text-xs uppercase tracking-wider text-white/30 px-2 mb-1">AI Study Agent</h2>
        <div className="flex-1 glass rounded-2xl p-4 space-y-3">
          {memories.length > 0 ? memories.slice(0, 4).map((m, i) => (
            <div key={m.id || i} className="text-xs text-white/50 p-2 rounded-lg bg-white/5">
              {m.content || 'Memory entry'}
            </div>
          )) : (
            <div className="flex flex-col items-center justify-center h-full gap-3 text-white/20">
              <Brain size={32} />
              <p className="text-xs text-center">Study agent is idle.<br />Start studying to get AI insights.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
