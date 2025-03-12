import { createContext } from "react";

/**
 * messages, dispatch
 */
export const ConversationContext = createContext({
    groupedConvs: {},
    dispatch: () => { },
});
