import { useReducer } from "react";
import PropTypes from "prop-types";

import { MessageContext } from "./index";
import { messagesReducer } from "./reducer";


export const MessageProvider = ({ children }) => {
    const [messages, dispatch] = useReducer(
        messagesReducer,
        /** @type {[{id: string, title: string?, messages: Array, active: boolean}]} */
        []
    );

    return (
        <MessageContext.Provider value={{ messages, dispatch }}>
            {children}
        </MessageContext.Provider>
    );
};

MessageProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
