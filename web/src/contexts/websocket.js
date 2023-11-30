import { createContext, useEffect, useRef, useState } from "react";

/**
 * ready, value, send
 */
export const WebsocketContext = createContext(false, null, () => { });

export const WebsocketProvider = ({ children }) => {
    const [isReady, setIsReady] = useState(false);
    const [val, setVal] = useState(null);

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
            socket.onmessage = (event) => setVal(event.data);
            return socket;
        }
        ws.current = conn();

        return () => {
            ws.current.close();
        };
    }, []);

    return (
        <WebsocketContext.Provider value={[isReady, val, ws.current?.send.bind(ws.current)]}>
            {children}
        </WebsocketContext.Provider>
    );
};
