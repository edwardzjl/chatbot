import styles from "../index.module.css";
import PropTypes from "prop-types";


const EmptyState = ({ isLoading }) => {
    if (isLoading) {
        return (
            <section className={styles.emptyState}>
                <p className={styles.EmptyStateText}>
                    Loading shares...
                </p>
                <p className={styles.emptyStateSubtext}>
                    Optimizing layout for your screen size
                </p>
            </section>
        );
    }

    return (
        <section className={styles.emptyState}>
            <p className={styles.EmptyStateText}>
                You haven&apos;t shared any conversations yet.
            </p>
            <p className={styles.emptyStateSubtext}>
                Share a conversation to see it listed here.
            </p>
        </section>
    );
};


EmptyState.propTypes = {
    isLoading: PropTypes.bool,
};

export default EmptyState;
