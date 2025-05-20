import styles from "./index.module.css";

import { useEffect, useMemo, useRef, useState } from "react";
import PropTypes from "prop-types";

import { useSnackbar } from "@/contexts/snackbar/hook";
import { useDialog } from "@/contexts/dialog/hook";


const ShareConvDialog = ({ id }) => {
    const dialogRef = useRef(null);
    const { dialogState, openDialog, closeDialog, registerDialogRef } = useDialog();

    const { isOpen, props: dialogProps } = dialogState[id] || { isOpen: false, props: {} };
    const targetConv = useMemo(() => {
        return dialogProps.convData || {};
    }, [dialogProps.convData]);

    const { setSnackbar } = useSnackbar();

    const [title, setTitle] = useState(targetConv?.title || "");

    useEffect(() => {
        registerDialogRef(id, dialogRef.current);

        return () => {
            registerDialogRef(id, null);
        };
    }, [id, registerDialogRef]);

    useEffect(() => {
        if (isOpen) {
            dialogRef.current?.showModal();
            setTitle(targetConv?.title || "");
        } else {
            dialogRef.current?.close();
        }
    }, [isOpen, targetConv]);

    const shareConv = async () => {
        const response = await fetch(`/api/shares`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: title, source_id: targetConv.id }),
        });
        if (response.ok) {
            const data = await response.json();
            closeDialog(id);
            openDialog('conv-shared-dialog', { convData: { title: data.title, url: data.url } });
        } else {
            setSnackbar({
                open: true,
                severity: "error",
                message: "Failed to share conversation",
            });
        }
    };

    const handleClose = () => {
        closeDialog(id);
    };

    return (
        <dialog
            id={id}
            className={styles.dialog}
            ref={dialogRef}
            onCancel={handleClose}
        >
            <h2>Share conversation</h2>
            <div className={styles.dialogContent}>
                <label htmlFor={`${id}-title-input`}>title:</label>
                <input
                    id={`${id}-title-input`}
                    type="text"
                    defaultValue={targetConv.title || ""}
                    onChange={(e) => setTitle(e.target.value)}
                />
            </div>
            <div className={styles.dialogActions}>
                <button autoFocus onClick={shareConv}>Ok</button>
                <button onClick={handleClose}>Cancel</button>
            </div>
        </dialog>
    );
};

ShareConvDialog.propTypes = {
    id: PropTypes.string.isRequired,
};

export default ShareConvDialog;
