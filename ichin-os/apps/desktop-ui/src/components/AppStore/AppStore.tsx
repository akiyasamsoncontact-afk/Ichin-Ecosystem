import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Star, Download, X, Shield, Sparkles } from 'lucide-react'
import { useUIStore } from '../../stores/uiStore'
import { appsApi } from '../../services/api'
import type { AppManifest } from '../../types'

const CATEGORIES = ['All', 'Productivity', 'Study', 'Coding', 'AI', 'Creativity', 'Utilities']

const SAMPLE_APPS: AppManifest[] = [
  { id: 'md-editor', name: 'Advanced Markdown Editor', description: 'Full-featured markdown with live preview and AI autocomplete', version: '2.1.0', author: 'Ichin Labs', icon: '', category: 'Productivity', permissions: [], aiCompatibility: 92, workspaceIntegration: ['study', 'coding'], rating: 4.5, aiTested: true },
  { id: 'flashmaster', name: 'FlashMaster Pro', description: 'AI-powered flashcard generation with spaced repetition', version: '1.3.0', author: 'StudyAI', icon: '', category: 'Study', permissions: [], aiCompatibility: 95, workspaceIntegration: ['study'], rating: 4.8, aiTested: true },
  { id: 'code-assist', name: 'Code Assist Pro', description: 'Real-time code suggestions, refactoring, and bug detection', version: '3.0.0', author: 'DevTools Inc', icon: '', category: 'Coding', permissions: [], aiCompatibility: 88, workspaceIntegration: ['coding'], rating: 4.3, aiTested: false },
  { id: 'mindforge', name: 'MindForge', description: 'Visual knowledge graph builder with AI connections', version: '1.0.0', author: 'NeuroAI', icon: '', category: 'AI', permissions: [], aiCompatibility: 97, workspaceIntegration: ['learning', 'study'], rating: 4.6, aiTested: true },
  { id: 'timeline', name: 'Timeline Planner', description: 'AI-optimized daily planning and time blocking', version: '2.0.0', author: 'ProductivityLabs', icon: '', category: 'Productivity', permissions: [], aiCompatibility: 78, workspaceIntegration: ['personal'], rating: 4.1, aiTested: false },
  { id: 'artisan', name: 'Artisan Canvas', description: 'AI-assisted digital art and design tool', version: '1.2.0', author: 'CreativeAI', icon: '', category: 'Creativity', permissions: [], aiCompatibility: 85, workspaceIntegration: ['personal'], rating: 4.4, aiTested: true },
]

export default function AppStore() {
  const isOpen = useUIStore((s) => s.spotlightOpen)
  const [category, setCategory] = useState('All')
  const [search, setSearch] = useState('')
  const [installed, setInstalled] = useState<Set<string>>(new Set())

  const filtered = SAMPLE_APPS.filter((app) => {
    if (category !== 'All' && app.category !== category) return false
    if (search && !app.name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const toggleInstall = async (id: string) => {
    if (installed.has(id)) {
      setInstalled((p) => { const n = new Set(p); n.delete(id); return n })
      try { await appsApi.uninstall(id) } catch {}
    } else {
      setInstalled((p) => new Set(p).add(id))
      try { await appsApi.install(id) } catch {}
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2 mb-3">
          <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5">
            <Search size={14} className="text-white/30" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search apps..."
              className="flex-1 bg-transparent text-sm text-white/60 placeholder:text-white/20 focus:outline-none"
            />
          </div>
        </div>
        <div className="flex gap-2 overflow-x-auto">
          {CATEGORIES.map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={`px-3 py-1.5 rounded-lg text-xs whitespace-nowrap transition-all ${
                category === c ? 'bg-white/15 text-white/80' : 'text-white/30 hover:text-white/50 hover:bg-white/5'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4">
        <div className="grid grid-cols-2 gap-3">
          {filtered.map((app) => (
            <motion.div
              key={app.id}
              className="glass rounded-2xl p-4 hover:bg-white/5 transition-all"
              whileHover={{ y: -2 }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="space-y-1">
                  <h3 className="text-sm text-white/80">{app.name}</h3>
                  <p className="text-xs text-white/30 line-clamp-2">{app.description}</p>
                </div>
                {app.aiTested && (
                  <span className="shrink-0 px-1.5 py-0.5 rounded bg-accent-coding/10 text-accent-coding text-[10px] flex items-center gap-0.5">
                    <Sparkles size={10} />
                    AI
                  </span>
                )}
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-0.5 text-xs text-white/30">
                    <Star size={11} className="text-yellow-500" />
                    {app.rating}
                  </div>
                  <span className="text-[10px] text-white/20">{app.category}</span>
                </div>
                <button
                  onClick={() => toggleInstall(app.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs transition-all ${
                    installed.has(app.id)
                      ? 'bg-white/10 text-white/60 hover:bg-white/15'
                      : 'bg-accent-coding/15 text-accent-coding hover:bg-accent-coding/25'
                  }`}
                >
                  {installed.has(app.id) ? 'Installed' : 'Install'}
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
