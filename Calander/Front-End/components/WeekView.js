function WeekView({ currentDate, tasks, onDateClick, onTaskClick }) {
    try {
        const weekDays = DateUtils.getWeekDays(currentDate);
        const hours = Array.from({ length: 24 }, (_, i) => i);
        const getTasksForDate = (date) => tasks.filter(t => DateUtils.isSameDay(new Date(t.dueDate), date));
        return (
            <div className="flex-1 overflow-auto" data-name="week-view" data-file="components/WeekView.js">
                <div className="sticky top-0 z-10 glass-panel grid grid-cols-8 border-b border-gray-200 dark:border-gray-700">
                    <div className="p-3"></div>
                    {weekDays.map((day, i) => (
                        <div key={i} onClick={() => onDateClick(day)} className="p-3 text-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-smooth">
                            <div className="text-xs text-gray-500 dark:text-gray-500">{DateUtils.dayNames[day.getDay()]}</div>
                            <div className={`text-lg font-semibold mt-1 ${DateUtils.isToday(day) ? 'w-8 h-8 mx-auto rounded-full bg-[var(--accent)] text-white flex items-center justify-center' : 'dark:text-white'}`}>
                                {day.getDate()}
                            </div>
                        </div>
                    ))}
                </div>
                <div className="relative">
                    {hours.map(hour => (
                        <div key={hour} className="grid grid-cols-8 border-b border-gray-100 dark:border-gray-800">
                            <div className="p-2 text-xs text-gray-400 text-right pr-4">{hour === 0 ? '12 AM' : hour < 12 ? `${hour} AM` : hour === 12 ? '12 PM' : `${hour - 12} PM`}</div>
                            {weekDays.map((day, i) => (
                                <div key={i} onClick={() => onDateClick(day)} className="h-12 border-l border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/30 cursor-pointer transition-smooth"></div>
                            ))}
                        </div>
                    ))}
                </div>
            </div>
        );
    } catch (error) { console.error('WeekView error:', error); return null; }
}