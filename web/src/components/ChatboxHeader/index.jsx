import styles from "./index.module.css";

import { useContext } from "react";
import PropTypes from "prop-types";

import Avatar from "@mui/material/Avatar";

import BrightnessMediumIcon from "@mui/icons-material/BrightnessMedium";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";

import { Dropdown, DropdownButton, DropdownMenu } from "@/components/DropdownMenu";
import { ThemeContext } from "@/contexts/theme";
import { UserContext } from "@/contexts/user";


const ThemeIcon = ({ theme }) => {
    switch (theme) {
        case "light":
            return <LightModeIcon />;
        case "dark":
            return <DarkModeIcon />;
        default:
            return <BrightnessMediumIcon />;
    }
}
ThemeIcon.propTypes = {
    theme: PropTypes.string,
};


const ChatboxHeader = () => {
    const { theme, setTheme } = useContext(ThemeContext);
    const { username, avatar } = useContext(UserContext);

    const onThemeClick = (theme) => {
        setTheme(theme);
    }

    const handleLogout = async (e) => {
        e.preventDefault();
        // See <https://oauth2-proxy.github.io/oauth2-proxy/docs/features/endpoints/>
        // This is a bit hard-coded?
        window.location.href = "/oauth2/sign_out";
    };

    return (
        <div className={styles.chatboxHeader}>
            <div className={styles.rightElems}>
                <Dropdown>
                    <DropdownButton className={styles.themeMenuTitle}>
                        <ThemeIcon theme={theme} />
                        <span className={styles.themeMenuText}>Theme</span>
                    </DropdownButton>
                    <DropdownMenu className={styles.themeMenuList}>
                        <li>
                            <button
                                className={`${styles.themeMenuItem} ${theme === "system" && styles.selected}`}
                                onClick={() => onThemeClick("system")}
                                aria-label="Set theme to system default"
                            >
                                <BrightnessMediumIcon />
                                <span className={styles.themeMenuText}>OS Default</span>
                            </button>
                        </li>
                        <li>
                            <button
                                className={`${styles.themeMenuItem} ${theme === "light" && styles.selected}`}
                                onClick={() => onThemeClick("light")}
                                aria-label="Set theme to light mode"
                            >
                                <LightModeIcon />
                                <span className={styles.themeMenuText}>Light</span>
                            </button>
                        </li>
                        <li>
                            <button
                                className={`${styles.themeMenuItem} ${theme === "dark" && styles.selected}`}
                                onClick={() => onThemeClick("dark")}
                                aria-label="Set theme to dark mode"
                            >
                                <DarkModeIcon />
                                <span className={styles.themeMenuText}>Dark</span>
                            </button>
                        </li>
                    </DropdownMenu>
                </Dropdown>
                <Dropdown>
                    <DropdownButton className={styles.userInfoMenu}>
                        <Avatar
                            // NOTE: className not working on Avatar
                            sx={{
                                width: 24,
                                height: 24,
                            }}
                            src={avatar}
                            alt={`${username}'s avatar`}
                        />
                    </DropdownButton>
                    <DropdownMenu className={styles.userInfoMenuList}>
                        <li><span>{username}</span></li>
                        <hr className={styles.userInfoMenuUsernameHr} />
                        <li>
                            <button className={styles.themeMenuItem} onClick={handleLogout} aria-label="Logout">
                                <span className={styles.themeMenuText}>Logout</span>
                            </button>
                        </li>
                    </DropdownMenu>
                </Dropdown>
            </div>
        </div>
    );
};

export default ChatboxHeader;
