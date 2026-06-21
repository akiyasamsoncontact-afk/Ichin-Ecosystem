function TaskModal({ isOpen, onClose, onSave, initialDate }) {
    try {
        const [task, setTask] = React.useState({ title: '', description: '', dueDate: initialDate || '', priority: 'medium', status: 'todo', tags: [] });
        React.useEffect(() => { setTask(t => ({ ...t, dueDate: initialDate || '' })); }, [initialDate]);
        if (!isOpen) return null;
        const handleSubmit = (e) => {
            e.preventDefault();
            if (!task.title.trim()) return;
            onSave({ ...task, id: Date.now().toString(), createdAt: new Date().toISOString() });
            setTask({ title: '', description: '', dueDate: '', priority: 'medium', status: 'todo', tags: [] });
            onClose();
        };
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" data-name="task-modal" data-file="components/TaskModal.js">
                <div className="glass-panel w-full max-w-md rounded-2xl p-6 m-4">
                    <h2 className="text-lg font-semibold mb-4 dark:text-white">New Task</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <input type="text" value={task.title} onChange={(e) => setTask({ ...task, title: e.target.value })} placeholder="Task title" autoFocus
                            className="w-full p-3 text-sm bg-gray-50 dark:bg-gray-800 rounded-xl border-none outline-none dark:text-white" />
                        <textarea value={task.description} onChange={(e) => setTask({ ...task, description: e.target.value })} placeholder="Description (optional)"
                            className="w-full h-20 p-3 text-sm bg-gray-50 dark:bg-gray-800 rounded-xl border-none outline-none resize-none dark:text-gray-300" />
                        <input type="date" value={task.dueDate} onChange={(e) => setTask({ ...task, dueDate: e.target.value })}
                            className="w-full p-3 text-sm bg-gray-50 dark:bg-gray-800 rounded-xl dark:text-gray-300" />
                        <div className="flex gap-2">
                            {['low', 'medium', 'high'].map(p => (
                                <button key={p} type="button" onClick={() => setTask({ ...task, priority: p })}
                                    className={`flex-1 py-2 text-sm rounded-xl capitalize ${task.priority === p ? p === 'high' ? 'bg-red-100 text-red-700' : p === 'medium' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}>{p}</button>
                            ))}
                        </div>
                        <div className="flex gap-3 pt-2">
                            <button type="button" onClick={onClose} className="flex-1 py-2.5 text-sm rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">Cancel</button>
                            <button type="submit" className="flex-1 py-2.5 text-sm rounded-xl bg-[var(--accent)] text-white font-medium">Create Task</button>
                        </div>
                    </form>
                </div>
            </div>
        );
    } catch (error) { console.error('TaskModal error:', error); return null; }
}
