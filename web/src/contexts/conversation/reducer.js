
export const conversationReducer = (groupedConvsArray, action) => {
    switch (action.type) {
    case "added": {
        const { conv } = action;
        const { groupKey, sortValue } = getConversationGroupingInfo(conv);

        const nextGroupedConvsArray = [...groupedConvsArray];
        for (let i = 0; i < nextGroupedConvsArray.length; i++) {
            const currentGroup = nextGroupedConvsArray[i];

            if (groupKey === currentGroup.key) {
                // target group found, insert the conversation
                const updatedConversations = sortConvs([conv, ...currentGroup.conversations]);
                nextGroupedConvsArray[i] = {
                    ...currentGroup,
                    conversations: updatedConversations,
                };
                return nextGroupedConvsArray;
            } else if (sortValue > currentGroup.sortValue) {
                // found a group with a smaller sort value, insert before it
                const newGroup = {
                    key: groupKey,
                    conversations: [conv],
                    sortValue: sortValue
                };
                nextGroupedConvsArray.splice(i, 0, newGroup);
                return nextGroupedConvsArray;
            }
        }

        // no group found with a smaller sort value, add to the end
        const newGroup = {
            groupKey: groupKey,
            sortValue: sortValue,
            conversations: [conv],
        };
        nextGroupedConvsArray.push(newGroup);

        return nextGroupedConvsArray;
    }
    case "deleted": {
        const { conv } = action;
        const nextGroupedConvsArray = [...groupedConvsArray];

        for (let i = 0; i < nextGroupedConvsArray.length; i++) {
            const currentGroup = nextGroupedConvsArray[i];
            const updatedConversations = currentGroup.conversations.filter(c => c.id !== conv.id);

            if (updatedConversations.length < currentGroup.conversations.length) {
                nextGroupedConvsArray[i] = {
                    ...currentGroup,
                    conversations: updatedConversations,
                };
                // early return if we found and removed the conversation
                return nextGroupedConvsArray.filter(group => group.conversations.length > 0);
            }
        }

        console.warn(`Conversation with id ${conv.id} not found in any group for deletion.`);
        return groupedConvsArray;
    }
    case "renamed": {
        const { conv } = action;
        const nextGroupedConvsArray = [...groupedConvsArray];

        for (let i = 0; i < nextGroupedConvsArray.length; i++) {
            const currentGroup = nextGroupedConvsArray[i];
            const convIndex = currentGroup.conversations.findIndex(c => c.id === conv.id);

            if (convIndex !== -1) {
                const updatedConversations = [...currentGroup.conversations];
                updatedConversations[convIndex] = {
                    ...updatedConversations[convIndex],
                    title: conv.title,
                };

                nextGroupedConvsArray[i] = {
                    ...currentGroup,
                    conversations: updatedConversations,
                };

                return nextGroupedConvsArray;
            }
        }

        console.warn(`Conversation with id ${conv.id} not found in any group for renaming.`);
        return groupedConvsArray;
    }
    case "reordered": {
        const { conv } = action;
        const currentAllConvs = getAllConvsFromState(groupedConvsArray);

        const updatedConvs = currentAllConvs.map((c) => {
            if (c.id === conv.id) {
                return { ...c, last_message_at: conv.last_message_at, pinned: conv.pinned };
            }
            return c;
        });

        const rawGroupedConvs = groupConvs(updatedConvs);
        return flattenAndSortGroupedConvs(rawGroupedConvs);
    }
    case "replaceAll": {
        const grouped = groupConvs(action.convs);
        return flattenAndSortGroupedConvs(grouped);
    }
    default: {
        console.error("Unknown action: ", action);
        return groupedConvsArray;
    }
    }
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
    const datesCache = getGroupComparisonDates();

    const grouped = {};
    conversations.forEach((item) => {
        const { groupKey, sortValue } = getConversationGroupingInfo(item, datesCache);

        if (!grouped[groupKey]) {
            grouped[groupKey] = {
                conversations: [],
                sortValue: sortValue
            };
        }
        grouped[groupKey].conversations.push(item);
    });

    return grouped;
};

/**
 * Transforms and sorts a grouped conversations object into a flattened array
 * suitable for rendering. All groups are sorted in descending order of their `groupSortValue`.
 *
 * @param {Object} groupedConvs - The object returned by `groupConvs`,
 * where each value is an object { conversations: Array, groupSortValue: number }.
 * @returns {Array<Object>} A sorted array of group objects, each containing
 * `key` (group name) and `conversations` (array of convs).
 */
export const flattenAndSortGroupedConvs = (groupedConvs) => {
    if (!groupedConvs) {
        return [];
    }

    const groupEntries = Object.entries(groupedConvs)
        .map(([key, value]) => ({
            key: key,
            conversations: value.conversations || [],
            sortValue: value.sortValue,
        }))
        .filter(group => group.conversations && group.conversations.length > 0);

    groupEntries.sort((a, b) => b.sortValue - a.sortValue);

    // sort conversations within each group
    groupEntries.forEach(group => {
        group.conversations = sortConvs(group.conversations);
    });

    return groupEntries;
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
 * Calculates and returns key date objects for grouping conversations.
 * All returned Date objects are set to 00:00:00 for accurate day-level comparison.
 *
 * @returns {Object} An object containing:
 * - today: Date object for the current day at 00:00:00.
 * - yesterday: Date object for yesterday at 00:00:00.
 * - lastSevenDays: Date object for 7 days ago at 00:00:00.
 */
export const getGroupComparisonDates = () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const lastSevenDays = new Date(today);
    lastSevenDays.setDate(lastSevenDays.getDate() - 7);

    return {
        today,
        yesterday,
        lastSevenDays,
    };
};

/**
 * Determines the group key and a numerical sort value for a given conversation.
 * The sort value allows for consistent chronological ordering of groups, with 'pinned' having the highest priority.
 *
 * @param {Object} conv - The conversation object, must contain `pinned` (boolean) and `last_message_at` (timestamp or Date string).
 * @param {Object} [datesCache] - Optional: An object containing pre-calculated comparison dates (`today`, `yesterday`, `lastSevenDays`).
 * If not provided, `getGroupComparisonDates()` will be called.
 * @returns {{groupKey: string, sortValue: number}} An object containing the determined group key and its corresponding sort value.
 */
export const getConversationGroupingInfo = (conv, datesCache) => {
    if (conv.pinned) {
        return {
            groupKey: "pinned",
            sortValue: Number.MAX_SAFE_INTEGER,
        };
    }
    const { today, yesterday, lastSevenDays } = datesCache || getGroupComparisonDates();
    const itemDate = new Date(conv.last_message_at);
    itemDate.setHours(0, 0, 0, 0);
    if (itemDate.getTime() === today.getTime()) {
        return {
            groupKey: "Today",
            sortValue: today.getTime(),
        };
    }
    if (itemDate.getTime() === yesterday.getTime()) {
        return {
            groupKey: "Yesterday",
            sortValue: yesterday.getTime(),
        };
    }
    if (itemDate.getTime() >= lastSevenDays.getTime()) {
        return {
            groupKey: "Last Seven Days",
            sortValue: lastSevenDays.getTime(),
        }
    }
    return {
        groupKey: `${itemDate.toLocaleString("default", { month: "long" })} ${itemDate.getFullYear()}`,
        sortValue: new Date(itemDate.getFullYear(), itemDate.getMonth(), 1).getTime(),
    }
};

/**
 * Helper function to extract all flattened conversations from the grouped state array.
 * @param {Array<Object>} groupedConvsArray - The reducer's state, an array of grouped conversations.
 * @returns {Array<Object>} A flat array of all conversation objects.
 */
const getAllConvsFromState = (groupedConvsArray) => {
    if (!groupedConvsArray || groupedConvsArray.length === 0) {
        return [];
    }
    return groupedConvsArray.flatMap(group => group.conversations);
};
