import styles from "../index.module.css";

const SharesHeader = ({ sharesCount, pageSize, isCalculated }) => {
    return (
        <p className={styles.sharesCount}>
            {sharesCount} shared conversation{sharesCount !== 1 ? 's' : ''}
            {isCalculated && (
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                    • Showing {pageSize} per page (optimized for your screen)
                </span>
            )}
        </p>
    );
};

export default SharesHeader;
