
export const messagesReducer = (messages, action) => {
    switch (action.type) {
    case "added": {
        console.debug("Adding message: ", action.message);
        // find reversly could potentially be faster as the full message usually is the last one (streamed).
        const match = messages.findLastIndex(message => message.id === action.message.id);
        if (match !== -1) {
            console.warn(`Message with id ${action.message.id} already exists, skip adding...`);
            return messages;
        }
        return [...messages, { ...action.message }];
    }
    case "appended": {
        console.debug("Appending message: ", action.message);
        const match = messages.findLastIndex(message => message.id === action.message.id);
        if (match === -1) {
            // we don't have this message, ignore it
            // this could happen when the user switch to another conversation and switch back
            console.warn(`Message with id ${action.message.id} not found, skip appending...`);
            return messages;
        }
        return [
            ...messages.slice(0, match),
            {
                ...messages[match],
                content: mergeContent(messages[match].content, action.message.content),
                additional_kwargs: deepMerge(messages[match].additional_kwargs, action.message.additional_kwargs)
            },
            ...messages.slice(match + 1)
        ];
    }
    case "updated": {
        console.debug("Updating message: ", action.message);
        // find reversly could potentially be faster as the full message usually is the last one (streamed).
        const match = messages.findLastIndex(message => message.id === action.message.id);
        if (match === -1) {
            console.warn(`Message with id ${action.message.id} not found, skip updating...`);
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


export const mergeContent = (a, b) => {
    if (typeof a === "string" && typeof b === "string") {
        return a + b;
    }
    if (typeof a === "string") {
        a = [{type: "text", text: a}];
    }
    if (typeof b === "string") {
        b = [{type: "text", text: b}];
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

    for (const e of right) {
        if (e === null || e === undefined) {
            continue;
        }
        if (typeof e !== "object") {
            merged.push(e);
            continue;
        }
        if (Array.isArray(e)) {
            merged.push(...e);
            continue;
        }
        if (!hasOwnProperty.call(e, "index") || !Number.isInteger(e.index)) {
            merged.push(e);
            continue;
        }
        // 如果是，则尝试在 merged 列表中查找具有相同 index 的元素。
        const toMergeIndex = merged.findIndex(eLeft =>
            // 确保 merged 中的元素也是带有 index 的普通对象，然后进行比较。
            typeof eLeft === 'object' && eLeft !== null && !Array.isArray(eLeft) &&
            hasOwnProperty.call(eLeft, 'index') && eLeft.index === e.index
        );
        if (toMergeIndex === -1) {
            merged.push(e);
            continue;
        }
        // handling for 'type'.
        const newE = (hasOwnProperty.call(e, 'type'))
            // 创建一个新对象，复制 e 的所有属性，除了 'type'
            ? Object.keys(e).reduce((obj, key) => {
                if (key !== 'type') {
                    obj[key] = e[key];
                }
                return obj;
            }, {})
            : e; // 如果没有 'type'，则使用元素本身进行合并

        // 使用 mergeObjects 函数合并对象。
        // 用合并结果替换 merged 列表中的元素。
        merged[toMergeIndex] = deepMerge(merged[toMergeIndex], newE);
    }

    // 返回最终合并后的列表。
    return merged;
};
