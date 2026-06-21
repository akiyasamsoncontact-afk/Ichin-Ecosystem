function MonthView({ currentDate, tasks, onDateClick, onTaskClick }) {
    try {
        const days = DateUtils.getMonthDays(currentDate.getFullYear(), currentDate.getMonth());
        const getTasksForDate = (date) => tasks.filter(t => DateUtils.isSameDay(new Date(t.dueDate), date));
        return (
            <div className="flex-1 p-4" data-name="month-view" data-file="components/MonthView.js">
                <div className="grid grid-cols-7 mb-2">
                    {DateUtils.dayNames.map(day => (
                        <div key={day} className="text-center text-xs font-medium text-gray-500 dark:text-gray-500 py-2">{day}</div>
                    ))}
                </div>
                <div className="grid grid-cols-7 gap-1">
                    {days.map((day, i) => {
                        const dayTasks = getTasksForDate(day.date);
                        const isToday = DateUtils.isToday(day.date);
                        return (
                            <div key={i} onClick={() => onDateClick(day.date)}
                                className={`min-h-24 p-2 rounded-xl cursor-pointer transition-smooth hover:bg-gray-50 dark:hover:bg-gray-800/50 ${!day.isCurrentMonth ? 'opacity-40' : ''}`}>
                                <span className={`inline-flex items-center justify-center w-7 h-7 text-sm font-medium rounded-lg ${isToday ? 'bg-[var(--accent)] text-white' : 'dark:text-gray-300'}`}>
                                    {day.date.getDate()}
                                </span>
                                <div className="mt-1 space-y-1">
                                    {dayTasks.slice(0, 2).map(task => (
                                        <div key={task.id} onClick={(e) => { e.stopPropagation(); onTaskClick(task); }}
                                            className={`text-xs px-2 py-1 rounded-md truncate cursor-pointer transition-smooth hover:opacity-80 ${task.status === 'done' ? 'line-through opacity-50' : ''} ${task.priority === 'high' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' : task.priority === 'medium' ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400' : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'}`}>
                                            {task.title}
                                        </div>
                                    ))}
                                    {dayTasks.length > 2 && <div className="text-xs text-gray-500 px-2">+{dayTasks.length - 2} more</div>}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    } catch (error) { console.error('MonthView error:', error); return null; }
}