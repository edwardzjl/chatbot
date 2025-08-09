import { useState, useEffect, useRef } from "react";

/**
 * Custom hook to calculate optimal page size based on actual available screen space
 * This approach measures the real available space rather than estimating component heights
 * @param {number} minPageSize - Minimum number of items per page (default: 3)
 * @param {number} maxPageSize - Maximum number of items per page (default: 20)
 * @param {number} fallbackItemHeight - Fallback height when measurement isn't available (default: 120)
 * @param {string} listSelector - CSS selector for the list container (default: '[data-list-container]')
 * @param {string} itemSelector - CSS selector to find items for measurement (default: '[data-list-item]')
 * @returns {object} { pageSize, containerRef, recalculate, isCalculated, measuredItemHeight, availableHeight }
 */
export const useDynamicPageSize = ({
    minPageSize = 3,
    maxPageSize = 20,
    fallbackItemHeight = 120,
    listSelector = '[data-list-container]',
    itemSelector = '[data-list-item]',
} = {}) => {
    const [pageSize, setPageSize] = useState(minPageSize);
    const [measuredItemHeight, setMeasuredItemHeight] = useState(fallbackItemHeight);
    const [availableHeight, setAvailableHeight] = useState(0);
    const containerRef = useRef(null);
    const [isCalculated, setIsCalculated] = useState(false);

    const measureActualItemHeight = () => {
        if (!containerRef.current) {
            return fallbackItemHeight;
        }

        // Find actual rendered items
        const items = containerRef.current.querySelectorAll(itemSelector);
        if (items.length === 0) {
            return fallbackItemHeight;
        }

        // Measure the height of the first few items and take average
        const itemsToMeasure = Math.min(items.length, 3);
        let totalHeight = 0;
        
        for (let i = 0; i < itemsToMeasure; i++) {
            const rect = items[i].getBoundingClientRect();
            totalHeight += rect.height;
        }
        
        const averageHeight = totalHeight / itemsToMeasure;
        
        // Add gap between items (from CSS gap property)
        const heightWithGap = averageHeight + 16; // 1rem gap
        
        return Math.ceil(heightWithGap);
    };

    const measureAvailableSpace = () => {
        if (!containerRef.current) return 0;

        // Find the list container within our main container
        const listContainer = containerRef.current.querySelector(listSelector);
        if (!listContainer) {
            // If list container doesn't exist yet, calculate based on viewport and container
            const containerRect = containerRef.current.getBoundingClientRect();
            const viewportHeight = window.innerHeight;
            const estimatedHeaderSpace = 200; // Conservative estimate for header space
            const estimatedPaginationSpace = 100; // Conservative estimate for pagination
            const availableSpace = viewportHeight - containerRect.top - estimatedHeaderSpace - estimatedPaginationSpace;
            return Math.max(200, availableSpace); // Minimum 200px
        }

        // Method 1: Measure from list position to container bottom
        const listRect = listContainer.getBoundingClientRect();
        const containerRect = containerRef.current.getBoundingClientRect();
        
        // Calculate available height: from list top to container bottom, minus pagination space
        const fromListToContainerBottom = (containerRect.bottom - listRect.top) - 100; // 100px for pagination + buffer
        
        // Method 2: Calculate based on viewport
        const viewportHeight = window.innerHeight;
        const fromListToViewportBottom = viewportHeight - listRect.top - 100; // 100px for pagination + buffer
        
        // Use the more conservative (smaller) measurement
        const availableSpace = Math.min(fromListToContainerBottom, fromListToViewportBottom);
        
        return Math.max(150, availableSpace); // Minimum 150px to fit at least minPageSize items
    };

    const calculatePageSize = () => {
        if (!containerRef.current) return;

        // Measure actual available space for the list
        const actualAvailableHeight = measureAvailableSpace();
        setAvailableHeight(actualAvailableHeight);

        // Always use a conservative approach for small screens
        const viewportHeight = window.innerHeight;
        const isSmallScreen = viewportHeight <= 700;
        
        let workingAvailableHeight = actualAvailableHeight;
        
        // For small screens, be extra conservative
        if (isSmallScreen) {
            const containerRect = containerRef.current.getBoundingClientRect();
            const conservativeHeight = viewportHeight - containerRect.top - 150; // More buffer for small screens
            workingAvailableHeight = Math.min(actualAvailableHeight, conservativeHeight);
        }

        // Measure actual item height
        const actualItemHeight = measureActualItemHeight();
        setMeasuredItemHeight(actualItemHeight);

        // Calculate how many items can fit
        const calculatedPageSize = Math.floor(workingAvailableHeight / actualItemHeight);

        // For small screens, be more conservative with page size
        let finalPageSize = Math.max(minPageSize, Math.min(maxPageSize, calculatedPageSize));
        
        if (isSmallScreen && finalPageSize > 4) {
            finalPageSize = Math.min(4, finalPageSize); // Cap at 4 items for small screens
        }

        setPageSize(finalPageSize);
        setIsCalculated(true);
    };

    // Recalculate on resize
    useEffect(() => {
        const handleResize = () => {
            calculatePageSize();
        };

        // Calculate initial page size
        const timer1 = setTimeout(calculatePageSize, 100);
        
        // Add resize listener
        window.addEventListener("resize", handleResize);

        // Recalculate when DOM settles
        const timer2 = setTimeout(calculatePageSize, 300);

        return () => {
            window.removeEventListener("resize", handleResize);
            clearTimeout(timer1);
            clearTimeout(timer2);
        };
    }, []);

    // Provide a method to manually recalculate (useful after DOM updates)
    const recalculate = () => {
        setTimeout(calculatePageSize, 100);
    };

    return {
        pageSize,
        containerRef,
        recalculate,
        isCalculated,
        measuredItemHeight,
        availableHeight
    };
};
