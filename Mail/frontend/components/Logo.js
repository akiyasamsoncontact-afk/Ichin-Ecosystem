function Logo({ collapsed }) {
    try {
        return (
            <div className="flex items-center gap-2 px-3 py-4" data-name="logo" data-file="components/Logo.js">
                <div className="w-8 h-8 bg-[var(--accent)] rounded-lg flex items-center justify-center">
                    <div className="icon-mail text-white text-lg"></div>
                </div>
                {!collapsed && (
                    <span className="font-semibold text-lg text-[var(--text-primary)]">Ichin Mail</span>
                )}
            </div>
        );
    } catch (error) {
        console.error('Logo component error:', error);
        return null;
    }
}