
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
