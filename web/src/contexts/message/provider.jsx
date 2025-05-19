import { useReducer } from "react";
import PropTypes from "prop-types";

import { MessageContext } from "./index";
import { messagesReducer } from "./reducer";


export const MessageProvider = ({ children }) => {
    const [currentConv, dispatch] = useReducer(
        messagesReducer,
        /** @type {[{id: string, title: string?, messages: Array, active: boolean}]} */
        {id: null, messages: []}
    );

    return (
        <MessageContext.Provider value={{ currentConv, dispatch }}>
            {children}
        </MessageContext.Provider>
    );
};

MessageProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
