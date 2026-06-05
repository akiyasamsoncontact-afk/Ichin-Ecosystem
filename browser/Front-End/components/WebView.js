import { isValidIchinUrl, sanitizeUrl } from '../utils/urlValidator';

function WebView({ url, title }) {
    try {
        // Validate and sanitize the URL to ensure Ichin-only access
        const safeUrl = isValidIchinUrl(url) ? url : sanitizeUrl(url);
        
        return (
            <div className="flex-1 bg-[var(--bg-primary)] rounded-tl-2xl overflow-hidden" data-name="webview" data-file="components/WebView.js">
                <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-[var(--bg-secondary)] to-[var(--bg-primary)]">
                    <div className="w-20 h-20 rounded-2xl bg-[var(--bg-tertiary)] flex items-center justify-center mb-6 shadow-2xl">
                        <div className="icon-globe text-4xl text-[var(--accent-blue)]"></div>
                    </div>
                    <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-2">{title}</h2>
                    <p className="text-sm text-[var(--text-muted)] mb-6">{safeUrl}</p>
                    <div className="flex items-center gap-4">
                        <div className="px-4 py-2 rounded-lg bg-[var(--bg-tertiary)] text-sm text-[var(--text-secondary)]">
                            Preview Mode
                        </div>
                    </div>
                </div>
            </div>
        );
    } catch (error) {
        console.error('WebView error:', error);
        return null;
    }
}