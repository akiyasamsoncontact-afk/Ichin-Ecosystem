function TabItem({ tab, isActive, onClick, onClose }) {
    try {
        const [showPreview, setShowPreview] = React.useState(false);

        return (
            <div
                className="relative"
                onMouseEnter={() => setShowPreview(true)}
                onMouseLeave={() => setShowPreview(false)}
                data-name="tab-item"
                data-file="components/TabItem.js"
            >
                <div
                    onClick={onClick}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-smooth group ${
                        isActive ? 'bg-[var(--bg-hover)]' : 'hover:bg-[var(--bg-tertiary)]'
                    }`}
                >
                    <div className={`${tab.favicon} text-base text-[var(--text-secondary)]`}></div>
                    <span className="flex-1 text-sm text-[var(--text-primary)] truncate">{tab.title}</span>
                    {!tab.pinned && (
                        <button
                            onClick={(e) => { e.stopPropagation(); onClose(tab.id); }}
                            className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-[var(--bg-hover)] transition-smooth"
                        >
                            <div className="icon-x text-sm text-[var(--text-muted)]"></div>
                        </button>
                    )}
                </div>
                {showPreview && (
                    <div className="absolute left-full ml-2 top-0 z-50 w-64 p-2 rounded-xl glass shadow-2xl">
                        <div className="w-full h-36 rounded-lg bg-[var(--bg-tertiary)] flex items-center justify-center">
                            <div className={`${tab.favicon} text-4xl text-[var(--text-muted)]`}></div>
                        </div>
                        <p className="mt-2 text-xs text-[var(--text-muted)] truncate">{tab.url}</p>
                    </div>
                )}
            </div>
        );
    } catch (error) {
        console.error('TabItem error:', error);
        return null;
    }
}