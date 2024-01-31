import "./index.css";

import { useContext, useEffect } from "react";
import { useLoaderData, redirect } from "react-router-dom";

import ChatboxHeader from "components/ChatboxHeader";

import { MessageContext } from "contexts/message";

import ChatLog from "./ChatLog";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

export async function action({ params, request }) {
    if (request.method === "PUT") {
        const conversation = await request.json();
        const resp = await fetch(`/api/conversations/${params.convId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                title: conversation.title,
                pinned: conversation.pinned,
            }),
        })
        if (!resp.ok) {
            console.error("error updating conversation", resp);
            // TODO: handle error
        }
        const _conv = await resp.json();
        return { _conv };
    }
    if (request.method === "DELETE") {
        await fetch(`/api/conversations/${params.convId}`, {
            method: "DELETE",
        })
        return redirect("/");
    }
}

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
    const { messages, dispatch } = useContext(MessageContext);

    useEffect(() => {
        if (conversation && conversation.messages) {
            dispatch({
                type: "replaceAll",
                messages: conversation.messages,
            });
        }
    }, [conversation, dispatch]);

    return (
        <>
            <ChatboxHeader />
            <ChatLog className="chat-log">
                {conversation && messages && messages.map((message, index) => (
                    <ChatMessage key={index} convId={conversation.id} idx={index} message={message} />
                ))}
            </ChatLog>
            <div className="input-bottom">
                <ChatInput conversation={{ ...conversation, messages: messages }} />
                <div className="footer">Chatbot can make mistakes. Consider checking important information.</div>
            </div>
        </>
    );
}

export default Conversation;
