function CalendarHeader({ currentDate, view, onViewChange, onNavigate, onToday }) {
    try {
        const views = ['month', 'week', 'day'];
        const title = view === 'day' 
            ? currentDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
            : `${DateUtils.monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
        return (
            <header className="flex items-center justify-between py-4 px-6" data-name="calendar-header" data-file="components/CalendarHeader.js">
                <div className="flex items-center gap-4">
                    <h1 className="text-xl font-semibold dark:text-white">{title}</h1>
                    <div className="flex items-center gap-1">
                        <button onClick={() => onNavigate(-1)} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-smooth">
                            <div className="icon-chevron-left text-gray-600 dark:text-gray-400"></div>
                        </button>
                        <button onClick={onToday} className="px-3 py-1.5 text-sm font-medium rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 dark:text-gray-300 transition-smooth">Today</button>
                        <button onClick={() => onNavigate(1)} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-smooth">
                            <div className="icon-chevron-right text-gray-600 dark:text-gray-400"></div>
                        </button>
                    </div>
                </div>
                <div className="flex items-center gap-1 p-1 rounded-xl bg-gray-100 dark:bg-gray-800">
                    {views.map(v => (
                        <button key={v} onClick={() => onViewChange(v)}
                            className={`px-4 py-1.5 text-sm font-medium rounded-lg capitalize transition-smooth ${view === v ? 'bg-white dark:bg-gray-700 shadow-sm dark:text-white' : 'text-gray-600 dark:text-gray-400'}`}>
                            {v}
                        </button>
                    ))}
                </div>
            </header>
        );
    } catch (error) { console.error('CalendarHeader error:', error); return null; }
}