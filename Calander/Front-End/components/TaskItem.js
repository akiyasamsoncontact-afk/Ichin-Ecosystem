function TaskItem({ task, onToggle, onClick }) {
    try {
        const priorityColors = {
            high: 'border-red-400',
            medium: 'border-amber-400',
            low: 'border-blue-400'
        };
        return (
            <div onClick={onClick} className="group flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer transition-smooth" data-name="task-item" data-file="components/TaskItem.js">
                <button onClick={(e) => { e.stopPropagation(); onToggle(task.id); }}
                    className={`w-5 h-5 rounded-md border-2 flex items-center justify-center transition-smooth ${priorityColors[task.priority]} ${task.status === 'done' ? 'bg-[var(--success)] border-[var(--success)]' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}>
                    {task.status === 'done' && <div className="icon-check text-white text-xs"></div>}
                </button>
                <div className="flex-1 min-w-0">
                    <div className={`font-medium text-sm truncate ${task.status === 'done' ? 'line-through text-gray-400' : 'dark:text-white'}`}>{task.title}</div>
                    {task.dueDate && (
                        <div className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
                            <div className="icon-calendar text-xs"></div>
                            {new Date(task.dueDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </div>
                    )}
                </div>
                {task.tags && task.tags.length > 0 && (
                    <div className="flex gap-1">
                        {task.tags.slice(0, 2).map((tag, i) => (
                            <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">{tag}</span>
                        ))}
                    </div>
                )}
            </div>
        );
    } catch (error) { console.error('TaskItem error:', error); return null; }
}