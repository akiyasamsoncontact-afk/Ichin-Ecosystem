function WorkspaceSwitcher({ workspaces, activeWorkspace, onSelect }) {
    try {
        return (
            <div className="p-3 border-b border-[var(--border-color)]" data-name="workspace-switcher" data-file="components/WorkspaceSwitcher.js">
                <p className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-2 px-1">Workspaces</p>
                <div className="flex gap-2">
                    {workspaces.map((ws) => (
                        <button
                            key={ws.id}
                            onClick={() => onSelect(ws.id)}
                            className={`w-10 h-10 rounded-xl flex items-center justify-center transition-smooth ${
                                activeWorkspace === ws.id ? 'ring-2 ring-offset-2 ring-offset-[var(--bg-secondary)]' : 'hover:scale-105'
                            }`}
                            style={{ 
                                backgroundColor: ws.color + '20',
                                ringColor: ws.color 
                            }}
                            title={ws.name}
                        >
                            <div className={`icon-${ws.icon} text-lg`} style={{ color: ws.color }}></div>
                        </button>
                    ))}
                    <button className="w-10 h-10 rounded-xl flex items-center justify-center bg-[var(--bg-tertiary)] hover:bg-[var(--bg-hover)] transition-smooth">
                        <div className="icon-plus text-lg text-[var(--text-muted)]"></div>
                    </button>
                </div>
            </div>
        );
    } catch (error) {
        console.error('WorkspaceSwitcher error:', error);
        return null;
    }
}