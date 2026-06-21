import { useState } from 'react'

const FILES = [
  { name: 'src', type: 'folder' as const, children: [
    { name: 'main.ts', type: 'file' as const },
    { name: 'utils.ts', type: 'file' as const },
    { name: 'components', type: 'folder' as const, children: [
      { name: 'App.tsx', type: 'file' as const },
      { name: 'Header.tsx', type: 'file' as const },
    ]},
  ]},
  { name: 'package.json', type: 'file' as const },
  { name: 'tsconfig.json', type: 'file' as const },
]

interface FileNode {
  name: string
  type: 'file' | 'folder'
  children?: FileNode[]
}

function FileTree({ items, depth = 0 }: { items: FileNode[]; depth?: number }) {
  return (
    <div>
      {items.map((item) => (
        <div key={item.name}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '4px 8px',
            borderRadius: 6,
            cursor: 'pointer',
            fontSize: 12,
            color: 'rgba(255,255,255,0.7)',
            paddingLeft: `${12 + depth * 16}px`,
          }}>
            <span style={{ fontSize: 12, color: item.type === 'folder' ? 'rgba(0,230,118,0.6)' : 'rgba(255,255,255,0.4)' }}>
              {item.type === 'folder' ? '▸' : '○'}
            </span>
            {item.name}
          </div>
          {item.type === 'folder' && item.children && <FileTree items={item.children} depth={depth + 1} />}
        </div>
      ))}
    </div>
  )
}

const WARNINGS = [
  { type: 'warning', msg: 'Unused variable: result', line: 23 },
  { type: 'error', msg: 'Type mismatch in fetchData()', line: 45 },
  { type: 'info', msg: 'Consider using const here', line: 12 },
]

const SUGGESTIONS = [
  'Add error boundary to App component',
  'Extract API calls into custom hook',
  'Add unit tests for utils module',
]

export default function CodingWorkspace() {
  const [showTerminal, setShowTerminal] = useState(false)

  return (
    <div style={{
      height: '100%',
      display: 'grid',
      gridTemplateColumns: '180px 1fr 260px',
      gap: 16,
      padding: 16,
    }}>
      <div>
        <h2 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8, padding: '0 8px' }}>
          Explorer
        </h2>
        <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 12, padding: 8 }}>
          <FileTree items={FILES} />
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{
          flex: 1,
          background: 'rgba(255,255,255,0.05)',
          borderRadius: 12,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '6px 12px',
            borderBottom: '1px solid rgba(255,255,255,0.05)',
          }}>
            <div style={{ display: 'flex', gap: 4 }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ff5f56' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ffbd2e' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#27c93f' }} />
            </div>
            <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', marginLeft: 8 }}>main.ts</span>
            <div style={{ flex: 1 }} />
            <button
              onClick={() => setShowTerminal(!showTerminal)}
              style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.3)', cursor: 'pointer', fontSize: 12 }}
            >
              $_ {showTerminal ? '▼' : '▲'}
            </button>
          </div>
          <div style={{
            flex: 1,
            padding: 16,
            fontFamily: 'monospace',
            fontSize: 13,
            color: 'rgba(255,255,255,0.6)',
            overflow: 'auto',
          }}>
            <span style={{ color: 'rgba(0,230,118,0.6)' }}>import </span>
            <span style={{ color: 'rgba(255,255,255,0.8)' }}>React</span>
            <span style={{ color: 'rgba(0,230,118,0.6)' }}> from </span>
            <span style={{ color: 'rgba(255,255,255,0.4)' }}>'react'</span><br />
            <span style={{ color: 'rgba(0,230,118,0.6)' }}>import </span>
            <span style={{ color: 'rgba(255,255,255,0.8)' }}>{'{ useState }'}</span>
            <span style={{ color: 'rgba(0,230,118,0.6)' }}> from </span>
            <span style={{ color: 'rgba(255,255,255,0.4)' }}>'react'</span><br /><br />
            <span style={{ color: 'rgba(0,230,118,0.6)' }}>function</span>
            {' '}<span style={{ color: 'rgba(255,255,255,0.8)' }}>App</span>() {'{'}<br />
            {'  '}<span style={{ color: 'rgba(0,230,118,0.6)' }}>const</span> [count, setCount] = useState(0)<br />
            {'  '}<span style={{ color: 'rgba(255,255,255,0.4)' }}>// TODO: implement</span><br />
            {'}'}
          </div>
        </div>

        {showTerminal && (
          <div style={{
            background: 'rgba(255,255,255,0.05)',
            borderRadius: 12,
            padding: 12,
            fontFamily: 'monospace',
            fontSize: 12,
          }}>
            <div style={{ color: 'rgba(0,230,118,0.6)', marginBottom: 4 }}>$ ~/project $</div>
            <div style={{ color: 'rgba(255,255,255,0.3)' }}>$ npm run dev</div>
            <div style={{ color: 'rgba(255,255,255,0.5)' }}>VITE v6.0.0  ready in 320ms</div>
            <div style={{ color: 'rgba(255,255,255,0.5)' }}>➜  Local:   http://localhost:1420</div>
            <div style={{ color: 'rgba(0,230,118,0.6)' }}>&gt; 3 warnings found</div>
          </div>
        )}
      </div>

      <div>
        <h2 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8, padding: '0 8px' }}>
          AI Coding Agent
        </h2>
        <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 12, padding: 12, marginBottom: 8 }}>
          <h3 style={{ fontSize: 9, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>Warnings</h3>
          {WARNINGS.map((w, i) => (
            <div key={i} style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 6,
              padding: '6px 8px',
              borderRadius: 8,
              background: 'rgba(255,255,255,0.03)',
              marginBottom: 4,
              fontSize: 11,
            }}>
              <span style={{
                color: w.type === 'error' ? '#FF5252' : w.type === 'warning' ? '#FFB300' : 'rgba(0,230,118,0.8)',
                fontWeight: 'bold',
              }}>!</span>
              <span style={{ color: 'rgba(255,255,255,0.5)' }}>{w.msg} <span style={{ color: 'rgba(255,255,255,0.2)' }}>L{w.line}</span></span>
            </div>
          ))}
        </div>
        <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 12, padding: 12 }}>
          <h3 style={{ fontSize: 9, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>Suggestions</h3>
          {SUGGESTIONS.map((s, i) => (
            <div key={i} style={{
              padding: '6px 8px',
              borderRadius: 6,
              cursor: 'pointer',
              fontSize: 11,
              color: 'rgba(255,255,255,0.5)',
            }}>
              → {s}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
