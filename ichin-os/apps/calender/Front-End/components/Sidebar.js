function Sidebar({ activeView, onViewChange, onNewTask, theme, onThemeToggle, connected }) {
    try {
        const navItems = [
            { id: 'today', icon: 'icon-sun', label: 'Today' },
            { id: 'upcoming', icon: 'icon-calendar-days', label: 'Upcoming' },
            { id: 'completed', icon: 'icon-circle-check', label: 'Completed' },
            { id: 'all', icon: 'icon-list', label: 'All Tasks' }
        ];
        return (
            <aside className="w-60 h-screen glass-panel flex flex-col p-4" data-name="sidebar" data-file="components/Sidebar.js">
                <div className="flex items-center gap-2 mb-8 px-2">
                    <div className="w-8 h-8 rounded-xl bg-[var(--accent)] flex items-center justify-center">
                        <div className="icon-calendar text-white text-sm"></div>
                    </div>
                    <span className="font-semibold text-lg dark:text-white">CalenTask</span>
                </div>
                <button onClick={onNewTask} className="w-full py-2.5 px-4 rounded-xl bg-[var(--accent)] text-white font-medium mb-6 transition-smooth hover:opacity-90 flex items-center justify-center gap-2">
                    <div className="icon-plus text-sm"></div>
                    New Task
                </button>
                <nav className="flex-1 space-y-1">
                    {navItems.map(item => (
                        <button key={item.id} onClick={() => onViewChange(item.id)}
                            className={`w-full px-3 py-2 rounded-xl flex items-center gap-3 transition-smooth ${activeView === item.id ? 'bg-[var(--accent-light)] text-[var(--accent)]' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}`}>
                            <div className={`${item.icon} text-base`}></div>
                            <span className="text-sm font-medium">{item.label}</span>
                        </button>
                    ))}
                </nav>
                <button onClick={onThemeToggle} className="px-3 py-2 rounded-xl flex items-center gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-smooth">
                    <div className={`${theme === 'dark' ? 'icon-sun' : 'icon-moon'} text-base`}></div>
                    <span className="text-sm font-medium">{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
                </button>
                <div className={`flex items-center gap-1.5 px-3 py-1.5 mt-1 text-xs font-medium rounded-lg ${connected ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
                    {connected ? 'Connected' : 'Offline'}
                </div>
            </aside>
        );
    } catch (error) { console.error('Sidebar error:', error); return null; }
}