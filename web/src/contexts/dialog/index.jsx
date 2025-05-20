import { createContext } from "react";


export const DialogContext = createContext({
    openDialog: () => {},
    closeDialog: () => {},
    dialogState: {},
});
