import styles from "./index.module.css";

import { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

const DeleteConvDialog = ({ isOpen, onClose, targetConv, onDelete }) => {
    const dialogRef = useRef(null);

    useEffect(() => {
        if (isOpen) {
            dialogRef.current?.showModal();
        } else {
            dialogRef.current?.close();
        }
    }, [isOpen]);

    const handleDelete = async () => {
        onDelete(targetConv.id);
        onClose();
    };

    return (
        <dialog
            id="del-conv-dialog"
            className={styles.dialog}
            ref={dialogRef}
            onCancel={onClose}
        >
            <h2>Delete conversation?</h2>
            <div className={styles.dialogContent}>
                <p>This will delete &quot;{targetConv.title}&quot;</p>
            </div>
            <div className={styles.dialogActions}>
                <button autoFocus onClick={handleDelete}>Delete</button>
                <button onClick={onClose}>Cancel</button>
            </div>
        </dialog>
    );
};

DeleteConvDialog.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    targetConv: PropTypes.object,
    onDelete: PropTypes.func.isRequired,
};

export default DeleteConvDialog;
