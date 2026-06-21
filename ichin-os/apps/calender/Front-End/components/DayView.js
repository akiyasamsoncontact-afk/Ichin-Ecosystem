function DayView({ currentDate, tasks, onTaskClick }) {
    try {
        const hours = Array.from({ length: 24 }, (_, i) => i);
        const dayTasks = tasks.filter(t => DateUtils.isSameDay(new Date(t.dueDate), currentDate));
        return (
            <div className="flex-1 overflow-auto" data-name="day-view" data-file="components/DayView.js">
                <div className="flex">
                    <div className="w-20 flex-shrink-0">
                        {hours.map(hour => (
                            <div key={hour} className="h-16 text-xs text-gray-400 text-right pr-4 pt-1">
                                {hour === 0 ? '12 AM' : hour < 12 ? `${hour} AM` : hour === 12 ? '12 PM' : `${hour - 12} PM`}
                            </div>
                        ))}
                    </div>
                    <div className="flex-1 relative border-l border-gray-200 dark:border-gray-700">
                        {hours.map(hour => (
                            <div key={hour} className="h-16 border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/30 cursor-pointer transition-smooth"></div>
                        ))}
                        <div className="absolute top-0 left-0 right-0 p-2">
                            {dayTasks.map(task => (
                                <div key={task.id} onClick={() => onTaskClick(task)}
                                    className={`mb-2 p-3 rounded-xl cursor-pointer transition-smooth ${task.priority === 'high' ? 'bg-red-100 dark:bg-red-900/30' : task.priority === 'medium' ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-blue-100 dark:bg-blue-900/30'}`}>
                                    <div className={`font-medium text-sm ${task.status === 'done' ? 'line-through opacity-50' : ''} dark:text-white`}>{task.title}</div>
                                    {task.description && <div className="text-xs text-gray-500 mt-1 truncate">{task.description}</div>}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    } catch (error) { console.error('DayView error:', error); return null; }
}