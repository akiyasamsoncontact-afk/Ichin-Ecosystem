function Toolbar({ url, onUrlChange, onBack, onForward, onRefresh, canGoBack, canGoForward, onSplitView, isSplitView }) {
    try {
        const [inputUrl, setInputUrl] = React.useState(url);

        React.useEffect(() => { setInputUrl(url); }, [url]);

        const handleSubmit = (e) => {
            e.preventDefault();
            onUrlChange(inputUrl);
        };

        return (
            <div className="flex items-center gap-2 px-4 py-2 bg-[var(--bg-secondary)] border-b border-[var(--border-color)]" data-name="toolbar" data-file="components/Toolbar.js">
                <div className="flex items-center gap-1">
                    <button onClick={onBack} disabled={!canGoBack} className={`p-2 rounded-lg transition-smooth ${canGoBack ? 'hover:bg-[var(--bg-hover)]' : 'opacity-40'}`}>
                        <div className="icon-arrow-left text-lg text-[var(--text-secondary)]"></div>
                    </button>
                    <button onClick={onForward} disabled={!canGoForward} className={`p-2 rounded-lg transition-smooth ${canGoForward ? 'hover:bg-[var(--bg-hover)]' : 'opacity-40'}`}>
                        <div className="icon-arrow-right text-lg text-[var(--text-secondary)]"></div>
                    </button>
                    <button onClick={onRefresh} className="p-2 rounded-lg hover:bg-[var(--bg-hover)] transition-smooth">
                        <div className="icon-refresh-cw text-lg text-[var(--text-secondary)]"></div>
                    </button>
                </div>
                <form onSubmit={handleSubmit} className="flex-1">
                    <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[var(--bg-tertiary)] border border-transparent focus-within:border-[var(--accent-blue)]">
                        <div className="icon-lock text-sm text-[var(--accent-green)]"></div>
                        <input
                            type="text"
                            value={inputUrl}
                            onChange={(e) => setInputUrl(e.target.value)}
                            className="flex-1 bg-transparent text-sm text-[var(--text-primary)] outline-none placeholder-[var(--text-muted)]"
                            placeholder="Enter URL or search..."
                        />
                    </div>
                </form>
                <div className="flex items-center gap-1">
                    <button onClick={onSplitView} className={`p-2 rounded-lg transition-smooth ${isSplitView ? 'bg-[var(--accent-blue)] bg-opacity-20' : 'hover:bg-[var(--bg-hover)]'}`}>
                        <div className={`icon-columns-2 text-lg ${isSplitView ? 'text-[var(--accent-blue)]' : 'text-[var(--text-secondary)]'}`}></div>
                    </button>
                    <button className="p-2 rounded-lg hover:bg-[var(--bg-hover)] transition-smooth">
                        <div className="icon-more-vertical text-lg text-[var(--text-secondary)]"></div>
                    </button>
                </div>
            </div>
        );
    } catch (error) {
        console.error('Toolbar error:', error);
        return null;
    }
}