import { Book, Code, Brain, User } from 'lucide-react'
import { motion } from 'framer-motion'
import type { WorkspaceType } from '../../types'
import { useWorkspaceStore } from '../../stores/workspaceStore'

const ICONS: Record<WorkspaceType, React.ReactNode> = {
  study: <Book size={20} />,
  coding: <Code size={20} />,
  learning: <Brain size={20} />,
  personal: <User size={20} />,
}

const COLORS: Record<WorkspaceType, string> = {
  study: '#4A9EFF',
  coding: '#00E676',
  learning: '#B388FF',
  personal: '#9E9E9E',
}

const LABELS: Record<WorkspaceType, string> = {
  study: 'Study',
  coding: 'Coding',
  learning: 'Learning',
  personal: 'Personal',
}

const ORDER: WorkspaceType[] = ['study', 'coding', 'learning', 'personal']

export default function Sidebar() {
  const active = useWorkspaceStore((s) => s.active)
  const setActive = useWorkspaceStore((s) => s.setActive)

  return (
    <div className="flex flex-col items-center gap-3 py-4 px-2">
      {ORDER.map((ws) => {
        const isActive = ws === active
        return (
          <motion.button
            key={ws}
            onClick={() => setActive(ws)}
            className="relative flex items-center justify-center w-10 h-10 rounded-xl transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            title={LABELS[ws]}
          >
            {isActive && (
              <motion.div
                layoutId="sidebar-active"
                className="absolute inset-0 rounded-xl"
                style={{ backgroundColor: COLORS[ws] + '20', borderColor: COLORS[ws], borderWidth: 1 }}
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
            )}
            <span style={{ color: isActive ? COLORS[ws] : '#666' }}>
              {ICONS[ws]}
            </span>
          </motion.button>
        )
      })}
    </div>
  )
}
