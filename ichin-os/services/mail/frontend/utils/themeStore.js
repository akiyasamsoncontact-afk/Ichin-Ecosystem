const useThemeStore = () => {
    const [theme, setThemeState] = React.useState(() => {
        const saved = localStorage.getItem('ichin-theme');
        return saved || 'dark';
    });

    const setTheme = (newTheme) => {
        setThemeState(newTheme);
        localStorage.setItem('ichin-theme', newTheme);
    };

    React.useEffect(() => {
        document.documentElement.classList.toggle('light-mode', theme === 'light');
    }, [theme]);

    return { theme, setTheme };
};