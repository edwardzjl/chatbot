
/**
 * Get ISO 8601 string of the input date in local timezone.
 */
export const toLocalISOString = (date) => {
    const offset = -date.getTimezoneOffset(); // offset in minutes
    if (offset === 0) {
        return date.toISOString();
    }

    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, "0");
    const day = date.getDate().toString().padStart(2, "0");
    const hours = date.getHours().toString().padStart(2, "0");
    const minutes = date.getMinutes().toString().padStart(2, "0");
    const seconds = date.getSeconds().toString().padStart(2, "0");
    const milliseconds = date.getMilliseconds().toString().padStart(3, "0");

    // Calculate the timezone offset in hours and minutes
    const offsetSign = offset >= 0 ? "+" : "-";
    const offsetHours = Math.abs(Math.floor(offset / 60)).toString().padStart(2, "0");
    const offsetMinutes = Math.abs(offset % 60).toString().padStart(2, "0");

    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}${offsetSign}${offsetHours}:${offsetMinutes}`;
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

export const createComparator = (options) => {
    return (a, b) => {
        for (const { key, order = "asc", compareFn } of options) {
            const aVal = a[key];
            const bVal = b[key];

            let result = 0;

            if (typeof compareFn === "function") {
                result = compareFn(a, b);
            } else {
                if (aVal == null && bVal != null) result = -1;
                else if (aVal != null && bVal == null) result = 1;
                else if (aVal == null && bVal == null) result = 0;
                else if (typeof aVal === "string" && typeof bVal === "string") {
                    result = aVal.localeCompare(bVal);
                } else if (aVal instanceof Date && bVal instanceof Date) {
                    result = aVal.getTime() - bVal.getTime();
                } else {
                    result = aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
                }
            }

            if (result !== 0) {
                return order === "asc" ? result : -result;
            }
        }
        return 0;
    };
}
