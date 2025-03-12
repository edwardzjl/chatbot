import { createContext } from "react";


/**
 * messages, dispatch
 */
export const MessageContext = createContext({
    messages: [],
    dispatch: () => { },
});
