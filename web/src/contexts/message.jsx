import { createContext, useReducer } from "react";
import PropTypes from "prop-types";


/**
 * messages, dispatch
 */
export const MessageContext = createContext({
    messages: [],
    dispatch: () => { },
});

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

export const messagesReducer = (messages, action) => {
    switch (action.type) {
    case "added": {
        // find reversly could potentially be faster as the full message usually is the last one (streamed).
        const match = messages.findLastIndex(message => message.id === action.message.id);
        if (match !== -1) {
            // message already exists, ignore it
            return messages;
        }
        return [...messages, { ...action.message }];
    }
    case "appended": {
        const match = messages.findLastIndex(message => message.id === action.message.id);
        if (match === -1) {
            // we don't have this message, ignore it
            // this could happen when the user switch to another conversation and switch back
            return messages;
        }
        return [...messages.slice(0, match), { ...messages[match], content: messages[match].content + action.message.content }, ...messages.slice(match + 1)];
    }
    case "updated": {
        // find reversly could potentially be faster as the full message usually is the last one (streamed).
        const match = messages.findLastIndex(message => message.id === action.message.id);
        if (match === -1) {
            // message does not exist, ignore it
            return messages;
        }
        return [...messages.slice(0, match), { ...messages[match], ...action.message }, ...messages.slice(match + 1)];
    }
    case "replaceAll": {
        return [...action.messages]
    }
    default: {
        console.error("Unknown action: ", action);
        return messages;
    }
    }
};
