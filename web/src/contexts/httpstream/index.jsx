import { createContext } from "react";


/**
 * HTTP streaming context to replace WebSocket
 * Provides: send, registerMessageHandler, unregisterMessageHandler
 */
export const HttpStreamContext = createContext({
    send: () => { },
    registerMessageHandler: () => { },
    unregisterMessageHandler: () => { },
});
