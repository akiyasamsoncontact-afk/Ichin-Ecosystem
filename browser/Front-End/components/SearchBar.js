function SearchBar({ onOpenCommand }) {
    try {
        return (
            <div className="px-3 py-2" data-name="search-bar" data-file="components/SearchBar.js">
                <button
                    onClick={onOpenCommand}
                    className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--bg-hover)] transition-smooth group"
                >
                    <div className="icon-search text-base text-[var(--text-muted)] group-hover:text-[var(--text-secondary)]"></div>
                    <span className="flex-1 text-left text-sm text-[var(--text-muted)]">Search or command...</span>
                    <kbd className="px-1.5 py-0.5 rounded bg-[var(--bg-hover)] text-xs text-[var(--text-muted)]">⌘K</kbd>
                </button>
            </div>
        );
    } catch (error) {
        console.error('SearchBar error:', error);
        return null;
    }
}