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
                ...conversations.map(c => { return { ...c, active: false } }),
            ];
        }
        case "deleted": {
            const toDelete = conversations.find((c) => {
                return c.id === action.id;
            })
            const remaining = conversations.filter((c) => c.id !== action.id);
            // nothing left, just return
            if (remaining.length === 0) {
                return [];
            }
            // not deleting active conversation, just return
            if (!toDelete.active) {
                return remaining;
            }
            // deleting active conversation, activate the first one
            return [{ ...remaining[0], active: true }, ...remaining.slice(1)]
        }
        case "updated": {
            return conversations.map((c) => {
                if (c.id === action.conversation.id) {
                    return { ...c, ...action.conversation };
                } else {
                    return c;
                }
            });
        }
        case "selected": {
            if (conversations[0].id === action.id && conversations[0].active) {
                return conversations;
            }
            return conversations.map((c) => {
                if (c.id === action.id) {
                    return {
                        ...c,
                        active: true,
                    };
                } else {
                    return {
                        ...c,
                        active: false,
                    };
                }
            });
        }
        case "moveToFirst": {
            const toMove = conversations.find((c) => {
                return c.id === action.id;
            })
            const others = conversations.filter((c) => c.id !== action.id);
            return [toMove, ...others];
        }
        case "replaceAll": {
            // set the first conversation to be active
            return [{ ...action.conversations[0], active: true }, ...action.conversations.slice(1).map((c) => { return { ...c, active: false } })]
        }
        case "messageAdded": {
            return conversations.map((c) => {
                if (c.id === action.id) {
                    return { ...c, messages: [...c.messages, action.message] };
                } else {
                    return c;
                }
            });
        }
        case "messageAppended": {
            return conversations.map((c) => {
                if (c.id === action.id) {
                    const lastMsg = c.messages[c.messages.length - 1];
                    return {
                        ...c,
                        messages: [...c.messages.slice(0, -1), { ...lastMsg, content: lastMsg.content + action.message.content }]
                    };
                } else {
                    return c;
                }
            });
        }
        default: {
            throw Error("Unknown action: " + action.type);
        }
    }
};

export const getCurrentConversation = (conversations) => {
    return conversations.find((c) => c.active);
}
