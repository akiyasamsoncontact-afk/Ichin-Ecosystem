function UserProfile() {
    try {
        return (
            <div className="flex items-center gap-3 p-4 border-b border-[var(--border-color)]" data-name="user-profile" data-file="components/UserProfile.js">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[var(--accent-blue)] to-[var(--accent-purple)] flex items-center justify-center">
                    <span className="text-sm font-semibold text-white">JD</span>
                </div>
                <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-[var(--text-primary)] truncate">John Doe</p>
                    <p className="text-xs text-[var(--text-muted)]">Pro Plan</p>
                </div>
                <button className="p-1.5 rounded-lg hover:bg-[var(--bg-hover)] transition-smooth">
                    <div className="icon-settings text-lg text-[var(--text-secondary)]"></div>
                </button>
            </div>
        );
    } catch (error) {
        console.error('UserProfile error:', error);
        return null;
    }
}