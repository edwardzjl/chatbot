import styles from "./index.module.css";

import { useContext } from "react";

import Avatar from "@mui/material/Avatar";

import BrightnessMediumIcon from "@mui/icons-material/BrightnessMedium";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";

import { DropdownMenu, DropdownHeader, DropdownList } from "components/DropdownMenu";
import { ThemeContext } from "contexts/theme";
import { UserContext } from "contexts/user";


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
                <DropdownMenu>
                    <DropdownHeader className={styles.themeMenuTitle}>
                        <ThemeIcon theme={theme} />
                        <span className={styles.themeMenuText}>Theme</span>
                    </DropdownHeader>
                    <DropdownList className={styles.themeMenuList}>
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
                    </DropdownList>
                </DropdownMenu>
                <DropdownMenu>
                    <DropdownHeader className={styles.userInfoMenu}>
                        <Avatar
                            // NOTE: className not working on Avatar
                            sx={{
                                width: 24,
                                height: 24,
                            }}
                            src={avatar}
                            alt={`${username}'s avatar`}
                        />
                    </DropdownHeader>
                    <DropdownList className={styles.userInfoMenuList}>
                        <li><span>{username}</span></li>
                        <hr className={styles.userInfoMenuUsernameHr} />
                        <li>
                            <button className={styles.themeMenuItem} onClick={handleLogout} aria-label="Logout">
                                <span className={styles.themeMenuText}>Logout</span>
                            </button>
                        </li>
                    </DropdownList>
                </DropdownMenu>
            </div>
        </div>
    );
};

export default ChatboxHeader;
