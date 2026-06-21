import { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Terminal, FileText, MessageSquare, ArrowRight } from 'lucide-react'
import { useSpotlightStore } from '../../stores/spotlightStore'
import { useWorkspaceStore } from '../../stores/workspaceStore'
import type { WorkspaceType } from '../../types'

interface Suggestion {
  type: 'command' | 'search' | 'ai' | 'action'
  label: string
  description: string
  icon: React.ReactNode
  action?: () => void
}

const CONTEXTUAL_ACTIONS: Record<WorkspaceType, Suggestion[]> = {
  study: [
    { type: 'command', label: 'Generate Flashcards', description: 'AI creates flashcards from your notes', icon: <Terminal size={14} /> },
    { type: 'ai', label: 'Quiz me on current topic', description: 'Start an AI-generated quiz', icon: <MessageSquare size={14} /> },
    { type: 'action', label: 'Summarize notes', description: 'Get AI summary of recent study material', icon: <FileText size={14} /> },
  ],
  coding: [
    { type: 'command', label: 'Explain this code', description: 'AI explains the selected code', icon: <Terminal size={14} /> },
    { type: 'ai', label: 'Find bugs', description: 'Scan for potential issues', icon: <MessageSquare size={14} /> },
    { type: 'action', label: 'Generate tests', description: 'Auto-create unit tests', icon: <FileText size={14} /> },
  ],
  learning: [
    { type: 'command', label: 'Continue learning path', description: 'Resume your course progression', icon: <Terminal size={14} /> },
    { type: 'ai', label: 'Explain concept', description: 'Get simplified explanation', icon: <MessageSquare size={14} /> },
    { type: 'search', label: 'Find resources', description: 'Search knowledge base', icon: <Search size={14} /> },
  ],
  personal: [
    { type: 'command', label: 'Add task', description: 'Create a new task', icon: <Terminal size={14} /> },
    { type: 'action', label: 'Plan my day', description: 'AI organizes your schedule', icon: <ArrowRight size={14} /> },
    { type: 'search', label: 'Find notes', description: 'Search personal notes', icon: <Search size={14} /> },
  ],
}

export default function Spotlight() {
  const isOpen = useSpotlightStore((s) => s.isOpen)
  const query = useSpotlightStore((s) => s.query)
  const setQuery = useSpotlightStore((s) => s.setQuery)
  const close = useSpotlightStore((s) => s.close)
  const activeWs = useWorkspaceStore((s) => s.active)
  const [selectedIdx, setSelectedIdx] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const allSuggestions = query
    ? CONTEXTUAL_ACTIONS[activeWs].filter((s) =>
        s.label.toLowerCase().includes(query.toLowerCase())
      )
    : CONTEXTUAL_ACTIONS[activeWs]

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50)
      setSelectedIdx(0)
    }
  }, [isOpen])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIdx((i) => Math.min(i + 1, allSuggestions.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIdx((i) => Math.max(i - 1, 0))
      } else if (e.key === 'Enter' && allSuggestions[selectedIdx]?.action) {
        allSuggestions[selectedIdx].action!()
        close()
      } else if (e.key === 'Escape') {
        close()
      }
    },
    [selectedIdx, allSuggestions, close]
  )

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          <div className="absolute inset-0 bg-black/60 backdrop-blur-xl" onClick={close} />
          <motion.div
            className="relative w-full max-w-xl glass-strong rounded-2xl overflow-hidden shadow-2xl"
            initial={{ y: -20, opacity: 0, scale: 0.98 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: -20, opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
          >
            <div className="flex items-center gap-3 px-4 py-3 border-b border-white/5">
              <Search size={16} className="text-white/30" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => { setQuery(e.target.value); setSelectedIdx(0) }}
                onKeyDown={handleKeyDown}
                placeholder="Search commands, files, or ask AI..."
                className="flex-1 bg-transparent text-sm text-white placeholder:text-white/20 focus:outline-none"
              />
              <kbd className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-white/30">ESC</kbd>
            </div>

            <div className="p-2 max-h-80 overflow-y-auto">
              {allSuggestions.map((s, i) => (
                <button
                  key={s.label + i}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all ${
                    i === selectedIdx ? 'bg-white/10' : 'hover:bg-white/5'
                  }`}
                  onClick={() => { s.action?.(); close() }}
                >
                  <span className="text-white/40">{s.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-white/80 truncate">{s.label}</div>
                    <div className="text-xs text-white/30 truncate">{s.description}</div>
                  </div>
                  <span className="text-[10px] uppercase text-white/20 bg-white/5 px-1.5 py-0.5 rounded">{s.type}</span>
                </button>
              ))}
              {allSuggestions.length === 0 && (
                <div className="text-center py-8 text-sm text-white/20">No results found</div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
