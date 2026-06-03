const mockEmails = [
    {
        id: '1',
        sender: { name: 'Alex Chen', email: 'alex@ichin.network', avatar: 'AC' },
        to: [{ name: 'You', email: 'me@ichin.network' }],
        subject: 'Q2 Financial Report Ready for Review',
        preview: 'Hi team, the quarterly financial report is now ready for your review...',
        body: 'Hi team,\n\nThe quarterly financial report is now ready for your review. Please take a look at the attached document and let me know if you have any questions.\n\nBest regards,\nAlex',
        timestamp: '2026-06-02T09:30:00',
        unread: true,
        starred: false,
        attachments: [{ name: 'Q2_Report.pdf', size: '2.4 MB' }],
        folder: 'inbox'
    },
    {
        id: '2',
        sender: { name: 'Sarah Kim', email: 'sarah@ichin.network', avatar: 'SK' },
        to: [{ name: 'You', email: 'me@ichin.network' }],
        subject: 'Meeting Tomorrow at 3 PM',
        preview: 'Just a reminder about our meeting tomorrow to discuss the new project...',
        body: 'Hi,\n\nJust a reminder about our meeting tomorrow at 3 PM to discuss the new project timeline.\n\nSee you then!\nSarah',
        timestamp: '2026-06-02T08:15:00',
        unread: true,
        starred: true,
        attachments: [],
        folder: 'inbox'
    },
    {
        id: '3',
        sender: { name: 'Dev Team', email: 'dev@ichin.network', avatar: 'DT' },
        to: [{ name: 'You', email: 'me@ichin.network' }],
        subject: 'System Update Scheduled',
        preview: 'We will be performing scheduled maintenance on the servers this weekend...',
        body: 'Dear users,\n\nWe will be performing scheduled maintenance on the servers this weekend. Expected downtime is 2 hours.\n\nThank you for your patience.',
        timestamp: '2026-06-01T16:45:00',
        unread: false,
        starred: false,
        attachments: [],
        folder: 'inbox'
    },
    {
        id: '4',
        sender: { name: 'Michael Torres', email: 'michael@ichin.network', avatar: 'MT' },
        to: [{ name: 'You', email: 'me@ichin.network' }],
        subject: 'Design Assets Attached',
        preview: 'Here are the design assets you requested for the landing page...',
        body: 'Hi,\n\nHere are the design assets you requested for the landing page redesign. Let me know if you need any modifications.\n\nCheers,\nMichael',
        timestamp: '2026-06-01T14:20:00',
        unread: false,
        starred: false,
        attachments: [{ name: 'designs.zip', size: '15.8 MB' }, { name: 'mockups.fig', size: '8.2 MB' }],
        folder: 'inbox'
    }
];