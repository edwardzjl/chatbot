import styles from "./index.module.css";

import { useContext } from "react";
import PropTypes from "prop-types";

import BrightnessMediumIcon from "@mui/icons-material/BrightnessMedium";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";

import { Dropdown, DropdownButton, DropdownMenu } from "@/components/DropdownMenu";
import { ThemeContext } from "@/contexts/theme";


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
    const { theme, setTheme } = useContext(ThemeContext);

    return (
        <Dropdown>
            <DropdownButton className={styles.themeMenuTitle}>
                <ThemeIcon theme={theme} />
                <span className={styles.themeMenuText}>Theme</span>
            </DropdownButton>
            <DropdownMenu className={styles.themeMenuList}>
                <li>
                    <button
                        className={`${styles.themeMenuItem} ${theme === "system" && styles.selected}`}
                        onClick={() => setTheme("system")}
                        aria-label="Set theme to system default"
                    >
                        <BrightnessMediumIcon />
                        <span className={styles.themeMenuText}>OS Default</span>
                    </button>
                </li>
                <li>
                    <button
                        className={`${styles.themeMenuItem} ${theme === "light" && styles.selected}`}
                        onClick={() => setTheme("light")}
                        aria-label="Set theme to light mode"
                    >
                        <LightModeIcon />
                        <span className={styles.themeMenuText}>Light</span>
                    </button>
                </li>
                <li>
                    <button
                        className={`${styles.themeMenuItem} ${theme === "dark" && styles.selected}`}
                        onClick={() => setTheme("dark")}
                        aria-label="Set theme to dark mode"
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
