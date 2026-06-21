function WeekView({ currentDate, tasks, onDateClick, onTaskClick }) {
    try {
        const weekDays = DateUtils.getWeekDays(currentDate);
        const hours = Array.from({ length: 24 }, (_, i) => i);
        const getTasksForDate = (date) => tasks.filter(t => DateUtils.isSameDay(new Date(t.dueDate), date));
        return (
            <div className="flex-1 overflow-auto" data-name="week-view" data-file="components/WeekView.js">
                <div className="sticky top-0 z-10 glass-panel border-b border-gray-200 dark:border-gray-700">
                    <div className="grid grid-cols-8">
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
                    <div className="grid grid-cols-8 border-t border-gray-200 dark:border-gray-700">
                        <div className="p-1"></div>
                        {weekDays.map((day, i) => {
                            const dayTasks = getTasksForDate(day);
                            return (
                                <div key={i} className="px-1 py-0.5 space-y-0.5 min-h-[32px]">
                                    {dayTasks.slice(0, 2).map(task => (
                                        <div key={task.id} onClick={(e) => { e.stopPropagation(); onTaskClick(task); }}
                                            className={`text-[10px] px-1.5 py-0.5 rounded truncate cursor-pointer transition-smooth hover:opacity-80 ${task.status === 'done' ? 'line-through opacity-50' : ''} ${task.priority === 'high' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' : task.priority === 'medium' ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400' : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'}`}>
                                            {task.title}
                                        </div>
                                    ))}
                                    {dayTasks.length > 2 && <div className="text-[10px] text-gray-500 px-1">+{dayTasks.length - 2}</div>}
                                </div>
                            );
                        })}
                    </div>
                </div>
                <div className="relative">
                    {hours.map(hour => (
                        <div key={hour} className="grid grid-cols-8 border-b border-gray-100 dark:border-gray-800">
                            <div className="p-2 text-xs text-gray-400 text-right pr-4">{hour === 0 ? '12 AM' : hour < 12 ? `${hour} AM` : hour === 12 ? '12 PM' : `${hour - 12} PM`}</div>
                            {weekDays.map((day, i) => {
                                const cellTasks = getTasksForDate(day).filter(t => {
                                    const createdHour = t.createdAt ? new Date(t.createdAt).getHours() : -1;
                                    return createdHour === hour;
                                });
                                return (
                                    <div key={i} onClick={() => onDateClick(day)} className="h-12 border-l border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/30 cursor-pointer transition-smooth relative p-0.5">
                                        {cellTasks.slice(0, 1).map(task => (
                                            <div key={task.id} onClick={(e) => { e.stopPropagation(); onTaskClick(task); }}
                                                className={`text-[9px] px-1 py-0.5 rounded truncate ${task.priority === 'high' ? 'bg-red-100 dark:bg-red-900/30' : task.priority === 'medium' ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-blue-100 dark:bg-blue-900/30'}`}>
                                                {task.title}
                                            </div>
                                        ))}
                                    </div>
                                );
                            })}
                        </div>
                    ))}
                </div>
            </div>
        );
    } catch (error) { console.error('WeekView error:', error); return null; }
}