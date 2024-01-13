import { createContext, useReducer } from "react";


/**
 * messages, dispatch
 */
export const MessageContext = createContext({
    messages: [],
    dispatch: () => { },
});

export const MessageProvider = ({ children }) => {
    const [messages, dispatch] = useReducer(
        messagessReducer,
        /** @type {[{id: string, title: string?, messages: Array, active: boolean}]} */
        []
    );

    return (
        <MessageContext.Provider value={{ messages, dispatch }}>
            {children}
        </MessageContext.Provider>
    );
}


export const messagessReducer = (messages, action) => {
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
        case "feedback": {
            // action: { idx, feedback }
            // action.idx: message index
            // action.feedback: feedback object, thumbup / thumbdown
            const msg = messages[action.idx];
            return [...messages.slice(0, action.idx), { ...msg, feedback: action.feedback }, ...messages.slice(action.idx + 1)];
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
