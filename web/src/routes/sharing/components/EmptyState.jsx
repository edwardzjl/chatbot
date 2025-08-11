import styles from "../index.module.css";


const EmptyState = () => {
    return (
        <section className={styles.emptyState}>
            <p className={styles.emptyStateText}>
                You haven&apos;t shared any conversations yet.
            </p>
            <p className={styles.emptyStateSubtext}>
                Share a conversation to see it listed here.
            </p>
        </section>
    );
};

export default EmptyState;
