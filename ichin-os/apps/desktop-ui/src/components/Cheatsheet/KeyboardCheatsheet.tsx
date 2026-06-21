import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Keyboard } from 'lucide-react'
import { useUIStore } from '../../stores/uiStore'

const GROUPS = [
  {
    label: 'Navigation',
    shortcuts: [
      { keys: 'Ctrl + Space', action: 'Open Spotlight' },
      { keys: 'Ctrl + Tab', action: 'Cycle Workspace' },
      { keys: 'Ctrl + Shift + W', action: 'Mission Control' },
    ],
  },
  {
    label: 'AI & Focus',
    shortcuts: [
      { keys: 'Ctrl + A', action: 'Open AI Council' },
      { keys: 'Ctrl + F', action: 'Cycle Focus Mode' },
    ],
  },
  {
    label: 'System',
    shortcuts: [
      { keys: 'Ctrl + ,', action: 'Open Settings' },
      { keys: 'Ctrl + /', action: 'This Cheatsheet' },
      { keys: 'Esc', action: 'Close / Go Back' },
    ],
  },
]

export default function KeyboardCheatsheet() {
  const isOpen = useUIStore((s) => s.cheatsheetOpen)
  const setOpen = useUIStore((s) => s.setCheatsheetOpen)

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    if (isOpen) window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen])

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setOpen(false)} />
          <motion.div
            className="relative w-full max-w-md glass-strong rounded-2xl overflow-hidden"
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
              <div className="flex items-center gap-2">
                <Keyboard size={16} className="text-white/40" />
                <h2 className="text-sm text-white/70">Keyboard Shortcuts</h2>
              </div>
              <button onClick={() => setOpen(false)} className="p-1 rounded hover:bg-white/10 text-white/30">
                <X size={16} />
              </button>
            </div>
            <div className="p-5 space-y-5">
              {GROUPS.map((group) => (
                <div key={group.label}>
                  <h3 className="text-xs uppercase tracking-wider text-white/30 mb-2">{group.label}</h3>
                  <div className="space-y-1">
                    {group.shortcuts.map((s) => (
                      <div key={s.action} className="flex items-center justify-between py-2">
                        <span className="text-sm text-white/60">{s.action}</span>
                        <kbd className="text-xs px-2 py-1 rounded bg-white/5 text-white/30 font-mono">{s.keys}</kbd>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
