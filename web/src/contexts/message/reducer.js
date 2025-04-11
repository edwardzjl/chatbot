
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
        return [
            ...messages.slice(0, match),
            {
                ...messages[match],
                // TODO: content can be string or array of objects. Need to consider how to merge
                content: messages[match].content + action.message.content,
                additional_kwargs: deepMerge(messages[match].additional_kwargs, action.message.additional_kwargs)
            },
            ...messages.slice(match + 1)
        ];
    }
    case "updated": {
        // find reversly could potentially be faster as the full message usually is the last one (streamed).
        const match = messages.findLastIndex(message => message.id === action.message.id);
        if (match === -1) {
            // message does not exist, ignore it
            return messages;
        }
        return [
            ...messages.slice(0, match),
            { ...messages[match], ...action.message },
            ...messages.slice(match + 1)
        ];
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


/**
 * Deeply merges two JavaScript objects with custom merge rules.
 *
 * Merge strategy:
 * - If the key exists in both objects:
 *   - If types differ (including array vs. object), `b`'s value overrides `a`'s.
 *   - Strings are concatenated.
 *   - Numbers are added.
 *   - Arrays are concatenated.
 *   - Objects are merged recursively.
 * - If the key only exists in `b`, it is added to the result.
 * - `null` and `undefined` values in `b` are ignored (they do not override `a`).
 *
 * @param {Object} a - The base object to merge into.
 * @param {Object} b - The object whose values will be merged into `a`.
 * @returns {Object} A new object that is the result of deeply merging `a` and `b`.
 */
export const deepMerge = (a, b) => {
    const result = { ...a };

    // Manipulate on non-null b entries
    // use '!=' and '==' to check null or undefined
    const filteredEntries = Object.entries(b).filter(([, bVal]) => bVal != null);
    for (const [key, bVal] of filteredEntries) {
        if (!(key in result)) {
            result[key] = bVal;
            continue;
        }

        const aVal = result[key];
        if (typeof aVal !== typeof bVal || Array.isArray(aVal) !== Array.isArray(bVal)) {
            result[key] = bVal;
        } else if (typeof aVal === "string") {
            result[key] = aVal + bVal;
        } else if (typeof aVal === "number") {
            result[key] = aVal + bVal;
        } else if (Array.isArray(aVal)) {
            result[key] = aVal.concat(bVal);
        } else if (typeof aVal === "object" && aVal !== null) {
            result[key] = deepMerge(aVal, bVal);
        } else {
            result[key] = bVal;
        }
    }

    return result;
};
