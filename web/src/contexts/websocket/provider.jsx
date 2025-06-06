import { useCallback, useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";

import { WebsocketContext } from "./index";


export const WebsocketProvider = ({ children }) => {
    const [isReady, setIsReady] = useState(false);
    const messageHandlers = useRef([]);

    const ws = useRef(null);

    useEffect(() => {
        const conn = () => {
            const wsurl = window.location.origin.replace(/^http/, "ws") + "/api/chat";
            console.debug("connecting to", wsurl);
            ws.current = new WebSocket(wsurl);

            ws.current.onopen = () => {
                console.debug("connected to", wsurl);
                setIsReady(true);
            };
            ws.current.onclose = () => {
                console.debug("connection closed");
                setIsReady(false);
                setTimeout(() => {
                    conn();
                }, 1000);
            };
            ws.current.onerror = (err) => {
                console.error("connection error", err);
                ws.current.close();
            };
            ws.current.onmessage = (event) => {
                messageHandlers.current.forEach(handler => {
                    try {
                        handler(event.data);
                    } catch (error) {
                        console.error("Error in message handler", error);
                    }
                })
            };
        }
        conn();

        return () => {
            // Only close the connection if it's open
            // See <https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/readyState#websocket.open>
            if (ws.current.readyState === 1) {
                ws.current.close();
            }
        };
    }, []);

    const send = useCallback(async (message) => {
        const MAX_RETRIES = 5;
        const interval = 500;  // milliseconds
        let retries = 0;

        while (retries < MAX_RETRIES) {
            try {
                ws.current?.send(JSON.stringify(message));
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
    }, []);

    const registerMessageHandler = useCallback((handler) => {
        messageHandlers.current.push(handler);
        return handler; // Return for unregistration reference
    }, []);

    const unregisterMessageHandler = useCallback((handler) => {
        messageHandlers.current = messageHandlers.current.filter(h => h !== handler);
    }, []);

    return (
        <WebsocketContext.Provider
            value={{
                ready: isReady,
                send,
                registerMessageHandler,
                unregisterMessageHandler,
            }}
        >
            {children}
        </WebsocketContext.Provider>
    )
};

WebsocketProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
