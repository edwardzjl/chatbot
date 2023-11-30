import { createContext, useReducer } from "react";

import { conversationsReducer } from "conversationsReducer";

/**
 * conversations, dispatch
 */
export const ConversationContext = createContext([], () => { });

export const ConversationProvider = ({ children }) => {
    const [conversations, dispatch] = useReducer(
        conversationsReducer,
        /** @type {[{id: string, title: string?, messages: Array, active: boolean}]} */
        []
    );
    return (
        <ConversationContext.Provider value={[conversations, dispatch]}>
            {children}
        </ConversationContext.Provider>
    );
}
