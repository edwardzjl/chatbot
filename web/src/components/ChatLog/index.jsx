import { useCallback, useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";


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
    const [isUserScrolling, setIsUserScrolling] = useState(false);
    // const [isNearBottom, setIsNearBottom] = useState(true);

    const scrollToBottom = useCallback(() => {
        if (!isUserScrolling) {
            messagesEndRef.current?.scrollIntoView({ behavior: smoothScroll ? "smooth" : "auto" });
        }
    }, [smoothScroll, isUserScrolling]);

    useEffect(() => {
        const container = chatLogRef.current;
        if (!container) return;

        // let scrollTimer;
        const handleUserScroll = () => {
            setIsUserScrolling(true);
            // checkIfNearBottom();

            // clearTimeout(scrollTimer);
            // scrollTimer = setTimeout(() => {
            //     setIsUserScrolling(false);
            // }, 1000);
        };

        container.addEventListener('scroll', handleUserScroll);
        return () => {
            container.removeEventListener('scroll', handleUserScroll);
            // clearTimeout(scrollTimer);
        };
    }, []);

    useEffect(() => {
        if (!window.ResizeObserver) {
            console.warn("ResizeObserver is not supported in this browser.");
            return;
        }

        const resizeObserver = new ResizeObserver(() => {
            scrollToBottom();
        });

        if (chatLogRef.current) {
            resizeObserver.observe(chatLogRef.current);
        }

        return () => {
            resizeObserver.disconnect();
        };
    }, [scrollToBottom]);

    return (
        <div ref={chatLogRef} className={className} role="region" aria-label="chat-log">
            {children}
            <div ref={messagesEndRef} />
            {!isUserScrolling && (
                <button
                    className="scroll-to-bottom-btn"
                    onClick={scrollToBottom}
                    aria-label="滚动到最新消息"
                >
                    ↓
                </button>
            )}
        </div>
    );
};

ChatLog.propTypes = {
    children: PropTypes.node.isRequired,
    className: PropTypes.string,
    smoothScroll: PropTypes.bool,
};

export default ChatLog;
