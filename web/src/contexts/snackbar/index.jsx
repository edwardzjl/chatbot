import { createContext } from "react";


export const SnackbarContext = createContext({
    snackbar: {
        open: false,
        severity: "info",
        message: "",
    },
    setSnackbar: () => { },
    closeSnackbar: () => { },
});
