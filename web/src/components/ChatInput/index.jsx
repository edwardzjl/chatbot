import "./index.css";

import { useContext, useState, useRef, useEffect } from "react";

import { ConversationContext } from "contexts/conversation";
import { UserContext } from "contexts/user";
import { WebsocketContext } from "contexts/websocket";

/**
 *
 */
const ChatInput = () => {
  const { username } = useContext(UserContext);
  const { conversations, currentConv, dispatch } = useContext(ConversationContext);
  const [ready, send] = useContext(WebsocketContext);

  const [input, setInput] = useState("");
  const inputRef = useRef(null);

  /**
   * Adjusting height of textarea.
   * Ref: <https://blog.muvon.io/frontend/creating-textarea-with-dynamic-height-react>
   */
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = '0px';
      const { scrollHeight } = inputRef.current;
      inputRef.current.style.height = `${scrollHeight}px`
    }
  }, [inputRef, input]);

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
    <form onSubmit={handleSubmit} className="input-container">
      <textarea
        className="input-text"
        ref={inputRef}
        autoFocus
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown} />
      <button disabled={!ready} className="input-submit-button" type="submit">
        Send
      </button>
    </form>
  );
};

export default ChatInput;
