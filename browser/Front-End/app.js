import React from 'react';
import ReactDOM from 'react-dom/client';

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
                        onUrlChange={() => {}}
                        onBack={() => {}}
                        onForward={() => {}}
                        onRefresh={() => {}}
                        canGoBack={false}
                        canGoForward={false}
                        onSplitView={() => setSplitView(!splitView)}
                        isSplitView={splitView}
                    />
                    <div className="flex-1 flex">
                        <WebView url={currentTab?.url || ''} title={currentTab?.title || ''} />
                        {splitView && <WebView url="https://notion.so" title="Notion" />}
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
