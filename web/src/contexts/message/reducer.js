
/**
 * This is actually a messages reducer.
 *
 * But I need to expose the conversation field to verify that the `replaceAll` action is finished.
 */
export const messagesReducer = (currentConv, action) => {
    switch (action.type) {
    case "added": {
        console.debug("Adding message: ", action.message);
        if (action.convId !== currentConv.id) {
            console.warn(
                `Message ${action.message.id} belongs to conversation ${action.convId}, not (${currentConv.id}), skip adding...`
            );
            return currentConv;
        }
        // find reversly could potentially be faster as the full message usually is the last one (streamed).
        const match = currentConv.messages.findLastIndex(message => message.id === action.message.id);
        if (match !== -1) {
            console.warn(`Message with id ${action.message.id} already exists, skip adding...`);
            return currentConv;
        }
        return { ...currentConv, messages: [...currentConv.messages, { ...action.message }] };
    }
    case "appended": {
        console.debug("Appending message: ", action.message);
        if (action.convId !== currentConv.id) {
            console.warn(
                `Message ${action.message.id} belongs to conversation ${action.convId}, not current conversation (${currentConv.id}), skip appending...`
            );
            return currentConv;
        }
        const match = currentConv.messages.findLastIndex(message => message.id === action.message.id);
        if (match === -1) {
            // we don't have this message, ignore it
            // this could happen when the user switch to another conversation and switch back
            console.warn(`Message with id ${action.message.id} not found, skip appending...`);
            return currentConv;
        }
        const matched = currentConv.messages[match];
        return {
            ...currentConv,
            messages: [
                ...currentConv.messages.slice(0, match),
                {
                    ...matched,
                    content: mergeContentChunks(matched.content, action.message.content),
                    additional_kwargs: deepMerge(matched.additional_kwargs, action.message.additional_kwargs)
                },
                ...currentConv.messages.slice(match + 1)
            ]
        }
    }
    case "updated": {
        console.debug("Updating message: ", action.message);
        if (action.convId !== currentConv.id) {
            console.warn(
                `Message ${action.message.id} belongs to conversation ${action.convId}, not (${currentConv.id}), skip updating...`
            );
            return currentConv;
        }
        // find reversly could potentially be faster as the full message usually is the last one (streamed).
        const match = currentConv.messages.findLastIndex(message => message.id === action.message.id);
        if (match === -1) {
            console.warn(`Message with id ${action.message.id} not found, skip updating...`);
            return currentConv;
        }
        return {
            ...currentConv,
            messages: [
                ...currentConv.messages.slice(0, match),
                { ...currentConv.messages[match], ...action.message },
                ...currentConv.messages.slice(match + 1)
            ]
        };
    }
    case "replaceAll": {
        return {id: action.convId, messages: [...action.messages]};
    }
    default: {
        console.error("Unknown action: ", action);
        return currentConv;
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


/**
 * Merge two OpenAI content chunks.
 *
 * Chunk should be either a string, or an array of objects.
 * If content is an array, each element should either be a string or an object with at least a 'type' property.
 *
 * If both chunks are strings, they will be concatenated.
 * If one chunk is a string and the other is an array, the string will be converted to an array with a single object.
 * If both chunks are arrays, they will be merged using the mergeLists function.
 */
export const mergeContentChunks = (a, b) => {
    if (typeof a === "string" && typeof b === "string") {
        return a + b;
    }
    if (typeof a === "string") {
        a = [{ type: "text", text: a }];
    }
    if (typeof b === "string") {
        b = [{ type: "text", text: b }];
    }
    if (Array.isArray(a) && Array.isArray(b)) {
        return mergeLists(a, b);
    }
    // Should not happen
    console.error(`Cannot merge contents. a: ${a}, b: ${b}`);
    return a;
};


/**
 * 合并两个列表，处理 null/undefined 以及根据 index 合并字典类对象。
 *
 * 如果两个列表中都包含带有整数 'index' 键的对象，
 * 则使用 mergeObjects 合并具有相同 index 的元素。
 * 否则，将 right 中的元素添加到 left 的副本中。
 *
 * @param {Array<any> | null | undefined} left 要合并的第一个列表。
 * @param {Array<any> | null | undefined} right 要合并到第一个列表中的第二个列表。
 * @returns {Array<any> | null | undefined} 合并后的列表。返回 left 的副本，如果 left 是 null/undefined 则返回 right 的副本，如果两者都是 null/undefined 则返回 null/undefined。
 */
const mergeLists = (left, right) => {
    if (left === null) {
        return [...right];
    }

    let merged = [...left];

    if (right === null || right === undefined) {
        return merged;
    }

    const hasOwnProperty = Object.prototype.hasOwnProperty;

    for (const part of right) {
        if (part === null || part === undefined) {
            continue;
        }
        if (typeof part !== "object") {
            merged.push(part);
            continue;
        }
        if (Array.isArray(part)) {
            // Should not happen
            merged.push(...part);
            continue;
        }
        if (!hasOwnProperty.call(part, "index") || !Number.isInteger(part.index)) {
            merged.push(part);
            continue;
        }
        // 如果是，则尝试在 merged 列表中查找具有相同 index 的元素。
        const toMergeIndex = merged.findIndex(eLeft =>
            // 确保 merged 中的元素也是带有 index 的普通对象，然后进行比较。
            typeof eLeft === "object" && eLeft !== null && !Array.isArray(eLeft) &&
            hasOwnProperty.call(eLeft, "index") && eLeft.index === part.index && eLeft.type === part.type
        );
        if (toMergeIndex === -1) {
            merged.push(part);
            continue;
        }

        const newPart = (hasOwnProperty.call(part, "type"))
            // 创建一个新对象，复制 part 的所有属性，除了 'type' 和 'index'
            ? Object.keys(part).reduce((obj, key) => {
                if (key !== "type" && key !== "index") {
                    obj[key] = part[key];
                }
                return obj;
            }, {})
            : part; // 如果没有 'type'，则使用元素本身进行合并

        merged[toMergeIndex] = deepMerge(merged[toMergeIndex], newPart);
    }
    return merged;
};
