const API_BASE = 'http://127.0.0.1:3002/api';

const StorageKeys = {
    TASKS: 'calentask_tasks',
    THEME: 'calentask_theme',
    VIEW: 'calentask_view'
};

let online = true;
const listeners = [];

function notifyListeners() {
    listeners.forEach(fn => fn(online));
}

function onStatusChange(fn) {
    listeners.push(fn);
    fn(online);
}

function toBackendTask(task) {
    return {
        title: task.title || task.Title || '',
        description: task.description || task.Description || '',
        due_date: task.dueDate || task.due_date || task.DueDate || '',
        priority: task.priority || task.Priority || 'medium',
        status: task.status || task.Status || 'todo',
        tags: task.tags || task.Tags || [],
    };
}

function toFrontendTask(task) {
    return {
        id: task.id || task.Id,
        title: task.title || task.Title,
        description: task.description || task.Description || '',
        dueDate: task.due_date || task.dueDate || task.DueDate || '',
        priority: task.priority || task.Priority || 'medium',
        status: task.status || task.Status || 'todo',
        tags: task.tags || task.Tags || [],
        createdAt: task.created_at || task.createdAt || task.CreatedAt || new Date().toISOString(),
    };
}

async function apiFetch(path, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${path}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        online = false;
        notifyListeners();
        throw e;
    }
}

const api = {
    getTasks: async () => {
        try {
            const data = await apiFetch('/tasks');
            if (!data.success) throw new Error(data.error || 'Failed to fetch tasks');
            online = true;
            notifyListeners();
            return (data.data || []).map(toFrontendTask);
        } catch (e) {
            return Storage.getTasks();
        }
    },

    createTask: async (task) => {
        try {
            const data = await apiFetch('/tasks', {
                method: 'POST',
                body: JSON.stringify(toBackendTask(task)),
            });
            if (!data.success) throw new Error(data.error || 'Failed to create task');
            online = true;
            notifyListeners();
            return toFrontendTask(data.data);
        } catch (e) {
            const local = { ...toFrontendTask(task), id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2) };
            Storage.saveTasks([...Storage.getTasks(), local]);
            return local;
        }
    },

    updateTask: async (task) => {
        try {
            const data = await apiFetch(`/tasks/${task.id}`, {
                method: 'PUT',
                body: JSON.stringify(toBackendTask(task)),
            });
            if (!data.success) throw new Error(data.error || 'Failed to update task');
            online = true;
            notifyListeners();
            return toFrontendTask(data.data);
        } catch (e) {
            const tasks = Storage.getTasks();
            const idx = tasks.findIndex(t => t.id === task.id);
            if (idx !== -1) {
                tasks[idx] = toFrontendTask(task);
                Storage.saveTasks(tasks);
            }
            return toFrontendTask(task);
        }
    },

    deleteTask: async (id) => {
        try {
            const data = await apiFetch(`/tasks/${id}`, { method: 'DELETE' });
            if (!data.success) throw new Error(data.error || 'Failed to delete task');
            online = true;
            notifyListeners();
            return true;
        } catch (e) {
            Storage.saveTasks(Storage.getTasks().filter(t => t.id !== id));
            return true;
        }
    },

    syncLocalToBackend: async () => {
        const localTasks = Storage.getTasks();
        if (localTasks.length === 0) return;

        try {
            const data = await apiFetch('/tasks');
            if (!data.success) return;
            const serverTasks = (data.data || []).map(toFrontendTask);
            const serverIds = new Set(serverTasks.map(t => t.id));

            const unsynced = localTasks.filter(t => !serverIds.has(t.id));
            for (const task of unsynced) {
                try {
                    await apiFetch('/tasks', {
                        method: 'POST',
                        body: JSON.stringify(toBackendTask(task)),
                    });
                } catch (e) {
                    return;
                }
            }

            online = true;
            notifyListeners();
        } catch (e) {
            // Backend still unavailable
        }
    }
};

const Storage = {
    getTasks: () => {
        try {
            const data = localStorage.getItem(StorageKeys.TASKS);
            return data ? JSON.parse(data).map(toFrontendTask) : [];
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

let syncInterval = null;

function startPeriodicSync(intervalMs = 30000) {
    stopPeriodicSync();
    syncInterval = setInterval(() => api.syncLocalToBackend(), intervalMs);
}

function stopPeriodicSync() {
    if (syncInterval) { clearInterval(syncInterval); syncInterval = null; }
}

// Try sync on load
setTimeout(() => api.syncLocalToBackend(), 1000);
