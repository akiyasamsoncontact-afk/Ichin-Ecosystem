const DateUtils = {
    getMonthDays: (year, month) => {
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const days = [];
        const startPad = firstDay.getDay();
        for (let i = startPad - 1; i >= 0; i--) {
            days.push({ date: new Date(year, month, -i), isCurrentMonth: false });
        }
        for (let i = 1; i <= lastDay.getDate(); i++) {
            days.push({ date: new Date(year, month, i), isCurrentMonth: true });
        }
        const remaining = 42 - days.length;
        for (let i = 1; i <= remaining; i++) {
            days.push({ date: new Date(year, month + 1, i), isCurrentMonth: false });
        }
        return days;
    },
    getWeekDays: (date) => {
        const start = new Date(date);
        start.setDate(start.getDate() - start.getDay());
        return Array.from({ length: 7 }, (_, i) => {
            const d = new Date(start);
            d.setDate(start.getDate() + i);
            return d;
        });
    },
    formatDate: (date) => date.toISOString().split('T')[0],
    isSameDay: (d1, d2) => DateUtils.formatDate(d1) === DateUtils.formatDate(d2),
    isToday: (date) => DateUtils.isSameDay(date, new Date()),
    monthNames: ['January','February','March','April','May','June','July','August','September','October','November','December'],
    dayNames: ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
};