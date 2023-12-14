import "./index.css";

import { useContext } from "react";

import Brightness4OutlinedIcon from '@mui/icons-material/Brightness4Outlined';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';

import { DropdownMenu, DropdownHeader, DropdownList } from "components/DropdownMenu";
import { ThemeContext } from "contexts/theme";



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

    const onThemeClick = (theme) => {
        setTheme(theme);
    }

    return (
        <div className="chatbox-header">
            <DropdownMenu className="theme-menu">
                <DropdownHeader className="theme-menu-title">
                    <ThemeIcon theme={theme} /><span className="theme-menu-text">Theme</span>
                </DropdownHeader>
                <DropdownList className="theme-menu-list">
                    <li>
                        <button className="theme-menu-item" onClick={() => onThemeClick("system")}>
                            <Brightness4OutlinedIcon /><span className="theme-menu-text">OS Default</span>
                        </button>
                    </li>
                    <li>
                        <button className="theme-menu-item" onClick={() => onThemeClick("light")}>
                            <LightModeIcon /><span className="theme-menu-text">Light</span>
                        </button>
                    </li>
                    <li>
                        <button className="theme-menu-item" onClick={() => onThemeClick("dark")}>
                            <DarkModeIcon /><span className="theme-menu-text">Dark</span>
                        </button>
                    </li>
                </DropdownList>
            </DropdownMenu>
        </div>
    );
};

export default ChatboxHeader;
