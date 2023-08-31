import "./index.css";

import { useContext, useState, useRef, useEffect } from "react";

import { TextField } from "@mui/material";

import { UserContext, ConversationContext } from "contexts";

/**
 * @param {Object} props
 * @param {string} props.chatId
 * @param {*} props.onSend
 */
const ChatInput = (props) => {
  const username = useContext(UserContext);
  const { conversations, dispatch } = useContext(ConversationContext);

  const [input, setInput] = useState("");
  const inputRef = useRef(null);

  /**
   * Focus on input when chatId changes.
   */
  useEffect(() => {
    if (props.chatId) {
      inputRef.current.focus();
    }
  }, [props.chatId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = input;
    setInput("");
    // append user input to chatlog
    dispatch({
      type: "messageAdded",
      id: props.chatId,
      message: { from: username, content: payload },
    });
    // if current chat is not the first in the list, move it to the first when send message.
    if (conversations[0].id !== props.chatId) {
      dispatch({
        type: "moveToFirst",
        id: props.chatId,
      });
    }
    await props.onSend(props.chatId, payload);
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
    <form onSubmit={handleSubmit} className="chat-input-form">
      {/* TODO: in order to get rid of css in js, I need to break TextField into smaller components.
        See https://mui.com/material-ui/react-text-field/#components.
       */}
      <TextField
        id="standard-multiline-flexible"
        className="chat-input-textarea"
        autoFocus
        inputRef={inputRef}
        inputProps={{
          style: {
            padding: "12px",
            color: "white",
            fontSize: "1.25em",
          },
        }}
        helperText="Enter to send message, Shift + Enter to add a new line"
        FormHelperTextProps={{
          style: {
            color: "white",
            paddingLeft: "12px",
          },
        }}
        multiline
        variant="standard"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button className="chat-input-submit-button" type="submit">
        Send
      </button>
    </form>
  );
};

export default ChatInput;
