function Sidebar({ activeFolder, setActiveFolder, collapsed, setCollapsed, onCompose, unreadCounts }) {
    try {
        const folders = [
            { id: 'inbox', name: 'Inbox', icon: 'icon-inbox', count: unreadCounts?.inbox || 0 },
            { id: 'sent', name: 'Sent', icon: 'icon-send' },
            { id: 'drafts', name: 'Drafts', icon: 'icon-file-text' },
            { id: 'archive', name: 'Archive', icon: 'icon-archive' },
            { id: 'trash', name: 'Trash', icon: 'icon-trash-2' },
            { id: 'spam', name: 'Spam', icon: 'icon-circle-alert' },
        ];

        return (
            <div className={`h-full bg-[var(--bg-surface)] border-r border-[var(--border-color)] flex flex-col transition-all ${collapsed ? 'w-16' : 'w-56'}`}>
                <div className="flex items-center justify-between pr-2">
                    <Logo collapsed={collapsed} />
                    <button onClick={() => setCollapsed(!collapsed)} className="p-1 rounded hover:bg-[var(--bg-hover)]">
                        <div className={`${collapsed ? 'icon-chevron-right' : 'icon-chevron-left'} text-[var(--text-secondary)]`}></div>
                    </button>
                </div>

                <div className="px-3 py-2">
                    <button onClick={onCompose} className={`btn-primary w-full flex items-center justify-center gap-2 ${collapsed ? 'px-2' : ''}`}>
                        <div className="icon-plus text-lg"></div>
                        {!collapsed && <span>Compose</span>}
                    </button>
                </div>

                <nav className="flex-1 px-2 py-2 space-y-1">
                    {folders.map(folder => (
                        <div key={folder.id} onClick={() => setActiveFolder(folder.id)} className={`sidebar-item ${activeFolder === folder.id ? 'active' : ''}`}>
                            <div className={`${folder.icon} text-lg`}></div>
                            {!collapsed && (
                                <>
                                    <span className="flex-1">{folder.name}</span>
                                    {folder.count > 0 && <span className="text-xs bg-[var(--accent)] text-white px-2 py-0.5 rounded-full">{folder.count}</span>}
                                </>
                            )}
                        </div>
                    ))}
                </nav>

                <div className="px-2 py-2 border-t border-[var(--border-color)]">
                    <a href="settings.html" className="sidebar-item">
                        <div className="icon-settings text-lg"></div>
                        {!collapsed && <span>Settings</span>}
                    </a>
                </div>
            </div>
        );
    } catch (error) {
        console.error('Sidebar error:', error);
        return null;
    }
}
