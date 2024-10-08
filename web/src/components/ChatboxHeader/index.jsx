import "./index.css";

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
        <div className="chatbox-header">
            <div className="right-elems">
                <DropdownMenu>
                    <DropdownHeader className="theme-menu-title">
                        <ThemeIcon theme={theme} /><span className="theme-menu-text">Theme</span>
                    </DropdownHeader>
                    <DropdownList className="theme-menu-list">
                        <li>
                            <button className={`theme-menu-item ${theme === "system" && "selected"}`} onClick={() => onThemeClick("system")}>
                                <BrightnessMediumIcon /><span className="theme-menu-text">OS Default</span>
                            </button>
                        </li>
                        <li>
                            <button className={`theme-menu-item ${theme === "light" && "selected"}`} onClick={() => onThemeClick("light")}>
                                <LightModeIcon /><span className="theme-menu-text">Light</span>
                            </button>
                        </li>
                        <li>
                            <button className={`theme-menu-item ${theme === "dark" && "selected"}`} onClick={() => onThemeClick("dark")}>
                                <DarkModeIcon /><span className="theme-menu-text">Dark</span>
                            </button>
                        </li>
                    </DropdownList>
                </DropdownMenu>
                <DropdownMenu>
                    <DropdownHeader className="user-info-menu">
                        <Avatar
                            // NOTE: className not working on Avatar
                            sx={{
                                width: 24,
                                height: 24,
                            }}
                            src={avatar}
                        />
                    </DropdownHeader>
                    <DropdownList className="user-info-menu-list">
                        <li><span>{username}</span></li>
                        <hr className="user-info-menu-username-hr" />
                        <li>
                            <button className="theme-menu-item" onClick={handleLogout}>
                                <span className="theme-menu-text">Logout</span>
                            </button>
                        </li>
                    </DropdownList>
                </DropdownMenu>
            </div>
        </div>
    );
};

export default ChatboxHeader;
