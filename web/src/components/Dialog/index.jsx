import styles from "./index.module.css";

import PropTypes from "prop-types";


const Dialog = ({ ref, title, content, actions, ...props }) => (
    <dialog ref={ref} className={styles.dialog} aria-labelledby="dialog-title" aria-describedby="dialog-content" {...props}>
        <h2 id="dialog-title" className={styles.dialogTitle}>{title}</h2>
        <div id="dialog-content" className={styles.dialogContent}>
            {content}
        </div>
        <div className={styles.dialogActions}>
            {actions}
        </div>
    </dialog>
);

Dialog.propTypes = {
    ref: PropTypes.any,
    title: PropTypes.string.isRequired,
    content: PropTypes.node.isRequired,
    actions: PropTypes.node.isRequired,
};

export default Dialog;
