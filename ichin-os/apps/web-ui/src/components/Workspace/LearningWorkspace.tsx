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
    <div style={{
      height: '100%',
      display: 'grid',
      gridTemplateColumns: '1fr 260px',
      gap: 16,
      padding: 16,
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{
          flex: 1,
          background: 'rgba(255,255,255,0.05)',
          borderRadius: 16,
          padding: 32,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 16,
        }}>
          <svg viewBox="0 0 100 100" width="160" height="160">
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
          <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)', textAlign: 'center', maxWidth: 280 }}>
            Knowledge graph visualization — showing connections between concepts in your learning path.
          </p>
        </div>

        <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 16 }}>
          <h3 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>
            Course Progression
          </h3>
          <div style={{ display: 'flex', gap: 8 }}>
            {COURSES.map((c, i) => (
              <div key={c.name} style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, flex: 1 }}>
                  <div style={{
                    width: 36,
                    height: 36,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 12,
                    background: c.status === 'complete' ? 'rgba(179,136,255,0.3)' :
                               c.status === 'in-progress' ? 'rgba(179,136,255,0.15)' :
                               'rgba(255,255,255,0.05)',
                    color: c.status === 'locked' ? 'rgba(255,255,255,0.2)' : '#B388FF',
                  }}>
                    {c.status === 'complete' ? '✓' : c.status === 'in-progress' ? Math.floor(c.progress / 10) : '?'}
                  </div>
                  <span style={{ fontSize: 9, color: 'rgba(255,255,255,0.3)', textAlign: 'center' }}>{c.name}</span>
                </div>
                {i < COURSES.length - 1 && <span style={{ color: 'rgba(255,255,255,0.1)', fontSize: 12 }}>→</span>}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div>
        <h2 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8, padding: '0 8px' }}>
          Resources
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {RESOURCES.map((r, i) => (
            <div key={i} style={{
              background: 'rgba(255,255,255,0.05)',
              borderRadius: 12,
              padding: 12,
              cursor: 'pointer',
              transition: 'background 0.15s ease',
            }}>
              <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.7)', marginBottom: 4 }}>{r.title}</div>
              <div style={{ display: 'flex', gap: 6 }}>
                <span style={{ fontSize: 9, color: '#B388FF', background: 'rgba(179,136,255,0.1)', padding: '2px 6px', borderRadius: 4 }}>
                  {r.type}
                </span>
                <span style={{ fontSize: 9, color: 'rgba(255,255,255,0.2)' }}>{r.source}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
