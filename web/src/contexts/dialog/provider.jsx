import { useState, useCallback, useRef } from "react";
import PropTypes from "prop-types";

import { DialogContext } from "./index";


export const DialogProvider = ({ children }) => {
    const [dialogState, setDialogState] = useState({});

    const dialogRefs = useRef({});

    const registerDialogRef = useCallback((id, ref) => {
        if (ref) {
            dialogRefs.current[id] = ref;
        } else {
            delete dialogRefs.current[id];
        }
    }, []);

    const openDialog = useCallback((id, props = {}) => {
        setDialogState(prev => {
            const newState = { ...prev };
            Object.keys(newState).forEach(key => {
                if (key !== id && newState[key].isOpen) {
                    newState[key] = { ...newState[key], isOpen: false };
                    dialogRefs.current[key]?.close();
                }
            });

            newState[id] = { isOpen: true, props: props };
            return newState;
        });
    }, []);

    const closeDialog = useCallback((id) => {
        setDialogState(prev => ({
            ...prev,
            [id]: { ...prev[id], isOpen: false, props: {} }
        }));
    }, []);

    const contextValue = {
        dialogState,
        openDialog,
        closeDialog,
        registerDialogRef,
    };

    return (
        <DialogContext.Provider value={contextValue}>
            {children}
        </DialogContext.Provider>
    );
};

DialogProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
