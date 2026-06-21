const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('browserEngineApi', {
  navigate: (url) => ipcRenderer.invoke('browser-engine:navigate', url),
  extractContent: () => ipcRenderer.invoke('browser-engine:extract-content'),
  executeResearch: (query) => ipcRenderer.invoke('browser-engine:execute-research', query),
  getStatus: () => ipcRenderer.invoke('browser-engine:status'),
});

contextBridge.exposeInMainWorld('searchApi', {
  search: (query, engines) => ipcRenderer.invoke('search:search', query, engines),
  spotlight: (query) => ipcRenderer.invoke('search:spotlight', query),
  getEngines: () => ipcRenderer.invoke('search:engines'),
});

contextBridge.exposeInMainWorld('voiceApi', {
  speak: (text, personality) => ipcRenderer.invoke('voice:speak', text, personality),
  transcribe: (audioData) => ipcRenderer.invoke('voice:transcribe', audioData),
  getPersonalities: () => ipcRenderer.invoke('voice:personalities'),
  setOrbState: (state) => ipcRenderer.invoke('voice:orb-state', state),
});

contextBridge.exposeInMainWorld('knowledgeGraphApi', {
  query: (query) => ipcRenderer.invoke('knowledge-graph:query', query),
  getWorkspace: (workspace) => ipcRenderer.invoke('knowledge-graph:workspace', workspace),
});

contextBridge.exposeInMainWorld('mailAiApi', {
  process: (emailContent) => ipcRenderer.invoke('mail-ai:process', emailContent),
  categorize: (email) => ipcRenderer.invoke('mail-ai:categorize', email),
});
