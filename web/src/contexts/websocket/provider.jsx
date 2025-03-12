import { useCallback, useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";

import { WebsocketContext } from "./index";


export const WebsocketProvider = ({ children }) => {
    const [isReady, setIsReady] = useState(false);
    const [messageHandlers, setMessageHandlers] = useState([]);

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
                messageHandlers.forEach(handler => {
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
    }, [messageHandlers]);

    const registerMessageHandler = useCallback((handler) => {
        setMessageHandlers(prev => [...prev, handler]);
        return handler; // Return for unregistration reference
    }, []);

    const unregisterMessageHandler = useCallback((handler) => {
        setMessageHandlers(prev => prev.filter(h => h !== handler));
    }, []);

    return (
        <WebsocketContext.Provider
            value={{
                ready: isReady,
                send: useCallback((...args) => ws.current?.send(...args), []),
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
