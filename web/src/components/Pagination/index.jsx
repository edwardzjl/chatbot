import styles from "./index.module.css";
import PropTypes from "prop-types";
import Icon from "@mui/material/Icon";


const Pagination = ({
    currentPage,
    previousPage,
    nextPage,
    total,
    onPrevious,
    onNext,
    className = ""
}) => {
    const hasPrevious = !!previousPage;
    const hasNext = !!nextPage;

    // For cursor-based pagination, show meaningful info even if total is unknown
    const getPaginationInfo = () => {
        // Check if currentPage is a meaningful integer (not a cursor string)
        const isNumericPage = currentPage && !isNaN(parseInt(currentPage, 10)) && parseInt(currentPage, 10).toString() === currentPage.toString();

        if (total && total > 0 && isNumericPage) {
            // Non cursor pagination usually has total count
            return `Page ${currentPage} • ${total} total`;
        } else if (isNumericPage) {
            return `Page ${currentPage}`;
        } else {
            // Probably a cursor-based pagination
            return "Navigate pages";
        }
    };

    return (
        <div className={`${styles.pagination} ${className}`}>
            <button
                className={styles.paginationButton}
                onClick={onPrevious}
                disabled={!hasPrevious}
                aria-label="Previous page"
            >
                <Icon baseClassName="material-symbols-outlined">chevron_left</Icon>
                <span className={styles.paginationButtonText}>Previous</span>
            </button>
            <span className={styles.paginationInfo}>
                {getPaginationInfo()}
            </span>
            <button
                className={styles.paginationButton}
                onClick={onNext}
                disabled={!hasNext}
                aria-label="Next page"
            >
                <span className={styles.paginationButtonText}>Next</span>
                <Icon baseClassName="material-symbols-outlined">chevron_right</Icon>
            </button>
        </div>
    );
};

Pagination.propTypes = {
    currentPage: PropTypes.string,
    previousPage: PropTypes.string,
    nextPage: PropTypes.string,
    total: PropTypes.number,
    onPrevious: PropTypes.func.isRequired,
    onNext: PropTypes.func.isRequired,
    className: PropTypes.string,
};

export default Pagination;
