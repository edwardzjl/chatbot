import { createContext, useEffect, useReducer, useState } from "react";

import {
    createConversation,
    getConversations,
    getConversation,
} from "requests";


/**
 * conversations, currentConversation, dispatch
 */
export const ConversationContext = createContext({
    conversations: [],
    currentConv: undefined,
    dispatch: () => { },
});

export const ConversationProvider = ({ children }) => {
    const [conversations, dispatch] = useReducer(
        conversationsReducer,
        /** @type {[{id: string, title: string?, messages: Array, active: boolean}]} */
        []
    );
    const [currentConv, setCurrentConv] = useState(undefined);

    useEffect(() => {
        const initialization = async () => {
            let convs = await getConversations();
            if (!convs.length) {
                console.debug("no chats, initializing a new one");
                const conv = await createConversation();
                convs = [conv];
            }
            const detailedConv = await getConversation(convs[0].id);
            convs[0] = { active: true, ...detailedConv };
            dispatch({
                type: "replaceAll",
                conversations: convs,
            });
        };

        initialization();

        return () => { };
    }, []);

    useEffect(() => {
        if (conversations?.length > 0) {
            const currentConv = conversations.find((c) => c.active);
            if (!currentConv) {
                console.error("no active conversation");
                return;
            }
            setCurrentConv(currentConv);
        }
    }, [conversations]);

    return (
        <ConversationContext.Provider value={{ conversations, currentConv, dispatch }}>
            {children}
        </ConversationContext.Provider>
    );
}


/**
 * Reducer for conversations.
 * @param {Array} conversations 
 * @param {string} conversation.id
 * @param {string} conversation.title
 * @param {Array} conversation.messages
 * @param {boolean} conversation.active
 * @param {*} action 
 * @returns 
 */
export const conversationsReducer = (conversations, action) => {
    switch (action.type) {
        case "added": {
            // new conversation will be added to the first and be activated.
            return [
                { ...action.conversation, messages: [], active: true },
                ...conversations.map(c => ({ ...c, active: false })),
            ];
        }
        case "deleted": {
            return conversations.filter((c) => c.id !== action.id);
        }
        case "updated": {
            return conversations.map((c) => (c.id !== action.conversation.id ? c : { ...c, ...action.conversation }));
        }
        case "selected": {
            return conversations.map((c) => (c.id === action.data.id ? { ...action.data, active: true } : { ...c, active: false }));
        }
        case "moveToFirst": {
            const toMove = conversations.find((c) => c.id === action.id)
            const others = conversations.filter((c) => c.id !== action.id);
            return [toMove, ...others];
        }
        case "replaceAll": {
            return [...action.conversations]
        }
        case "messageAdded": {
            return conversations.map((c) => {
                if (c.id !== action.id) {
                    return c;
                }
                // find reversly could potentially be faster as the full message usually is the last one (streamed).
                const match = c.messages.findLastIndex(message => message.id === action.message.id);
                if (match !== -1) {
                    // message already exists, ignore it
                    return c;
                }
                return { ...c, messages: [...c.messages, { ...action.message }] }
            }
            );
        }
        case "messageAppended": {
            return conversations.map((c) => {
                if (c.id !== action.id) {
                    return c;
                }
                // find reversly could potentially be faster as the streaming message usually is the last one.
                const match = c.messages.findLastIndex(message => message.id === action.message.id);
                if (match === -1) {
                    // we don't have this message, ignore it
                    // this could happen when the user switch to another conversation and switch back
                    return c;
                }
                return {
                    ...c,
                    messages: [...c.messages.slice(0, match), { ...c.messages[match], content: c.messages[match].content + action.message.content }, ...c.messages.slice(match + 1)]
                };
            });
        }
        case "feedback": {
            // action: { id, idx, feedback }
            // action.id: conversation id
            // action.idx: message index
            // action.feedback: feedback object, thumbup / thumbdown
            return conversations.map((c) => {
                if (c.id !== action.id) {
                    return c;
                }
                const msg = c.messages[action.idx];
                return {
                    ...c,
                    messages: [...c.messages.slice(0, action.idx), { ...msg, feedback: action.feedback }, ...c.messages.slice(action.idx + 1)]
                };
            });
        }
        default: {
            console.error("Unknown action: ", action);
            return conversations;
        }
    }
};
