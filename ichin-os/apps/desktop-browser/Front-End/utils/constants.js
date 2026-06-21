const WORKSPACES = [
    { id: 'work', name: 'Work', color: '#3b82f6', icon: 'briefcase' },
    { id: 'personal', name: 'Personal', color: '#22c55e', icon: 'home' },
    { id: 'research', name: 'Research', color: '#8b5cf6', icon: 'book-open' },
    { id: 'social', name: 'Social', color: '#ec4899', icon: 'users' },
];

const INITIAL_TABS = [
    { id: '1', title: 'GitHub', url: 'https://github.com', favicon: 'icon-github', pinned: true },
    { id: '2', title: 'Notion', url: 'https://notion.so', favicon: 'icon-file-text', pinned: true },
    { id: '3', title: 'Linear', url: 'https://linear.app', favicon: 'icon-layers', pinned: false },
    { id: '4', title: 'Figma', url: 'https://figma.com', favicon: 'icon-pen-tool', pinned: false },
    { id: '5', title: 'Vercel', url: 'https://vercel.com', favicon: 'icon-triangle', pinned: false },
];

const ICHIN_AI_ROUTER_URL = 'http://localhost:8020';
const ICHIN_VOICE_ENGINE_URL = 'http://localhost:8030';
const ICHIN_BROWSER_ENGINE_URL = 'http://localhost:8040';
const ICHIN_SEARCH_URL = 'http://localhost:8050';
const ICHIN_MAIL_AI_URL = 'http://localhost:8060';
const ICHIN_KNOWLEDGE_GRAPH_URL = 'http://localhost:8070';
const ICHIN_ORCHESTRATOR_URL = 'http://localhost:8000';
const ICHIN_AGENTS_URL = 'http://localhost:8012';
const ICHIN_MEMORY_URL = 'http://localhost:8003';
const ICHIN_AI_STUDIO_URL = 'http://localhost:8016';

const FAVORITES = [
    { id: 'f1', title: 'Stack Overflow', url: 'https://stackoverflow.com', icon: 'icon-code' },
    { id: 'f2', title: 'MDN Web Docs', url: 'https://developer.mozilla.org', icon: 'icon-book' },
    { id: 'f3', title: 'Twitter', url: 'https://twitter.com', icon: 'icon-at-sign' },
];