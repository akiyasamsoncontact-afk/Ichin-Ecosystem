const API_BASE = 'http://127.0.0.1:3002/api';

const StorageKeys = {
    TASKS: 'calentask_tasks',
    THEME: 'calentask_theme',
    VIEW: 'calentask_view'
};

const api = {
    getTasks: async () => {
        try {
            const res = await fetch(`${API_BASE}/tasks`);
            const data = await res.json();
            if (data.success) return data.data;
            throw new Error(data.error || 'Failed to fetch tasks');
        } catch (e) {
            console.warn('API unavailable, falling back to localStorage:', e.message);
            return Storage.getTasks();
        }
    },
    createTask: async (task) => {
        try {
            const res = await fetch(`${API_BASE}/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: task.title,
                    description: task.description,
                    due_date: task.dueDate,
                    priority: task.priority,
                    status: task.status,
                    tags: task.tags,
                }),
            });
            const data = await res.json();
            if (data.success) return data.data;
            throw new Error(data.error || 'Failed to create task');
        } catch (e) {
            console.warn('API unavailable, saving to localStorage:', e.message);
            Storage.saveTasks([...Storage.getTasks(), task]);
            return task;
        }
    },
    updateTask: async (task) => {
        try {
            const res = await fetch(`${API_BASE}/tasks/${task.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: task.title,
                    description: task.description,
                    due_date: task.dueDate,
                    priority: task.priority,
                    status: task.status,
                    tags: task.tags,
                }),
            });
            const data = await res.json();
            if (data.success) return data.data;
            throw new Error(data.error || 'Failed to update task');
        } catch (e) {
            console.warn('API unavailable, updating localStorage:', e.message);
            const tasks = Storage.getTasks();
            const idx = tasks.findIndex(t => t.id === task.id);
            if (idx !== -1) tasks[idx] = task;
            Storage.saveTasks(tasks);
            return task;
        }
    },
    deleteTask: async (id) => {
        try {
            const res = await fetch(`${API_BASE}/tasks/${id}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.success) return true;
            throw new Error(data.error || 'Failed to delete task');
        } catch (e) {
            console.warn('API unavailable, deleting from localStorage:', e.message);
            Storage.saveTasks(Storage.getTasks().filter(t => t.id !== id));
            return true;
        }
    }
};

const Storage = {
    getTasks: () => {
        try {
            const data = localStorage.getItem(StorageKeys.TASKS);
            return data ? JSON.parse(data) : [];
        } catch (e) { console.error(e); return []; }
    },
    saveTasks: (tasks) => {
        try { localStorage.setItem(StorageKeys.TASKS, JSON.stringify(tasks)); }
        catch (e) { console.error(e); }
    },
    getTheme: () => localStorage.getItem(StorageKeys.THEME) || 'light',
    saveTheme: (theme) => localStorage.setItem(StorageKeys.THEME, theme),
    getView: () => localStorage.getItem(StorageKeys.VIEW) || 'month',
    saveView: (view) => localStorage.setItem(StorageKeys.VIEW, view)
};
