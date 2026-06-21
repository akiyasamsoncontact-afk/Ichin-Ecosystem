import { useEffect, useRef, useState, useCallback } from 'react'
import { useUIStore } from '../stores/uiStore'
import { useWorkspaceStore } from '../stores/workspaceStore'
import type { WorkspaceType } from '../types'

interface Suggestion {
  type: 'command' | 'search' | 'ai' | 'action'
  label: string
  description: string
}

const CONTEXTUAL_ACTIONS: Record<WorkspaceType, Suggestion[]> = {
  study: [
    { type: 'command', label: 'Generate Flashcards', description: 'AI creates flashcards from your notes' },
    { type: 'ai', label: 'Quiz me on current topic', description: 'Start an AI-generated quiz' },
    { type: 'action', label: 'Summarize notes', description: 'Get AI summary of recent study material' },
  ],
  coding: [
    { type: 'command', label: 'Explain this code', description: 'AI explains the selected code' },
    { type: 'ai', label: 'Find bugs', description: 'Scan for potential issues' },
    { type: 'action', label: 'Generate tests', description: 'Auto-create unit tests' },
  ],
  learning: [
    { type: 'command', label: 'Continue learning path', description: 'Resume your course progression' },
    { type: 'ai', label: 'Explain concept', description: 'Get simplified explanation' },
    { type: 'search', label: 'Find resources', description: 'Search knowledge base' },
  ],
  personal: [
    { type: 'command', label: 'Add task', description: 'Create a new task' },
    { type: 'action', label: 'Plan my day', description: 'AI organizes your schedule' },
    { type: 'search', label: 'Find notes', description: 'Search personal notes' },
  ],
}

export default function Spotlight() {
  const isOpen = useUIStore((s) => s.spotlightOpen)
  const setOpen = useUIStore((s) => s.setSpotlightOpen)
  const [query, setQuery] = useState('')
  const activeWs = useWorkspaceStore((s) => s.active)
  const [selectedIdx, setSelectedIdx] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const close = () => { setOpen(false); setQuery('') }

  const allSuggestions = query
    ? CONTEXTUAL_ACTIONS[activeWs].filter((s) =>
        s.label.toLowerCase().includes(query.toLowerCase())
      )
    : CONTEXTUAL_ACTIONS[activeWs]

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50)
      setSelectedIdx(0)
      setQuery('')
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
      } else if (e.key === 'Enter' && allSuggestions[selectedIdx]) {
        close()
      } else if (e.key === 'Escape') {
        close()
      }
    },
    [selectedIdx, allSuggestions]
  )

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) close()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 999,
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'center',
      paddingTop: '15vh',
    }}>
      <div
        onClick={close}
        style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(12px)' }}
      />
      <div style={{
        position: 'relative',
        width: '100%',
        maxWidth: 520,
        background: 'rgba(255,255,255,0.08)',
        backdropFilter: 'blur(20px)',
        borderRadius: 16,
        border: '1px solid rgba(255,255,255,0.12)',
        overflow: 'hidden',
        boxShadow: '0 24px 48px rgba(0,0,0,0.4)',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '12px 16px',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
        }}>
          <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 14 }}>⌕</span>
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => { setQuery(e.target.value); setSelectedIdx(0) }}
            onKeyDown={handleKeyDown}
            placeholder="Search commands, files, or ask AI..."
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              color: '#fff',
              fontSize: 14,
              outline: 'none',
            }}
          />
          <kbd style={{ fontSize: 9, padding: '2px 6px', borderRadius: 4, background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.3)' }}>
            ESC
          </kbd>
        </div>

        <div style={{ padding: 8, maxHeight: 320, overflow: 'auto' }}>
          {allSuggestions.map((s, i) => (
            <button
              key={s.label + i}
              onClick={close}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '10px 12px',
                borderRadius: 8,
                textAlign: 'left',
                background: i === selectedIdx ? 'rgba(255,255,255,0.1)' : 'transparent',
                border: 'none',
                cursor: 'pointer',
                transition: 'background 0.1s ease',
              }}
            >
              <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12 }}>
                {s.type === 'command' ? '>' : s.type === 'search' ? '⌕' : s.type === 'ai' ? '✦' : '→'}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.8)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {s.label}
                </div>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {s.description}
                </div>
              </div>
              <span style={{
                fontSize: 9,
                color: 'rgba(255,255,255,0.2)',
                background: 'rgba(255,255,255,0.05)',
                padding: '2px 6px',
                borderRadius: 4,
                textTransform: 'uppercase',
              }}>
                {s.type}
              </span>
            </button>
          ))}
          {allSuggestions.length === 0 && (
            <div style={{ textAlign: 'center', padding: 24, fontSize: 13, color: 'rgba(255,255,255,0.2)' }}>
              No results found
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
