import styles from "./index.module.css";

import { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";

import Tooltip from "@mui/material/Tooltip";

import ContentCopyIcon from "@mui/icons-material/ContentCopy";

const ConvSharedDialog = ({ isOpen, onClose, targetConv }) => {
    const dialogRef = useRef(null);
    const [copyTooltipTitle, setCopyTooltipTitle] = useState("copy url");

    useEffect(() => {
        if (isOpen) {
            dialogRef.current?.showModal();
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

    return (
        <dialog
            id="conv-shared-dialog"
            className={styles.dialog}
            ref={dialogRef}
            onCancel={onClose}
        >
            <h2>Conversation shared</h2>
            <div className={styles.dialogContent}>
                <input id="shared-url" type="url" readOnly value={targetConv.url || ""} />
                {/* Set slotProps or the tooltip won't be visible */}
                {/* See <https://github.com/mui/material-ui/issues/40870#issuecomment-2044719356> */}
                <Tooltip title={copyTooltipTitle} slotProps={{ popper: { disablePortal: true } }} >
                    <ContentCopyIcon onClick={() => onCopyClick(targetConv.url)} />
                </Tooltip>
            </div>
            <div className={styles.dialogActions}>
                <button onClick={onClose}>Ok</button>
            </div>
        </dialog>
    );
};

ConvSharedDialog.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    targetConv: PropTypes.object,
};

export default ConvSharedDialog;
