import { useState } from 'react'
import { motion } from 'framer-motion'
import { File, Folder, Code as CodeIcon, Bug, Terminal, Lightbulb, AlertTriangle } from 'lucide-react'

const FILES = [
  { name: 'src', type: 'folder', children: [
    { name: 'main.ts', type: 'file' },
    { name: 'utils.ts', type: 'file' },
    { name: 'components', type: 'folder', children: [
      { name: 'App.tsx', type: 'file' },
      { name: 'Header.tsx', type: 'file' },
    ]},
  ]},
  { name: 'package.json', type: 'file' },
  { name: 'tsconfig.json', type: 'file' },
]

function FileTree({ items, depth = 0 }: { items: typeof FILES; depth?: number }) {
  return (
    <div>
      {items.map((item) => (
        <div key={item.name}>
          <div
            className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/5 text-xs cursor-pointer"
            style={{ paddingLeft: `${12 + depth * 16}px` }}
          >
            {item.type === 'folder' ? <Folder size={14} className="text-accent-coding/60" /> : <File size={14} className="text-white/40" />}
            <span className="text-white/70">{item.name}</span>
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
    <div className="h-full grid grid-cols-[200px_1fr_280px] gap-4 p-4" style={{ backgroundColor: 'rgba(0, 230, 118, 0.02)' }}>
      <div className="flex flex-col gap-2">
        <h2 className="text-xs uppercase tracking-wider text-white/30 px-2 mb-1">Explorer</h2>
        <div className="flex-1 glass rounded-2xl p-2 overflow-auto">
          <FileTree items={FILES} />
        </div>
      </div>

      <div className="flex flex-col gap-2 relative">
        <div className="flex-1 glass rounded-2xl overflow-hidden flex flex-col">
          <div className="flex items-center gap-2 px-4 py-2 border-b border-white/5">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/30" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/30" />
              <div className="w-3 h-3 rounded-full bg-green-500/30" />
            </div>
            <span className="text-xs text-white/30 ml-2">main.ts</span>
            <div className="flex-1" />
            <button
              onClick={() => setShowTerminal(!showTerminal)}
              className="p-1 rounded text-white/30 hover:text-white/60"
            >
              <Terminal size={14} />
            </button>
          </div>
          <div className="flex-1 p-4 font-mono text-sm text-white/60 overflow-auto">
            <span className="text-accent-coding/60">import</span>{' '}<span className="text-white/80">React</span>{' '}<span className="text-accent-coding/60">from</span>{' '}<span className="text-white/40">'react'</span>{'\n'}
            <span className="text-accent-coding/60">import</span>{' '}<span className="text-white/80">{'{ useState }'}</span>{' '}<span className="text-accent-coding/60">from</span>{' '}<span className="text-white/40">'react'</span>{'\n\n'}
            <span className="text-accent-coding/60">function</span>{' '}<span className="text-white/80">App</span>() {'{'}{'\n'}
            {'  '}<span className="text-accent-coding/60">const</span> [count, setCount] = useState(0){'\n'}
            {'  '}<span className="text-white/40">// TODO: implement</span>{'\n'}
            {'}'}
          </div>
        </div>

        <motion.div
          className="glass rounded-2xl overflow-hidden"
          animate={{ height: showTerminal ? 160 : 0 }}
          transition={{ duration: 0.3 }}
        >
          {showTerminal && (
            <div className="p-3 font-mono text-xs text-white/50">
              <div className="flex items-center gap-2 text-accent-coding/60 mb-2">
                <Terminal size={12} /> ~/project $
              </div>
              <div className="space-y-1">
                <div className="text-white/30">$ npm run dev</div>
                <div className="text-white/50">VITE v6.0.0  ready in 320ms</div>
                <div className="text-white/50">➜  Local:   http://localhost:1420</div>
                <div className="text-accent-coding/60">&gt; 3 warnings found</div>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      <div className="flex flex-col gap-3">
        <h2 className="text-xs uppercase tracking-wider text-white/30 px-2 mb-1">AI Coding Agent</h2>
        <div className="glass rounded-2xl p-3 space-y-2">
          <h3 className="text-[10px] uppercase text-white/30 tracking-wider">Warnings</h3>
          {WARNINGS.map((w, i) => (
            <div key={i} className="flex items-start gap-2 text-xs p-2 rounded-lg bg-white/5">
              {w.type === 'error' ? <AlertTriangle size={12} className="text-red-400 mt-0.5" /> :
               w.type === 'warning' ? <AlertTriangle size={12} className="text-yellow-400 mt-0.5" /> :
               <Lightbulb size={12} className="text-accent-coding mt-0.5" />}
              <div>
                <span className="text-white/70">{w.msg}</span>
                <span className="text-white/20 ml-1">L{w.line}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="glass rounded-2xl p-3 space-y-2">
          <h3 className="text-[10px] uppercase text-white/30 tracking-wider">Suggestions</h3>
          {SUGGESTIONS.map((s, i) => (
            <div key={i} className="flex items-center gap-2 text-xs text-white/50 p-2 rounded-lg hover:bg-white/5 cursor-pointer">
              <CodeIcon size={12} className="text-accent-coding" />
              {s}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
