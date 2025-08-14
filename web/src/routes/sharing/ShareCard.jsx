import styles from "./index.module.css";

import { memo } from "react";
import PropTypes from "prop-types";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";

import { formatTimestamp } from "@/commons";


const ShareCard = memo(({ share, onCopy, onDelete }) => {
    return (
        <div className={styles.shareCard} data-list-item>
            <div className={styles.shareCardContent}>
                <h2 className={styles.shareTitle}>
                    {share.title}
                </h2>
                <p className={styles.shareMeta}>
                    Created: {formatTimestamp(share.created_at)}
                </p>
                <a
                    href={share.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.shareUrl}
                >
                    {share.url}
                </a>
            </div>
            <div className={styles.shareCardActions}>
                <button
                    className={styles.actionButton}
                    onClick={() => onCopy(share.url)}
                    aria-label="Copy share URL"
                    title="Copy share URL"
                >
                    <ContentCopyIcon />
                </button>
                <button
                    className={`${styles.actionButton} ${styles.actionButtonDanger}`}
                    onClick={() => onDelete(share.id)}
                    aria-label="Delete share"
                    title="Delete share"
                >
                    <DeleteOutlinedIcon />
                </button>
            </div>
        </div>
    );
});

ShareCard.propTypes = {
    share: PropTypes.shape({
        id: PropTypes.string.isRequired, // UUID string
        title: PropTypes.string.isRequired,
        url: PropTypes.string.isRequired,
        created_at: PropTypes.oneOfType([
            // API returns ISO string; accept a few common timestamp forms
            PropTypes.string,
            PropTypes.number, // epoch millis
            PropTypes.instanceOf(Date),
        ]).isRequired,
        owner: PropTypes.string, // not displayed here but part of schema
        messages: PropTypes.arrayOf(PropTypes.object), // messages not rendered in card list
    }).isRequired,
    onCopy: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
};


ShareCard.displayName = "ShareCard";

export default ShareCard;
