function EmailView({ email, onClose, onAction }) {
    try {
        const [loading, setLoading] = React.useState(false);

        if (!email) {
            return (
                <div className="flex-1 flex items-center justify-center bg-[var(--bg-primary)]">
                    <div className="text-center text-[var(--text-secondary)]">
                        <div className="icon-mail text-5xl mb-4 opacity-30"></div>
                        <p>Select an email to read</p>
                    </div>
                </div>
            );
        }

        const formatDate = (timestamp) => {
            return new Date(timestamp).toLocaleString('en-US', {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: '2-digit'
            });
        };

        const handleAction = async (action) => {
            setLoading(true);
            try {
                await api.messageAction(email.id, action);
                if (onAction) onAction();
                onClose();
            } catch (err) {
                console.error('Action failed:', err);
            }
            setLoading(false);
        };

        const handleStar = async () => {
            try {
                await api.toggleStar(email.id);
                if (onAction) onAction();
            } catch (err) {
                console.error('Star failed:', err);
            }
        };

        return (
            <div className="flex-1 flex flex-col bg-[var(--bg-primary)] overflow-hidden">
                <div className="flex items-center justify-between p-4 border-b border-[var(--border-color)]">
                    <div className="flex items-center gap-2">
                        <button onClick={() => handleAction('archive')} disabled={loading} title="Archive" className="p-2 rounded-lg hover:bg-[var(--bg-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
                            <div className="icon-archive text-lg"></div>
                        </button>
                        <button onClick={() => handleAction('trash')} disabled={loading} title="Trash" className="p-2 rounded-lg hover:bg-[var(--bg-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
                            <div className="icon-trash-2 text-lg"></div>
                        </button>
                    </div>
                    <div className="flex items-center gap-2">
                        <button onClick={handleStar} className="p-2 rounded-lg hover:bg-[var(--bg-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
                            <div className={`${email.starred ? 'icon-star text-yellow-500' : 'icon-star'} text-lg`}></div>
                        </button>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-6">
                    <h1 className="text-2xl font-semibold text-[var(--text-primary)] mb-4">{email.subject}</h1>

                    <div className="flex items-start gap-4 mb-6">
                        <div className="w-12 h-12 rounded-full bg-[var(--accent)] flex items-center justify-center text-white font-medium">{email.sender.avatar}</div>
                        <div className="flex-1">
                            <div className="flex items-center gap-2">
                                <span className="font-medium text-[var(--text-primary)]">{email.sender.name}</span>
                                <span className="text-sm text-[var(--text-secondary)]">&lt;{email.sender.email}&gt;</span>
                            </div>
                            <p className="text-sm text-[var(--text-secondary)]">To: {email.to.map(r => r.email).join(', ')}</p>
                            <p className="text-sm text-[var(--text-secondary)]">{formatDate(email.timestamp)}</p>
                        </div>
                    </div>

                    <div className="prose prose-invert max-w-none text-[var(--text-primary)] whitespace-pre-wrap">{email.body}</div>

                    {email.attachments.length > 0 && (
                        <div className="mt-6 pt-6 border-t border-[var(--border-color)]">
                            <h3 className="text-sm font-medium text-[var(--text-secondary)] mb-3">Attachments ({email.attachments.length})</h3>
                            <div className="flex flex-wrap gap-3">
                                {email.attachments.map((att, i) => (
                                    <div key={i} className="flex items-center gap-3 p-3 bg-[var(--bg-surface)] rounded-lg border border-[var(--border-color)]">
                                        <div className="icon-file text-[var(--accent)] text-xl"></div>
                                        <div>
                                            <p className="text-sm font-medium text-[var(--text-primary)]">{att.name}</p>
                                            <p className="text-xs text-[var(--text-secondary)]">{att.size}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        );
    } catch (error) {
        console.error('EmailView error:', error);
        return null;
    }
}
