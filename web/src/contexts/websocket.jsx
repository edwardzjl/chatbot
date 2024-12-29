import { createContext, useCallback, useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";


/**
 * ready, data, send
 */
export const WebsocketContext = createContext({
    ready: false,
    data: null,
    send: () => { }
});

export const WebsocketProvider = ({ children }) => {
    const [isReady, setIsReady] = useState(false);
    const [val, setVal] = useState(null);

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
                setVal(event.data);
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

    return (
        <WebsocketContext.Provider
            value={{
                ready: isReady,
                data: val,
                send: useCallback((...args) => ws.current?.send(...args), []),
            }}
        >
            {children}
        </WebsocketContext.Provider>
    )
};

WebsocketProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
