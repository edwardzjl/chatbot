import styles from "../index.module.css";
import { memo } from "react";
import Icon from "@mui/material/Icon";
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
                    <Icon baseClassName="material-symbols-outlined">content_copy</Icon>
                </button>
                <button
                    className={`${styles.actionButton} ${styles.actionButtonDanger}`}
                    onClick={() => onDelete(share.id)}
                    aria-label="Delete share"
                    title="Delete share"
                >
                    <Icon baseClassName="material-symbols-outlined">delete</Icon>
                </button>
            </div>
        </div>
    );
});

ShareCard.displayName = 'ShareCard';

export default ShareCard;
