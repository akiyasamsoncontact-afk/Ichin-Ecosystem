function WebView({ url, title, onUrlChange, onLoadingChange }) {
    try {
        const [loading, setLoading] = React.useState(true);
        const [error, setError] = React.useState(null);
        const iframeRef = React.useRef(null);

        React.useEffect(() => {
            setLoading(true);
            setError(null);
            if (onLoadingChange) onLoadingChange(true);
        }, [url]);

        const handleIframeLoad = () => {
            setLoading(false);
            if (onLoadingChange) onLoadingChange(false);
            try {
                const iframe = iframeRef.current;
                if (iframe && iframe.contentWindow) {
                    const title = iframe.contentDocument?.title;
                    if (title && onUrlChange) onUrlChange(url, title);
                }
            } catch (e) {
                // cross-origin access denied - expected for external content
            }
        };

        const handleIframeError = () => {
            setLoading(false);
            setError('Failed to load page');
            if (onLoadingChange) onLoadingChange(false);
        };

        const showError = !url || url === '/' || url === '';
        const showIframe = url && url !== '/' && url !== '';

        return (
            <div className="flex-1 bg-[var(--bg-primary)] rounded-tl-2xl overflow-hidden relative" data-name="webview">
                {loading && showIframe && (
                    <div className="absolute inset-0 flex items-center justify-center bg-[var(--bg-primary)] z-10">
                        <div className="flex flex-col items-center gap-3">
                            <div className="w-8 h-8 border-2 border-[var(--accent-blue)] border-t-transparent rounded-full animate-spin"></div>
                            <span className="text-sm text-[var(--text-muted)]">Loading...</span>
                        </div>
                    </div>
                )}
                {error && (
                    <div className="w-full h-full flex flex-col items-center justify-center bg-[var(--bg-secondary)]">
                        <div className="w-16 h-16 rounded-2xl bg-[var(--bg-tertiary)] flex items-center justify-center mb-4">
                            <span className="text-3xl text-[var(--accent-orange)]">!</span>
                        </div>
                        <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">Failed to load page</h2>
                        <p className="text-sm text-[var(--text-muted)] mb-4">{error}</p>
                        <p className="text-xs text-[var(--text-muted)]">{url}</p>
                        <button onClick={() => { setError(null); setLoading(true); }} className="mt-4 px-4 py-2 rounded-lg bg-[var(--accent-blue)] text-white text-sm hover:opacity-90 transition-smooth">
                            Retry
                        </button>
                    </div>
                )}
                {showIframe && !error && (
                    <iframe
                        ref={iframeRef}
                        src={url}
                        className="w-full h-full border-0"
                        title={title || 'Ichin Browser'}
                        sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                        onLoad={handleIframeLoad}
                        onError={handleIframeError}
                    />
                )}
                {showError && (
                    <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-[var(--bg-secondary)] to-[var(--bg-primary)]">
                        <div className="w-20 h-20 rounded-2xl bg-[var(--bg-tertiary)] flex items-center justify-center mb-6 shadow-2xl">
                            <span className="text-4xl text-[var(--accent-blue)]">+</span>
                        </div>
                        <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-2">{title || 'New Tab'}</h2>
                        <p className="text-sm text-[var(--text-muted)]">Enter a URL in the address bar to start browsing</p>
                    </div>
                )}
            </div>
        );
    } catch (error) {
        console.error('WebView error:', error);
        return null;
    }
}
