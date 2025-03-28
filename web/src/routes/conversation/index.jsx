import styles from "./index.module.css";

import { useContext, useEffect, useRef, useState } from "react";
import { redirect, useLoaderData, useNavigation } from "react-router-dom";
// import { loadPyodide } from "pyodide";

import ChatboxHeader from "@/components/ChatboxHeader";
import ChatLog from "@/components/ChatLog";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";

import { ConversationContext } from "@/contexts/conversation";
import { MessageContext } from "@/contexts/message";
import { UserContext } from "@/contexts/user";
import { WebsocketContext } from "@/contexts/websocket";

import { workerManager } from "@/pybox/manager.js";
// import { asyncRun } from "./workerApi.js";


async function loader({ params }) {
    const resp = await fetch(`/api/conversations/${params.convId}`, {});
    if (!resp.ok) {
        return redirect("/");
    }
    const conversation = await resp.json();
    return { conversation };
}

const HEARTBEAT_INTERVAL = 5000; // Send heartbeat every 5 seconds

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
    const { messages, dispatch } = useContext(MessageContext);
    // Only rendering messages of the following types
    const rendering_messages = new Set(["human", "ai"]);

    const [pybox, setPybox] = useState(null);
    const heartbeatIntervalRef = useRef(null);


    useEffect(() => {
        // Update the message context.
        dispatch({
            type: "replaceAll",
            messages: conversation.messages,
        });
        if (conversation.messages && conversation.messages.length > 0) {
            // Already has messages, no need to check for init message.
            return;
        }

        // Check if there's an init message to send.
        const initMsgKey = `init-msg:${conversation.id}`;
        const initMsg = sessionStorage.getItem(initMsgKey);
        if (initMsg === undefined || initMsg === null) {
            return;
        }

        // Send the init message if there's any.
        const message = JSON.parse(initMsg);
        const attemptSend = async () => {
            const MAX_RETRIES = 5;
            const interval = 500;  // milliseconds
            let retries = 0;

            while (retries < MAX_RETRIES) {
                try {
                    send(JSON.stringify({ additional_kwargs: { require_summarization: true }, ...message }));
                    sessionStorage.removeItem(initMsgKey);
                    dispatch({
                        type: "added",
                        message: message,
                    });
                    break;
                } catch (error) {
                    if (error.name === "InvalidStateError") {
                        console.warn(`WebSocket not ready, retrying in 0.5 second... (${retries + 1}/${MAX_RETRIES})`);
                        retries++;
                        await new Promise(resolve => setTimeout(resolve, interval));
                    } else {
                        console.error("Error sending init message:", error);
                        break;
                    }
                }
            }
        }

        attemptSend();

    }, [conversation, dispatch, send]);


    useEffect(() => {
        if (conversation.id) {
            workerManager.getWorkerForConversation(conversation.id).then(setPybox);

            // Start heartbeat when component mounts and has a conversation ID
            heartbeatIntervalRef.current = setInterval(() => {
                workerManager.sendHeartbeat(conversation.id);
            }, HEARTBEAT_INTERVAL);
        }

        return () => {
            // Stop heartbeat when component unmounts
            clearInterval(heartbeatIntervalRef.current);
        };
    }, [conversation.id]);

    // useEffect(() => {
    //     const initPyodide = async () => {
    //         const pyodide = await loadPyodide();

    //         // See <https://pyodide.org/en/stable/usage/file-system.html>
    //         // <https://developer.mozilla.org/en-US/docs/Web/API/StorageManager/getDirectory>
    //         // <https://developer.mozilla.org/en-US/docs/Web/API/File_System_API/Origin_private_file_system>
    //         // quota: <https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria>
    //         const dirHandle = await navigator.storage.getDirectory();
    //         const permissionStatus = await dirHandle.requestPermission({
    //             mode: "readwrite",
    //         });
    //         if (permissionStatus !== "granted") {
    //             throw new Error("readwrite access to directory not granted");
    //         }
    //         // See <https://pyodide.org/en/stable/usage/api/js-api.html#pyodide.mountNativeFS>
    //         const nativefs = await pyodide.mountNativeFS("/mount_dir", dirHandle);
    //         try {
    //             let stdout = "";
    //             pyodide.setStdout({ batched: (msg) => stdout += msg });
    //             await pyodide.runPythonAsync(`print("Hello from Python!")`);
    //             console.log("stdout", stdout);
    //         } catch (error) {
    //             // TODO: format error message for LLM
    //             // <https://pyodide.org/en/stable/usage/type-conversions.html#errors>
    //             // the `reformat_exception` does not seems to be what I want
    //             // The only useful thing I get for now is the `error.type`
    //             console.log("error type", error.type);
    //         }
    //         await nativefs.syncfs();
    //     }

    //     initPyodide();
    // }, []);

    const sendMessage = async (message) => {
        const payload = {
            conversation: conversation.id,
            from: username,
            ...message,
        };
        // `send` may throw an `InvalidStateError` if `WebSocket.readyState` is `CONNECTING`.
        // See <https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/send>
        send(JSON.stringify(payload));
        // append user input to chatlog
        dispatch({
            type: "added",
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


        // TODO: experiment only, run the content in pyodide directly
        if (!pybox) {
            workerManager.getWorkerForConversation(conversation.id).then(setPybox);
        }

        try {
            const response = await workerManager.runPython(conversation.id, message.content);
            if (response.result) {
                console.log("pyodideWorker result:", response.result);
                // TODO: 处理结果并更新聊天记录
            } else if (response.error) {
                console.error("pyodideWorker error:", response.error);
                // TODO: 处理错误并显示给用户
            }
        } catch (error) {
            console.error("Error running Python code:", error);
        }
    };

    return (
        <section className={`${styles.chatbox} ${navigation.state === "loading" ? "loading" : ""}`}>
            <ChatboxHeader />
            <ChatLog>
                {/* We ignore system messages when displaying. */}
                {conversation && messages?.filter(message => rendering_messages.has(message.type)).map((message, index) => (
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
