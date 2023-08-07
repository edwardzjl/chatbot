import "./index.css";
import { useEffect, useRef } from "react";

/**
 * ChatLog is a container for ChatMessage that will automatically scroll to bottom when window size changes.
 * @param {Object} props 
 * @param {Array} props.children
 */
const ChatLog = ({ children }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    const chatLogElem = document.getElementById("chat-log");
    const resizeObserver = new ResizeObserver(() => {
      scrollToBottom();
    });
    resizeObserver.observe(chatLogElem);
  }, []);

  return (
    <div id="chat-log" className="chat-log">
      {children}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatLog;
