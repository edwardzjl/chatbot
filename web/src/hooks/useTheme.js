import { useState, useEffect } from "react";
import { darcula, googlecode } from "react-syntax-highlighter/dist/esm/styles/hljs";

/**
 * Check if dark theme should be applied based on current state
 *
 * @returns {boolean} true if dark theme should be applied
 *
 * IMPORTANT: This function replicates the EXACT logic from HTML head script:
 * localStorage.theme === "dark" ||
 * (!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches)
 */
const shouldUseDarkTheme = () => {
    return localStorage.theme === "dark" ||
        (!("theme" in localStorage) && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
};

/**
 * Get current theme setting from localStorage
 *
 * @returns {string} "light", "dark", or "system"
 *
 * Logic matches HTML head script:
 * - If localStorage.theme exists → return its value
 * - If localStorage.theme doesn't exist → return "system" (follow OS)
 */
const getTheme = () => {
    const theme = localStorage.getItem("theme");
    return theme || "system";
};

/**
 * Get effective theme (actually applied theme)
 *
 * @param {string} theme - User's preference: "light", "dark", or "system"
 * @returns {string} Always "light" or "dark" (never "system")
 *
 * This function resolves "system" to an actual theme by checking OS preference.
 * Uses the same logic as HTML head script to ensure consistency.
 */
const getEffectiveTheme = (theme) => {
    if (theme === "dark") return "dark";
    if (theme === "light") return "light";

    // For "system" theme, use the same logic as HTML head script
    return shouldUseDarkTheme() ? "dark" : "light";
};

/**
 * Update HTML document's dark class
 *
 * @param {string} theme - User's theme preference
 *
 * This function:
 * 1. Resolves the theme to actual "light" or "dark"
 * 2. Adds/removes "dark" class on <html> element
 * 3. Works together with CSS that uses .dark selector
 *
 * Why needed:
 * - HTML head script only runs once on page load
 * - Runtime theme changes need manual DOM updates
 * - Keeps DOM in sync with React state
 */
const updateDocumentTheme = (theme) => {
    const effectiveTheme = getEffectiveTheme(theme);
    document.documentElement.classList.toggle("dark", effectiveTheme === "dark");
};

/**
 * Get code syntax highlighting theme
 *
 * @param {string} theme - User's theme preference
 * @returns {Object} Theme object for react-syntax-highlighter
 *
 * Maps effective theme to highlighting styles:
 * - Dark theme → darcula (dark syntax highlighting)
 * - Light theme → googlecode (light syntax highlighting)
 */
const getCodeTheme = (theme) => {
    const effectiveTheme = getEffectiveTheme(theme);
    return effectiveTheme === "dark" ? darcula : googlecode;
};

/**
 * Simplified theme hook
 *
 * This hook manages theme state and keeps it synchronized with:
 * 1. localStorage (for persistence)
 * 2. HTML document class (for CSS styling)
 * 3. Code highlighting theme (for syntax highlighting)
 * 4. System theme changes (when user selects "follow system")
 * 5. Cross-tab synchronization (when theme changes in other tabs)
 */
export const useTheme = () => {
    // State: user's theme preference ("light" | "dark" | "system")
    const [theme, setThemeState] = useState(getTheme);

    // State: code highlighting theme object (darcula for dark, googlecode for light)
    const [codeTheme, setCodeTheme] = useState(() => getCodeTheme(getTheme()));

    /**
     * Set theme function
     *
     * @param {string} newTheme - "light" | "dark" | "system"
     *
     * Logic:
     * - "system": Remove theme from localStorage (so HTML head script treats it as system default)
     * - Other themes: Store in localStorage for persistence
     *
     * Note: This function only updates React state and localStorage.
     * The actual DOM update happens in the useEffect below.
     */
    const setTheme = (newTheme) => {
        if (newTheme === "system") {
            // Remove from localStorage so HTML head script uses system default
            localStorage.removeItem("theme");
        } else {
            // Store explicit theme choice
            localStorage.setItem("theme", newTheme);
        }
        // Update React state (this will trigger the first useEffect)
        setThemeState(newTheme);
    };

    /**
     * Effect 1: Handle theme changes
     *
     * Triggers when: theme state changes (user selects different theme)
     *
     * Purpose:
     * - Update HTML document class (add/remove "dark" class on <html>)
     * - Update code highlighting theme to match
     *
     * Why needed:
     * - HTML head script only runs once on page load
     * - When user changes theme, we need to manually update DOM
     * - Keeps HTML class in sync with React state
     */
    useEffect(() => {
        updateDocumentTheme(theme);
        setCodeTheme(getCodeTheme(theme));
    }, [theme]);

    /**
     * Effect 2: Handle system theme changes
     *
     * Triggers when: theme state changes
     * Active only when: theme === "system"
     *
     * Purpose:
     * - Listen for system theme changes (light/dark mode toggle in OS)
     * - Update app theme automatically when system theme changes
     *
     * Why needed:
     * - When user selects "follow system", app should respond to OS theme changes
     * - localStorage doesn't change (still empty = "system")
     * - React state doesn't change (still "system")
     * - Only way to detect change is via matchMedia listener
     * - Without this, changing OS theme wouldn't update the app
     *
     * Example scenario:
     * 1. User selects "OS Default" in app
     * 2. User goes to OS settings and switches light → dark
     * 3. This listener detects the change and updates app theme
     */
    useEffect(() => {
        if (theme === "system") {
            const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
            const handleChange = () => {
                // Re-evaluate system preference and update DOM
                updateDocumentTheme(theme);
                setCodeTheme(getCodeTheme(theme));
            };

            mediaQuery.addEventListener("change", handleChange);
            return () => mediaQuery.removeEventListener("change", handleChange);
        }
    }, [theme]);

    /**
     * Effect 3: Handle cross-tab synchronization
     *
     * Triggers: Only on mount (empty dependency array)
     * Listens for: localStorage changes from other browser tabs
     *
     * Purpose:
     * - Keep theme synchronized across multiple tabs of the same app
     * - When user changes theme in Tab A, Tab B should update automatically
     *
     * How it works:
     * - Browser fires 'storage' event when localStorage changes in other tabs
     * - We check if the changed key is 'theme' (or null for localStorage.clear())
     * - Read the new theme value and update React state
     * - This triggers Effect 1 above, which updates DOM and code theme
     *
     * Note: 'storage' event only fires for changes from OTHER tabs, not current tab
     */
    useEffect(() => {
        const handleStorageChange = (e) => {
            if (e.key === "theme" || e.key === null) {
                const newTheme = getTheme();
                setThemeState(newTheme);
            }
        };

        window.addEventListener("storage", handleStorageChange);
        return () => window.removeEventListener("storage", handleStorageChange);
    }, []);

    // Return public API
    return {
        theme,        // User's preference: "light" | "dark" | "system"
        codeTheme,    // Code highlighting theme object
        setTheme      // Function to change theme
    };
};
