import "./index.css";

import { useContext, useState, useRef, useEffect } from "react";

import { UserContext } from "contexts/user";
import { MessageContext } from "contexts/message";
import { ConversationContext } from "contexts/conversation";
import { WebsocketContext } from "contexts/websocket";


/**
 *
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
    <form onSubmit={handleSubmit} className="input-container">
      <textarea
        id="input-text"
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
