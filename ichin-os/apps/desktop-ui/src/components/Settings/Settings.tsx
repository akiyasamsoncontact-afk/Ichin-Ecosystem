import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Sliders, Eye, Palette, Shield, Keyboard, Lock } from 'lucide-react'
import { useUIStore } from '../../stores/uiStore'

const SECTIONS = [
  { id: 'behavior', label: 'AI Behavior', icon: Sliders },
  { id: 'focus', label: 'Focus Mode', icon: Eye },
  { id: 'themes', label: 'Workspace Themes', icon: Palette },
  { id: 'permissions', label: 'Agent Permissions', icon: Shield },
  { id: 'shortcuts', label: 'Shortcuts', icon: Keyboard },
  { id: 'privacy', label: 'Privacy Controls', icon: Lock },
]

const SHORTCUTS = [
  { keys: 'Ctrl + Space', action: 'Open Spotlight' },
  { keys: 'Ctrl + A', action: 'Open AI Council' },
  { keys: 'Ctrl + F', action: 'Cycle Focus Mode' },
  { keys: 'Ctrl + Tab', action: 'Cycle Workspace' },
  { keys: 'Ctrl + Shift + W', action: 'Mission Control' },
  { keys: 'Ctrl + ,', action: 'Open Settings' },
  { keys: 'Ctrl + /', action: 'Keyboard Cheatsheet' },
  { keys: 'Esc', action: 'Close panel / Go back' },
]

export default function Settings() {
  const isOpen = useUIStore((s) => s.settingsOpen)
  const setOpen = useUIStore((s) => s.setSettingsOpen)
  const [section, setSection] = useState('behavior')

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
          <div className="absolute inset-0 bg-black/60 backdrop-blur-lg" onClick={() => setOpen(false)} />
          <motion.div
            className="relative w-full max-w-2xl max-h-[80vh] glass-strong rounded-2xl overflow-hidden flex"
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
          >
            <div className="w-44 border-r border-white/5 p-3 space-y-1">
              {SECTIONS.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setSection(s.id)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs transition-all ${
                    section === s.id ? 'bg-white/10 text-white/80' : 'text-white/30 hover:text-white/50 hover:bg-white/5'
                  }`}
                >
                  <s.icon size={14} />
                  {s.label}
                </button>
              ))}
            </div>

            <div className="flex-1 p-5 overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-sm font-medium text-white/80">{SECTIONS.find((s) => s.id === section)?.label}</h2>
                <button onClick={() => setOpen(false)} className="p-1 rounded hover:bg-white/10 text-white/30">
                  <X size={16} />
                </button>
              </div>

              {section === 'behavior' && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs text-white/40">AI Aggression Level</label>
                    <input type="range" min="0" max="100" defaultValue={50}
                      className="w-full accent-white/50"
                    />
                    <div className="flex justify-between text-[10px] text-white/20">
                      <span>Passive</span><span>Balanced</span><span>Aggressive</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs text-white/40">Suggestion Frequency</label>
                    <input type="range" min="0" max="100" defaultValue={40}
                      className="w-full accent-white/50"
                    />
                    <div className="flex justify-between text-[10px] text-white/20">
                      <span>Rarely</span><span>Normal</span><span>Often</span>
                    </div>
                  </div>
                </div>
              )}

              {section === 'focus' && (
                <div className="space-y-3">
                  {['Normal', 'Focus', 'Deep Focus', 'Lock'].map((m) => (
                    <div key={m} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                      <span className="text-sm text-white/70">{m}</span>
                      <div className="flex gap-2">
                        {['block', 'notify', 'allow'].map((a) => (
                          <label key={a} className="flex items-center gap-1 text-xs text-white/30 cursor-pointer">
                            <input type="checkbox" defaultChecked={a === 'allow'} className="accent-white/30" />
                            {a}
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {section === 'themes' && (
                <div className="space-y-3">
                  {['Study', 'Coding', 'Learning', 'Personal'].map((ws) => (
                    <div key={ws} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                      <span className="text-sm text-white/70">{ws}</span>
                      <input type="color" defaultValue={
                        ws === 'Study' ? '#4A9EFF' : ws === 'Coding' ? '#00E676' : ws === 'Learning' ? '#B388FF' : '#9E9E9E'
                      } className="w-8 h-8 rounded cursor-pointer bg-transparent" />
                    </div>
                  ))}
                </div>
              )}

              {section === 'permissions' && (
                <div className="space-y-3">
                  {['orion', 'nova', 'sage', 'pulse', 'echo', 'iris', 'atlas', 'aegis'].map((agent) => (
                    <div key={agent} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                      <span className="text-sm text-white/70 capitalize">{agent}</span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" defaultChecked className="sr-only peer" />
                        <div className="w-9 h-5 rounded-full bg-white/10 peer-checked:bg-white/30 transition-all" />
                      </label>
                    </div>
                  ))}
                </div>
              )}

              {section === 'shortcuts' && (
                <div className="space-y-2">
                  {SHORTCUTS.map((s) => (
                    <div key={s.action} className="flex items-center justify-between p-2.5 rounded-lg hover:bg-white/5">
                      <span className="text-sm text-white/60">{s.action}</span>
                      <kbd className="text-xs px-2 py-1 rounded bg-white/5 text-white/30 font-mono">{s.keys}</kbd>
                    </div>
                  ))}
                </div>
              )}

              {section === 'privacy' && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-white/5 space-y-3">
                    <h3 className="text-xs text-white/50">Memory Management</h3>
                    <p className="text-xs text-white/30">Total stored memories: 1,432 items (45 MB)</p>
                    <div className="flex gap-2">
                      <button className="px-3 py-1.5 rounded-lg bg-white/10 text-xs text-white/60 hover:bg-white/15">
                        Clear Session
                      </button>
                      <button className="px-3 py-1.5 rounded-lg bg-red-500/10 text-xs text-red-400/60 hover:bg-red-500/20">
                        Delete All
                      </button>
                    </div>
                  </div>
                  <div className="p-4 rounded-xl bg-white/5 space-y-3">
                    <h3 className="text-xs text-white/50">Data Deletion</h3>
                    <p className="text-xs text-white/30">Permanently remove all stored data</p>
                    <button className="px-3 py-1.5 rounded-lg bg-red-500/10 text-xs text-red-400/60 hover:bg-red-500/20">
                      Factory Reset
                    </button>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
