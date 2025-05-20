import { useContext } from "react";

import { MessageContext } from "./index";

export const useCurrentConv = () => {
    const context = useContext(MessageContext);
    if (context === undefined) {
        throw new Error("useCurrentConv must be used within a MessageProvider");
    }
    return context;
};
