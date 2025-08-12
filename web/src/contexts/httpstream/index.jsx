import { createContext } from "react";


/**
 * HTTP streaming context to replace WebSocket
 * Provides: ready, send, registerMessageHandler, unregisterMessageHandler
 */
export const HttpStreamContext = createContext({
    ready: false,
    send: () => { },
    registerMessageHandler: () => { },
    unregisterMessageHandler: () => { },
});
