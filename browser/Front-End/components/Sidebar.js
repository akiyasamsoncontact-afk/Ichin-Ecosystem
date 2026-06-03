function Sidebar({ isCollapsed, onToggle, tabs, activeTab, onTabClick, onTabClose, activeWorkspace, onWorkspaceSelect, onOpenCommand }) {
    try {
        const pinnedTabs = tabs.filter(t => t.pinned);
        const activeTabs = tabs.filter(t => !t.pinned);

        if (isCollapsed) {
            return (
                <div className="w-16 h-full bg-[var(--bg-secondary)] border-r border-[var(--border-color)] flex flex-col items-center py-4" data-name="sidebar-collapsed" data-file="components/Sidebar.js">
                    <button onClick={onToggle} className="p-2 rounded-lg hover:bg-[var(--bg-hover)] transition-smooth mb-4">
                        <div className="icon-panel-left text-xl text-[var(--text-secondary)]"></div>
                    </button>
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[var(--accent-blue)] to-[var(--accent-purple)] flex items-center justify-center mb-4">
                        <span className="text-sm font-semibold text-white">JD</span>
                    </div>
                    <div className="flex-1"></div>
                </div>
            );
        }

        return (
            <div className="w-[var(--sidebar-width)] h-full bg-[var(--bg-secondary)] border-r border-[var(--border-color)] flex flex-col" data-name="sidebar" data-file="components/Sidebar.js">
                <div className="flex items-center justify-between px-4 py-3">
                    <span className="text-lg font-semibold bg-gradient-to-r from-[var(--accent-blue)] to-[var(--accent-purple)] bg-clip-text text-transparent">Ichin</span>
                    <button onClick={onToggle} className="p-1.5 rounded-lg hover:bg-[var(--bg-hover)] transition-smooth">
                        <div className="icon-panel-left text-lg text-[var(--text-secondary)]"></div>
                    </button>
                </div>
                <UserProfile />
                <WorkspaceSwitcher workspaces={WORKSPACES} activeWorkspace={activeWorkspace} onSelect={onWorkspaceSelect} />
                <SearchBar onOpenCommand={onOpenCommand} />
                <div className="flex-1 overflow-y-auto scrollbar-thin">
                    <TabSection title="Pinned" icon="pin" tabs={pinnedTabs} activeTab={activeTab} onTabClick={onTabClick} onTabClose={onTabClose} />
                    <TabSection title="Tabs" icon="layers" tabs={activeTabs} activeTab={activeTab} onTabClick={onTabClick} onTabClose={onTabClose} />
                    <div className="px-3 py-2 border-t border-[var(--border-color)] mt-2">
                        <p className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-2 px-1">Favorites</p>
                        {FAVORITES.map((fav) => (
                            <div key={fav.id} className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-[var(--bg-tertiary)] cursor-pointer transition-smooth">
                                <div className={`${fav.icon} text-base text-[var(--text-secondary)]`}></div>
                                <span className="text-sm text-[var(--text-primary)]">{fav.title}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    } catch (error) {
        console.error('Sidebar error:', error);
        return null;
    }
}