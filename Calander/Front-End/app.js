class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false }; }
  static getDerivedStateFromError(error) { return { hasError: true }; }
  componentDidCatch(error, info) { console.error('ErrorBoundary:', error, info.componentStack); }
  render() {
    if (this.state.hasError) return <div className="min-h-screen flex items-center justify-center"><p className="text-gray-600">Something went wrong. Please reload.</p></div>;
    return this.props.children;
  }
}

function App() {
  try {
    const [theme, setTheme] = React.useState(Storage.getTheme());
    const [tasks, setTasks] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [currentDate, setCurrentDate] = React.useState(new Date());
    const [calendarView, setCalendarView] = React.useState(Storage.getView());
    const [sidebarView, setSidebarView] = React.useState('all');
    const [selectedTask, setSelectedTask] = React.useState(null);
    const [modalOpen, setModalOpen] = React.useState(false);
    const [modalDate, setModalDate] = React.useState('');
    const [cmdPaletteOpen, setCmdPaletteOpen] = React.useState(false);
    const [connected, setConnected] = React.useState(true);

    React.useEffect(() => {
      startPeriodicSync();
      onStatusChange(setConnected);
      api.getTasks().then(data => {
        setTasks(data);
        setLoading(false);
      }).catch(() => {
        setTasks(Storage.getTasks());
        setLoading(false);
      });
      return () => stopPeriodicSync();
    }, []);

    React.useEffect(() => { document.documentElement.classList.toggle('dark', theme === 'dark'); Storage.saveTheme(theme); }, [theme]);
    React.useEffect(() => { Storage.saveView(calendarView); }, [calendarView]);
    React.useEffect(() => {
      const handleKey = (e) => { if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); setCmdPaletteOpen(true); } };
      window.addEventListener('keydown', handleKey);
      return () => window.removeEventListener('keydown', handleKey);
    }, []);

    const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');
    const addTask = async (task) => {
      const created = await api.createTask(task);
      setTasks(prev => [...prev, created]);
    };
    const updateTask = async (updated) => {
      const saved = await api.updateTask(updated);
      setTasks(prev => prev.map(t => t.id === saved.id ? saved : t));
    };
    const deleteTask = async (id) => {
      await api.deleteTask(id);
      setTasks(prev => prev.filter(t => t.id !== id));
      setSelectedTask(null);
    };
    const toggleTask = async (id) => {
      const task = tasks.find(t => t.id === id);
      if (!task) return;
      const updated = { ...task, status: task.status === 'done' ? 'todo' : 'done' };
      const saved = await api.updateTask(updated);
      setTasks(prev => prev.map(t => t.id === saved.id ? saved : t));
    };
    const navigate = (dir) => {
      const d = new Date(currentDate);
      if (calendarView === 'month') d.setMonth(d.getMonth() + dir);
      else if (calendarView === 'week') d.setDate(d.getDate() + dir * 7);
      else d.setDate(d.getDate() + dir);
      setCurrentDate(d);
    };
    const handleDateClick = (date) => { setModalDate(DateUtils.formatDate(date)); setModalOpen(true); };
    const getFilteredTasks = () => {
      const today = DateUtils.formatDate(new Date());
      if (sidebarView === 'today') return tasks.filter(t => t.dueDate === today);
      if (sidebarView === 'upcoming') return tasks.filter(t => t.dueDate >= today && t.status !== 'done');
      if (sidebarView === 'completed') return tasks.filter(t => t.status === 'done');
      return tasks;
    };

    if (loading) {
      return (
        <div className="flex h-screen bg-[var(--light-bg)] dark:bg-[var(--dark-bg)] items-center justify-center">
          <p className="text-gray-500 dark:text-gray-400">Loading tasks...</p>
        </div>
      );
    }

    return (
      <div className="flex h-screen bg-[var(--light-bg)] dark:bg-[var(--dark-bg)]" data-name="app" data-file="app.js">
        <Sidebar activeView={sidebarView} onViewChange={setSidebarView} onNewTask={() => setModalOpen(true)} theme={theme} onThemeToggle={toggleTheme} connected={connected} />
        <main className="flex-1 flex flex-col overflow-hidden">
          <CalendarHeader currentDate={currentDate} view={calendarView} onViewChange={setCalendarView} onNavigate={navigate} onToday={() => setCurrentDate(new Date())} connected={connected} />
          {calendarView === 'month' && <MonthView currentDate={currentDate} tasks={tasks} onDateClick={handleDateClick} onTaskClick={setSelectedTask} />}
          {calendarView === 'week' && <WeekView currentDate={currentDate} tasks={tasks} onDateClick={handleDateClick} onTaskClick={setSelectedTask} />}
          {calendarView === 'day' && <DayView currentDate={currentDate} tasks={tasks} onTaskClick={setSelectedTask} />}
          <div className="border-t border-gray-200 dark:border-gray-700 p-4 max-h-64 overflow-auto">
            <h3 className="text-sm font-medium text-gray-500 mb-2">{sidebarView === 'today' ? "Today's Tasks" : sidebarView === 'upcoming' ? 'Upcoming' : sidebarView === 'completed' ? 'Completed' : 'All Tasks'}</h3>
            {getFilteredTasks().map(task => <TaskItem key={task.id} task={task} onToggle={toggleTask} onClick={() => setSelectedTask(task)} />)}
            {getFilteredTasks().length === 0 && <p className="text-sm text-gray-400 py-4 text-center">No tasks</p>}
          </div>
        </main>
        {selectedTask && <TaskPanel task={selectedTask} onClose={() => setSelectedTask(null)} onUpdate={updateTask} onDelete={deleteTask} />}
        <TaskModal isOpen={modalOpen} onClose={() => setModalOpen(false)} onSave={addTask} initialDate={modalDate} />
        <CommandPalette isOpen={cmdPaletteOpen} onClose={() => setCmdPaletteOpen(false)} tasks={tasks} onTaskSelect={setSelectedTask} onNewTask={() => setModalOpen(true)} />
      </div>
    );
  } catch (error) { console.error('App error:', error); return null; }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<ErrorBoundary><App /></ErrorBoundary>);
