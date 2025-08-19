import styles from "./index.module.css";

import { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router";

import GitHubIcon from "@mui/icons-material/GitHub";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import MailOutlineIcon from "@mui/icons-material/MailOutline";
import MapsUgcOutlinedIcon from "@mui/icons-material/MapsUgcOutlined";
import MenuIcon from "@mui/icons-material/Menu";
import MenuOpenOutlinedIcon from "@mui/icons-material/MenuOpenOutlined";

import { useConversations } from "@/contexts/conversation/hook";
import { useInfiniteScroll } from "@/hooks/useInfiniteScroll";

import ConvItem from "./ConvItem";


const LeftPanel = () => {
    const { groupedConvsArray: convs, fetchMoreConvs, isLoading, hasMore } = useConversations();
    const loadMoreRef = useRef();

    // Check if device is mobile on initial load
    const [isCollapsed, setIsCollapsed] = useState(() => {
        if (typeof window !== 'undefined') {
            return window.innerWidth <= 768;
        }
        return false;
    });

    const navigate = useNavigate();

    // Handle window resize to auto-collapse on mobile
    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth <= 768) {
                setIsCollapsed(true);
            }
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    useInfiniteScroll({
        targetRef: loadMoreRef,
        onLoadMore: fetchMoreConvs,
        hasMore,
        isLoading,
    });

    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    };

    return (
        <aside className={`${styles.sidebar} ${isCollapsed && styles.collapsed}`}>
            <header className={styles.sidebarHeader}>
                <button
                    className={`${styles.newChatButton} ${isCollapsed && styles.iconButton}`}
                    onClick={() => navigate("/")}
                    title="New Chat"
                    aria-label="New Chat"
                >
                    <MapsUgcOutlinedIcon />
                    {!isCollapsed && "New Chat"}
                </button>
                <button
                    className={`${styles.toggleButton} ${styles.iconButton}`}
                    onClick={toggleSidebar}
                    aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                    title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                >
                    {isCollapsed ? <MenuIcon /> : <MenuOpenOutlinedIcon />}
                </button>
            </header>
            {!isCollapsed && (
                <>
                    <nav className={`${styles.convList} scroll-box`}>
                        {convs && convs
                            .filter(group => group.conversations && group.conversations.length > 0) // Filter out empty lists
                            .map(group => (
                                <div key={group.key}>
                                    <div className={styles.sidebarDateGroup}>{group.key}</div>
                                    {group.conversations.map((conv) => (
                                        <ConvItem key={conv.id} chat={conv} />
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
                    <footer className={styles.sidebarBottomGroup}>
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
                    </footer>
                </>
            )}
        </aside>
    );
};

export default LeftPanel;
