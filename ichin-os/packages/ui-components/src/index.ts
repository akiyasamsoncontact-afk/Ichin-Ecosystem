import React, { useState, useEffect, useRef, useCallback } from 'react'
import type { OrbState, WorkspaceType, Task as TaskType, AppManifest, CouncilDecision, FocusMode, LayoutConfig } from '@ichin/shared-types'

/* ─── GlassPanel ─── */

interface GlassPanelProps {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'elevated' | 'critical'
  onClick?: () => void
}

const glassBase: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(16px)',
  WebkitBackdropFilter: 'blur(16px)',
  border: '1px solid rgba(255, 255, 255, 0.08)',
  borderRadius: '16px',
}

const glassVariants: Record<string, React.CSSProperties> = {
  default: {},
  elevated: {
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    border: '1px solid rgba(255, 255, 255, 0.12)',
  },
  critical: {
    boxShadow: '0 8px 32px rgba(255, 82, 82, 0.25)',
    border: '1px solid rgba(255, 82, 82, 0.3)',
    background: 'rgba(255, 82, 82, 0.08)',
  },
}

export const GlassPanel: React.FC<GlassPanelProps> = ({
  children,
  className,
  variant = 'default',
  onClick,
}) => (
  <div
    className={className}
    onClick={onClick}
    style={{ ...glassBase, ...glassVariants[variant] }}
  >
    {children}
  </div>
)

/* ─── OrbIndicator ─── */

interface OrbIndicatorProps {
  state?: OrbState
  countdown?: number
  size?: number
}

const orbColors: Record<OrbState, { main: string; glow: string }> = {
  idle: { main: '#4A9EFF', glow: 'rgba(74, 158, 255, 0.4)' },
  active: { main: '#00E676', glow: 'rgba(0, 230, 118, 0.4)' },
  critical: { main: '#FF5252', glow: 'rgba(255, 82, 82, 0.5)' },
}

const CountdownRing: React.FC<{ countdown: number; color: string; size: number }> = ({
  countdown,
  color,
  size,
}) => {
  const radius = size * 0.4
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - countdown / 30)
  const viewBox = size

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${viewBox} ${viewBox}`}
      style={{ position: 'absolute' }}
    >
      <circle
        cx={viewBox / 2}
        cy={viewBox / 2}
        r={radius}
        fill="none"
        stroke="rgba(255,255,255,0.05)"
        strokeWidth={2}
      />
      <circle
        cx={viewBox / 2}
        cy={viewBox / 2}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={2}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${viewBox / 2} ${viewBox / 2})`}
        style={{ transition: 'stroke-dashoffset 1s linear' }}
      />
    </svg>
  )
}

export const OrbIndicator: React.FC<OrbIndicatorProps> = ({
  state = 'idle',
  countdown = 30,
  size = 48,
}) => {
  const colors = orbColors[state]

  return (
    <div
      style={{
        position: 'relative',
        width: size,
        height: size,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: colors.main + '20',
        boxShadow: `0 0 20px ${colors.glow}, 0 0 40px ${colors.glow}`,
        transition: 'box-shadow 0.3s ease',
      }}
    >
      <div
        style={{
          width: size * 0.5,
          height: size * 0.5,
          borderRadius: '50%',
          backgroundColor: colors.main,
          boxShadow: `0 0 12px ${colors.glow}`,
          transition: 'background-color 0.3s ease',
        }}
      />
      {state !== 'idle' && (
        <CountdownRing countdown={countdown} color={colors.main} size={size} />
      )}
    </div>
  )
}

/* ─── SpotlightInput ─── */

interface SuggestionItem {
  type: string
  label: string
  description: string
  action?: () => void
}

interface SpotlightInputProps {
  isOpen: boolean
  onClose: () => void
  suggestions?: SuggestionItem[]
  placeholder?: string
}

export const SpotlightInput: React.FC<SpotlightInputProps> = ({
  isOpen,
  onClose,
  suggestions = [],
  placeholder = 'Search commands, files, or ask AI...',
}) => {
  const [query, setQuery] = useState('')
  const [selectedIdx, setSelectedIdx] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const filtered = query
    ? suggestions.filter((s) =>
        s.label.toLowerCase().includes(query.toLowerCase())
      )
    : suggestions

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
        setSelectedIdx((i) => Math.min(i + 1, filtered.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIdx((i) => Math.max(i - 1, 0))
      } else if (e.key === 'Enter' && filtered[selectedIdx]?.action) {
        filtered[selectedIdx].action!()
        onClose()
      } else if (e.key === 'Escape') {
        onClose()
      }
    },
    [selectedIdx, filtered, onClose]
  )

  if (!isOpen) return null

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '15vh',
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.6)',
          backdropFilter: 'blur(24px)',
          WebkitBackdropFilter: 'blur(24px)',
        }}
        onClick={onClose}
      />
      <div
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: 600,
          background: 'rgba(255, 255, 255, 0.06)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 16,
          overflow: 'hidden',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '12px 16px',
            borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
          }}
        >
          <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 14 }}>
            <SearchIcon />
          </span>
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => { setQuery(e.target.value); setSelectedIdx(0) }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'rgba(255,255,255,0.8)',
              fontSize: 14,
              fontFamily: 'inherit',
            }}
          />
          <kbd
            style={{
              fontSize: 10,
              padding: '2px 6px',
              borderRadius: 4,
              background: 'rgba(255,255,255,0.05)',
              color: 'rgba(255,255,255,0.3)',
              fontFamily: 'inherit',
            }}
          >
            ESC
          </kbd>
        </div>

        <div style={{ padding: 8, maxHeight: 320, overflowY: 'auto' }}>
          {filtered.map((s, i) => (
            <button
              key={s.label + i}
              onClick={() => { s.action?.(); onClose() }}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '10px 12px',
                borderRadius: 8,
                border: 'none',
                background: i === selectedIdx ? 'rgba(255,255,255,0.1)' : 'transparent',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'background 0.15s',
                fontFamily: 'inherit',
              }}
              onMouseEnter={() => setSelectedIdx(i)}
            >
              <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12 }}>{s.type}</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {s.label}
                </div>
                <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 11, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {s.description}
                </div>
              </div>
            </button>
          ))}
          {filtered.length === 0 && (
            <div style={{ textAlign: 'center', padding: '24px 0', color: 'rgba(255,255,255,0.2)', fontSize: 13 }}>
              No results found
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/* ─── WorkspaceContainer ─── */

interface WorkspaceContainerProps {
  children: React.ReactNode
  accentColor?: string
  layout?: LayoutConfig
  sidebarExpanded?: boolean
  style?: React.CSSProperties
}

export const WorkspaceContainer: React.FC<WorkspaceContainerProps> = ({
  children,
  accentColor = '#4A9EFF',
  layout,
  sidebarExpanded = true,
  style,
}) => (
  <div
    style={{
      display: 'flex',
      height: '100%',
      width: '100%',
      position: 'relative',
      ...style,
    }}
  >
    {sidebarExpanded && (
      <div
        style={{
          width: 48,
          borderRight: '1px solid rgba(255,255,255,0.05)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: '8px 0',
          gap: 8,
          flexShrink: 0,
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            backgroundColor: accentColor + '20',
            border: `1px solid ${accentColor}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 14,
            color: accentColor,
          }}
        />
        <div style={{ width: 24, height: 24, borderRadius: 6, background: 'rgba(255,255,255,0.05)' }} />
        <div style={{ width: 24, height: 24, borderRadius: 6, background: 'rgba(255,255,255,0.05)' }} />
        <div style={{ width: 24, height: 24, borderRadius: 6, background: 'rgba(255,255,255,0.05)' }} />
      </div>
    )}
    <div style={{ flex: 1, overflow: 'auto', padding: layout ? 16 : 0 }}>
      <div
        style={{
          width: '100%',
          height: '100%',
          '--accent-color': accentColor,
        } as React.CSSProperties}
      >
        {children}
      </div>
    </div>
  </div>
)

interface AIAgentCardType {
  name: string
  role: string
  recommendation: string
  confidence: number
  risk: number
  color?: string
}

/* ─── AIAgentCard ─── */

interface AIAgentCardProps {
  agent: AIAgentCardType
}

export const AIAgentCard: React.FC<AIAgentCardProps> = ({ agent }) => (
  <div
    style={{
      padding: 16,
      borderRadius: 12,
      background: 'rgba(255,255,255,0.05)',
      border: '1px solid rgba(255,255,255,0.06)',
      borderLeft: `2px solid ${agent.color || '#666'}`,
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
      <span style={{ fontSize: 13, fontWeight: 500, color: 'rgba(255,255,255,0.8)' }}>
        {agent.name}
      </span>
      <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)' }}>
        {agent.role}
      </span>
    </div>
    <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 8, lineHeight: '1.4em' }}>
      {agent.recommendation}
    </div>
    <div style={{ display: 'flex', gap: 12 }}>
      <span style={{ fontSize: 10, color: agent.confidence > 0.7 ? '#00E676' : '#FFB300' }}>
        {(agent.confidence * 100).toFixed(0)}%
      </span>
      <span style={{ fontSize: 10, color: agent.risk > 0.5 ? '#FF5252' : '#B0B0B0' }}>
        Risk: {(agent.risk * 100).toFixed(0)}%
      </span>
    </div>
  </div>
)

/* ─── CouncilPanel ─── */

interface CouncilPanelProps {
  isOpen: boolean
  onClose: () => void
  outputs: AIAgentCardType[]
  decision: CouncilDecision | null
  loading?: boolean
  onOrchestrate?: (input: string) => void
}

export const CouncilPanel: React.FC<CouncilPanelProps> = ({
  isOpen,
  onClose,
  outputs,
  decision,
  loading = false,
  onOrchestrate,
}) => {
  const [input, setInput] = useState('')

  const handleOrchestrate = () => {
    if (!input.trim() || !onOrchestrate) return
    onOrchestrate(input)
  }

  if (!isOpen) return null

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(0,0,0,0.6)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
        }}
        onClick={onClose}
      />
      <div
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: 672,
          maxHeight: '80vh',
          background: 'rgba(255,255,255,0.06)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 16,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px 20px',
            borderBottom: '1px solid rgba(255,255,255,0.05)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 14, fontWeight: 500, color: 'rgba(255,255,255,0.8)' }}>
              AI Council
            </span>
          </div>
          <button
            onClick={onClose}
            style={{
              padding: 6,
              borderRadius: 8,
              border: 'none',
              background: 'transparent',
              color: 'rgba(255,255,255,0.3)',
              cursor: 'pointer',
            }}
          >
            ✕
          </button>
        </div>

        <div style={{ padding: 20, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleOrchestrate()}
              placeholder="What would you like the council to decide?"
              style={{
                flex: 1,
                padding: '10px 16px',
                borderRadius: 12,
                border: '1px solid rgba(255,255,255,0.1)',
                background: 'rgba(255,255,255,0.05)',
                color: 'rgba(255,255,255,0.8)',
                fontSize: 13,
                outline: 'none',
                fontFamily: 'inherit',
              }}
            />
            <button
              onClick={handleOrchestrate}
              disabled={loading || !input.trim()}
              style={{
                padding: '10px 16px',
                borderRadius: 12,
                border: 'none',
                background: 'rgba(255,255,255,0.1)',
                color: 'rgba(255,255,255,0.8)',
                fontSize: 13,
                cursor: 'pointer',
                opacity: loading || !input.trim() ? 0.3 : 1,
                fontFamily: 'inherit',
              }}
            >
              {loading ? 'Consulting...' : 'Orchestrate'}
            </button>
          </div>

          {loading && (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 24 }}>
              <div style={{ display: 'flex', gap: 4 }}>
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: 'rgba(255,255,255,0.3)',
                      animation: 'none',
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {outputs.length > 0 && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {outputs.map((o) => (
                <AIAgentCard key={o.name} agent={o} />
              ))}
            </div>
          )}

          {decision && (
            <div
              style={{
                padding: 16,
                borderRadius: 12,
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.06)',
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: 13, fontWeight: 500, color: 'rgba(255,255,255,0.8)' }}>
                  Council Decision
                </span>
                <span style={{
                  fontSize: 11,
                  color: decision.riskLevel === 'critical' ? '#FF5252'
                    : decision.riskLevel === 'high' ? '#FFB300'
                    : decision.riskLevel === 'medium' ? '#FFA726'
                    : '#00E676',
                }}>
                  {(decision.confidence * 100).toFixed(0)}% confidence · {decision.riskLevel} risk
                </span>
              </div>
              <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', lineHeight: '1.5em' }}>
                {decision.reasoning.slice(0, 200)}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/* ─── FocusOverlay ─── */

interface FocusOverlayProps {
  mode: FocusMode
  blockedProcesses?: string[]
}

const focusConfig: Record<FocusMode, { label: string; description: string; color: string; bg: string; border: string }> = {
  normal: {
    label: 'Normal Mode',
    description: 'All processes allowed. Full system access.',
    color: '#666',
    bg: 'rgba(255,255,255,0.02)',
    border: 'rgba(255,255,255,0.05)',
  },
  focus: {
    label: 'Focus Mode',
    description: 'Non-essential notifications suppressed. Distractions minimized.',
    color: '#00E676',
    bg: 'rgba(0,230,118,0.05)',
    border: 'rgba(0,230,118,0.2)',
  },
  deep_focus: {
    label: 'Deep Focus Mode',
    description: 'Only critical notifications. All social/entertainment blocked.',
    color: '#FFB300',
    bg: 'rgba(255,179,0,0.05)',
    border: 'rgba(255,179,0,0.2)',
  },
  lock: {
    label: 'Lock Mode',
    description: 'Maximum restriction. Only essential apps allowed.',
    color: '#FF5252',
    bg: 'rgba(255,82,82,0.05)',
    border: 'rgba(255,82,82,0.2)',
  },
}

export const FocusOverlay: React.FC<FocusOverlayProps> = ({
  mode,
  blockedProcesses = [],
}) => {
  if (mode === 'normal') return null

  const config = focusConfig[mode]

  return (
    <div
      style={{
        position: 'fixed',
        top: 48,
        left: 0,
        right: 0,
        zIndex: 30,
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          margin: '0 auto',
          maxWidth: 512,
          borderBottomLeftRadius: 16,
          borderBottomRightRadius: 16,
          padding: '12px 24px',
          textAlign: 'center',
          backgroundColor: config.bg,
          borderLeft: `1px solid ${config.border}`,
          borderRight: `1px solid ${config.border}`,
          borderBottom: `1px solid ${config.border}`,
        }}
      >
        <span style={{ fontSize: 13, fontWeight: 500, color: config.color }}>
          {config.label}
        </span>
        <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', margin: '2px 0 0 0' }}>
          {config.description}
        </p>
        {blockedProcesses.length > 0 && (
          <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 8 }}>
            {blockedProcesses.map((p) => (
              <span
                key={p}
                style={{
                  fontSize: 10,
                  padding: '2px 8px',
                  borderRadius: 12,
                  background: 'rgba(255,255,255,0.05)',
                  color: 'rgba(255,255,255,0.3)',
                }}
              >
                Blocked: {p}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

/* ─── TaskCard ─── */

interface TaskCardProps {
  task: TaskType
  onToggle?: (id: string) => void
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, onToggle }) => {
  const priorityColors: Record<number, string> = {
    1: '#4A9EFF',
    2: '#00E676',
    3: '#FFB300',
    4: '#FF5252',
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: 12,
        padding: 12,
        borderRadius: 12,
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.06)',
        transition: 'background 0.15s',
      }}
    >
      <button
        onClick={() => onToggle?.(task.id)}
        style={{
          width: 20,
          height: 20,
          borderRadius: '50%',
          border: `2px solid ${task.completed ? '#00E676' : 'rgba(255,255,255,0.2)'}`,
          background: task.completed ? '#00E676' : 'transparent',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          marginTop: 2,
        }}
      >
        {task.completed && (
          <span style={{ color: '#fff', fontSize: 10 }}>✓</span>
        )}
      </button>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
          <span style={{
            fontSize: 13,
            color: task.completed ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.8)',
            textDecoration: task.completed ? 'line-through' : 'none',
          }}>
            {task.title}
          </span>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: priorityColors[task.priority] || '#666',
              flexShrink: 0,
            }}
          />
        </div>
        {task.description && (
          <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', margin: 0, lineHeight: '1.4em' }}>
            {task.description}
          </p>
        )}
        <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
          <span style={{
            fontSize: 10,
            padding: '1px 6px',
            borderRadius: 4,
            background: 'rgba(255,255,255,0.05)',
            color: 'rgba(255,255,255,0.3)',
          }}>
            {task.workspace}
          </span>
          {task.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              style={{
                fontSize: 10,
                padding: '1px 6px',
                borderRadius: 4,
                background: 'rgba(255,255,255,0.05)',
                color: 'rgba(255,255,255,0.2)',
              }}
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ─── FileBrowser ─── */

type FileViewMode = 'folder' | 'tag' | 'graph'

interface FileBrowserProps {
  initialView?: FileViewMode
}

const sampleFiles = [
  { name: 'main.ts', type: 'file' as const, folder: 'src/' },
  { name: 'App.tsx', type: 'file' as const, folder: 'src/' },
  { name: 'utils.ts', type: 'file' as const, folder: 'src/' },
  { name: 'api.ts', type: 'file' as const, folder: 'src/' },
  { name: 'README.md', type: 'file' as const, folder: 'docs/' },
  { name: 'package.json', type: 'file' as const, folder: 'config/' },
  { name: 'tsconfig.json', type: 'file' as const, folder: 'config/' },
]

const fileTags: Record<string, string[]> = {
  'main.ts': ['typescript', 'core'],
  'App.tsx': ['react', 'ui'],
  'utils.ts': ['typescript', 'utility'],
  'api.ts': ['typescript', 'api'],
  'README.md': ['docs'],
  'package.json': ['config'],
  'tsconfig.json': ['config'],
}

const graphRelations = [
  { from: 'main.ts', to: 'utils.ts', strength: 0.85 },
  { from: 'main.ts', to: 'api.ts', strength: 0.72 },
  { from: 'App.tsx', to: 'main.ts', strength: 0.64 },
  { from: 'api.ts', to: 'package.json', strength: 0.3 },
]

const allTags = [...new Set(Object.values(fileTags).flat())]

export const FileBrowser: React.FC<FileBrowserProps> = ({
  initialView = 'folder',
}) => {
  const [view, setView] = useState<FileViewMode>(initialView)
  const [search, setSearch] = useState('')

  const viewModeStyle: React.CSSProperties = {
    display: 'flex',
    gap: 8,
    padding: '8px 16px',
    borderBottom: '1px solid rgba(255,255,255,0.05)',
    alignItems: 'center',
  }

  const tabButton = (active: boolean): React.CSSProperties => ({
    padding: '4px 12px',
    borderRadius: 6,
    border: 'none',
    fontSize: 11,
    cursor: 'pointer',
    background: active ? 'rgba(255,255,255,0.1)' : 'transparent',
    color: active ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.3)',
    fontFamily: 'inherit',
    transition: 'all 0.15s',
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={viewModeStyle}>
        {(['folder', 'tag', 'graph'] as FileViewMode[]).map((v) => (
          <button
            key={v}
            onClick={() => setView(v)}
            style={tabButton(view === v)}
          >
            {v.charAt(0).toUpperCase() + v.slice(1)}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <input
          placeholder="Filter..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            padding: '4px 8px',
            borderRadius: 6,
            border: 'none',
            background: 'rgba(255,255,255,0.05)',
            color: 'rgba(255,255,255,0.6)',
            fontSize: 11,
            width: 100,
            outline: 'none',
            fontFamily: 'inherit',
          }}
        />
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: 8 }}>
        {view === 'folder' && (
          <div>
            {['src/', 'docs/', 'config/'].map((folder) => {
              const files = sampleFiles.filter((f) => f.folder === folder)
              return (
                <div key={folder}>
                  <div style={{ padding: '6px 8px', fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>
                    📁 {folder}
                  </div>
                  {files
                    .filter((f) => !search || f.name.toLowerCase().includes(search.toLowerCase()))
                    .map((f) => (
                      <div
                        key={f.name}
                        style={{
                          padding: '6px 8px 6px 28px',
                          borderRadius: 6,
                          fontSize: 12,
                          color: 'rgba(255,255,255,0.6)',
                          cursor: 'pointer',
                        }}
                      >
                        📄 {f.name}
                      </div>
                    ))}
                </div>
              )
            })}
          </div>
        )}

        {view === 'tag' && (
          <div>
            {allTags
              .filter((t) => !search || t.includes(search))
              .map((tag) => (
                <div key={tag} style={{ marginBottom: 12 }}>
                  <div style={{ padding: '6px 8px', fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>
                    # {tag}
                  </div>
                  {Object.entries(fileTags)
                    .filter(([_, tags]) => tags.includes(tag))
                    .map(([fileName]) => (
                      <div
                        key={fileName}
                        style={{
                          padding: '4px 8px 4px 28px',
                          borderRadius: 6,
                          fontSize: 12,
                          color: 'rgba(255,255,255,0.5)',
                          cursor: 'pointer',
                        }}
                      >
                        📄 {fileName}
                      </div>
                    ))}
                </div>
              ))}
          </div>
        )}

        {view === 'graph' && (
          <div style={{ padding: 8 }}>
            {graphRelations.map((rel) => (
              <div
                key={`${rel.from}-${rel.to}`}
                style={{
                  padding: 12,
                  borderRadius: 8,
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  marginBottom: 8,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'rgba(255,255,255,0.7)', marginBottom: 4 }}>
                  <span>{rel.from}</span>
                  <span style={{ fontSize: 10, color: '#B388FF' }}>
                    {(rel.strength * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)' }}>
                  → {rel.to}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

/* ─── AppCard ─── */

interface AppCardProps {
  app: AppManifest
  installed?: boolean
  onToggle?: (id: string) => void
}

export const AppCard: React.FC<AppCardProps> = ({
  app,
  installed = false,
  onToggle,
}) => (
  <div
    style={{
      padding: 16,
      borderRadius: 16,
      background: 'rgba(255,255,255,0.04)',
      border: '1px solid rgba(255,255,255,0.06)',
      transition: 'all 0.15s',
    }}
  >
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
      <div>
        <div style={{ fontSize: 13, fontWeight: 500, color: 'rgba(255,255,255,0.8)', marginBottom: 4 }}>
          {app.name}
        </div>
        <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', margin: 0, lineHeight: '1.4em' }}>
          {app.description}
        </p>
      </div>
      {app.aiTested && (
        <span
          style={{
            padding: '2px 6px',
            borderRadius: 4,
            background: 'rgba(0,230,118,0.1)',
            color: '#00E676',
            fontSize: 9,
            whiteSpace: 'nowrap',
          }}
        >
          AI
        </span>
      )}
    </div>
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 11, color: '#FFB300' }}>★ {app.rating}</span>
        <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.2)' }}>{app.category}</span>
      </div>
      <button
        onClick={() => onToggle?.(app.id)}
        style={{
          padding: '6px 12px',
          borderRadius: 8,
          border: 'none',
          fontSize: 11,
          cursor: 'pointer',
          background: installed
            ? 'rgba(255,255,255,0.1)'
            : 'rgba(0,230,118,0.15)',
          color: installed
            ? 'rgba(255,255,255,0.6)'
            : '#00E676',
          fontFamily: 'inherit',
          transition: 'all 0.15s',
        }}
      >
        {installed ? 'Installed' : 'Install'}
      </button>
    </div>
  </div>
)

/* ─── Inline SearchIcon ─── */

const SearchIcon: React.FC = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
)
