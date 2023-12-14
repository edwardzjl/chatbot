import { createContext, useEffect, useState } from "react";

export const ThemeContext = createContext({
    theme: "",
    setTheme: () => { },
});

const getTheme = () => {
    const theme = localStorage.getItem("theme");
    if (theme) {
        return theme;
    }
    return "system";
};

export const ThemeProvider = ({ children }) => {
    // "light", "dark", "system"
    const [theme, setTheme] = useState(getTheme());

    useEffect(() => {
        const refreshTheme = () => {
            localStorage.setItem("theme", theme);
        };
        refreshTheme();
    }, [theme]);

    return (
        <ThemeContext.Provider value={{ theme, setTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}
