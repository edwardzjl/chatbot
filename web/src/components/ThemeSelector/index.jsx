import styles from "./index.module.css";

import PropTypes from "prop-types";

import BrightnessMediumIcon from "@mui/icons-material/BrightnessMedium";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";

import { Dropdown, DropdownButton, DropdownMenu } from "@/components/DropdownMenu";
import { useTheme } from "@/hooks/useTheme";


const ThemeIcon = ({ theme }) => {
    switch (theme) {
    case "light":
        return <LightModeIcon />;
    case "dark":
        return <DarkModeIcon />;
    default:
        return <BrightnessMediumIcon />;
    }
};
ThemeIcon.propTypes = {
    theme: PropTypes.string,
};


const ThemeSelector = () => {
    const { theme, setTheme } = useTheme();

    return (
        <Dropdown>
            <DropdownButton className={styles.themeMenuTitle} title="Change Theme" aria-label="Change Theme">
                <ThemeIcon theme={theme} />
                <span className={styles.themeMenuText}>Theme</span>
            </DropdownButton>
            <DropdownMenu className={styles.themeMenuList}>
                <li>
                    <button
                        className={`${styles.themeMenuItem} ${theme === "system" && styles.selected}`}
                        onClick={() => setTheme("system")}
                        title="Use system theme"
                        aria-label="Use system theme"
                    >
                        <BrightnessMediumIcon />
                        <span className={styles.themeMenuText}>OS Default</span>
                    </button>
                </li>
                <li>
                    <button
                        className={`${styles.themeMenuItem} ${theme === "light" && styles.selected}`}
                        onClick={() => setTheme("light")}
                        title="Use light theme"
                        aria-label="Use light theme"
                    >
                        <LightModeIcon />
                        <span className={styles.themeMenuText}>Light</span>
                    </button>
                </li>
                <li>
                    <button
                        className={`${styles.themeMenuItem} ${theme === "dark" && styles.selected}`}
                        onClick={() => setTheme("dark")}
                        title="Use dark theme"
                        aria-label="Use dark theme"
                    >
                        <DarkModeIcon />
                        <span className={styles.themeMenuText}>Dark</span>
                    </button>
                </li>
            </DropdownMenu>
        </Dropdown>
    );
};

export default ThemeSelector;
