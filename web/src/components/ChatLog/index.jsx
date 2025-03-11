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
    const scrollTimeoutRef = useRef(null);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: smoothScroll ? "smooth" : "auto" });
    }, [smoothScroll]);

    // Debounced scroll to avoid too many scroll operations during typing
    const debouncedScrollToBottom = useCallback(() => {
        if (scrollTimeoutRef.current) {
            clearTimeout(scrollTimeoutRef.current);
        }

        scrollTimeoutRef.current = setTimeout(() => {
            scrollToBottom();
        }, 50); // Small delay to batch scroll events
    }, [scrollToBottom]);

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
        if (!window.MutationObserver) {
            console.warn("MutationObserver is not supported in this browser.");
            return;
        }

        // Create a mutation observer to detect content changes including text changes
        const mutationObserver = new MutationObserver((mutations) => {
            if (!isNearBottomRef.current) {
                return;
            }

            let shouldScroll = false;

            for (const mutation of mutations) {
                // Check for character data changes (typing)
                if (mutation.type === "characterData") {
                    shouldScroll = true;
                    break;
                }
                // Check for added nodes (new messages)
                if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
                    shouldScroll = true;
                    break;
                }
                // Check for attribute changes that might affect layout
                if (mutation.type === "attributes") {
                    shouldScroll = true;
                    break;
                }
            }

            if (shouldScroll) {
                debouncedScrollToBottom();
            }
        });

        // Use MutationObserver to monitor changes in the chatLog DOM.
        // Primarily focus on text content changes (characterData) of child nodes to respond to dynamic message updates in real-time.
        // Additionally, observe child node lists (childList) and attributes (attributes) to ensure comprehensive capture of DOM modifications.
        // subtree: true ensures observation coverage extends to all descendant nodes, accommodating nested message structures.
        if (chatLogRef.current) {
            mutationObserver.observe(chatLogRef.current, {
                childList: true,  // Observe changes to the child nodes (additions, removals, reorderings)
                characterData: true,  // Observe changes to the text content (e.g., nodeValue of text nodes)
                attributes: true,  // Observe changes to attributes (e.g., class, src)
                subtree: true,  // Recursively observe changes in all descendant nodes
            });
        }

        return () => {
            mutationObserver.disconnect();
            if (scrollTimeoutRef.current) {
                clearTimeout(scrollTimeoutRef.current);
            }
        };
    }, [debouncedScrollToBottom]);

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
