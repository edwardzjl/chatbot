
/**
 * Get ISO 8601 string of the input date in local timezone.
 */
export const toLocalISOString = (date) => {
    const isoString = date.toISOString();
    const offset = -date.getTimezoneOffset(); // offset in minutes
    if (offset === 0) {
        return isoString;
    }

    const offsetHours = Math.abs(Math.floor(offset / 60));
    const offsetMinutes = Math.abs(offset % 60);
    const offsetSign = offset >= 0 ? "+" : "-";

    return isoString.slice(0, -1) + offsetSign +
        String(offsetHours).padStart(2, "0") +
        ":" +
        String(offsetMinutes).padStart(2, "0");
};

export const getFirstLetters = (str) => {
    if (!str) {
        return "";
    }
    return str.split(" ").map(word => word[0])
};

/**
 * <https://github.com/mui/material-ui/issues/12700#issuecomment-416869593>
 */
export const stringToColor = (string) => {
    if (!string) {
        return "#000000";
    }

    let hash = 0;
    let i;

    for (i = 0; i < string.length; i += 1) {
        hash = string.charCodeAt(i) + ((hash << 5) - hash);
    }

    let color = "#";

    for (i = 0; i < 3; i += 1) {
        const value = (hash >> (i * 8)) & 0xff;
        color += `00${value.toString(16)}`.substr(-2);
    }

    return color;
}

/**
 * <https://stackoverflow.com/a/15724300/6564721>
 */
export const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

export const DEFAULT_CONV_TITLE = "New Chat";

export const formatTimestamp = (timestamp) => {
    const ts = new Date(timestamp);
    const userLocale = navigator.language || "en-US"; // Fallback to "en-US" if not available

    return ts.toLocaleString(userLocale, {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
};

/**
 * Parses a text string to identify sections enclosed in <think>...</think> tags.
 * Returns an array of segments, each marked as 'text' or 'think'.
 *
 * @param {string} text - The input text string.
 * @returns {Array<{type: 'text' | 'think', content: string}>} - An array of parsed segments.
 */
export const parseThinkBlocks = (text) => {
    const segments = [];
    // Regex to find <think>...</think> blocks.
    // The 's' flag allows '.' to match newlines.
    // The 'g' flag finds all matches.
    // The '?' makes the match non-greedy. This is crucial for correct extraction.
    const regex = /<think>(.*?)<\/think>/gs;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
        // Add the text before the current match as a 'text' segment
        if (match.index > lastIndex) {
            segments.push({
                type: "text",
                content: text.substring(lastIndex, match.index)
            });
        }

        // Add the content inside the <think> tags as a 'think' segment
        // match[1] contains the captured content within the tags
        segments.push({
            type: "think",
            content: match[1] // The captured group inside <think>...</think>
        });

        // Update lastIndex to be the end of the current match
        lastIndex = regex.lastIndex;
    }

    // Add any remaining text after the last match as a 'text' segment
    if (lastIndex < text.length) {
        segments.push({
            type: "text",
            content: text.substring(lastIndex)
        });
    }

    return segments;
};
