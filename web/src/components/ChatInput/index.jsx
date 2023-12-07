import "./index.css";

import { useContext, useState, useRef, useEffect } from "react";
import Input from '@mui/material/Input';

import { ConversationContext } from "contexts/conversation";
import { UserContext } from "contexts/user";
import { WebsocketContext } from "contexts/websocket";

/**
 *
 */
const ChatInput = () => {
  const [username,] = useContext(UserContext);
  const [conversations, currentConv, dispatch] = useContext(ConversationContext);
  const [ready, send] = useContext(WebsocketContext);

  const [input, setInput] = useState("");
  const inputRef = useRef(null);

  /**
   * Focus on input when currentConvId changes.
   */
  useEffect(() => {
    if (currentConv?.id) {
      inputRef.current.focus();
    }
  }, [currentConv]);

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
      id: currentConv.id,
      message: { from: username, content: payload, type: "text" },
    });
    // if current chat is not the first in the list, move it to the first when send message.
    if (conversations[0].id !== currentConv.id) {
      dispatch({
        type: "moveToFirst",
        id: currentConv.id,
      });
    }
    send(JSON.stringify({
      conversation: currentConv.id,
      from: username,
      content: payload,
      type: "text",
    }));
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
      <div className="input-box">
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
        <div className="input-helper">
          Enter to send message, Shift + Enter to add a new line
        </div>
      </div>
      <button disabled={!ready} className="input-submit-button" type="submit">
        Send
      </button>
    </form>
  );
};

export default ChatInput;
