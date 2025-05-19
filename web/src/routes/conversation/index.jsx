import styles from "./index.module.css";

import { useContext, useEffect } from "react";
import { redirect, useLoaderData, useNavigation } from "react-router-dom";

import ChatboxHeader from "@/components/ChatboxHeader";
import ChatLog from "@/components/ChatLog";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";

import { ConversationContext } from "@/contexts/conversation";
import { MessageContext } from "@/contexts/message";
import { UserContext } from "@/contexts/user";
import { WebsocketContext } from "@/contexts/websocket";


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
    const { send } = useContext(WebsocketContext);
    const { currentConv, dispatch } = useContext(MessageContext);
    // Only rendering messages of the following types
    const rendering_messages = new Set(["human", "ai"]);


    useEffect(() => {
        if (conversation.id === currentConv.id) {
            return;
        }
        // Update the message context.
        dispatch({
            type: "replaceAll",
            convId: conversation.id,
            messages: conversation.messages,
        });
    }, [conversation, currentConv, dispatch]);

    useEffect(() => {
        // `currentConv.id !== conversation.id` means that the `replaceAll` action is finished.
        if (currentConv.id !== conversation.id) {
            return;
        }
        // Already has messages, no need to check for init message.
        if (currentConv.messages && currentConv.messages.length > 0) {
            return;
        }

        // Check if there's an init message to send.
        const initMsgKey = `init-msg:${currentConv.id}`;
        const initMsg = sessionStorage.getItem(initMsgKey);
        if (initMsg === undefined || initMsg === null) {
            return;
        }

        // Send the init message if there's any.
        const message = JSON.parse(initMsg);
        const toSend = {
            ...message,
            additional_kwargs: {
                ...(message.additional_kwargs || {}),
                require_summarization: true,
            },
        };
        send(toSend);
        sessionStorage.removeItem(initMsgKey);
        dispatch({
            type: "added",
            convId: conversation.id,
            message: message,
        });
    }, [conversation, currentConv, dispatch, send]);

    const sendMessage = async (message) => {
        const payload = {
            conversation: conversation.id,
            from: username,
            ...message,
        };
        // `send` may throw an `InvalidStateError` if `WebSocket.readyState` is `CONNECTING`.
        // See <https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/send>
        send(payload);
        // append user input to chatlog
        dispatch({
            type: "added",
            convId: conversation.id,
            message: payload,
        });
        // update last_message_at of the conversation to re-order conversations
        // TODO: this seems buggy
        if (conversation.pinned && groupedConvs.pinned && groupedConvs.pinned[0]?.id !== conversation.id) {
            dispatchConv({
                type: "reordered",
                conv: { id: conversation.id, last_message_at: message.sent_at },
            });
        } else if (groupedConvs.Today && groupedConvs.Today[0]?.id !== conversation.id) {
            dispatchConv({
                type: "reordered",
                conv: { id: conversation.id, last_message_at: message.sent_at },
            });
        }
    };

    return (
        <section className={`${styles.chatbox} ${navigation.state === "loading" ? "loading" : ""}`}>
            <ChatboxHeader />
            <ChatLog>
                {/* We ignore system messages when displaying. */}
                {conversation && currentConv?.messages?.filter(message => rendering_messages.has(message.type)).map((message, index) => (
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
