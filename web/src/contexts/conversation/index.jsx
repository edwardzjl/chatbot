import { createContext } from "react";

/**
 * groupedConvsArray, dispatch
 */
export const ConversationContext = createContext({
    groupedConvsArray: [],
    dispatch: () => { },
    hasMore: false,
    fetchMoreConvs: () => { },
    isLoading: false,
});
