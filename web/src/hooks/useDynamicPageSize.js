import { useState, useEffect, useRef } from "react";

/**
 * Custom hook to calculate optimal page size based on available screen space
 * @param {number} minPageSize - Minimum number of items per page (default: 3)
 * @param {number} maxPageSize - Maximum number of items per page (default: 20)
 * @param {number} itemHeight - Estimated height of a single item in pixels (default: 120)
 * @param {number} headerHeight - Height reserved for header, title, etc. (default: 200)
 * @param {number} paginationHeight - Height reserved for pagination (default: 80)
 * @returns {object} { pageSize, containerRef, recalculate }
 */
export const useDynamicPageSize = ({
    minPageSize = 3,
    maxPageSize = 20,
    itemHeight = 120, // Estimated height of each share card
    headerHeight = 200, // Height for header + title + count
    paginationHeight = 80, // Height for pagination component
} = {}) => {
    const [pageSize, setPageSize] = useState(minPageSize);
    const containerRef = useRef(null);
    const [isCalculated, setIsCalculated] = useState(false);

    const calculatePageSize = () => {
        if (!containerRef.current) return;

        // Get the viewport height
        const viewportHeight = window.innerHeight;

        // Get the container's position to calculate available space
        const containerRect = containerRef.current.getBoundingClientRect();
        const containerTop = containerRect.top;

        // Calculate available height for the list
        // Available height = viewport height - container top position - header space - pagination space - padding
        const availableHeight = viewportHeight - containerTop - headerHeight - paginationHeight - 40; // 40px extra padding

        // Calculate how many items can fit
        const calculatedPageSize = Math.floor(availableHeight / itemHeight);

        // Ensure the page size is within bounds
        const finalPageSize = Math.max(minPageSize, Math.min(maxPageSize, calculatedPageSize));

        console.log("Dynamic page size calculation:", {
            viewportHeight,
            containerTop,
            availableHeight,
            calculatedPageSize,
            finalPageSize
        });

        setPageSize(finalPageSize);
        setIsCalculated(true);
    };

    // Recalculate on resize
    useEffect(() => {
        const handleResize = () => {
            calculatePageSize();
        };

        // Calculate initial page size
        calculatePageSize();

        // Add resize listener
        window.addEventListener("resize", handleResize);

        // Also recalculate when DOM is fully loaded
        const timer = setTimeout(calculatePageSize, 100);

        return () => {
            window.removeEventListener("resize", handleResize);
            clearTimeout(timer);
        };
    }, []);

    // Provide a method to manually recalculate (useful after DOM updates)
    const recalculate = () => {
        setTimeout(calculatePageSize, 50);
    };

    return {
        pageSize,
        containerRef,
        recalculate,
        isCalculated
    };
};
