import "./index.css";

import { useContext, useEffect } from "react";
import { useLoaderData, redirect } from "react-router-dom";

import ChatboxHeader from "components/ChatboxHeader";
import ChatLog from "components/ChatLog";

import { MessageContext } from "contexts/message";
import { WebsocketContext } from "contexts/websocket";

import ChatMessage from "./ChatMessage";
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
    const [ready, send] = useContext(WebsocketContext);
    const { messages, dispatch } = useContext(MessageContext);

    useEffect(() => {
        if (conversation?.messages) {
            dispatch({
                type: "replaceAll",
                messages: conversation.messages,
            });
            const initMsg = sessionStorage.getItem(`init-msg:${conversation.id}`);
            if (initMsg === undefined || initMsg === null) {
                return;
            }
            const message = JSON.parse(initMsg);
            dispatch({
                type: "added",
                message: message,
            });
            if (ready) {
                // TODO: should I wait until ready?
                send(JSON.stringify({ additional_kwargs: { require_summarization: true }, ...message }));
            }
            sessionStorage.removeItem(`init-msg:${conversation.id}`);
        }
    }, [conversation]);

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
                <ChatInput conv={conversation} />
                <div className="footer">Chatbot can make mistakes. Consider checking important information.</div>
            </div>
        </>
    );
}

export default Conversation;
