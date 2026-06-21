function SearchBar({ searchQuery, setSearchQuery, filter, setFilter }) {
    try {
        return (
            <div className="p-4 border-b border-[var(--border-color)]" data-name="search-bar" data-file="components/SearchBar.js">
                <div className="relative">
                    <div className="icon-search absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]"></div>
                    <input
                        type="text"
                        placeholder="Search emails..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-[var(--bg-hover)] text-[var(--text-primary)] pl-10 pr-4 py-2 rounded-lg border border-[var(--border-color)] focus:outline-none focus:border-[var(--accent)]"
                    />
                </div>
                <div className="flex gap-2 mt-3">
                    {['All', 'Unread', 'Starred', 'Attachments'].map(f => (
                        <button
                            key={f}
                            onClick={() => setFilter(f.toLowerCase())}
                            className={`px-3 py-1 text-sm rounded-full transition-colors ${filter === f.toLowerCase() ? 'bg-[var(--accent)] text-white' : 'bg-[var(--bg-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'}`}
                        >
                            {f}
                        </button>
                    ))}
                </div>
            </div>
        );
    } catch (error) {
        console.error('SearchBar component error:', error);
        return null;
    }
}