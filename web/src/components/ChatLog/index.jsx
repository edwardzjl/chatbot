import styles from "./index.module.css";

import { useCallback, useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";

import VerticalAlignBottomIcon from "@mui/icons-material/VerticalAlignBottom";

/**
 * ChatLog is a container for ChatMessage that will automatically scroll to the bottom when window size changes.
 * @param {Object} props
 * @param {Array} props.children - Chat message components.
 * @param {string} [props.className] - Additional CSS classes for the chat log container.
 * @param {boolean} [props.smoothScroll=true] - Whether to enable smooth scrolling.
 */
const ChatLog = ({ children, className = "", smoothScroll = true }) => {
    const chatLogRef = useRef(null);
    const messagesEndRef = useRef(null);
    const isNearBottomRef = useRef(true);
    const [showScrollButton, setShowScrollButton] = useState(false);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: smoothScroll ? "smooth" : "auto" });
    }, [smoothScroll]);

    // Add scroll event handler to detect if user is near bottom
    useEffect(() => {
        const handleScroll = () => {
            if (chatLogRef.current) {
                const { scrollHeight, scrollTop, clientHeight } = chatLogRef.current;
                const scrollBottom = scrollHeight - scrollTop - clientHeight;
                const isNearBottom = scrollBottom < 50; // within 50px of bottom
                isNearBottomRef.current = isNearBottom;
                setShowScrollButton(!isNearBottom);
            }
        };

        const chatLogElement = chatLogRef.current;
        if (chatLogElement) {
            chatLogElement.addEventListener("scroll", handleScroll);
        }

        return () => {
            if (chatLogElement) {
                chatLogElement.removeEventListener("scroll", handleScroll);
            }
        };
    }, []);

    useEffect(() => {
        if (!window.ResizeObserver) {
            console.warn("ResizeObserver is not supported in this browser.");
            return;
        }

        const resizeObserver = new ResizeObserver(() => {
            if (isNearBottomRef.current) {
                scrollToBottom();
            }
        });

        if (chatLogRef.current) {
            resizeObserver.observe(chatLogRef.current);
        }

        return () => {
            resizeObserver.disconnect();
        };
    }, [scrollToBottom]);

    return (
        <>
            <div ref={chatLogRef} className={`${styles.chatLog} ${className}`} role="region" aria-label="chat-log">
                {children}
                <div ref={messagesEndRef} />
            </div>
            {showScrollButton && (
                <button
                    className={styles.scrollButton}
                    onClick={scrollToBottom}
                    aria-label="Scroll to bottom"
                    title="Scroll to bottom"
                >
                    <VerticalAlignBottomIcon />
                </button>
            )}
        </>
    );
};

ChatLog.propTypes = {
    children: PropTypes.node.isRequired,
    className: PropTypes.string,
    smoothScroll: PropTypes.bool,
};

export default ChatLog;
