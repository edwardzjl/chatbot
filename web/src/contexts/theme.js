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
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        localStorage.setItem("theme", "dark");
        return "dark";
    }
    localStorage.setItem("theme", "light");
    return "light";
};

export const ThemeProvider = ({ children }) => {
    const [theme, setTheme] = useState(getTheme);

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
