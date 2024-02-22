import { createContext, useEffect, useReducer } from "react";


/**
 * messages, dispatch
 */
export const ConversationContext = createContext({
    groupedConvs: {},
    dispatch: () => { },
});

const flatConvs = (groupedConvs) => {
    return Object.entries(groupedConvs).flatMap(([_, convs]) => (
        [...convs]
    ));
};

const sortConvs = (conversations) => {
    // sort by pinned and last_message_at
    // See <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/toSorted>
    // and <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#sorting_array_of_objects>
    return conversations.toSorted((a, b) => {
        if (a.pinned && !b.pinned) {
            return -1;
        }
        if (!a.pinned && b.pinned) {
            return 1;
        }
        if (a.last_message_at > b.last_message_at) {
            return -1;
        }
        if (a.last_message_at < b.last_message_at) {
            return 1;
        }
        return 0;
    });
};

const groupConvs = (conversations) => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const lastSevenDays = new Date(today);
    lastSevenDays.setDate(lastSevenDays.getDate() - 7);

    return Object.groupBy(conversations, (item) => {
        if (item.pinned) {
            return "pinned";
        }
        const itemDate = new Date(item.last_message_at);
        if (itemDate.toDateString() === today.toDateString()) {
            return "Today";
        } else if (itemDate.toDateString() === yesterday.toDateString()) {
            return "Yesterday";
        } else if (itemDate > lastSevenDays) {
            return "Last seven days";
        } else {
            return `${itemDate.toLocaleString("default", { month: "long" })} ${itemDate.getFullYear()}`;
        }
    });
};

export const ConversationProvider = ({ children }) => {

    // It seems that I can't use async function as the `init` param.
    // So I opt to use `useEffect` instead.
    const [groupedConvs, dispatch] = useReducer(
        conversationReducer,
        {},
    );

    useEffect(() => {
        const init = async () => {
            const convs = await fetch("/api/conversations", {
            }).then((res) => res.json());

            // This assumes that the convs are already sorted by the server.
            // Otherwise, I need to call `sortConvs` first.
            const groupedConvs = groupConvs(convs);

            dispatch({
                type: "replaceAll",
                groupedConvs
            });
        };

        init();
    }, []);

    return (
        <ConversationContext.Provider value={{ groupedConvs, dispatch }}>
            {children}
        </ConversationContext.Provider>
    );
}


export const conversationReducer = (groupedConvs, action) => {
    switch (action.type) {
        case "added": {
            // action.conv: { id, title, created_at, last_message_at, owner, pinned }
            // I'm not sorting convs here, so the order matters.
            if (groupedConvs.Today) {
                return { ...groupedConvs, Today: [action.conv, ...groupedConvs.Today || []] };
            }
            if (groupedConvs.pinned) {
                return {pinned: groupedConvs.pinned, Today: [action.conv], ...groupedConvs};
            }
            return {Today: [action.conv], ...groupedConvs};
        }
        case "deleted": {
            const convs = flatConvs(groupedConvs);
            return groupConvs(convs.filter((conv) => conv.id !== action.convId));
        }
        case "renamed": {
            const convs = flatConvs(groupedConvs);
            return groupConvs(convs.map((conv) => {
                if (conv.id === action.convId) {
                    return { ...conv, title: action.title };
                }
                return conv;
            }));
        }
        case "reordered": {
            const convs = flatConvs(groupedConvs);
            const updatedConvs = convs.map((conv) => {
                if (conv.id === action.conv.id) {
                    return { ...conv, ...action.conv };
                }
                return conv;
            });
            const sortedConvs = sortConvs(updatedConvs);
            return groupConvs(sortedConvs);
        }
        case "replaceAll": {
            return { ...action.groupedConvs };
        }
        default: {
            console.error("Unknown action: ", action);
            return groupedConvs;
        }
    }
};
