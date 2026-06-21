function SettingsApp() {
    try {
        const { theme, setTheme } = useThemeStore();
        const [serverStatus, setServerStatus] = React.useState(null);
        const [loading, setLoading] = React.useState(true);

        React.useEffect(() => {
            api.getStatus()
                .then(status => {
                    setServerStatus(status);
                    setLoading(false);
                })
                .catch(() => {
                    setLoading(false);
                });
        }, []);

        const sections = [
            { id: 'appearance', name: 'Appearance', icon: 'icon-palette' },
            { id: 'account', name: 'Account', icon: 'icon-user' },
            { id: 'security', name: 'Security', icon: 'icon-shield' },
        ];

        return (
            <div className="min-h-screen bg-[var(--bg-primary)]">
                <header className="flex items-center gap-4 p-4 border-b border-[var(--border-color)]">
                    <a href="/" className="p-2 rounded-lg hover:bg-[var(--bg-hover)]">
                        <div className="icon-arrow-left text-[var(--text-secondary)] text-xl"></div>
                    </a>
                    <h1 className="text-xl font-semibold">Settings</h1>
                </header>
                <div className="max-w-2xl mx-auto p-6 space-y-6">
                    <section className="bg-[var(--bg-surface)] rounded-xl p-4 border border-[var(--border-color)]">
                        <h2 className="text-lg font-medium mb-4 flex items-center gap-2">
                            <div className="icon-palette text-[var(--accent)]"></div> Appearance
                        </h2>
                        <div className="flex gap-3">
                            {['dark', 'light'].map(t => (
                                <button key={t} onClick={() => setTheme(t)} className={`flex-1 p-3 rounded-lg border ${theme === t ? 'border-[var(--accent)] bg-[var(--bg-hover)]' : 'border-[var(--border-color)]'}`}>
                                    <div className={`icon-${t === 'dark' ? 'moon' : 'sun'} text-xl mb-2`}></div>
                                    <p className="text-sm capitalize">{t} Mode</p>
                                </button>
                            ))}
                        </div>
                    </section>
                    <section className="bg-[var(--bg-surface)] rounded-xl p-4 border border-[var(--border-color)]">
                        <h2 className="text-lg font-medium mb-4 flex items-center gap-2">
                            <div className="icon-user text-[var(--accent)]"></div> Account
                        </h2>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between py-2">
                                <span className="text-[var(--text-secondary)]">Email Address</span>
                                <span>me@ichin.network</span>
                            </div>
                            <div className="flex items-center justify-between py-2">
                                <span className="text-[var(--text-secondary)]">Protocol Version</span>
                                <span>{loading ? '...' : serverStatus?.version || 'unknown'}</span>
                            </div>
                        </div>
                    </section>
                    <section className="bg-[var(--bg-surface)] rounded-xl p-4 border border-[var(--border-color)]">
                        <h2 className="text-lg font-medium mb-4 flex items-center gap-2">
                            <div className="icon-shield text-[var(--accent)]"></div> Security & Network
                        </h2>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between py-2">
                                <span className="text-[var(--text-secondary)]">Connection</span>
                                {loading ? (
                                    <span className="text-[var(--text-secondary)]">Checking...</span>
                                ) : serverStatus ? (
                                    <span className="text-green-500 flex items-center gap-1"><div className="icon-circle-check text-sm"></div> Connected</span>
                                ) : (
                                    <span className="text-red-500 flex items-center gap-1"><div className="icon-circle-alert text-sm"></div> Offline</span>
                                )}
                            </div>
                            <div className="flex items-center justify-between py-2">
                                <span className="text-[var(--text-secondary)]">Encryption</span>
                                <span className="text-green-500 flex items-center gap-1"><div className="icon-lock text-sm"></div> TLS 1.3</span>
                            </div>
                            <div className="flex items-center justify-between py-2">
                                <span className="text-[var(--text-secondary)]">Message Signing</span>
                                <span className="text-green-500 flex items-center gap-1"><div className="icon-check-check text-sm"></div> Ed25519</span>
                            </div>
                        </div>
                    </section>
                </div>
                <footer className="text-center text-[var(--text-secondary)] text-sm py-6">© 2026 Ichin Mail v1.0.0</footer>
            </div>
        );
    } catch (error) {
        console.error('SettingsApp error:', error);
        return null;
    }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<SettingsApp />);
