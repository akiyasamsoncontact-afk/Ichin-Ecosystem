import { BookOpen, Sparkles, Layers, ArrowRight, Circle } from 'lucide-react'

const COURSES = [
  { name: 'Mathematics', progress: 100, status: 'complete' },
  { name: 'Machine Learning', progress: 65, status: 'in-progress' },
  { name: 'Deep Learning', progress: 30, status: 'in-progress' },
  { name: 'NLP', progress: 0, status: 'locked' },
]

const RESOURCES = [
  { title: 'Attention Is All You Need', type: 'Paper', source: 'arXiv' },
  { title: 'Deep Learning Book', type: 'Book', source: 'MIT Press' },
  { title: 'Transformers Course', type: 'Course', source: 'Hugging Face' },
]

export default function LearningWorkspace() {
  return (
    <div className="h-full grid grid-cols-[1fr_280px] gap-4 p-4" style={{ backgroundColor: 'rgba(179, 136, 255, 0.02)' }}>
      <div className="flex flex-col gap-4">
        <div className="glass rounded-2xl p-6 flex-1 flex flex-col items-center justify-center gap-4">
          <div className="relative w-48 h-48">
            <svg viewBox="0 0 100 100" className="w-full h-full">
              <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(179,136,255,0.1)" strokeWidth="1" />
              <circle cx="50" cy="50" r="25" fill="none" stroke="rgba(179,136,255,0.15)" strokeWidth="1" />
              <circle cx="50" cy="50" r="10" fill="rgba(179,136,255,0.2)" />
              <line x1="50" y1="10" x2="50" y2="90" stroke="rgba(179,136,255,0.08)" strokeWidth="0.5" />
              <line x1="10" y1="50" x2="90" y2="50" stroke="rgba(179,136,255,0.08)" strokeWidth="0.5" />
              <circle cx="65" cy="35" r="4" fill="#B388FF" opacity="0.6" />
              <circle cx="30" cy="40" r="3" fill="#B388FF" opacity="0.4" />
              <circle cx="70" cy="60" r="3.5" fill="#B388FF" opacity="0.5" />
              <circle cx="35" cy="65" r="2.5" fill="#B388FF" opacity="0.3" />
              <line x1="50" y1="50" x2="65" y2="35" stroke="rgba(179,136,255,0.2)" strokeWidth="0.5" />
              <line x1="50" y1="50" x2="30" y2="40" stroke="rgba(179,136,255,0.2)" strokeWidth="0.5" />
              <line x1="50" y1="50" x2="70" y2="60" stroke="rgba(179,136,255,0.2)" strokeWidth="0.5" />
              <line x1="50" y1="50" x2="35" y2="65" stroke="rgba(179,136,255,0.2)" strokeWidth="0.5" />
            </svg>
          </div>
          <p className="text-sm text-white/40 text-center max-w-xs">
            Knowledge graph visualization — showing connections between concepts in your learning path.
          </p>
        </div>

        <div className="glass rounded-2xl p-4">
          <h3 className="text-xs uppercase tracking-wider text-white/30 mb-3">Course Progression</h3>
          <div className="flex items-center gap-2">
            {COURSES.map((c, i) => (
              <div key={c.name} className="flex items-center gap-2 flex-1">
                <div className="flex flex-col items-center gap-1 flex-1">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs ${
                      c.status === 'complete' ? 'bg-accent-learning/30 text-accent-learning' :
                      c.status === 'in-progress' ? 'bg-accent-learning/15 text-accent-learning' :
                      'bg-white/5 text-white/20'
                    }`}
                  >
                    {c.status === 'complete' ? '✓' : c.status === 'in-progress' ? Math.floor(c.progress / 10) : '?'}
                  </div>
                  <span className="text-[10px] text-white/30 truncate max-w-16 text-center">{c.name}</span>
                </div>
                {i < COURSES.length - 1 && <ArrowRight size={12} className="text-white/10 shrink-0" />}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <h2 className="text-xs uppercase tracking-wider text-white/30 px-2 mb-1">Resources</h2>
        <div className="flex-1 glass rounded-2xl p-3 space-y-2 overflow-auto">
          {RESOURCES.map((r, i) => (
            <div key={i} className="p-3 rounded-xl bg-white/5 hover:bg-white/10 cursor-pointer transition-all">
              <div className="text-sm text-white/70">{r.title}</div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-accent-learning/10 text-accent-learning">
                  {r.type}
                </span>
                <span className="text-[10px] text-white/20">{r.source}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
