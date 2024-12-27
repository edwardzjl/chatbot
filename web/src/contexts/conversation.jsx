import { createContext, useEffect, useReducer } from "react";
import PropTypes from "prop-types";


/**
 * messages, dispatch
 */
export const ConversationContext = createContext({
    groupedConvs: {},
    dispatch: () => { },
});

/**
 * Flattens a grouped conversation object into a single array of conversations.
 * 
 * The function takes an object where the keys represent group identifiers, and the values are arrays of conversations.
 * It returns a new array containing all the individual conversations from the grouped object, preserving their order.
 * 
 * @param {Object} groupedConvs - An object where each key is a group identifier, and each value is an array of conversations.
 * @returns {Array} A flattened array containing all conversations from the input object.
 */
export const flatConvs = (groupedConvs) => {
    return Object.values(groupedConvs).flatMap(convs => [...convs]);
};

/**
 * Sorts an array of conversations based on their pinned status and the last message timestamp.
 * 
 * The function first sorts conversations by whether they are pinned, with pinned conversations appearing first.
 * If two conversations have the same pinned status, they are then sorted by the `last_message_at` timestamp, with the most recent messages appearing first.
 * 
 * This function uses `Array.toSorted()` to create a new array with the conversations sorted according to the specified criteria.
 * 
 * @param {Array} conversations - An array of conversation objects, where each object contains at least a `pinned` boolean and a `last_message_at` timestamp.
 * @returns {Array} A new array of conversations sorted first by pinned status and then by the `last_message_at` timestamp in descending order.
 */
export const sortConvs = (conversations) => {
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

/**
 * Groups an array of conversations based on their pinned status and the date of the last message.
 * 
 * The function categorizes conversations into the following groups:
 * - "pinned": for pinned conversations
 * - "Today": for conversations with the latest message sent today
 * - "Yesterday": for conversations with the latest message sent yesterday
 * - "Last seven days": for conversations with the latest message sent within the last seven days
 * - A month-year format (e.g., "January 2024") for conversations older than seven days
 * 
 * This is achieved by comparing the `last_message_at` timestamp of each conversation with the current date, yesterday's date, and a week-old date.
 * 
 * @param {Array} conversations - An array of conversation objects, where each object contains at least a `last_message_at` timestamp and a `pinned` boolean.
 * @returns {Object} An object where each key is a group label and each value is an array of conversations that belong to that group.
 */
export const groupConvs = (conversations) => {
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
};

ConversationProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export const conversationReducer = (groupedConvs, action) => {
    switch (action.type) {
        case "added": {
            // NOTE: To save computation, this does not sort nor group the convs.
            // It simply insert the new conv to the first element of group 'Today'.
            // So the returnning order matters.

            // action.conv: { id, title, created_at, last_message_at, owner, pinned }
            const { conv } = action;
            // Update 'Today' group only if it exists, without side effects
            const updatedGroupedConvs = { ...groupedConvs };

            if (updatedGroupedConvs.Today) {
                updatedGroupedConvs.Today = [conv, ...updatedGroupedConvs.Today];
            } else {
                updatedGroupedConvs.Today = [conv];
            }

            return updatedGroupedConvs;
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
