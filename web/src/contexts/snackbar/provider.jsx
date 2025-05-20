import { useCallback, useState } from "react";
import PropTypes from "prop-types";

import { SnackbarContext } from "./index";


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

    const closeSnackbar = useCallback((event, reason) => {
        if (reason === "clickaway") {
            return;
        }
        setSnackbar(prevSnackbar => ({ ...prevSnackbar, open: false }));
    }, []);

    return (
        <SnackbarContext.Provider value={{ snackbar, setSnackbar, closeSnackbar }}>
            {children}
        </SnackbarContext.Provider>
    );
};

SnackbarProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
