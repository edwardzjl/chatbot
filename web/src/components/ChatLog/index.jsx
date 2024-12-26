import { useEffect, useRef } from "react";

/**
 * ChatLog is a container for ChatMessage that will automatically scroll to bottom when window size changes.
 * @param {Array} children
 */
const ChatLog = ({ children, className }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (window.ResizeObserver) {
      const chatLogElem = document.getElementById("chat-log");
      const resizeObserver = new ResizeObserver(() => {
        scrollToBottom();
      });
      resizeObserver.observe(chatLogElem);

      return () => {
        resizeObserver.disconnect();
      };
    }
  }, []);

  return (
    <div id="chat-log" className={className}>
      {children}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatLog;
