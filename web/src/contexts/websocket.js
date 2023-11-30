import { createContext, useContext, useEffect, useRef, useState } from "react";

import { ConversationContext } from "contexts/conversation";
import { SnackbarContext } from "contexts/snackbar";


/**
 * ready, send
 */
export const WebsocketContext = createContext(false, () => { });

export const WebsocketProvider = ({ children }) => {
    const [, dispatch] = useContext(ConversationContext);
    const [, setSnackbar] = useContext(SnackbarContext);
    const [isReady, setIsReady] = useState(false);
    const ws = useRef(null);

    useEffect(() => {
        const conn = () => {
            const wsurl = window.location.origin.replace(/^http/, "ws") + "/api/chat";
            console.debug("connecting to", wsurl);
            const socket = new WebSocket(wsurl);

            socket.onopen = () => {
                console.debug("connected to", wsurl);
                setIsReady(true);
            }
            socket.onclose = () => {
                console.debug("connection closed");
                setIsReady(false);
                setTimeout(() => {
                    conn();
                }, 1000);
            }
            socket.onerror = (err) => {
                console.error("connection error", err);
                ws.current.close();
            };
            socket.onmessage = (event) => {
                // <https://react.dev/learn/queueing-a-series-of-state-updates>
                // <https://react.dev/learn/updating-arrays-in-state>
                try {
                    const { type, conversation, from, content } = JSON.parse(event.data);
                    switch (type) {
                        case "start":
                            dispatch({
                                type: "messageAdded",
                                id: conversation,
                                message: { from: from, content: content || "", type: "stream" },
                            });
                            break;
                        case "stream":
                            dispatch({
                                type: "messageAppended",
                                id: conversation,
                                message: { from: from, content: content, type: "stream" },
                            });
                            break;
                        case "error":
                            setSnackbar({
                                open: true,
                                severity: "error",
                                message: "Something goes wrong, please try again later.",
                            });
                            break;
                        case "text":
                            dispatch({
                                type: "messageAdded",
                                id: conversation,
                                message: { from: from, content: content, type: "text" },
                            });
                            break;
                        case "end":
                            break;
                        default:
                            console.warn("unknown message type", type);
                    }
                } catch (error) {
                    console.debug("not a json message", event.data);
                }
            }
            return socket;
        }
        ws.current = conn();

        return () => {
            ws.current.close();
        };
    }, []);

    return (
        <WebsocketContext.Provider value={[isReady, ws.current?.send.bind(ws.current)]}>
            {children}
        </WebsocketContext.Provider>
    );
};
