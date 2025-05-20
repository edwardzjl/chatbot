import { useContext } from "react";

import { ConversationContext } from "./index";

export const useConversations = () => {
    const context = useContext(ConversationContext);
    if (context === undefined) {
        throw new Error("useConversations must be used within a ConversationProvider");
    }
    return context;
};
