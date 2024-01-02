import "./index.css";

import { useContext } from "react";

import Avatar from "@mui/material/Avatar";

import Brightness4OutlinedIcon from '@mui/icons-material/Brightness4Outlined';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';

import { DropdownMenu, DropdownHeader, DropdownList } from "components/DropdownMenu";
import { ThemeContext } from "contexts/theme";
import { UserContext } from "contexts/user";
import { getFirstLetters, stringToColor } from "commons";


const ThemeIcon = ({ theme }) => {
    switch (theme) {
        case "light":
            return <LightModeIcon />;
        case "dark":
            return <DarkModeIcon />;
        default:
            return <Brightness4OutlinedIcon />;
    }
}


const ChatboxHeader = () => {
    const { theme, setTheme } = useContext(ThemeContext);
    const { username } = useContext(UserContext);

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
                                <Brightness4OutlinedIcon /><span className="theme-menu-text">OS Default</span>
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
                    <DropdownHeader className="user-info-menu-avatar">
                        <Avatar
                            // className not working on Avatar
                            sx={{
                                width: 24,
                                height: 24,
                                bgcolor: stringToColor(username),
                            }}
                        >
                            {getFirstLetters(username)}
                        </Avatar>
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
