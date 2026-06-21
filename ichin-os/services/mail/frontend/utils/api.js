const API_BASE = window.location.origin;

const api = {
    async request(method, path, body = null) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) opts.body = JSON.stringify(body);
        const res = await fetch(`${API_BASE}${path}`, opts);
        if (!res.ok) {
            const err = await res.text();
            throw new Error(err || `HTTP ${res.status}`);
        }
        return res.json();
    },

    async getStatus() {
        return this.request('GET', '/api/status');
    },

    async listMessages(folder = 'inbox') {
        return this.request('GET', `/api/messages?folder=${folder}`);
    },

    async getMessage(id) {
        return this.request('GET', `/api/messages/${id}`);
    },

    async sendMessage({ to, subject, body, from }) {
        return this.request('POST', '/api/messages', { to, subject, body, from });
    },

    async messageAction(id, action) {
        return this.request('POST', `/api/messages/${id}/action`, { action });
    },

    async markRead(id) {
        return this.request('POST', `/api/messages/${id}/read`);
    },

    async toggleStar(id) {
        return this.request('POST', `/api/messages/${id}/star`);
    },

    async getUnreadCounts() {
        return this.request('GET', '/api/unread-counts');
    },

    async fetchWithCache(key, fetcher, ttl = 5000) {
        const cached = sessionStorage.getItem(key);
        if (cached) {
            const { data, time } = JSON.parse(cached);
            if (Date.now() - time < ttl) return data;
        }
        const data = await fetcher();
        sessionStorage.setItem(key, JSON.stringify({ data, time: Date.now() }));
        return data;
    },

    clearCache(key) {
        if (key) sessionStorage.removeItem(key);
        else sessionStorage.clear();
    }
};
