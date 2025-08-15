import styles from "./index.module.css";

import { useEffect, useMemo, useRef } from "react";
import { useNavigate } from "react-router";
import PropTypes from "prop-types";

import { useConversations } from "@/contexts/conversation/hook";
import { useDialog } from "@/contexts/dialog/hook";


const DeleteConvDialog = ({ id }) => {
    const dialogRef = useRef(null);
    const navigate = useNavigate();
    const { dispatch } = useConversations();

    const { dialogState, closeDialog, registerDialogRef } = useDialog();

    const { isOpen, props: dialogProps } = dialogState[id] || { isOpen: false, props: {} };
    const targetConv = useMemo(() => {
        return dialogProps.convData || {};
    }, [dialogProps.convData]);

    useEffect(() => {
        registerDialogRef(id, dialogRef.current);

        return () => {
            registerDialogRef(id, null);
        };
    }, [id, registerDialogRef]);

    useEffect(() => {
        if (isOpen) {
            dialogRef.current?.showModal();
        } else {
            dialogRef.current?.close();
        }
    }, [isOpen]);

    const deleteConv = async () => {
        await fetch(`/api/conversations/${targetConv.id}`, { method: "DELETE" });
        dispatch({ type: "deleted", conv: targetConv });
        closeDialog(id);
        navigate("/");
    };

    const handleClose = () => {
        closeDialog(id);
    };

    return (
        <dialog
            id="del-conv-dialog"
            className={styles.dialog}
            ref={dialogRef}
            onCancel={handleClose}
        >
            <h2>Delete conversation?</h2>
            <div className={styles.dialogContent}>
                <p>This will delete &quot;{targetConv.title}&quot;</p>
            </div>
            <div className={styles.dialogActions}>
                <button autoFocus onClick={deleteConv}>Delete</button>
                <button onClick={handleClose}>Cancel</button>
            </div>
        </dialog>
    );
};

DeleteConvDialog.propTypes = {
    id: PropTypes.string.isRequired,
};

export default DeleteConvDialog;
