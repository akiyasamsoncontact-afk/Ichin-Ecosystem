const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const http = require('http');

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile(path.join(__dirname, 'Front-End', 'index.html'));
}

function apiCall(host, port, endpoint, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: host,
      port,
      path: endpoint,
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch { resolve(data); }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

ipcMain.handle('browser-engine:navigate', async (event, url) => {
  return apiCall('localhost', 8040, '/api/navigate', 'POST', { url });
});

ipcMain.handle('browser-engine:extract-content', async () => {
  return apiCall('localhost', 8040, '/api/extract', 'POST', {});
});

ipcMain.handle('browser-engine:execute-research', async (event, query) => {
  return apiCall('localhost', 8040, '/api/research', 'POST', { query });
});

ipcMain.handle('browser-engine:status', async () => {
  return apiCall('localhost', 8040, '/health', 'GET');
});

ipcMain.handle('search:search', async (event, query, engines) => {
  return apiCall('localhost', 8050, '/api/search', 'POST', { query, engines: engines || [] });
});

ipcMain.handle('search:spotlight', async (event, query) => {
  return apiCall('localhost', 8050, '/api/spotlight', 'POST', { query });
});

ipcMain.handle('search:engines', async () => {
  return apiCall('localhost', 8050, '/api/engines', 'GET');
});

ipcMain.handle('voice:speak', async (event, text, personality) => {
  return apiCall('localhost', 8030, '/api/tts', 'POST', { text, personality: personality || 'neutral' });
});

ipcMain.handle('voice:transcribe', async (event, audioData) => {
  return apiCall('localhost', 8030, '/api/stt', 'POST', { audio_data: audioData });
});

ipcMain.handle('voice:personalities', async () => {
  return apiCall('localhost', 8030, '/api/personalities', 'GET');
});

ipcMain.handle('voice:orb-state', async (event, state) => {
  return apiCall('localhost', 8030, '/api/orb/state', 'POST', { state });
});

ipcMain.handle('knowledge-graph:query', async (event, query) => {
  return apiCall('localhost', 8070, '/api/query', 'POST', { query });
});

ipcMain.handle('knowledge-graph:workspace', async (event, workspace) => {
  return apiCall('localhost', 8070, '/api/workspace', 'POST', { workspace });
});

ipcMain.handle('mail-ai:process', async (event, emailContent) => {
  return apiCall('localhost', 8060, '/api/process', 'POST', emailContent);
});

ipcMain.handle('mail-ai:categorize', async (event, email) => {
  return apiCall('localhost', 8060, '/api/categorize', 'POST', email);
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
