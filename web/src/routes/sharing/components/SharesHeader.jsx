import styles from "../index.module.css";
import PropTypes from "prop-types";

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

SharesHeader.propTypes = {
    sharesCount: PropTypes.number.isRequired,
    pageSize: PropTypes.number.isRequired,
    isCalculated: PropTypes.bool,
};

export default SharesHeader;
