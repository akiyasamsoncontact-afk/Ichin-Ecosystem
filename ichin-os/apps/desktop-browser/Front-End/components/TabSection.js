function TabSection({ title, tabs, activeTab, onTabClick, onTabClose, icon }) {
    try {
        if (tabs.length === 0) return null;

        return (
            <div className="px-3 py-2" data-name="tab-section" data-file="components/TabSection.js">
                <div className="flex items-center gap-2 mb-2 px-1">
                    <div className={`icon-${icon} text-xs text-[var(--text-muted)]`}></div>
                    <p className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">{title}</p>
                    <span className="text-xs text-[var(--text-muted)]">({tabs.length})</span>
                </div>
                <div className="space-y-0.5">
                    {tabs.map((tab) => (
                        <TabItem
                            key={tab.id}
                            tab={tab}
                            isActive={activeTab === tab.id}
                            onClick={() => onTabClick(tab.id)}
                            onClose={onTabClose}
                        />
                    ))}
                </div>
            </div>
        );
    } catch (error) {
        console.error('TabSection error:', error);
        return null;
    }
}