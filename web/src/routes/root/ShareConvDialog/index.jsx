import styles from "./index.module.css";

import { useRef, useState, useEffect } from "react";
import PropTypes from "prop-types";


const ShareConvDialog = ({ isOpen, onClose, targetConv, onShare }) => {
    const dialogRef = useRef(null);
    const [title, setTitle] = useState(targetConv?.title || "");

    useEffect(() => {
        if (isOpen) {
            dialogRef.current?.showModal();
            setTitle(targetConv?.title || "");
        } else {
            dialogRef.current?.close();
        }
    }, [isOpen, targetConv]);

    const handleShare = () => {
        onShare(targetConv.id, title);
        onClose();
    };

    return (
        <dialog
            id="share-conv-dialog"
            className={styles.dialog}
            ref={dialogRef}
            onCancel={onClose}
        >
            <h2>Share conversation</h2>
            <div className={styles.dialogContent}>
                <label htmlFor="share-title-input">title:</label>
                <input
                    id="share-title-input"
                    type="text"
                    defaultValue={targetConv.title || ""}
                    onChange={(e) => setTitle(e.target.value)}
                />
            </div>
            <div className={styles.dialogActions}>
                <button autoFocus onClick={handleShare}>Ok</button>
                <button onClick={onClose}>Cancel</button>
            </div>
        </dialog>
    );
};

ShareConvDialog.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func,
    targetConv: PropTypes.object,
    onShare: PropTypes.func.isRequired,
};

export default ShareConvDialog;
