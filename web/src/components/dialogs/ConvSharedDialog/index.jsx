import styles from "./index.module.css";

import { useEffect, useMemo, useRef, useState } from "react";
import PropTypes from "prop-types";

import Tooltip from "@mui/material/Tooltip";

import ContentCopyIcon from "@mui/icons-material/ContentCopy";

import { useDialog } from "@/contexts/dialog/hook";


const ConvSharedDialog = ({ id }) => {
    const dialogRef = useRef(null);
    const { dialogState, closeDialog, registerDialogRef } = useDialog();

    const { isOpen, props: dialogProps } = dialogState[id] || { isOpen: false, props: {} };
    const targetConv = useMemo(() => {
        return dialogProps.convData || {};
    }, [dialogProps.convData]);

    const [copyTooltipTitle, setCopyTooltipTitle] = useState("copy url");

    useEffect(() => {
        registerDialogRef(id, dialogRef.current);

        return () => {
            registerDialogRef(id, null);
        };
    }, [id, registerDialogRef]);

    useEffect(() => {
        if (isOpen) {
            dialogRef.current?.showModal();
            setCopyTooltipTitle("copy url");
        } else {
            dialogRef.current?.close();
        }
    }, [isOpen]);

    const onCopyClick = (content) => {
        navigator.clipboard.writeText(content);
        setCopyTooltipTitle("copied!");
        setTimeout(() => {
            setCopyTooltipTitle("copy url");
        }, 3000);
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
            <h2>Conversation shared</h2>
            <div className={styles.dialogContent}>
                <input id={`${id}-url`} type="url" readOnly value={targetConv.url || ""} />
                {/* Set slotProps or the tooltip won't be visible */}
                {/* See <https://github.com/mui/material-ui/issues/40870#issuecomment-2044719356> */}
                <Tooltip title={copyTooltipTitle} slotProps={{ popper: { disablePortal: true } }} >
                    <ContentCopyIcon onClick={() => onCopyClick(targetConv.url)} />
                </Tooltip>
            </div>
            <div className={styles.dialogActions}>
                <button onClick={handleClose}>Ok</button>
            </div>
        </dialog>
    );
};

ConvSharedDialog.propTypes = {
    id: PropTypes.string.isRequired,
};

export default ConvSharedDialog;
