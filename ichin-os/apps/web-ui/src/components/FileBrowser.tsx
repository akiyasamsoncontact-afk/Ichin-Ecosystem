import { useState } from 'react'

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
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ display: 'flex', background: 'rgba(255,255,255,0.05)', borderRadius: 8, padding: 2 }}>
          {(['folder', 'tag', 'ai'] as ViewMode[]).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              style={{
                padding: '4px 12px',
                borderRadius: 6,
                fontSize: 11,
                border: 'none',
                background: view === v ? 'rgba(255,255,255,0.1)' : 'transparent',
                color: view === v ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.3)',
                cursor: 'pointer',
              }}
            >
              {v === 'folder' ? '📁 ' : v === 'tag' ? '🏷 ' : '🔀 '}
              {v.charAt(0).toUpperCase() + v.slice(1)}
            </button>
          ))}
        </div>
        <div style={{ flex: 1 }} />
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '4px 8px', borderRadius: 6, background: 'rgba(255,255,255,0.05)' }}>
          <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)' }}>⌕</span>
          <input
            placeholder="Filter..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: 100,
              background: 'transparent',
              border: 'none',
              color: 'rgba(255,255,255,0.6)',
              fontSize: 11,
              outline: 'none',
            }}
          />
        </div>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: 8 }}>
        {view === 'folder' && (
          <div>
            {['src/', 'public/', 'docs/', 'tests/'].map((folder) => (
              <div key={folder} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '6px 10px',
                borderRadius: 6,
                cursor: 'pointer',
                fontSize: 12,
                color: 'rgba(255,255,255,0.6)',
              }}>
                <span style={{ color: 'rgba(74,158,255,0.5)', fontSize: 12 }}>📁</span>
                {folder}
              </div>
            ))}
            {['main.ts', 'App.tsx', 'utils.ts', 'api.ts'].map((file) => (
              <div key={file} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '6px 10px',
                borderRadius: 6,
                cursor: 'pointer',
                fontSize: 12,
                color: 'rgba(255,255,255,0.6)',
              }}>
                <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12 }}>📄</span>
                {file}
              </div>
            ))}
          </div>
        )}

        {view === 'tag' && (
          <div>
            {TAGS.filter((t) => !search || t.includes(search)).map((tag) => (
              <div key={tag} style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '4px 10px', marginBottom: 4 }}>
                  <span style={{ fontSize: 11, color: '#9E9E9E' }}>🏷</span>
                  <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>{tag}</span>
                  <span style={{ fontSize: 9, color: 'rgba(255,255,255,0.2)' }}>({TAGGED_FILES[tag].length})</span>
                </div>
                {TAGGED_FILES[tag].map((f) => (
                  <div key={f} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '4px 10px',
                    paddingLeft: 32,
                    borderRadius: 6,
                    cursor: 'pointer',
                    fontSize: 11,
                    color: 'rgba(255,255,255,0.6)',
                  }}>
                    <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)' }}>📄</span>
                    {f}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}

        {view === 'ai' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {AI_FILES.map((f) => (
              <div key={f.name} style={{
                background: 'rgba(255,255,255,0.05)',
                borderRadius: 12,
                padding: 12,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)' }}>{f.name}</span>
                  <span style={{ fontSize: 9, color: '#B388FF' }}>
                    {(f.strength * 100).toFixed(0)}% related
                  </span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                  {f.related.map((r) => (
                    <span key={r} style={{
                      fontSize: 9,
                      padding: '2px 6px',
                      borderRadius: 4,
                      background: 'rgba(255,255,255,0.05)',
                      color: 'rgba(255,255,255,0.3)',
                    }}>
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
