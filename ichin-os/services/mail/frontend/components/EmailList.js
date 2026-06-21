function EmailList({ emails, selectedEmail, setSelectedEmail, searchQuery, filter }) {
    try {
        const formatTime = (timestamp) => {
            const date = new Date(timestamp);
            const now = new Date();
            if (date.toDateString() === now.toDateString()) {
                return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
            }
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        };

        const filteredEmails = emails.filter(email => {
            const matchesSearch = !searchQuery ||
                email.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
                email.sender.name.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesFilter = filter === 'all' ||
                (filter === 'unread' && email.unread) ||
                (filter === 'starred' && email.starred) ||
                (filter === 'attachments' && email.attachments.length > 0);
            return matchesSearch && matchesFilter;
        });

        if (emails.length === 0) {
            return (
                <div className="flex-1 flex flex-col bg-[var(--bg-surface)] border-r border-[var(--border-color)] w-80">
                    <div className="flex-1 flex items-center justify-center text-[var(--text-secondary)]">
                        <div className="text-center">
                            <div className="icon-inbox text-4xl mb-2 opacity-30"></div>
                            <p className="text-sm">No messages</p>
                        </div>
                    </div>
                </div>
            );
        }

        return (
            <div className="h-full flex flex-col bg-[var(--bg-surface)] border-r border-[var(--border-color)] w-80">
                <div className="flex-1 overflow-y-auto">
                    {filteredEmails.map(email => (
                        <div
                            key={email.id}
                            onClick={() => setSelectedEmail(email)}
                            className={`email-item ${email.unread ? 'unread' : ''} ${selectedEmail?.id === email.id ? 'bg-[var(--bg-hover)]' : ''}`}
                        >
                            <div className="flex items-start gap-3">
                                <div className="w-10 h-10 rounded-full bg-[var(--accent)] flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
                                    {email.sender.avatar}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between">
                                        <span className={`text-sm ${email.unread ? 'font-semibold text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}`}>{email.sender.name}</span>
                                        <span className="text-xs text-[var(--text-secondary)]">{formatTime(email.timestamp)}</span>
                                    </div>
                                    <p className={`text-sm truncate ${email.unread ? 'font-medium text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}`}>{email.subject}</p>
                                    <p className="text-xs text-[var(--text-secondary)] truncate mt-1">{email.preview}</p>
                                </div>
                            </div>
                            {(email.starred || email.attachments.length > 0) && (
                                <div className="flex items-center gap-2 mt-2 ml-13">
                                    {email.starred && <div className="icon-star text-yellow-500 text-sm"></div>}
                                    {email.attachments.length > 0 && <div className="icon-paperclip text-[var(--text-secondary)] text-sm"></div>}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        );
    } catch (error) {
        console.error('EmailList error:', error);
        return null;
    }
}
