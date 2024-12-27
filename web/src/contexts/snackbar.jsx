import { createContext, useState } from "react";
import PropTypes from "prop-types";


export const SnackbarContext = createContext({
    snackbar: {
        open: false,
        severity: "info",
        message: "",
    },
    setSnackbar: () => { },
});

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
        <SnackbarContext.Provider value={{ snackbar, setSnackbar }}>
            {children}
        </SnackbarContext.Provider>
    );
};

SnackbarProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
