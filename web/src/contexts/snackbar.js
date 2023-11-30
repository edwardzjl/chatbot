import { createContext, useState } from "react";

export const SnackbarContext = createContext({
    open: false,
    severity: "info",
    message: "",
}, () => { });

export const SnackbarProvider = ({ children }) => {
    /**
     * open, severity, message
     */
    const [snackbar, setSnackbar] = useState(
        /** @type {{open: boolean, severity: string?, message: string}} */
        {
            open: false,
            severity: "info",
            message: "",
        }
    );

    return (
        <SnackbarContext.Provider value={[snackbar, setSnackbar]}>
            {children}
        </SnackbarContext.Provider>
    );
}
