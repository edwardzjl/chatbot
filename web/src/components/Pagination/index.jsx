import PropTypes from "prop-types";

import "./index.css";

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

    return (
        <div className={`pagination ${className}`}>
            <button 
                className="pagination-button"
                onClick={onPrevious}
                disabled={!hasPrevious}
                aria-label="Previous page"
            >
                <span className="material-icons">chevron_left</span>
                Previous
            </button>
            <span className="pagination-info">
                {total > 0 ? `Page ${currentPage} • ${total} total` : "No items"}
            </span>
            <button 
                className="pagination-button"
                onClick={onNext}
                disabled={!hasNext}
                aria-label="Next page"
            >
                Next
                <span className="material-icons">chevron_right</span>
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
