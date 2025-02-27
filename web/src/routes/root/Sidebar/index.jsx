import styles from "./index.module.css";

import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import PropTypes from "prop-types";

import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import GitHubIcon from "@mui/icons-material/GitHub";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import MailOutlineIcon from "@mui/icons-material/MailOutline";

import { ConversationContext } from "@/contexts/conversation";

import ChatTab from "../ChatTab";


const Sidebar = ({ onShareClick, onDeleteClick }) => {
    const { groupedConvs } = useContext(ConversationContext);
    const navigate = useNavigate();

    return (
        <aside className={styles.sidebar}>
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
        </aside>
    );
};

Sidebar.propTypes = {
    onShareClick: PropTypes.func.isRequired,
    onDeleteClick: PropTypes.func.isRequired,
};

export default Sidebar;
