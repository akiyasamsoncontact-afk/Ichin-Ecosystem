function CommandPalette({ isOpen, onClose }) {
    try {
        const [query, setQuery] = React.useState('');

        React.useEffect(() => {
            const handleKeyDown = (e) => {
                if (e.key === 'Escape') onClose();
            };
            if (isOpen) document.addEventListener('keydown', handleKeyDown);
            return () => document.removeEventListener('keydown', handleKeyDown);
        }, [isOpen, onClose]);

        if (!isOpen) return null;

        const commands = [
            { id: 'new-tab', label: 'New Tab', icon: 'plus', shortcut: '⌘T' },
            { id: 'new-window', label: 'New Window', icon: 'square', shortcut: '⌘N' },
            { id: 'close-tab', label: 'Close Tab', icon: 'x', shortcut: '⌘W' },
            { id: 'split-view', label: 'Toggle Split View', icon: 'columns-2', shortcut: '⌘\\' },
            { id: 'settings', label: 'Settings', icon: 'settings', shortcut: '⌘,' },
            { id: 'history', label: 'History', icon: 'clock', shortcut: '⌘Y' },
        ].filter(cmd => cmd.label.toLowerCase().includes(query.toLowerCase()));

        return (
            <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]" onClick={onClose} data-name="command-palette" data-file="components/CommandPalette.js">
                <div className="absolute inset-0 bg-black bg-opacity-60 backdrop-blur-sm"></div>
                <div className="relative w-full max-w-xl glass rounded-2xl shadow-2xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center gap-3 px-4 py-4 border-b border-[var(--border-color)]">
                        <div className="icon-search text-xl text-[var(--text-muted)]"></div>
                        <input
                            autoFocus
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Type a command or search..."
                            className="flex-1 bg-transparent text-lg text-[var(--text-primary)] outline-none placeholder-[var(--text-muted)]"
                        />
                    </div>
                    <div className="max-h-80 overflow-y-auto scrollbar-thin">
                        {commands.map((cmd) => (
                            <div key={cmd.id} className="flex items-center gap-3 px-4 py-3 hover:bg-[var(--bg-hover)] cursor-pointer transition-smooth">
                                <div className={`icon-${cmd.icon} text-lg text-[var(--text-secondary)]`}></div>
                                <span className="flex-1 text-sm text-[var(--text-primary)]">{cmd.label}</span>
                                <kbd className="px-2 py-1 rounded bg-[var(--bg-tertiary)] text-xs text-[var(--text-muted)]">{cmd.shortcut}</kbd>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    } catch (error) {
        console.error('CommandPalette error:', error);
        return null;
    }
}