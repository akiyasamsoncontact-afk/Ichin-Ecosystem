import { useState } from 'react'
import { Calendar, CheckCircle2, Circle as CircleIcon, Plus, Sparkles, Clock, Mail } from 'lucide-react'
import { useAppStore } from '../../stores/appStore'
import type { Task, WorkspaceType } from '../../types'

const SAMPLE_TASKS: Task[] = [
  { id: '1', title: 'Review quarterly goals', completed: false, workspace: 'personal', priority: 3, createdAt: Date.now(), tags: ['planning'] },
  { id: '2', title: 'Prepare presentation slides', completed: true, workspace: 'personal', priority: 2, createdAt: Date.now(), tags: ['work'] },
  { id: '3', title: 'Read AI paper', completed: false, workspace: 'personal', priority: 1, createdAt: Date.now(), tags: ['learning'] },
  { id: '4', title: 'Update portfolio', completed: false, workspace: 'personal', priority: 2, createdAt: Date.now(), tags: ['career'] },
]

const EVENTS = [
  { time: '09:00', title: 'Team standup' },
  { time: '11:30', title: 'Design review' },
  { time: '14:00', title: 'Deep work block' },
  { time: '16:00', title: 'Project sync' },
]

export default function PersonalWorkspace() {
  const { tasks, addTask, toggleTask, removeTask } = useAppStore()
  const [newTask, setNewTask] = useState('')
  const displayTasks = tasks.length > 0 ? tasks : SAMPLE_TASKS

  const handleAdd = () => {
    if (!newTask.trim()) return
    addTask({
      id: crypto.randomUUID?.() || Date.now().toString(),
      title: newTask,
      completed: false,
      workspace: 'personal' as WorkspaceType,
      priority: 1,
      createdAt: Date.now(),
      tags: [],
    })
    setNewTask('')
  }

  return (
    <div className="h-full grid grid-cols-[1fr_280px] gap-4 p-4" style={{ backgroundColor: 'rgba(158, 158, 158, 0.02)' }}>
      <div className="flex flex-col gap-4">
        <div className="glass rounded-2xl p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs uppercase tracking-wider text-white/30">Today's Timeline</h3>
            <Calendar size={14} className="text-white/20" />
          </div>
          <div className="space-y-3">
            {EVENTS.map((e) => (
              <div key={e.time} className="flex items-center gap-3">
                <div className="text-xs text-white/30 w-12 text-right">{e.time}</div>
                <div className="w-px h-8 bg-white/5" />
                <div className="text-sm text-white/70">{e.title}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 glass rounded-2xl p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs uppercase tracking-wider text-white/30">Tasks</h3>
            <span className="text-xs text-white/20">
              {displayTasks.filter((t) => t.completed).length}/{displayTasks.length}
            </span>
          </div>
          <div className="space-y-1 mb-4">
            {displayTasks.map((task) => (
              <div key={task.id} className="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-white/5 group">
                <button onClick={() => toggleTask(task.id)}>
                  {task.completed
                    ? <CheckCircle2 size={16} className="text-accent-personal" />
                    : <CircleIcon size={16} className="text-white/20 group-hover:text-white/40" />
                  }
                </button>
                <span className={`flex-1 text-sm ${task.completed ? 'text-white/30 line-through' : 'text-white/70'}`}>
                  {task.title}
                </span>
                <button
                  onClick={() => removeTask(task.id)}
                  className="text-white/10 hover:text-white/40 opacity-0 group-hover:opacity-100 text-xs"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <input
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
              placeholder="Add a task..."
              className="flex-1 bg-transparent text-sm text-white/60 placeholder:text-white/20 focus:outline-none"
            />
            <button onClick={handleAdd} className="p-1.5 rounded-lg hover:bg-white/10 text-white/30 hover:text-white/60">
              <Plus size={14} />
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <h2 className="text-xs uppercase tracking-wider text-white/30 px-2 mb-1">AI Productivity</h2>
        <div className="glass rounded-2xl p-4 space-y-3">
          <div className="flex items-center gap-2 text-sm text-white/50">
            <Sparkles size={14} className="text-accent-personal" />
            <span>Suggestions for today:</span>
          </div>
          <div className="text-xs text-white/30 space-y-2">
            <p className="p-2 rounded-lg bg-white/5">• Block 2 hours for deep work on project</p>
            <p className="p-2 rounded-lg bg-white/5">• Review pending emails before noon</p>
            <p className="p-2 rounded-lg bg-white/5">• Take a 15-min break every 90 mins</p>
          </div>
        </div>
        <div className="glass rounded-2xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Mail size={14} className="text-white/20" />
            <span className="text-xs text-white/30">Recent Activity</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-white/30">
            <Clock size={12} />
            <span>Last session: 2h ago</span>
          </div>
        </div>
      </div>
    </div>
  )
}
