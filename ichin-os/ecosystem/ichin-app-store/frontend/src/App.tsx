import React, { useEffect, useState } from 'react'
import type { AppListItem, AppDetail, Category, InstalledApp } from './types'
import * as api from './api'

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#0a0a0a',
    color: '#e0e0e0',
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
    padding: 0,
    margin: 0,
  },
  header: {
    borderBottom: '1px solid #1a1a1a',
    padding: '16px 32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    background: 'rgba(10,10,10,0.9)',
    backdropFilter: 'blur(12px)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  logo: { fontSize: 20, fontWeight: 700, letterSpacing: -0.5, color: '#fff' },
  searchInput: {
    background: '#1a1a1a',
    border: '1px solid #2a2a2a',
    borderRadius: 8,
    padding: '8px 16px',
    color: '#e0e0e0',
    fontSize: 14,
    width: 280,
    outline: 'none',
  },
  tabs: {
    display: 'flex',
    gap: 4,
    padding: '12px 32px',
    borderBottom: '1px solid #1a1a1a',
    overflowX: 'auto',
  },
  tab: {
    padding: '6px 16px',
    borderRadius: 6,
    border: 'none',
    background: 'transparent',
    color: '#666',
    cursor: 'pointer',
    fontSize: 13,
    whiteSpace: 'nowrap',
  },
  tabActive: {
    background: '#1a1a1a',
    color: '#fff',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
    gap: 16,
    padding: '24px 32px',
  },
  card: {
    background: '#111',
    border: '1px solid #1a1a1a',
    borderRadius: 12,
    padding: 16,
    cursor: 'pointer',
    transition: 'border-color 0.2s',
  },
  cardIcon: {
    width: 48,
    height: 48,
    borderRadius: 10,
    background: '#1a1a1a',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 20,
    marginBottom: 12,
  },
  cardName: { fontSize: 15, fontWeight: 600, marginBottom: 4 },
  cardDesc: { fontSize: 12, color: '#666', marginBottom: 8, lineHeight: '1.4em', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' },
  cardMeta: { display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: '#888' },
  badge: {
    padding: '2px 8px',
    borderRadius: 4,
    fontSize: 11,
    background: '#1a1a1a',
    color: '#888',
  },
  badgeAi: { background: '#1a2a1a', color: '#4caf50' },
  btn: {
    padding: '6px 14px',
    borderRadius: 6,
    border: 'none',
    cursor: 'pointer',
    fontSize: 13,
    fontWeight: 500,
  },
  btnPrimary: { background: '#fff', color: '#000' },
  btnSecondary: { border: '1px solid #2a2a2a', background: 'transparent', color: '#e0e0e0' },
  detailOverlay: {
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex',
    alignItems: 'center', justifyContent: 'center', zIndex: 200, padding: 32,
  },
  detailPanel: {
    background: '#111', border: '1px solid #1a1a1a', borderRadius: 16,
    maxWidth: 640, width: '100%', maxHeight: '80vh', overflowY: 'auto', padding: 32,
  },
  detailHeader: { display: 'flex', gap: 16, marginBottom: 24, alignItems: 'flex-start' },
  detailIcon: { width: 64, height: 64, borderRadius: 14, background: '#1a1a1a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, flexShrink: 0 },
  detailName: { fontSize: 22, fontWeight: 700, marginBottom: 4 },
  detailAuthor: { fontSize: 13, color: '#666', marginBottom: 4 },
  detailDesc: { fontSize: 14, lineHeight: '1.6', color: '#aaa', marginBottom: 24 },
  section: { marginBottom: 24 },
  sectionTitle: { fontSize: 13, fontWeight: 600, color: '#888', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 },
  reviewCard: {
    background: '#0a0a0a', border: '1px solid #1a1a1a', borderRadius: 8, padding: 12, marginBottom: 8,
  },
  reviewScore: { display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 12, color: '#888' },
  permissionItem: { display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0', fontSize: 13, color: '#aaa' },
}

const ICONS: Record<string, string> = {
  productivity: 'zap', study: 'book', coding: 'code', 'ai-agents': 'brain', learning: 'graduation-cap', system: 'puzzle',
}

export default function App() {
  const [apps, setApps] = useState<AppListItem[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [installed, setInstalled] = useState<InstalledApp[]>([])
  const [activeTab, setActiveTab] = useState('all')
  const [search, setSearch] = useState('')
  const [selectedApp, setSelectedApp] = useState<AppDetail | null>(null)
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null)
  const [view, setView] = useState<'browse' | 'installed'>('browse')

  useEffect(() => {
    api.fetchCategories().then(setCategories)
    api.fetchInstalled().then(setInstalled)
  }, [])

  useEffect(() => {
    api.fetchApps(activeTab === 'all' ? undefined : activeTab, search || undefined).then(setApps)
  }, [activeTab, search])

  async function openDetail(id: string) {
    setSelectedAppId(id)
    const detail = await api.fetchApp(id)
    setSelectedApp(detail)
  }

  async function handleInstall(id: string) {
    await api.installApp(id)
    const updated = await api.fetchInstalled()
    setInstalled(updated)
  }

  async function handleUninstall(id: string) {
    await api.uninstallApp(id)
    const updated = await api.fetchInstalled()
    setInstalled(updated)
  }

  function isInstalled(id: string) {
    return installed.some(i => i.installRecord.appId === id)
  }

  const filtered = view === 'installed'
    ? apps.filter(a => isInstalled(a.id))
    : apps

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.logo}>ICHIN App Store</div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <button style={{ ...styles.btn, ...(view === 'browse' ? styles.btnPrimary : styles.btnSecondary) }} onClick={() => setView('browse')}>Browse</button>
          <button style={{ ...styles.btn, ...(view === 'installed' ? styles.btnPrimary : styles.btnSecondary) }} onClick={() => setView('installed')}>
            Installed ({installed.length})
          </button>
          <input
            style={styles.searchInput}
            placeholder="Search apps..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div style={styles.tabs}>
        <button
          style={{ ...styles.tab, ...(activeTab === 'all' ? styles.tabActive : {}) }}
          onClick={() => setActiveTab('all')}
        >All</button>
        {categories.map(c => (
          <button
            key={c.id}
            style={{ ...styles.tab, ...(activeTab === c.id ? styles.tabActive : {}) }}
            onClick={() => setActiveTab(c.id)}
          >{c.name}</button>
        ))}
      </div>

      <div style={styles.grid}>
        {filtered.map(app => (
          <div key={app.id} style={styles.card} onClick={() => openDetail(app.id)}>
            <div style={styles.cardIcon}>{app.icon || ICONS[app.category] || 'box'}</div>
            <div style={styles.cardName}>{app.name}</div>
            <div style={styles.cardDesc}>{app.description}</div>
            <div style={styles.cardMeta}>
              <span>★ {app.rating.toFixed(1)}</span>
              <span style={styles.badge}>{app.category}</span>
              {app.aiTested && <span style={{ ...styles.badge, ...styles.badgeAi }}>AI Tested</span>}
            </div>
          </div>
        ))}
      </div>

      {selectedApp && selectedAppId && (
        <div style={styles.detailOverlay} onClick={() => { setSelectedApp(null); setSelectedAppId(null) }}>
          <div style={styles.detailPanel} onClick={e => e.stopPropagation()}>
            <div style={styles.detailHeader}>
              <div style={styles.detailIcon}>{selectedApp.manifest.icon || ICONS[selectedApp.manifest.category] || 'box'}</div>
              <div style={{ flex: 1 }}>
                <div style={styles.detailName}>{selectedApp.manifest.name}</div>
                <div style={styles.detailAuthor}>by {selectedApp.manifest.author} · v{selectedApp.manifest.version}</div>
                <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                  <span style={styles.badge}>{selectedApp.manifest.category}</span>
                  <span style={{ ...styles.badge, ...styles.badgeAi }}>AI {Math.round(selectedApp.manifest.aiCompatibility * 100)}%</span>
                  <span style={styles.badge}>★ {selectedApp.ratings.average.toFixed(1)} ({selectedApp.ratings.count})</span>
                </div>
              </div>
            </div>

            <div style={styles.detailDesc}>{selectedApp.manifest.description}</div>

            <div style={styles.section}>
              <div style={styles.sectionTitle}>Permissions</div>
              {selectedApp.manifest.permissions.map(p => (
                <div key={p.id} style={styles.permissionItem}>
                  <span style={{ color: p.granted ? '#4caf50' : '#888' }}>{p.granted ? '✓' : '○'}</span>
                  <span>{p.name}</span>
                  <span style={{ color: '#666', fontSize: 12 }}>— {p.description}</span>
                </div>
              ))}
            </div>

            {selectedApp.reviews.length > 0 && (
              <div style={styles.section}>
                <div style={styles.sectionTitle}>AI Review</div>
                {selectedApp.reviews.slice(-1).map(r => (
                  <div key={r.id} style={styles.reviewCard}>
                    <div style={{ display: 'flex', gap: 12, fontSize: 13, marginBottom: 8 }}>
                      <span style={styles.reviewScore}>Security: {r.securityScore}</span>
                      <span style={styles.reviewScore}>Sandbox: {r.sandboxScore}</span>
                      <span style={styles.reviewScore}>AI: {r.aiScore}</span>
                      <span style={styles.reviewScore}>Overall: {r.overallScore}</span>
                    </div>
                    <div style={{ fontSize: 12, color: r.status === 'approved' ? '#4caf50' : '#ff9800' }}>
                      Status: {r.status}
                    </div>
                    {r.issues.length > 0 && (
                      <div style={{ fontSize: 12, color: '#ff9800', marginTop: 4 }}>
                        Issues: {r.issues.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
              {isInstalled(selectedAppId) ? (
                <button style={{ ...styles.btn, ...styles.btnSecondary }} onClick={() => handleUninstall(selectedAppId)}>
                  Uninstall
                </button>
              ) : (
                <button style={{ ...styles.btn, ...styles.btnPrimary }} onClick={() => handleInstall(selectedAppId)}>
                  Install
                </button>
              )}
              <button style={{ ...styles.btn, ...styles.btnSecondary }} onClick={() => { setSelectedApp(null); setSelectedAppId(null) }}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
