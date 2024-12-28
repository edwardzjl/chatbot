import styles from "./index.module.css";

import { useContext, useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";

import { UserContext } from "@/contexts/user";
import { MessageContext } from "@/contexts/message";
import { ConversationContext } from "@/contexts/conversation";
import { WebsocketContext } from "@/contexts/websocket";


/**
 * ChatInput component for capturing and sending user input in a chat conversation.
 * 
 * The component renders a textarea for the user to type their message and a send button.
 * It dynamically adjusts the height of the textarea based on the content and focuses on the input 
 * when the conversation ID (`conv.id`) changes. Upon submitting the form, the message is added 
 * to the chat log, and the conversation's last message timestamp is updated.
 * 
 * @component
 * @example
 * // Example usage of the ChatInput component
 * <ChatInput conv={conversation} />
 * 
 * @param {Object} props - The props for the component.
 * @param {Object} props.conv - The current conversation object.
 * @param {string} props.conv.id - The ID of the conversation.
 * @param {boolean} [props.conv.pinned] - Whether the conversation is pinned (optional).
 */
const ChatInput = ({ conv }) => {
  const { username } = useContext(UserContext);
  const { dispatch } = useContext(MessageContext);
  const { groupedConvs, dispatch: dispatchConv } = useContext(ConversationContext);
  const [ready, send] = useContext(WebsocketContext);

  const [input, setInput] = useState("");
  const inputRef = useRef(null);

  /**
   * Focus on input when convId changes.
   */
  useEffect(() => {
    if (conv.id) {
      inputRef.current.focus();
    }
  }, [conv.id]);

  /**
   * Adjusting height of textarea.
   * Ref: <https://blog.muvon.io/frontend/creating-textarea-with-dynamic-height-react>
   */
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "0px";
      const { scrollHeight } = inputRef.current;
      inputRef.current.style.height = `${scrollHeight}px`
    }
  }, [inputRef, input]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!ready) {
      return;
    }
    const message = { id: crypto.randomUUID(), from: username, content: input, type: "text" };
    const payload = {
      conversation: conv.id,
      ...message,
    };
    setInput("");
    // append user input to chatlog
    dispatch({
      type: "added",
      message: message,
    });
    // update last_message_at of the conversation to re-order conversations
    if (conv.pinned && groupedConvs.pinned && groupedConvs.pinned[0]?.id !== conv.id) {
      dispatchConv({
        type: "reordered",
        conv: { id: conv.id, last_message_at: new Date().toISOString() },
      });
    } else if (groupedConvs.Today && groupedConvs.Today[0]?.id !== conv.id) {
      dispatchConv({
        type: "reordered",
        conv: { id: conv.id, last_message_at: new Date().toISOString() },
      });
    }
    send(JSON.stringify(payload));
  };

  const handleKeyDown = async (e) => {
    // TODO: this will trigger in Chinese IME on OSX
    if (e.key === "Enter") {
      if (e.ctrlKey || e.shiftKey || e.altKey) {
        // won't trigger submit here, but only shift key will add a new line
        return true;
      }
      e.preventDefault();
      await handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.inputContainer}>
      <textarea
        id="input-text"
        className={styles.inputText}
        ref={inputRef}
        autoFocus
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown} />
      <button disabled={!ready} className={styles.inputSubmitButton} type="submit">
        Send
      </button>
    </form>
  );
};

ChatInput.propTypes = {
  conv: PropTypes.shape({
    id: PropTypes.string.isRequired,
    pinned: PropTypes.bool,
  }).isRequired,
};

export default ChatInput;
