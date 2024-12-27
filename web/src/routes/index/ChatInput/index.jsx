import styles from './index.module.css';

import { useContext, useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";

import { WebsocketContext } from "@/contexts/websocket";


/**
 * ChatInput component renders a text input area for users to type messages.
 * It automatically adjusts its height based on the content and provides a "Send" button
 * to submit the message. The submission is handled by a function passed as a prop (`onSubmit`).
 * 
 * The component also handles "Enter" key behavior:
 * - Pressing "Enter" without any modifier keys submits the form.
 * - Pressing "Enter" with modifier keys (Ctrl, Shift, Alt) allows adding new lines.
 * 
 * @component
 * @example
 * // Usage example in a parent component:
 * <ChatInput onSubmit={handleSubmit} />
 * 
 * @param {Object} props - The component's props.
 * @param {Function} props.onSubmit - A function to handle the submission of the input message.
 * @returns {JSX.Element} The rendered `ChatInput` component.
 */
const ChatInput = ({ onSubmit }) => {
  const [ready,] = useContext(WebsocketContext);
  const [input, setInput] = useState("");
  const inputRef = useRef(null);

  /**
   * Adjusting height of textarea.
   * Ref: <https://blog.muvon.io/frontend/creating-textarea-with-dynamic-height-react>
   */
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';  // Reset height first
      const { scrollHeight } = inputRef.current;
      inputRef.current.style.height = `${scrollHeight}px`;  // Set height based on content
    }
  }, [input]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(input);
    setInput(""); // Clear the input after submit
  };

  /**
   * Handle the keydown event for the textarea.
   * If the user presses "Enter" without any modifier keys, the form is submitted.
   * If modifier keys like "Ctrl", "Shift", or "Alt" are pressed, it allows adding a new line.
   */
  const handleKeyDown = (e) => {
    // TODO: this will trigger in Chinese IME on OSX
    if (e.key === "Enter") {
      if (e.ctrlKey || e.shiftKey || e.altKey) {
        // won't trigger submit here, but only shift key will add a new line
        return true;
      }
      e.preventDefault();
      handleSubmit(e);
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
  onSubmit: PropTypes.func.isRequired,
};

export default ChatInput;
