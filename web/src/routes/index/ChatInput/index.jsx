import "./index.css";

import { useContext, useState, useRef, useEffect } from "react";
import { Form, useSubmit } from "react-router-dom";

import { UserContext } from "contexts/user";
import { MessageContext } from "contexts/message";
import { WebsocketContext } from "contexts/websocket";
import { DEFAULT_CONV_TITLE } from "commons";


/**
 *
 */
const ChatInput = () => {
  const { username } = useContext(UserContext);
  const { dispatch } = useContext(MessageContext);
  const [ready, send] = useContext(WebsocketContext);
  const submit = useSubmit();
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
    e.preventDefault();
    if (!ready) {
      return;
    }
    // I need to use the conversation id later so I need to create a conversation here instead of in the 'react router action'
    const conversation = await fetch("/api/conversations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title: DEFAULT_CONV_TITLE }),
    }).then((res) => res.json());
    submit(conversation, { method: "post", action: "/", encType: "application/json" });
    const message = { id: crypto.randomUUID(), from: username, content: input, type: "text" };
    const payload = {
      conversation: conversation.id,
      additional_kwargs: { require_summarization: true },
      ...message,
    };
    send(JSON.stringify(payload));
    setInput("");
    // append user input to chatlog
    dispatch({
      type: "added",
      message: message,
    });
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
    <Form className="input-container" method="post">
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
    </Form>
  );
};

export default ChatInput;
