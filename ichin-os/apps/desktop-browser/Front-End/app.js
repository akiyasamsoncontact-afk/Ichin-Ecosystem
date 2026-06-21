class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo.componentStack);
    }
    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-[var(--bg-primary)]">
                    <div className="text-center">
                        <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-4">Something went wrong</h1>
                        <button onClick={() => window.location.reload()} className="px-4 py-2 rounded-lg bg-[var(--accent-blue)] text-white">Reload</button>
                    </div>
                </div>
            );
        }
        return this.props.children;
    }
}

function App() {
    try {
        const [tabs, setTabs] = React.useState(INITIAL_TABS);
        const [activeTab, setActiveTab] = React.useState('1');
        const [activeWorkspace, setActiveWorkspace] = React.useState('work');
        const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
        const [commandOpen, setCommandOpen] = React.useState(false);
        const [splitView, setSplitView] = React.useState(false);

        const currentTab = tabs.find(t => t.id === activeTab) || tabs[0];
        const tabHistory = currentTab?.history || [currentTab?.url].filter(Boolean);
        const historyIndex = currentTab?.historyIndex || 0;
        const canGoBack = historyIndex > 0;
        const canGoForward = historyIndex < tabHistory.length - 1;

        React.useEffect(() => {
            const handleKeyDown = (e) => {
                if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                    e.preventDefault();
                    setCommandOpen(true);
                }
            };
            document.addEventListener('keydown', handleKeyDown);
            return () => document.removeEventListener('keydown', handleKeyDown);
        }, []);

        React.useEffect(() => {
            async function fetchBrowserStatus() {
                try {
                    const resp = await fetch('http://localhost:8040/health');
                    const data = await resp.json();
                    console.log('Browser Engine:', data);
                } catch (err) {
                    console.warn('Browser Engine unavailable:', err.message);
                }
            }
            fetchBrowserStatus();
        }, []);

        const updateTabUrl = (tabId, url, title) => {
            setTabs(tabs.map(t => {
                if (t.id !== tabId) return t;
                const history = t.history || [t.url];
                const historyIndex = t.historyIndex || 0;
                const newHistory = history.slice(0, historyIndex + 1);
                newHistory.push(url);
                return { ...t, url, title: title || t.title, history: newHistory, historyIndex: newHistory.length - 1 };
            }));
        };

        const handleUrlChange = (url) => {
            updateTabUrl(activeTab, url);
        };

        const handleBack = () => {
            const tab = tabs.find(t => t.id === activeTab);
            if (!tab) return;
            const history = tab.history || [tab.url];
            const idx = tab.historyIndex || 0;
            if (idx > 0) {
                const newIdx = idx - 1;
                setTabs(tabs.map(t => t.id === activeTab ? { ...t, url: history[newIdx], historyIndex: newIdx } : t));
            }
        };

        const handleForward = () => {
            const tab = tabs.find(t => t.id === activeTab);
            if (!tab) return;
            const history = tab.history || [tab.url];
            const idx = tab.historyIndex || 0;
            if (idx < history.length - 1) {
                const newIdx = idx + 1;
                setTabs(tabs.map(t => t.id === activeTab ? { ...t, url: history[newIdx], historyIndex: newIdx } : t));
            }
        };

        const handleRefresh = () => {
            const tab = tabs.find(t => t.id === activeTab);
            if (!tab) return;
            setTabs(tabs.map(t => t.id === activeTab ? { ...t, url: tab.url } : t));
        };

        const handleCloseTab = (tabId) => {
            setTabs(tabs.filter(t => t.id !== tabId));
            if (activeTab === tabId) setActiveTab(tabs[0]?.id || '');
        };

        return (
            <div className="flex h-screen w-screen" data-name="app" data-file="app.js">
                <Sidebar
                    isCollapsed={sidebarCollapsed}
                    onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
                    tabs={tabs}
                    activeTab={activeTab}
                    onTabClick={setActiveTab}
                    onTabClose={handleCloseTab}
                    activeWorkspace={activeWorkspace}
                    onWorkspaceSelect={setActiveWorkspace}
                    onOpenCommand={() => setCommandOpen(true)}
                />
                <div className="flex-1 flex flex-col min-w-0">
                    <Toolbar
                        url={currentTab?.url || ''}
                        onUrlChange={handleUrlChange}
                        onBack={handleBack}
                        onForward={handleForward}
                        onRefresh={handleRefresh}
                        canGoBack={canGoBack}
                        canGoForward={canGoForward}
                        onSplitView={() => setSplitView(!splitView)}
                        isSplitView={splitView}
                    />
                    <div className="flex-1 flex">
                        <WebView url={currentTab?.url || ''} title={currentTab?.title || ''} />
                        {splitView && <WebView url={currentTab?.url || ''} title={currentTab?.title || ''} />}
                    </div>
                </div>
                <CommandPalette isOpen={commandOpen} onClose={() => setCommandOpen(false)} />
            </div>
        );
    } catch (error) {
        console.error('App error:', error);
        return null;
    }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<ErrorBoundary><App /></ErrorBoundary>);
