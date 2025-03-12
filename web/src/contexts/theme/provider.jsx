import { useEffect, useState } from "react";
import PropTypes from "prop-types";

import { ThemeContext } from "./index";


/**
 * Retrieves the current theme from localStorage.
 * 
 * This function checks if a theme is stored in the browser's localStorage under the key "theme".
 * If a theme is found, it returns the stored value. Otherwise, it returns the default value "system".
 * 
 * @returns {string} The theme stored in localStorage if present, otherwise the default theme "system".
 */
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
};

ThemeProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
