import { useEffect, useRef } from "react";

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: smoothScroll ? "smooth" : "auto" });
  };

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
  }, []);

  return (
    <div ref={chatLogRef} className={className} role="region" aria-label="chat-log">
      {children}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatLog;
