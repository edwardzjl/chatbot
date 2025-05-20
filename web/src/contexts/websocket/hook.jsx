import { useContext } from "react";

import { WebsocketContext } from "./index";

export const useWebsocket = () => {
    const context = useContext(WebsocketContext);
    if (context === undefined) {
        throw new Error("useWebsocket must be used within a WebsocketProvider");
    }
    return context;
};
