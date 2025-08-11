import styles from "./index.module.css";

import { useState, useEffect, useCallback } from "react";
import { useLoaderData, useNavigate, useSearchParams } from "react-router-dom";

import ChatboxHeader from "@/components/ChatboxHeader";
import { useSnackbar } from "@/contexts/snackbar/hook";
import Pagination from "@/components/Pagination";
import { useDynamicPageSize } from "@/hooks/useDynamicPageSize";

// Local components
import ShareCard from "./components/ShareCard";
import EmptyState from "./components/EmptyState";
import SharesHeader from "./components/SharesHeader";

// Constants
const DYNAMIC_PAGE_SIZE_CONFIG = {
    minPageSize: 2, // Allow 2 items minimum for very small screens
    maxPageSize: 15,
    fallbackItemHeight: 120,
    listSelector: '[data-list-container]',
    itemSelector: '[data-list-item]',
};

// API helper function
const fetchShares = async (size, cursor = null) => {
    const apiUrl = new URL("/api/shares", window.location.origin);
    if (cursor) {
        apiUrl.searchParams.set("cursor", cursor);
    }
    apiUrl.searchParams.set("size", size.toString());

    const response = await fetch(apiUrl.toString());
    if (!response.ok) {
        throw new Error(`Failed to fetch shares: ${response.statusText}`);
    }
    return response.json();
};

async function loader({ request }) {
    const url = new URL(request.url);
    const cursor = url.searchParams.get("cursor");
    const size = url.searchParams.get("size");

    // Initial load without size parameter - let component handle with dynamic sizing
    if (!size) {
        return {
            shares: [],
            pagination: null,
            requestedSize: null,
            isInitialLoad: true
        };
    }

    // Navigation with known size - fetch data normally
    try {
        const data = await fetchShares(size, cursor);
        return {
            shares: data.items || [],
            pagination: {
                currentPage: data.current_page,
                previousPage: data.previous_page,
                nextPage: data.next_page,
                total: null // Always null for cursor-based pagination
            },
            requestedSize: parseInt(size, 10),
            isInitialLoad: false
        };
    } catch (error) {
        throw new Error(`Failed to load shares: ${error.message}`);
    }
}

const Sharing = () => {
    const loaderData = useLoaderData();
    const { shares: initialShares, pagination: initialPagination, requestedSize, isInitialLoad } = loaderData;

    // State
    const [shares, setShares] = useState(initialShares);
    const [pagination, setPagination] = useState(initialPagination);
    const [isLoading, setIsLoading] = useState(isInitialLoad);

    // Hooks
    const { setSnackbar } = useSnackbar();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    // Dynamic page size calculation
    const { pageSize, containerRef, isCalculated, recalculate } = useDynamicPageSize(DYNAMIC_PAGE_SIZE_CONFIG);

    // Memoized values
    const hasShares = shares.length > 0;
    const shouldOptimizePage = isCalculated && !isInitialLoad && requestedSize && pageSize !== requestedSize;

    // Load shares with specified parameters
    const loadShares = useCallback(async (size, cursor = null) => {
        setIsLoading(true);

        try {
            const data = await fetchShares(size, cursor);

            setShares(data.items || []);
            setPagination({
                currentPage: data.current_page,
                previousPage: data.previous_page,
                nextPage: data.next_page,
                total: null // Always null for cursor-based pagination
            });
        } catch (err) {
            setSnackbar({
                open: true,
                message: `Error loading shares: ${err.message}`,
                severity: "error",
            });
        } finally {
            setIsLoading(false);
        }
    }, [setSnackbar]);

    // Handle navigation
    const navigateToPage = useCallback((cursor) => {
        const params = new URLSearchParams(searchParams);
        if (cursor) {
            params.set("cursor", cursor);
        } else {
            params.delete("cursor");
        }
        params.set("size", pageSize.toString());
        navigate(`/sharing?${params.toString()}`);
    }, [searchParams, pageSize, navigate]);

    // Page navigation handlers
    const goToNextPage = useCallback(() => {
        if (pagination?.nextPage) {
            navigateToPage(pagination.nextPage);
        }
    }, [pagination?.nextPage, navigateToPage]);

    const goToPreviousPage = useCallback(() => {
        if (pagination?.previousPage) {
            navigateToPage(pagination.previousPage);
        }
    }, [pagination?.previousPage, navigateToPage]);

    // Share actions
    const deleteShare = useCallback(async (shareId) => {
        try {
            const response = await fetch(`/api/shares/${shareId}`, {
                method: "DELETE",
            });

            if (response.ok) {
                setShares(current => current.filter(share => share.id !== shareId));
                setSnackbar({
                    open: true,
                    message: "Share deleted successfully",
                    severity: "success",
                });
            } else {
                throw new Error(`Failed to delete share: ${response.statusText}`);
            }
        } catch (err) {
            setSnackbar({
                open: true,
                message: `Error deleting share: ${err.message}`,
                severity: "error",
            });
        }
    }, [setSnackbar]);

    const copyToClipboard = useCallback(async (url) => {
        try {
            await navigator.clipboard.writeText(url);
            setSnackbar({
                open: true,
                message: "Share URL copied to clipboard",
                severity: "success",
            });
        } catch {
            setSnackbar({
                open: true,
                message: "Failed to copy URL",
                severity: "error",
            });
        }
    }, [setSnackbar]);

    // Effects
    // Handle initial load with dynamic page size
    useEffect(() => {
        if (isCalculated && isInitialLoad) {
            loadShares(pageSize);
        }
    }, [isCalculated, isInitialLoad, pageSize, loadShares]);

    // Update state when loader provides new data (navigation)
    useEffect(() => {
        if (!isInitialLoad && initialShares) {
            setShares(initialShares);
            setPagination(initialPagination);
            setIsLoading(false);
        }
    }, [initialShares, initialPagination, isInitialLoad]);

    // Recalculate page size when shares are rendered (to measure actual heights)
    useEffect(() => {
        if (hasShares && isCalculated) {
            // Small delay to ensure DOM is updated
            const timer = setTimeout(() => {
                recalculate();
            }, 100);
            
            return () => clearTimeout(timer);
        }
    }, [hasShares, isCalculated, recalculate, shares.length]);

    // Handle page size optimization for existing data
    useEffect(() => {
        if (shouldOptimizePage) {
            const newSearchParams = new URLSearchParams(searchParams);
            newSearchParams.set("size", pageSize.toString());
            newSearchParams.delete("cursor"); // Reset to first page with new size
            navigate(`?${newSearchParams.toString()}`, { replace: true });
        }
    }, [shouldOptimizePage, searchParams, pageSize, navigate]);

    return (
        <div className={styles.sharingContainer}>
            <ChatboxHeader />
            <div className={styles.sharingContent} ref={containerRef}>
                <h1 className={styles.sharingTitle}>My Shares</h1>

                {(isLoading || !hasShares) ? (
                    <EmptyState isLoading={isLoading} />
                ) : (
                    <div>
                        <SharesHeader
                            sharesCount={shares.length}
                            pageSize={pageSize}
                            isCalculated={isCalculated}
                        />

                        <div className={styles.sharesList} data-list-container>
                            {shares.map((share) => (
                                <ShareCard
                                    key={share.id}
                                    share={share}
                                    onCopy={copyToClipboard}
                                    onDelete={deleteShare}
                                />
                            ))}
                        </div>

                        {pagination && (
                            <Pagination
                                currentPage={pagination.currentPage}
                                previousPage={pagination.previousPage}
                                nextPage={pagination.nextPage}
                                total={pagination.total}
                                onPrevious={goToPreviousPage}
                                onNext={goToNextPage}
                            />
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Sharing;
Sharing.loader = loader;
