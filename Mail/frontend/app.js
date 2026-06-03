class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary:', error, errorInfo.componentStack);
    }
    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-[var(--bg-primary)]">
                    <div className="text-center">
                        <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-4">Something went wrong</h1>
                        <p className="text-[var(--text-secondary)] mb-4">{this.state.error?.message}</p>
                        <button onClick={() => window.location.reload()} className="btn-primary">Reload Page</button>
                    </div>
                </div>
            );
        }
        return this.props.children;
    }
}

function App() {
    try {
        const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
        const [activeFolder, setActiveFolder] = React.useState('inbox');
        const [selectedEmail, setSelectedEmail] = React.useState(null);
        const [composeOpen, setComposeOpen] = React.useState(false);
        const [searchQuery, setSearchQuery] = React.useState('');
        const [filter, setFilter] = React.useState('all');
        const [messages, setMessages] = React.useState([]);
        const [loading, setLoading] = React.useState(true);
        const [error, setError] = React.useState(null);
        const [unreadCounts, setUnreadCounts] = React.useState({});
        const [refreshKey, setRefreshKey] = React.useState(0);

        const triggerRefresh = () => setRefreshKey(k => k + 1);

        // Fetch messages when folder changes
        React.useEffect(() => {
            setLoading(true);
            setError(null);
            api.listMessages(activeFolder)
                .then(data => {
                    setMessages(data);
                    setSelectedEmail(null);
                    setLoading(false);
                })
                .catch(err => {
                    console.error('Failed to load messages:', err);
                    setError(err.message);
                    setLoading(false);
                });
        }, [activeFolder, refreshKey]);

        // Fetch unread counts
        React.useEffect(() => {
            api.getUnreadCounts()
                .then(counts => setUnreadCounts(counts))
                .catch(() => {});
        }, [refreshKey]);

        // Poll for new messages every 30s
        React.useEffect(() => {
            const interval = setInterval(() => {
                api.listMessages(activeFolder)
                    .then(data => setMessages(data))
                    .catch(() => {});
                api.getUnreadCounts()
                    .then(counts => setUnreadCounts(counts))
                    .catch(() => {});
            }, 30000);
            return () => clearInterval(interval);
        }, [activeFolder]);

        const handleSelectEmail = (email) => {
            setSelectedEmail(email);
            if (email.unread) {
                api.markRead(email.id).then(() => triggerRefresh()).catch(() => {});
            }
        };

        const handleMessageUpdate = () => {
            triggerRefresh();
        };

        return (
            <div className="h-screen flex overflow-hidden">
                <Sidebar
                    activeFolder={activeFolder}
                    setActiveFolder={setActiveFolder}
                    collapsed={sidebarCollapsed}
                    setCollapsed={setSidebarCollapsed}
                    onCompose={() => setComposeOpen(true)}
                    unreadCounts={unreadCounts}
                />
                <div className="flex-1 flex overflow-hidden">
                    <div className="flex flex-col flex-1">
                        <SearchBar searchQuery={searchQuery} setSearchQuery={setSearchQuery} filter={filter} setFilter={setFilter} />
                        {loading ? (
                            <div className="flex-1 flex items-center justify-center text-[var(--text-secondary)]">
                                <div className="flex items-center gap-2">
                                    <div className="icon-loader-2 animate-spin text-lg"></div>
                                    <span>Loading messages...</span>
                                </div>
                            </div>
                        ) : error ? (
                            <div className="flex-1 flex items-center justify-center text-[var(--text-secondary)]">
                                <div className="text-center">
                                    <div className="icon-wifi-off text-4xl mb-2"></div>
                                    <p>Could not connect to server</p>
                                    <p className="text-sm mt-1">{error}</p>
                                    <button onClick={triggerRefresh} className="btn-primary mt-4">Retry</button>
                                </div>
                            </div>
                        ) : (
                            <EmailList
                                emails={messages}
                                selectedEmail={selectedEmail}
                                setSelectedEmail={handleSelectEmail}
                                searchQuery={searchQuery}
                                filter={filter}
                            />
                        )}
                    </div>
                    <EmailView
                        email={selectedEmail}
                        onClose={() => setSelectedEmail(null)}
                        onAction={handleMessageUpdate}
                    />
                </div>
                <ComposeModal
                    isOpen={composeOpen}
                    onClose={() => setComposeOpen(false)}
                    onSent={handleMessageUpdate}
                />
            </div>
        );
    } catch (error) {
        console.error('App error:', error);
        return null;
    }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <ErrorBoundary>
        <App />
    </ErrorBoundary>
);
