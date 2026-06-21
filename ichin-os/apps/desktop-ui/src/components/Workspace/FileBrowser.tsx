import { useState } from 'react'
import { Folder, File, Tags, Search as SearchIcon, GitBranch } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

type ViewMode = 'folder' | 'tag' | 'ai'

const TAGS = ['typescript', 'react', 'api', 'docs', 'config', 'test']

const TAGGED_FILES: Record<string, string[]> = {
  typescript: ['main.ts', 'utils.ts', 'api.ts'],
  react: ['App.tsx', 'Header.tsx'],
  api: ['api.ts', 'routes.ts'],
  docs: ['README.md', 'CONTRIBUTING.md'],
  config: ['package.json', 'tsconfig.json'],
  test: ['main.test.ts'],
}

const AI_FILES = [
  { name: 'main.ts', related: ['utils.ts', 'api.ts', 'App.tsx'], strength: 0.85 },
  { name: 'App.tsx', related: ['Header.tsx', 'main.ts'], strength: 0.72 },
  { name: 'api.ts', related: ['routes.ts', 'main.ts'], strength: 0.64 },
]

export default function FileBrowser() {
  const [view, setView] = useState<ViewMode>('folder')
  const [search, setSearch] = useState('')

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-white/5">
        <div className="flex bg-white/5 rounded-lg p-0.5">
          {(['folder', 'tag', 'ai'] as ViewMode[]).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-3 py-1 rounded-md text-xs transition-all ${
                view === v ? 'bg-white/10 text-white/80' : 'text-white/30 hover:text-white/50'
              }`}
            >
              {v === 'folder' && <Folder size={12} className="inline mr-1" />}
              {v === 'tag' && <Tags size={12} className="inline mr-1" />}
              {v === 'ai' && <GitBranch size={12} className="inline mr-1" />}
              {v.charAt(0).toUpperCase() + v.slice(1)}
            </button>
          ))}
        </div>
        <div className="flex-1" />
        <div className="flex items-center gap-1 px-2 py-1 rounded-lg bg-white/5 text-xs text-white/30">
          <SearchIcon size={12} />
          <input
            placeholder="Filter..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-24 bg-transparent text-white/60 placeholder:text-white/20 focus:outline-none"
          />
        </div>
      </div>

      <div className="flex-1 overflow-auto p-2">
        {view === 'folder' && (
          <div className="space-y-0.5">
            {['src/', 'public/', 'docs/', 'tests/'].map((folder) => (
              <div key={folder} className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/5 text-sm text-white/60 cursor-pointer">
                <Folder size={14} className="text-accent-study/50" />
                {folder}
              </div>
            ))}
            {['main.ts', 'App.tsx', 'utils.ts', 'api.ts'].map((file) => (
              <div key={file} className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/5 text-sm text-white/60 cursor-pointer">
                <File size={14} className="text-white/30" />
                {file}
              </div>
            ))}
          </div>
        )}

        {view === 'tag' && (
          <div className="space-y-3">
            {TAGS.filter((t) => !search || t.includes(search)).map((tag) => (
              <div key={tag}>
                <div className="flex items-center gap-2 px-2 py-1.5">
                  <Tags size={12} className="text-accent-personal" />
                  <span className="text-xs text-white/40">{tag}</span>
                  <span className="text-[10px] text-white/20">({TAGGED_FILES[tag].length})</span>
                </div>
                {TAGGED_FILES[tag].map((f) => (
                  <div key={f} className="flex items-center gap-2 px-6 py-1.5 rounded-lg hover:bg-white/5 text-xs text-white/60 cursor-pointer">
                    <File size={12} className="text-white/30" />
                    {f}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}

        {view === 'ai' && (
          <div className="space-y-4">
            {AI_FILES.map((f) => (
              <div key={f.name} className="glass rounded-xl p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-white/70">{f.name}</span>
                  <span className="text-[10px] text-accent-learning">
                    {(f.strength * 100).toFixed(0)}% related
                  </span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {f.related.map((r) => (
                    <span key={r} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-white/30">
                      {r}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
