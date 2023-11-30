import { createContext, useEffect, useReducer } from "react";

import {
    createConversation,
    getConversations,
    getConversation,
} from "requests";


/**
 * conversations, dispatch
 */
export const ConversationContext = createContext([], () => { });

export const ConversationProvider = ({ children }) => {
    const [conversations, dispatch] = useReducer(
        conversationsReducer,
        /** @type {[{id: string, title: string?, messages: Array, active: boolean}]} */
        []
    );

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

    return (
        <ConversationContext.Provider value={[conversations, dispatch]}>
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
            return conversations.map((c) =>
                c.id !== action.id ? c : { ...c, messages: [...c.messages, { ...action.message }] }
            );
        }
        case "messageAppended": {
            return conversations.map((c) => {
                if (c.id !== action.id) {
                    return c;
                }
                const lastMsg = c.messages[c.messages.length - 1];
                return {
                    ...c,
                    messages: [...c.messages.slice(0, -1), { ...lastMsg, content: lastMsg.content + action.message.content }]
                };
            });
        }
        default: {
            throw Error("Unknown action: " + action.type);
        }
    }
};
