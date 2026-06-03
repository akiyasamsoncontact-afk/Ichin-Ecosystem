function ComposeModal({ isOpen, onClose, onSent }) {
    try {
        const [to, setTo] = React.useState('');
        const [cc, setCc] = React.useState('');
        const [subject, setSubject] = React.useState('');
        const [body, setBody] = React.useState('');
        const [showCc, setShowCc] = React.useState(false);
        const [sending, setSending] = React.useState(false);
        const [error, setError] = React.useState(null);

        if (!isOpen) return null;

        const handleSend = async () => {
            if (!to.trim()) {
                setError('Please enter at least one recipient');
                return;
            }
            if (!subject.trim()) {
                setError('Please enter a subject');
                return;
            }
            setSending(true);
            setError(null);
            try {
                const recipients = to.split(',').map(r => r.trim()).filter(Boolean);
                const result = await api.sendMessage({
                    to: recipients,
                    subject: subject.trim(),
                    body: body.trim(),
                    from: 'me@ichin.network',
                });
                console.log('Message sent:', result);
                setTo('');
                setCc('');
                setSubject('');
                setBody('');
                setShowCc(false);
                if (onSent) onSent();
                onClose();
            } catch (err) {
                console.error('Send failed:', err);
                setError(err.message || 'Failed to send message');
            }
            setSending(false);
        };

        return (
            <div className="fixed inset-0 bg-black/50 flex items-end justify-center sm:items-center z-50">
                <div className="w-full max-w-2xl bg-[var(--bg-surface)] rounded-t-xl sm:rounded-xl shadow-2xl flex flex-col max-h-[90vh]">
                    <div className="flex items-center justify-between p-4 border-b border-[var(--border-color)]">
                        <h2 className="font-semibold text-[var(--text-primary)]">New Message</h2>
                        <button onClick={onClose} className="p-1 rounded hover:bg-[var(--bg-hover)]">
                            <div className="icon-x text-[var(--text-secondary)] text-xl"></div>
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                        {error && (
                            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">{error}</div>
                        )}
                        <div className="flex items-center gap-2">
                            <label className="w-12 text-sm text-[var(--text-secondary)]">To:</label>
                            <input
                                type="text"
                                value={to}
                                onChange={(e) => setTo(e.target.value)}
                                placeholder="recipient@example.com"
                                className="flex-1 bg-transparent border-b border-[var(--border-color)] py-1 text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
                            />
                            {!showCc && <button onClick={() => setShowCc(true)} className="text-sm text-[var(--accent)]">Cc/Bcc</button>}
                        </div>

                        {showCc && (
                            <div className="flex items-center gap-2">
                                <label className="w-12 text-sm text-[var(--text-secondary)]">Cc:</label>
                                <input type="email" value={cc} onChange={(e) => setCc(e.target.value)} className="flex-1 bg-transparent border-b border-[var(--border-color)] py-1 text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]" />
                            </div>
                        )}

                        <div className="flex items-center gap-2">
                            <label className="w-12 text-sm text-[var(--text-secondary)]">Subject:</label>
                            <input type="text" value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Subject" className="flex-1 bg-transparent border-b border-[var(--border-color)] py-1 text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]" />
                        </div>

                        <textarea value={body} onChange={(e) => setBody(e.target.value)} placeholder="Write your message..." className="w-full h-64 bg-transparent text-[var(--text-primary)] resize-none focus:outline-none mt-4" />
                    </div>

                    <div className="flex items-center justify-between p-4 border-t border-[var(--border-color)]">
                        <div className="flex items-center gap-2">
                            <button disabled className="p-2 rounded-lg text-[var(--text-secondary)] opacity-50">
                                <div className="icon-paperclip text-lg"></div>
                            </button>
                        </div>
                        <div className="flex items-center gap-2">
                            <button onClick={onClose} className="px-4 py-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)]">Discard</button>
                            <button onClick={handleSend} disabled={sending} className="btn-primary flex items-center gap-2 disabled:opacity-50">
                                <div className={`${sending ? 'icon-loader-2 animate-spin' : 'icon-send'} text-lg`}></div>
                                <span>{sending ? 'Sending...' : 'Send'}</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    } catch (error) {
        console.error('ComposeModal error:', error);
        return null;
    }
}
