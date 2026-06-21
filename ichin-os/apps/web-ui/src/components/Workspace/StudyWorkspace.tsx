import { useState } from 'react'

const TOPICS = [
  { id: 't1', name: 'Quantum Mechanics', progress: 65, cards: 42 },
  { id: 't2', name: 'Linear Algebra', progress: 80, cards: 28 },
  { id: 't3', name: 'Data Structures', progress: 45, cards: 56 },
  { id: 't4', name: 'Machine Learning', progress: 30, cards: 71 },
]

export default function StudyWorkspace() {
  const [selectedTopic, setSelectedTopic] = useState(TOPICS[0])

  return (
    <div style={{
      height: '100%',
      display: 'grid',
      gridTemplateColumns: '220px 1fr 260px',
      gap: 16,
      padding: 16,
    }}>
      <div>
        <h2 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8, padding: '0 8px' }}>
          Topics
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {TOPICS.map((t) => {
            const isActive = selectedTopic.id === t.id
            return (
              <button
                key={t.id}
                onClick={() => setSelectedTopic(t)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '10px 12px',
                  borderRadius: 12,
                  textAlign: 'left',
                  background: isActive ? 'rgba(255,255,255,0.05)' : 'transparent',
                  border: isActive ? '1px solid rgba(74, 158, 255, 0.3)' : '1px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <span style={{ color: '#4A9EFF', fontSize: 14 }}>📘</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.8)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {t.name}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
                    <div style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.1)', borderRadius: 2 }}>
                      <div style={{ height: '100%', width: `${t.progress}%`, background: '#4A9EFF', borderRadius: 2 }} />
                    </div>
                    <span style={{ fontSize: 9, color: 'rgba(255,255,255,0.3)' }}>{t.progress}%</span>
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{
          flex: 1,
          background: 'rgba(255,255,255,0.05)',
          borderRadius: 16,
          padding: 24,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 16,
        }}>
          <span style={{ fontSize: 40, color: 'rgba(74,158,255,0.3)' }}>📚</span>
          <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)', textAlign: 'center', maxWidth: 240 }}>
            {selectedTopic.name} — Flashcard generation, quizzes, and notes available.
          </p>
          <button style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '8px 20px',
            borderRadius: 10,
            background: 'rgba(74,158,255,0.15)',
            border: 'none',
            color: '#4A9EFF',
            fontSize: 13,
            cursor: 'pointer',
          }}>
            ✨ Generate Flashcards →
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
          {[
            { label: 'Flashcards', value: selectedTopic.cards, color: '#4A9EFF' },
            { label: 'Quizzes', value: Math.floor(selectedTopic.cards * 0.3), color: '#4A9EFF' },
            { label: 'Progress', value: `${selectedTopic.progress}%`, color: '#4A9EFF' },
          ].map((stat) => (
            <div key={stat.label} style={{
              background: 'rgba(255,255,255,0.05)',
              borderRadius: 12,
              padding: '12px 16px',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: 20, fontWeight: 500, color: stat.color }}>{stat.value}</div>
              <div style={{ fontSize: 9, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1 }}>{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8, padding: '0 8px' }}>
          AI Study Agent
        </h2>
        <div style={{
          flex: 1,
          background: 'rgba(255,255,255,0.05)',
          borderRadius: 16,
          padding: 16,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 12,
          minHeight: 200,
          color: 'rgba(255,255,255,0.2)',
        }}>
          <span style={{ fontSize: 32 }}>🧠</span>
          <p style={{ fontSize: 11, textAlign: 'center', lineHeight: 1.6 }}>
            Study agent is idle.<br />Start studying to get AI insights.
          </p>
        </div>
      </div>
    </div>
  )
}
