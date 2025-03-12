import styles from "./index.module.css";

import { useContext, useEffect } from "react";
import { redirect, useLoaderData, useNavigation } from "react-router-dom";

import ChatboxHeader from "@/components/ChatboxHeader";
import ChatLog from "@/components/ChatLog";
import ChatMessage from "@/components/ChatMessage";

import { ConversationContext } from "@/contexts/conversation";
import { MessageContext } from "@/contexts/message";
import { UserContext } from "@/contexts/user";
import { WebsocketContext } from "@/contexts/websocket";

import ChatInput from "./ChatInput";


async function loader({ params }) {
    const resp = await fetch(`/api/conversations/${params.convId}`, {});
    if (!resp.ok) {
        return redirect("/");
    }
    const conversation = await resp.json();
    return { conversation };
}

/**
 * Conversation Component
 *
 * This component handles the rendering and functionality of a single conversation in the chat application.
 * It integrates with multiple contexts to manage conversation data, user messages, WebSocket communication, 
 * and UI updates. The component is designed to display messages, handle message input, and manage WebSocket interactions.
 *
 * Loader:
 * - Fetches conversation data from the API using the conversation ID provided in the route parameters.
 * - Redirects to the homepage if the conversation ID is invalid or the fetch request fails.
 *
 * Contexts Used:
 * - ConversationContext: Manages the list of grouped conversations and dispatch actions.
 * - UserContext: Provides the current user's details, such as the username.
 * - WebsocketContext: Manages WebSocket connection status and message-sending functionality.
 * - MessageContext: Manages the state of messages within the current conversation.
 *
 * Effects:
 * - Initializes the message context with messages from the fetched conversation.
 * - Handles sending an "init message" if present in `sessionStorage`, and removes it after sending.
 *
 * Functions:
 * - sendMessage: Sends a message via WebSocket and updates the UI with the user's message. 
 *   Also reorders conversations based on the latest message timestamp.
 *
 * UI Components:
 * - ChatboxHeader: Displays the header for the chatbox.
 * - ChatLog: Renders a scrollable area containing the chat messages.
 * - ChatMessage: Renders individual chat messages, excluding system messages.
 * - ChatInput: Provides a text input field for sending messages.
 * - Footer: Displays a disclaimer below the input field.
 *
 * Props: None
 *
 * Usage:
 * - This component is typically used as a route target in a React Router configuration for `/conversations/:convId`.
 * - It relies on the `loader` function to pre-fetch conversation data.
 */
const Conversation = () => {
    const { conversation } = useLoaderData();
    const navigation = useNavigation();
    const { groupedConvs, dispatch: dispatchConv } = useContext(ConversationContext);
    const { username } = useContext(UserContext);
    const { ready, send } = useContext(WebsocketContext);
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
        const message = { id: crypto.randomUUID(), from: username, content: text, type: "human" };
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
        <section className={`${styles.chatbox} ${navigation.state === "loading" ? "loading" : ""}`}>
            <ChatboxHeader />
            <ChatLog>
                {/* We ignore system messages when displaying. */}
                {conversation && messages?.filter(message => message.from !== "system").map((message, index) => (
                    <ChatMessage key={index} convId={conversation.id} message={message} />
                ))}
            </ChatLog>
            <div className={styles.inputBottom}>
                <ChatInput onSubmit={sendMessage} />
                <div className={styles.footer}>Chatbot can make mistakes. Consider checking important information.</div>
            </div>
        </section>
    );
}

export default Conversation;
Conversation.loader = loader;
