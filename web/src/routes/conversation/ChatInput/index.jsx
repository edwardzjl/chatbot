import styles from "./index.module.css";

import { useContext, useState, useRef, useEffect } from "react";
import { useParams } from "react-router";
import PropTypes from "prop-types";
import SendRoundedIcon from '@mui/icons-material/SendRounded';

import { WebsocketContext } from "@/contexts/websocket";


/**
 * ChatInput Component
 *
 * This component renders a chat input form with a dynamically resizing textarea and a submit button. 
 * It integrates with a WebSocket context to disable the submit button when the WebSocket is not ready.
 * The component also focuses on the textarea when the conversation ID changes and supports keyboard 
 * shortcuts for submitting the input.
 *
 * Props:
 * @param {Object} props - The props object.
 * @param {Function} props.onSubmit - Callback function to handle the submission of user input.
 *                                     Receives the input string as an argument.
 *
 * Features:
 * - Dynamically adjusts the textarea height based on its content.
 * - Autofocuses the textarea when the conversation ID (`convId`) changes.
 * - Disables the submit button when the WebSocket is not ready.
 * - Supports "Enter" key for submission unless used with Ctrl, Shift, or Alt (Shift adds a new line).
 *
 * Contexts:
 * - Uses the `WebsocketContext` to determine the readiness state (`ready`) of the WebSocket.
 *
 * Hooks:
 * - `useState` for managing the input text.
 * - `useRef` for accessing the textarea DOM node.
 * - `useEffect` for handling focus and dynamic height adjustments.
 *
 * Usage:
 * ```jsx
 * <ChatInput onSubmit={(message) => console.log("User input:", message)} />
 * ```
 */
const ChatInput = ({ onSubmit }) => {
  const params = useParams();
  const { ready } = useContext(WebsocketContext);

  const [input, setInput] = useState("");
  const inputRef = useRef(null);

  /**
   * Focus on input when convId changes.
   */
  useEffect(() => {
    if (params.convId) {
      inputRef.current.focus();
    }
  }, [params]);

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
      // TODO: let user know.
      console.error("Websocket not ready!");
      return;
    }
    onSubmit(input);
    setInput("");
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
        <SendRoundedIcon sx={{ fontSize: "1rem" }} />
      </button>
    </form>
  );
};

ChatInput.propTypes = {
  onSubmit: PropTypes.func.isRequired,
};

export default ChatInput;
