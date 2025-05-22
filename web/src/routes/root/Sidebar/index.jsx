import styles from "./index.module.css";

import { useRef } from "react";
import { useNavigate } from "react-router-dom";

import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import GitHubIcon from "@mui/icons-material/GitHub";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import MailOutlineIcon from "@mui/icons-material/MailOutline";

import { useConversations } from "@/contexts/conversation/hook";
import { useInfiniteScroll } from "@/hooks/useInfiniteScroll";

import ChatTab from "../ChatTab";


const Sidebar = () => {
    const { groupedConvsArray: convs, fetchMoreConvs, isLoading, hasMore } = useConversations();
    const loadMoreRef = useRef();

    const navigate = useNavigate();

    useInfiniteScroll({
        targetRef: loadMoreRef,
        onLoadMore: fetchMoreConvs,
        isLoading,
        canLoadMore: hasMore,
    });

    return (
        <aside className={styles.sidebar}>
            <button className={styles.sidebarButton} onClick={() => navigate("/")}>
                <AddOutlinedIcon />
                New Chat
            </button>
            <nav className={styles.convList}>
                {convs && convs
                    .filter(group => group.conversations && group.conversations.length > 0) // Filter out empty lists
                    .map(group => (
                        <div key={group.key}>
                            <div className={styles.sidebarDateGroup}>{group.key}</div>
                            {group.conversations.map((conv) => (
                                <ChatTab key={conv.id} chat={conv} />
                            ))}
                        </div>
                    ))}
                <div ref={loadMoreRef} className={styles.loadMoreAnchor}>
                    {isLoading ? (
                        <div className={styles.spinner} />
                    ) : (
                        // placeholder
                        <div style={{ width: 24, height: 24, visibility: "hidden" }} />
                    )}
                </div>
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

export default Sidebar;
