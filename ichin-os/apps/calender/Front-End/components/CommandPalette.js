function CommandPalette({ isOpen, onClose, tasks, onTaskSelect, onNewTask }) {
    try {
        const [query, setQuery] = React.useState('');
        const inputRef = React.useRef(null);
        React.useEffect(() => { if (isOpen && inputRef.current) inputRef.current.focus(); }, [isOpen]);
        React.useEffect(() => { setQuery(''); }, [isOpen]);
        if (!isOpen) return null;
        const filtered = tasks.filter(t => t.title.toLowerCase().includes(query.toLowerCase())).slice(0, 8);
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') onClose();
        };
        return (
            <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/30 backdrop-blur-sm" onClick={onClose} data-name="command-palette" data-file="components/CommandPalette.js">
                <div className="glass-panel w-full max-w-lg rounded-2xl overflow-hidden m-4" onClick={e => e.stopPropagation()}>
                    <div className="flex items-center gap-3 p-4 border-b border-gray-200 dark:border-gray-700">
                        <div className="icon-search text-gray-400"></div>
                        <input ref={inputRef} type="text" value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={handleKeyDown}
                            placeholder="Search tasks or type a command..." className="flex-1 bg-transparent border-none outline-none text-sm dark:text-white" />
                        <kbd className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 rounded text-gray-500">ESC</kbd>
                    </div>
                    <div className="max-h-80 overflow-auto p-2">
                        <button onClick={() => { onNewTask(); onClose(); }} className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-smooth">
                            <div className="icon-plus text-[var(--accent)]"></div>
                            <span className="text-sm dark:text-white">Create new task</span>
                        </button>
                        {filtered.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-800">
                                <div className="px-3 py-1 text-xs text-gray-400">Tasks</div>
                                {filtered.map(task => (
                                    <button key={task.id} onClick={() => { onTaskSelect(task); onClose(); }} className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-smooth">
                                        <div className={`w-2 h-2 rounded-full ${task.priority === 'high' ? 'bg-red-400' : task.priority === 'medium' ? 'bg-amber-400' : 'bg-blue-400'}`}></div>
                                        <span className={`text-sm truncate ${task.status === 'done' ? 'line-through text-gray-400' : 'dark:text-white'}`}>{task.title}</span>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        );
    } catch (error) { console.error('CommandPalette error:', error); return null; }
}