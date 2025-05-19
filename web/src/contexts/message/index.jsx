import { createContext } from "react";


/**
 * currentConv, dispatch
 */
export const MessageContext = createContext({
    currentConv: {id: null, messages: []},
    dispatch: () => { },
});
