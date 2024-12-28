import "./index.css";

import { useContext, useEffect } from "react";
import { useLoaderData, redirect } from "react-router-dom";

import ChatboxHeader from "@/components/ChatboxHeader";
import ChatLog from "@/components/ChatLog";
import ChatMessage from "@/components/ChatMessage";

import { ConversationContext } from "@/contexts/conversation";
import { MessageContext } from "@/contexts/message";
import { UserContext } from "@/contexts/user";
import { WebsocketContext } from "@/contexts/websocket";

import ChatInput from "./ChatInput";


export async function loader({ params }) {
    const resp = await fetch(`/api/conversations/${params.convId}`, {});
    if (!resp.ok) {
        return redirect("/");
    }
    const conversation = await resp.json();
    return { conversation };
}

const Conversation = () => {
    const { conversation } = useLoaderData();
    const { groupedConvs, dispatch: dispatchConv } = useContext(ConversationContext);
    const { username } = useContext(UserContext);
    const {ready, send} = useContext(WebsocketContext);
    const { messages, dispatch } = useContext(MessageContext);

    useEffect(() => {
        // Update the message context.
        dispatch({
            type: "replaceAll",
            messages: conversation.messages,
        });
        if (!ready) {
            console.error("Websocket not ready!");
            return;
        }

        const initMsg = sessionStorage.getItem(`init-msg:${conversation.id}`);
        if (initMsg === undefined || initMsg === null) {
            return;
        }
        const message = JSON.parse(initMsg);
        dispatch({
            type: "added",
            message: message,
        });
        // Send the init message if there's any.
        send(JSON.stringify({ additional_kwargs: { require_summarization: true }, ...message }));
        sessionStorage.removeItem(`init-msg:${conversation.id}`);
    }, [conversation, dispatch, ready, send]);

    const sendMessage = async (text) => {
      if (!ready) {
          console.error("Websocket not ready!");
        return;
      }
      const message = { id: crypto.randomUUID(), from: username, content: text, type: "text" };
      const payload = {
        conversation: conversation.id,
        ...message,
      };
      // append user input to chatlog
      dispatch({
        type: "added",
        message: message,
      });
      // update last_message_at of the conversation to re-order conversations
      // TODO: this seems buggy
      if (conversation.pinned && groupedConvs.pinned && groupedConvs.pinned[0]?.id !== conversation.id) {
        dispatchConv({
          type: "reordered",
          conv: { id: conversation.id, last_message_at: new Date().toISOString() },
        });
      } else if (groupedConvs.Today && groupedConvs.Today[0]?.id !== conversation.id) {
        dispatchConv({
          type: "reordered",
          conv: { id: conversation.id, last_message_at: new Date().toISOString() },
        });
      }
      send(JSON.stringify(payload));
    };

    return (
        <>
            <ChatboxHeader />
            <ChatLog className="chat-log">
                {/* We ignore system messages when displaying. */}
                {conversation && messages?.filter(message => message.from !== "system").map((message, index) => (
                    <ChatMessage key={index} convId={conversation.id} message={message} />
                ))}
            </ChatLog>
            <div className="input-bottom">
                <ChatInput onSubmit={sendMessage} />
                <div className="footer">Chatbot can make mistakes. Consider checking important information.</div>
            </div>
        </>
    );
}

export default Conversation;
