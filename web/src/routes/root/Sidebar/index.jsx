import styles from "./index.module.css";

import { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import GitHubIcon from "@mui/icons-material/GitHub";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import MailOutlineIcon from "@mui/icons-material/MailOutline";
import MenuIcon from "@mui/icons-material/Menu";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";

import { useConversations } from "@/contexts/conversation/hook";
import { useInfiniteScroll } from "@/hooks/useInfiniteScroll";

import ChatTab from "../ChatTab";


const Sidebar = () => {
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
        isLoading,
        canLoadMore: hasMore,
    });

    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    };

    return (
        <>
            {/* Mobile toggle button - always visible on mobile */}
            <button
                className={`${styles.toggleButton} ${styles.mobileToggle}`}
                onClick={toggleSidebar}
                aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
                {isCollapsed ? <MenuIcon /> : <ChevronLeftIcon />}
            </button>
            
            <aside className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ''}`}>
                <div className={styles.sidebarHeader}>
                    <button
                        className={`${styles.toggleButton} ${styles.desktopToggle}`}
                        onClick={toggleSidebar}
                        aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                        title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                    >
                        {isCollapsed ? <MenuIcon /> : <ChevronLeftIcon />}
                    </button>
                    <button
                        className={`${styles.sidebarButton} ${isCollapsed ? styles.iconOnly : ''}`}
                        onClick={() => navigate("/")}
                        title="New Chat"
                        aria-label="New Chat"
                    >
                        <AddOutlinedIcon />
                        {!isCollapsed && "New Chat"}
                    </button>
                </div>
                {!isCollapsed && (
                    <>
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
                    </>
                )}
            </aside>
        </>
    );
};

export default Sidebar;
