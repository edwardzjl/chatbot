import { useState, useLayoutEffect, useRef, useCallback } from "react";

/**
 * Custom hook to calculate optimal page size based on actual available screen space
 * This approach measures the real available space rather than estimating component heights
 * @param {number} maxPageSize - Maximum number of items per page (default: 20)
 * @param {string} itemSelector - CSS selector to find items for measurement inside the container (default: '[data-list-item]')
 * @param {number} minAvailableHeight - Minimum usable height applied regardless of list render state (default: 160)
 * @param {number} debounceMs - Debounce delay (ms) for resizing recalculations (default: 120)
 * @returns {object} { pageSize, containerRef, recalculate, isCalculated }
 */
export const useDynamicPageSize = ({
    maxPageSize = 20,
    itemSelector = '[data-list-item]',
    minAvailableHeight = 160,
    debounceMs = 120,
} = {}) => {
    const [pageSize, setPageSize] = useState(1);
    const containerRef = useRef(null);
    const [isCalculated, setIsCalculated] = useState(false);
    const resizeTimerRef = useRef(null);
    const rafRef = useRef(null);

    // Guard / normalize maxPageSize
    const safeMax = Math.max(1, maxPageSize || 1);

    const computeAndSetPageSize = useCallback(() => {
        const root = containerRef.current;
        if (!root || typeof window === 'undefined') return;

        // The container itself is the list element
        const listEl = root;
        const vh = window.innerHeight;

        // Measure rects only once per element to avoid repeated layouts
        const listRect = listEl.getBoundingClientRect();
        const containerRect = root.getBoundingClientRect();

        // Available vertical space (conservative)
        const optionContainer = containerRect.bottom - listRect.top;
        const optionViewport = vh - listRect.top;
        const availableRaw = Math.min(optionContainer, optionViewport);
        const available = Math.max(minAvailableHeight, availableRaw);

        // Fit items by checking if each item's bottom stays within limit
        const items = listEl.querySelectorAll(itemSelector);
        let fittedCount = 0;
        let lastBottom = listRect.top;
        const limit = listRect.top + available;
        if (items.length) {
            for (let i = 0; i < items.length; i++) {
                const rect = items[i].getBoundingClientRect();
                if (rect.bottom > limit) break; // this item would overflow
                fittedCount += 1;
                lastBottom = rect.bottom;
            }
        }

        let pageByFit = fittedCount;
        if (fittedCount === 0) {
            // No items yet or first item too tall; default to 1 until items render and a manual recalc occurs
            pageByFit = 1;
        } else if (fittedCount === items.length && lastBottom < limit) {
            // All rendered items fit and extra space remains -> extrapolate using average per-item span
            const totalSpan = lastBottom - listRect.top;
            const avgSpan = totalSpan / fittedCount;
            if (avgSpan > 0) {
                const extra = Math.floor((limit - lastBottom) / avgSpan);
                pageByFit += extra;
            }
        }

        const finalPage = Math.min(safeMax, Math.max(1, pageByFit));

        setPageSize(finalPage);
        setIsCalculated(true);
    }, [itemSelector, minAvailableHeight, safeMax]);

    // Debounced scheduling (shared by events / observers)
    const scheduleRecalc = useCallback(() => {
        if (resizeTimerRef.current) clearTimeout(resizeTimerRef.current);
        resizeTimerRef.current = setTimeout(() => {
            if (typeof requestAnimationFrame !== 'undefined') {
                if (rafRef.current) cancelAnimationFrame(rafRef.current);
                rafRef.current = requestAnimationFrame(computeAndSetPageSize);
            } else {
                computeAndSetPageSize();
            }
        }, debounceMs);
    }, [computeAndSetPageSize, debounceMs]);

    // Initial + resize listener
    useLayoutEffect(() => {
        if (typeof window === 'undefined') return undefined;

        scheduleRecalc(); // asap

        const t2 = setTimeout(scheduleRecalc, 80);
        const t3 = setTimeout(scheduleRecalc, 200);
        const onResize = () => scheduleRecalc();

        window.addEventListener('resize', onResize);
        return () => {
            window.removeEventListener('resize', onResize);
            clearTimeout(t2);
            clearTimeout(t3);
        };
    }, [scheduleRecalc]);

    // Provide a method to manually recalculate (useful after DOM updates)
    const recalculate = scheduleRecalc;

    return { pageSize, containerRef, recalculate, isCalculated };
};
