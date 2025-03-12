import { createContext } from "react";


/**
 * ready, data, send
 */
export const WebsocketContext = createContext({
    ready: false,
    data: null,
    send: () => { }
});
