import { useEffect, useState } from "react";
import PropTypes from "prop-types";

import { darcula, googlecode } from "react-syntax-highlighter/dist/esm/styles/hljs";

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

/**
 * Get code syntax highlight theme based on the current theme.
 *
 * @param {string} theme "dark", "light" or "system"
 *
 * @returns {*} code theme, darcula or googlecode
 */
const getCodeTheme = (theme) => {
    switch (theme) {
    case "dark":
        return darcula;
    case "light":
        return googlecode;
    default: {  // "system"
        if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
            return darcula;
        }
        return googlecode;
    }
    }
};

export const ThemeProvider = ({ children }) => {
    // "light", "dark", "system"
    const [theme, setTheme] = useState(getTheme());
    const [codeTheme, setCodeTheme] = useState(getCodeTheme(theme));

    // Flush the theme to localStorage
    useEffect(() => {
        localStorage.setItem("theme", theme);
    }, [theme]);

    // Update code theme based on the current theme
    useEffect(() => {
        setCodeTheme(getCodeTheme(theme));
    }, [theme]);

    return (
        <ThemeContext.Provider value={{ theme, codeTheme, setTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

ThemeProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
