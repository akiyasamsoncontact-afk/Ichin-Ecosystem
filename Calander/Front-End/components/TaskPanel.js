function TaskPanel({ task, onClose, onUpdate, onDelete }) {
    try {
        const [editedTask, setEditedTask] = React.useState(task);
        React.useEffect(() => setEditedTask(task), [task]);
        if (!task) return null;
        const handleSave = () => { onUpdate(editedTask); };
        const priorities = ['low', 'medium', 'high'];
        const statuses = ['todo', 'in-progress', 'done'];
        return (
            <aside className="w-80 h-screen glass-panel border-l border-gray-200 dark:border-gray-700 flex flex-col" data-name="task-panel" data-file="components/TaskPanel.js">
                <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                    <h2 className="font-semibold dark:text-white">Task Details</h2>
                    <button onClick={onClose} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-smooth">
                        <div className="icon-x text-gray-500"></div>
                    </button>
                </div>
                <div className="flex-1 overflow-auto p-4 space-y-4">
                    <input type="text" value={editedTask.title} onChange={(e) => setEditedTask({ ...editedTask, title: e.target.value })} onBlur={handleSave}
                        className="w-full text-lg font-semibold bg-transparent border-none outline-none dark:text-white" placeholder="Task title" />
                    <textarea value={editedTask.description || ''} onChange={(e) => setEditedTask({ ...editedTask, description: e.target.value })} onBlur={handleSave}
                        className="w-full h-24 p-3 text-sm bg-gray-50 dark:bg-gray-800 rounded-xl border-none outline-none resize-none dark:text-gray-300" placeholder="Add description..." />
                    <div className="space-y-3">
                        <label className="block text-sm text-gray-500">Due Date</label>
                        <input type="date" value={editedTask.dueDate || ''} onChange={(e) => { setEditedTask({ ...editedTask, dueDate: e.target.value }); }}
                            className="w-full p-2 text-sm bg-gray-50 dark:bg-gray-800 rounded-xl dark:text-gray-300" />
                    </div>
                    <div className="space-y-3">
                        <label className="block text-sm text-gray-500">Priority</label>
                        <div className="flex gap-2">
                            {priorities.map(p => (
                                <button key={p} onClick={() => { setEditedTask({ ...editedTask, priority: p }); onUpdate({ ...editedTask, priority: p }); }}
                                    className={`flex-1 py-2 text-sm font-medium rounded-xl capitalize transition-smooth ${editedTask.priority === p ? p === 'high' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : p === 'medium' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}>
                                    {p}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div className="space-y-3">
                        <label className="block text-sm text-gray-500">Status</label>
                        <select value={editedTask.status} onChange={(e) => { setEditedTask({ ...editedTask, status: e.target.value }); onUpdate({ ...editedTask, status: e.target.value }); }}
                            className="w-full p-2 text-sm bg-gray-50 dark:bg-gray-800 rounded-xl dark:text-gray-300">
                            {statuses.map(s => <option key={s} value={s}>{s.replace('-', ' ')}</option>)}
                        </select>
                    </div>
                </div>
                <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                    <button onClick={() => onDelete(task.id)} className="w-full py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-smooth">Delete Task</button>
                </div>
            </aside>
        );
    } catch (error) { console.error('TaskPanel error:', error); return null; }
}