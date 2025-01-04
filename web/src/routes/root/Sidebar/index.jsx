import styles from "./index.module.css";

import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import PropTypes from "prop-types";

import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import GitHubIcon from "@mui/icons-material/GitHub";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import MailOutlineIcon from "@mui/icons-material/MailOutline";
import MenuIcon from "@mui/icons-material/Menu";
import MenuOpenIcon from "@mui/icons-material/MenuOpen";

import { ConversationContext } from "@/contexts/conversation";

import CollapsibleWrapper from "@/components/CollapsibleWrapper";

import ChatTab from "../ChatTab";


const DEFAULT_COLLAPSE_THRESHOLD = 768;


const Sidebar = ({ onShareClick, onDeleteClick, collapseThreshold = DEFAULT_COLLAPSE_THRESHOLD }) => {
    const { groupedConvs } = useContext(ConversationContext);
    const navigate = useNavigate();

    return (
        <CollapsibleWrapper collapseThreshold={collapseThreshold}>
            {({ isCollapsed, toggle }) => (
                <aside className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ""}`}>
                    <button className={styles.toggleButton} onClick={toggle}>
                        {isCollapsed ? <MenuIcon /> : <MenuOpenIcon />}
                    </button>

                    <div className={styles.sidebarContent}>
                        <button className={styles.sidebarButton} onClick={() => navigate("/")}>
                            <AddOutlinedIcon />
                            New Chat
                        </button>
                        <nav className={styles.convList}>
                            {groupedConvs && Object.entries(groupedConvs)
                                .filter(([, convs]) => convs && convs.length > 0) // Filter out empty lists
                                .flatMap(([grp, convs]) => (
                                    [
                                        <div key={grp}>
                                            <div className={styles.sidebarDateGroup}>{grp}</div>
                                            {convs.map((conv) => (
                                                <ChatTab key={conv.id} chat={conv} onShareClick={onShareClick} onDeleteClick={onDeleteClick} />
                                            ))}
                                        </div>
                                    ]
                                ))}
                        </nav>
                        <hr className={styles.sidebarBottom} />
                        <div className={styles.sidebarBottomGroup}>
                            <div className={styles.sidebarBottomGroupItem}>
                                <InfoOutlinedIcon />
                            </div>
                            <div className={styles.sidebarBottomGroupItem}>
                                <a href="https://github.com/edwardzjl/chatbot" target="_blank" rel="noreferrer"> <GitHubIcon /> </a>
                            </div>
                            <div className={styles.sidebarBottomGroupItem}>
                                <a href="mailto:jameszhou2108@hotmail.com">
                                    <MailOutlineIcon />
                                </a>
                            </div>
                        </div>
                    </div>
                </aside>
            )}
        </CollapsibleWrapper>
    );
};

Sidebar.propTypes = {
    onShareClick: PropTypes.func.isRequired,
    onDeleteClick: PropTypes.func.isRequired,
    collapseThreshold: PropTypes.number,
};

export default Sidebar;
