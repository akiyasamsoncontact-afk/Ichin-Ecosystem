import { useState } from 'react'

interface Task {
  id: string
  title: string
  completed: boolean
}

const EVENTS = [
  { time: '09:00', title: 'Team standup' },
  { time: '11:30', title: 'Design review' },
  { time: '14:00', title: 'Deep work block' },
  { time: '16:00', title: 'Project sync' },
]

const SAMPLE_TASKS: Task[] = [
  { id: '1', title: 'Review quarterly goals', completed: false },
  { id: '2', title: 'Prepare presentation slides', completed: true },
  { id: '3', title: 'Read AI paper', completed: false },
  { id: '4', title: 'Update portfolio', completed: false },
]

export default function PersonalWorkspace() {
  const [tasks, setTasks] = useState<Task[]>(SAMPLE_TASKS)
  const [newTask, setNewTask] = useState('')

  const toggleTask = (id: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    )
  }

  const addTask = () => {
    if (!newTask.trim()) return
    setTasks([...tasks, { id: Date.now().toString(), title: newTask, completed: false }])
    setNewTask('')
  }

  return (
    <div style={{
      height: '100%',
      display: 'grid',
      gridTemplateColumns: '1fr 260px',
      gap: 16,
      padding: 16,
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1 }}>
              Today's Timeline
            </h3>
            <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.2)' }}>📅</span>
          </div>
          {EVENTS.map((e) => (
            <div key={e.time} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', width: 48, textAlign: 'right' }}>{e.time}</div>
              <div style={{ width: 1, height: 28, background: 'rgba(255,255,255,0.05)' }} />
              <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.7)' }}>{e.title}</div>
            </div>
          ))}
        </div>

        <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1 }}>
              Tasks
            </h3>
            <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.2)' }}>
              {tasks.filter((t) => t.completed).length}/{tasks.length}
            </span>
          </div>
          {tasks.map((task) => (
            <div
              key={task.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '6px 8px',
                borderRadius: 8,
                cursor: 'pointer',
              }}
              onClick={() => toggleTask(task.id)}
            >
              <span style={{
                fontSize: 14,
                color: task.completed ? '#9E9E9E' : 'rgba(255,255,255,0.2)',
              }}>
                {task.completed ? '✓' : '○'}
              </span>
              <span style={{
                flex: 1,
                fontSize: 13,
                color: task.completed ? 'rgba(255,255,255,0.3)' : 'rgba(255,255,255,0.7)',
                textDecoration: task.completed ? 'line-through' : 'none',
              }}>
                {task.title}
              </span>
            </div>
          ))}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            marginTop: 8,
            paddingTop: 8,
            borderTop: '1px solid rgba(255,255,255,0.05)',
          }}>
            <input
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addTask()}
              placeholder="Add a task..."
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                color: 'rgba(255,255,255,0.6)',
                fontSize: 13,
                outline: 'none',
              }}
            />
            <button
              onClick={addTask}
              style={{
                background: 'none',
                border: 'none',
                color: 'rgba(255,255,255,0.3)',
                cursor: 'pointer',
                fontSize: 16,
              }}
            >
              +
            </button>
          </div>
        </div>
      </div>

      <div>
        <h2 style={{ fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8, padding: '0 8px' }}>
          AI Productivity
        </h2>
        <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 16, marginBottom: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
            <span style={{ color: '#9E9E9E', fontSize: 14 }}>✦</span>
            <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>Suggestions for today:</span>
          </div>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ padding: '6px 8px', borderRadius: 6, background: 'rgba(255,255,255,0.03)' }}>• Block 2 hours for deep work on project</div>
            <div style={{ padding: '6px 8px', borderRadius: 6, background: 'rgba(255,255,255,0.03)' }}>• Review pending emails before noon</div>
            <div style={{ padding: '6px 8px', borderRadius: 6, background: 'rgba(255,255,255,0.03)' }}>• Take a 15-min break every 90 mins</div>
          </div>
        </div>
        <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.2)' }}>📧</span>
            <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)' }}>Recent Activity</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'rgba(255,255,255,0.3)' }}>
            <span>🕐</span>
            <span>Last session: 2h ago</span>
          </div>
        </div>
      </div>
    </div>
  )
}
