import { motion, AnimatePresence } from 'framer-motion'
import { useFocusStore } from '../../stores/focusStore'

const FOCUS_CONFIG = {
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

export default function FocusOverlay() {
  const mode = useFocusStore((s) => s.mode)
  const blockedProcesses = useFocusStore((s) => s.blockedProcesses)
  const config = FOCUS_CONFIG[mode]

  return (
    <AnimatePresence>
      {mode !== 'normal' && (
        <motion.div
          className="fixed top-12 left-0 right-0 z-30 pointer-events-none"
          initial={{ y: -40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -40, opacity: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
        >
          <div
            className="mx-auto max-w-lg rounded-b-2xl px-6 py-3 text-center"
            style={{ backgroundColor: config.bg, borderLeft: `1px solid ${config.border}`, borderRight: `1px solid ${config.border}`, borderBottom: `1px solid ${config.border}` }}
          >
            <span className="text-sm font-medium" style={{ color: config.color }}>{config.label}</span>
            <p className="text-xs text-white/40 mt-0.5">{config.description}</p>
            {blockedProcesses.length > 0 && (
              <div className="flex justify-center gap-2 mt-2">
                {blockedProcesses.map((p) => (
                  <span key={p} className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-white/30">
                    Blocked: {p}
                  </span>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
