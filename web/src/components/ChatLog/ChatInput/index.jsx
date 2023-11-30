import "./index.css";

import { useContext, useState, useRef, useEffect } from "react";
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import Input from '@mui/material/Input';

import { ConversationContext } from "contexts/conversation";
import { UserContext } from "contexts/user";
import { WebsocketContext } from "contexts/websocket";

/**
 * @param {string} chatId
 */
const ChatInput = ({ chatId }) => {
  const [username,] = useContext(UserContext);
  const [conversations, dispatch] = useContext(ConversationContext);
  const [ready, send] = useContext(WebsocketContext);

  const [input, setInput] = useState("");
  const inputRef = useRef(null);

  /**
   * Focus on input when chatId changes.
   */
  useEffect(() => {
    if (chatId) {
      inputRef.current.focus();
    }
  }, [chatId]);

  const handleSubmit = async (e) => {
    if (!ready) {
      return;
    }
    e.preventDefault();
    const payload = input;
    setInput("");
    // append user input to chatlog
    dispatch({
      type: "messageAdded",
      id: chatId,
      message: { from: username, content: payload, type: "text" },
    });
    // if current chat is not the first in the list, move it to the first when send message.
    if (conversations[0].id !== chatId) {
      dispatch({
        type: "moveToFirst",
        id: chatId,
      });
    }
    send(
      JSON.stringify({
        conversation: chatId,
        from: username,
        content: payload,
        type: "text",
      })
    );
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
    <form onSubmit={handleSubmit} className="input-form">
      <FormControl variant="standard" className="input-form-control">
        <Input
          id="chat-input"
          // TODO: className not working
          // className="input-text"
          inputProps={{
            style: {
              padding: "12px",
              color: "white",
              fontSize: "1.25em",
            },
          }}
          multiline
          inputRef={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          aria-describedby="input-helper-text"
        />
        <FormHelperText
          id="input-helper-text"
          // TODO: className not working
          // className="input-helper"
          sx={{
            color: "white",
            paddingLeft: "12px",
          }}
        >
          Enter to send message, Shift + Enter to add a new line
        </FormHelperText>
      </FormControl>
      <button disabled={!ready} className="input-submit-button" type="submit">
        Send
      </button>
    </form>
  );
};

export default ChatInput;
